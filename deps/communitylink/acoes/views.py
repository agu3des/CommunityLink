from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from django.utils.http import url_has_allowed_host_and_scheme
from django.http import HttpResponseNotAllowed
from django.http import HttpResponseForbidden
from django.contrib import messages
from .models import Acao, Inscricao, Notificacao
from .forms import AcaoForm, SignUpForm, SignInForm, UserUpdateForm, PerfilUpdateForm
from django.db.models import Q # Importante para filtros complexos
import datetime # Importante para o filtro de data
from django.urls import reverse # Para criar links nas notificações
from django.utils import timezone # para a lista de acoes gerais ser mostrada de hoje em diante

# --- FUNÇÃO AUXILIAR DE PAGINAÇÃO ---
def paginar_queryset(request, queryset, itens_por_pagina=5, param_name='page'):
    """
    Pagina um queryset e retorna o objeto da página atual.
    param_name permite usar nomes diferentes na URL (ex: page_acoes, page_inscricoes)
    """
    paginator = Paginator(queryset, itens_por_pagina)
    page_number = request.GET.get(param_name)
    page_obj = paginator.get_page(page_number)
    return page_obj

# --- Lógica de Filtro Reutilizável ---
# (Vamos colocar a lógica de filtro aqui para não repetir)
def filtrar_acoes_queryset(request, queryset):
    """ Aplica filtros de GET a um queryset de Ações ou Inscrições. """
    
    # Pega os valores da URL (do formulário GET)
    categoria_filter = request.GET.get('categoria')
    local_filter = request.GET.get('local')
    data_inicio_filter = request.GET.get('data_inicio')

    # Define o prefixo de busca (para o modelo Inscricao)
    # Se o queryset for de Inscrição, precisamos filtrar por 'acao__categoria'
    prefix = 'acao__' if queryset.model == Inscricao else ''

    if categoria_filter:
        queryset = queryset.filter(**{f'{prefix}categoria': categoria_filter})
    
    if local_filter:
        queryset = queryset.filter(**{f'{prefix}local__icontains': local_filter})
        
    if data_inicio_filter:
        try:
            # Converte a data do filtro
            data_filtro = datetime.datetime.strptime(data_inicio_filter, '%Y-%m-%d').date()
            # Filtra por 'data__gte' (maior ou igual)
            queryset = queryset.filter(**{f'{prefix}data__gte': data_filtro})
        except ValueError:
            pass # Ignora data inválida

    return queryset

# --- CRUD Views ---

# READ (List)
def acao_list(request):
    """ Mostra a lista de todas as ações. """
    # filtra apenas ações de hoje em diante.
    acoes_list = Acao.objects.filter(data__gte=timezone.localdate())

    # --- Aplica os filtros do formulário (categoria, local, etc.) ---
    acoes_list = filtrar_acoes_queryset(request, acoes_list)
    
    # Ordena DEPOIS de filtrar
    acoes_list = acoes_list.order_by('data')

    # Paginação
    page_obj = paginar_queryset(request, acoes_list, itens_por_pagina=10)

    context = {
        'acoes': page_obj,
        'categorias_choices': Acao.CATEGORIA_CHOICES, # Passa as opções de categoria
        'filter_values': request.GET, # Passa os valores do filtro (para preencher o form)
        'page_param': 'page' # Nome do parametro na URL
    }
    return render(request, 'acoes/acao_list.html', context)

# READ (Detail)
def acao_detail(request, pk):
    """ Mostra os detalhes de uma única ação. """
    acao = get_object_or_404(Acao, pk=pk)
    
    # Lógica de inscrição
    ja_inscrito = False
    inscricao_status = None
    if request.user.is_authenticated:
        try:
            inscricao = Inscricao.objects.get(acao=acao, voluntario=request.user)
            ja_inscrito = True
            inscricao_status = inscricao.get_status_display()
        except Inscricao.DoesNotExist:
            ja_inscrito = False
            
    context = {
        'acao': acao,
        'ja_inscrito': ja_inscrito,
        'inscricao_status': inscricao_status,
        'is_owner': acao.organizador == request.user
    }
    return render(request, 'acoes/acao_detail.html', context)

# CREATE
@login_required # Exige que o usuário esteja logado
def acao_create(request):
    """ Cria uma nova ação. """
    
    # Verifica se o usuário NÃO é organizador E TAMBÉM NÃO é superuser
    is_organizador = request.user.groups.filter(name='Organizadores').exists()
    if not is_organizador and not request.user.is_superuser:
        messages.error(request, 'Apenas organizadores podem criar ações.')
        return redirect('acoes:acao_list')
    
    if request.method == 'POST':
        form = AcaoForm(request.POST)
        if form.is_valid():

            # --- Validação da Data ---
            data_da_acao = form.cleaned_data.get('data')
            
            # Verifica se a data foi preenchida e se é no passado
            if data_da_acao and data_da_acao < timezone.now():
                # Adiciona um erro ao campo 'data' do formulário
                form.add_error('data', 'A data da ação não pode ser no passado.')
                messages.error(request, 'Por favor, corrija o erro no formulário.')
            else:
                # Se a data for válida, salva a ação
                acao = form.save(commit=False) 
                acao.organizador = request.user 
                acao.save()
                messages.success(request, 'Ação criada com sucesso!')
                return redirect(acao.get_absolute_url())
    else:
        form = AcaoForm()
        
    context = {'form': form, 'is_create': True}
    return render(request, 'acoes/acao_form.html', context)

# UPDATE
@login_required
def acao_update(request, pk):
    """ Atualiza uma ação existente. """
    acao = get_object_or_404(Acao, pk=pk)

    # Verifica se o usuário logado é o organizador
    # Superusuários também devem poder editar
    if acao.organizador != request.user and not request.user.is_superuser:
        messages.error(request, 'Você não tem permissão para editar esta ação.')
        return redirect(acao.get_absolute_url())
    
    # --- TRAVA DE SEGURANÇA PARA AÇÕES PASSADAS ---
    if acao.ja_aconteceu:
        messages.error(request, 'Esta ação já foi concluída e não pode mais ser editada.')
        return redirect(acao.get_absolute_url())

    if request.method == 'POST':
        form = AcaoForm(request.POST, instance=acao)
        if form.is_valid():
            # validação da data (igual ao create)
            data_da_acao = form.cleaned_data.get('data')
            if data_da_acao and data_da_acao < timezone.now():
                form.add_error('data', 'A data da ação não pode ser no passado!')
                return render(request, 'acoes/acao_form.html', {'form': form, 'acao': acao})
            acao = form.save()
            messages.success(request, 'Ação atualizada com sucesso!')

            # --- NOVO: Notificar voluntários sobre a edição ---
            # Pega todos que estão aceitos ou pendentes
            inscritos = Inscricao.objects.filter(acao=acao, status__in=['ACEITO', 'PENDENTE'])
            for inscr in inscritos:
                Notificacao.objects.create(
                    destinatario=inscr.voluntario,
                    mensagem=f"A ação '{acao.titulo}' sofreu alterações pelo organizador.",
                    link=reverse('acoes:acao_detail', args=[acao.pk])
                )
            
            return redirect(acao.get_absolute_url())
    else:
        form = AcaoForm(instance=acao)
        
    context = {'form': form, 'acao': acao, 'is_create': False}
    return render(request, 'acoes/acao_form.html', context)

# DELETE
@login_required
def acao_delete(request, pk):
    """ Deleta uma ação e notifica os inscritos """
    acao = get_object_or_404(Acao, pk=pk)
    
    # Superusuários também devem poder deletar
    if acao.organizador != request.user and not request.user.is_superuser:
        messages.error(request, 'Você não tem permissão para deletar esta ação.')
        return redirect(acao.get_absolute_url())
    
    # --- TRAVA DE SEGURANÇA ---
    if acao.ja_aconteceu:
        messages.error(request, 'Não é possível deletar uma ação que já aconteceu (para manter o histórico).')
        return redirect(acao.get_absolute_url())

    if request.method == 'POST':
        # --- PASSO A: Guardar informações antes de deletar ---
        titulo_acao = acao.titulo
        
        # Pegamos os usuários que estão inscritos (Inscricao)
        # Filtramos por status para não avisar quem já tinha sido rejeitado ou cancelado, se quiser
        inscricoes_afetadas = Inscricao.objects.filter(acao=acao, status__in=['ACEITO', 'PENDENTE'])
        
        # Criamos uma lista com os objetos User dos voluntários
        # É IMPORTANTE converter para list() agora, para buscar do banco antes de deletar
        voluntarios_para_avisar = [i.voluntario for i in inscricoes_afetadas]

        # --- PASSO B: Deletar a ação ---
        # Isso vai apagar a Ação e todas as Inscrições (CASCADE)
        acao.delete()

        # --- PASSO C: Enviar Notificações ---
        for voluntario in voluntarios_para_avisar:
            Notificacao.objects.create(
                destinatario=voluntario,
                mensagem=f"Atenção: A ação '{titulo_acao}' foi cancelada/excluída pelo organizador.",
                link="" # DEIXE VAZIO! A página da ação não existe mais (daria Erro 404)
            )

        messages.success(request, 'Ação deletada e voluntários notificados com sucesso.')
        return redirect('acoes:acao_list')
        
    context = {'acao': acao}
    return render(request, 'acoes/acao_confirm_delete.html', context)

# --- Lógica de Inscrição ---

@login_required
def acao_apply(request, pk):
    """ View para um voluntário se inscrever em uma ação. """
    if request.method != 'POST':
        return redirect('acoes:acao_detail', pk=pk)

    acao = get_object_or_404(Acao, pk=pk)

    # Organizador não pode se inscrever na própria ação
    if acao.organizador == request.user:
        messages.warning(request, 'Você não pode se voluntariar na sua própria ação.')
        return redirect(acao.get_absolute_url())
        
    # Verifica se já está cheio
    if acao.esta_cheia:
        messages.error(request, 'Esta ação já atingiu o número máximo de voluntários.')
        return redirect(acao.get_absolute_url())
    
    # Validação extra: não pode entrar se já passou
    if acao.ja_aconteceu:
        messages.error(request, 'Esta ação já foi concluída.')
        return redirect(acao.get_absolute_url())

    # Cria a inscrição (ou informa se já existe)
    # o .get_or_create() retorna (objeto, foi_criado)
    inscricao, created = Inscricao.objects.get_or_create(
        acao=acao,
        voluntario=request.user
    )

    # CASO 1: Nova inscrição (Created = True)
    if created:
        messages.success(request, 'Sua solicitação foi enviada! O organizador irá analisá-la.')
        # Notificar Organizador
        Notificacao.objects.create(
            destinatario=acao.organizador,
            mensagem=f"{request.user.username} solicitou participação em '{acao.titulo}'.",
            link=reverse('acoes:acao_manage', args=[acao.pk])
        )

    # CASO 2: Já existia, mas estava CANCELADA ou REJEITADA (Permitir tentar de novo)
    elif inscricao.status in ['CANCELADO', 'REJEITADO']:
        inscricao.status = 'PENDENTE'
        inscricao.save()
        messages.success(request, 'Sua solicitação foi reativada e enviada para análise!')
        
        # Notificar Organizador novamente
        Notificacao.objects.create(
            destinatario=acao.organizador,
            mensagem=f"{request.user.username} solicitou participação novamente em '{acao.titulo}'.",
            link=reverse('acoes:acao_manage', args=[acao.pk])
        )

    # CASO 3: Já existe e está Pendente ou Aceito
    else:
        messages.info(request, f'Você já tem uma solicitação ativa ({inscricao.get_status_display()}) para esta ação.')

    return redirect(acao.get_absolute_url())


@login_required
def acao_manage(request, pk):
    """ Página para o organizador gerenciar as solicitações. """
    acao = get_object_or_404(Acao, pk=pk)

    # Superusuários também devem poder gerenciar
    if acao.organizador != request.user and not request.user.is_superuser:
        messages.error(request, 'Você não tem permissão para gerenciar esta ação.')
        return redirect(acao.get_absolute_url())
        
    # Processa mudanças de status (Aceitar/Rejeitar)
    if request.method == 'POST':
        inscricao_id = request.POST.get('inscricao_id')
        novo_status = request.POST.get('status')
        
        if novo_status not in ['ACEITO', 'REJEITADO']:
            messages.error(request, 'Status inválido.')
            return redirect('acoes:acao_manage', pk=pk)
            
        try:
            inscricao = Inscricao.objects.get(id=inscricao_id, acao=acao)

            # Lógica para remover (que é basicamente cancelar/rejeitar alguém já aceito)
            if novo_status == 'REMOVIDO': 
                # --- TRAVA DE SEGURANÇA 2 ---
                if acao.ja_aconteceu:
                    messages.error(request, 'Você não pode remover voluntários de uma ação que já foi realizada.')
                    return redirect('acoes:acao_manage', pk=pk)
                # ----------------------------

                # Vamos usar o status CANCELADO ou REJEITADO. Usarei CANCELADO para diferenciar.
                inscricao.status = 'CANCELADO'
                inscricao.save()
                messages.warning(request, f'{inscricao.voluntario.username} foi removido da ação.')
                
                # Notificar o voluntário
                Notificacao.objects.create(
                    destinatario=inscricao.voluntario,
                    mensagem=f"Você foi removido da ação '{acao.titulo}' pelo organizador.",
                    link=reverse('acoes:acao_detail', args=[acao.pk])
                )

            elif novo_status in ['ACEITO', 'REJEITADO']:
                # --- TRAVA DE SEGURANÇA 3 (Opcional, mas recomendada) ---
                # Impede aceitar gente nova em ação velha
                if acao.ja_aconteceu:
                    messages.error(request, 'Esta ação já foi concluída. Não é possível alterar inscrições.')
                    return redirect('acoes:acao_manage', pk=pk)
            
                # Se for aceitar, verifica se ainda há vagas
                if novo_status == 'ACEITO' and acao.esta_cheia:
                    messages.warning(request, 'Não foi possível aceitar. As vagas estão preenchidas.')
                else:
                    inscricao.status = novo_status
                    inscricao.save()
                    status_display = "Aceita" if novo_status == 'ACEITO' else "Rejeitada"
                    messages.success(request, f'Solicitação de {inscricao.voluntario.username} foi atualizada.')

                    # --- Criar Notificação para o Voluntário ---
                    Notificacao.objects.create(
                        destinatario=inscricao.voluntario,
                        mensagem=f"Sua inscrição para '{acao.titulo}' foi {status_display}.",
                        link=reverse('acoes:acao_detail', args=[acao.pk]) # Link para a página da ação
                    )
                
        except Inscricao.DoesNotExist:
            messages.error(request, 'Solicitação não encontrada.')
            
        return redirect('acoes:acao_manage', pk=pk)


    # Pega todas as inscrições para esta ação
    solicitacoes_pendentes = acao.inscricao_set.filter(status='PENDENTE').order_by('data_inscricao')
    solicitacoes_aceitas = acao.inscricao_set.filter(status='ACEITO').order_by('voluntario__username')
    solicitacoes_rejeitadas = acao.inscricao_set.filter(status='REJEITADO').order_by('voluntario__username')

    context = {
        'acao': acao,
        'pendentes': solicitacoes_pendentes,
        'aceitas': solicitacoes_aceitas,
        'rejeitadas': solicitacoes_rejeitadas,
    }
    return render(request, 'acoes/acao_manage.html', context)

    # --- NOVA VIEW PARA VOLUNTÁRIOS ---

@login_required
def minhas_inscricoes(request):
    """ Mostra todas as ações nas quais o usuário logado se inscreveu. """
    
    # Filtra as inscrições pelo usuário logado
    inscricoes_list = Inscricao.objects.filter(voluntario=request.user)

    inscricoes_list = filtrar_acoes_queryset(request, inscricoes_list)
    
    inscricoes_list = inscricoes_list.order_by('acao__data')

    # Paginação
    page_obj = paginar_queryset(request, inscricoes_list)
    
    context = {
        'inscricoes': page_obj,
        'categorias_choices': Acao.CATEGORIA_CHOICES, # Passa as opções
        'filter_values': request.GET, # Passa os valores
        'page_param': 'page'
    }
    return render(request, 'acoes/minhas_inscricoes.html', context)

# --- NOVA VIEW PARA ORGANIZADORES ---

@login_required
def minhas_acoes(request):
    """ Mostra todas as ações criadas pelo usuário logado (organizador). """
    
    # Filtra as ações pelo organizador (usuário logado)
    acoes_list = Acao.objects.filter(organizador=request.user)

    acoes_list = filtrar_acoes_queryset(request, acoes_list)
        
    acoes_list = acoes_list.order_by('-data')

    # Paginação
    page_obj = paginar_queryset(request, acoes_list)
    
    context = {
        'acoes': page_obj,
        'categorias_choices': Acao.CATEGORIA_CHOICES, # Passa as opções
        'filter_values': request.GET, # Passa os valores
        'page_param': 'page'
    }
    return render(request, 'acoes/minhas_acoes.html', context)

# --- VIEW PARA NOTIFICACOES ---

@login_required
def notificacoes_list(request):
    qs = Notificacao.objects.filter(destinatario=request.user)
    
    # Marcando como lida (Pode manter aqui ou fazer via AJAX, mas vamos manter simples)
    # OBS: Ao paginar, ele só vai marcar como lida as 10 da página atual.
    nao_lidas = qs.filter(lida=False)
    
    # Paginação
    page_obj = paginar_queryset(request, qs, itens_por_pagina=10)
    
    # Atualiza as que estão SENDO EXIBIDAS agora
    for notif in page_obj:
        if not notif.lida:
            notif.lida = True
            notif.save()

    # Recalcula contagem geral para o botão limpar
    lidas_count = Notificacao.objects.filter(destinatario=request.user, lida=True).count()

    context = {
        'notificacoes': page_obj,
        'lidas_count': lidas_count,
        'page_param': 'page'
    }
    return render(request, 'acoes/notificacoes_list.html', context)

@login_required
def notificacoes_clear(request):
    """ Deleta todas as notificações LIDAS do usuário. """
    
    # Só aceita POST para segurança
    if request.method != 'POST':
        return redirect('acoes:notificacoes_list')

    # Deleta apenas as notificações que já foram lidas
    Notificacao.objects.filter(destinatario=request.user, lida=True).delete()
    
    messages.success(request, 'Notificações lidas foram apagadas.')
    
    return redirect('acoes:notificacoes_list')

# --- VIEWS DE AUTENTICAÇÃO ---
def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            # 1. Salva o usuário no banco (mas ainda sem o grupo)
            user = form.save()
            # 2. Pega a escolha do formulário
            tipo = form.cleaned_data.get('tipo_usuario')

            # 3. Adiciona ao grupo correto
            # Usamos get_or_create para garantir que o grupo exista e não dê erro
            if tipo == 'ORGANIZADOR':
                group, created = Group.objects.get_or_create(name='Organizadores')
                user.groups.add(group)
            else: # Default é Voluntario
                group, created = Group.objects.get_or_create(name='Voluntarios')
                user.groups.add(group)

            # 4. Loga o usuário e redireciona
            login(request, user)

            if tipo == 'ORGANIZADOR':
                 return redirect('acoes:minhas_acoes')
            return redirect('acoes:acao_list')
    else:
        form = SignUpForm()
    return render(request, 'acoes/sign_up.html', {'form': form})


def signin_view(request):
    if request.method == 'POST':
        form = SignInForm(request=request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_url = request.POST.get('next') or request.GET.get('next')
            if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
                return redirect(next_url)
            return redirect('acoes:acao_list')
    else:
        form = SignInForm()
    return render(request, 'acoes/sign_in.html', {'form': form})


def logout_view(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    logout(request)
    return redirect('acoes:signin')

# --- VIEWS PARA ATUALIZAR PERFIL DO USUÁRIO ---
@login_required
def perfil_view(request):
    """ Exibe e processa a atualização de dados do usuário. """
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = PerfilUpdateForm(request.POST, instance=request.user.perfil)
        
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Seu perfil foi atualizado com sucesso!')
            return redirect('acoes:perfil')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = PerfilUpdateForm(instance=request.user.perfil)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, 'acoes/perfil.html', context)

@login_required
def historico_view(request):
    hoje = timezone.now()
    
    is_organizador = request.user.groups.filter(name='Organizadores').exists()

    # --- Lógica de Salvar Comentário ---
    if request.method == 'POST':
        # --- CENÁRIO A: Organizador salvando notas na Ação ---
        if 'acao_id' in request.POST and is_organizador:
            acao_id = request.POST.get('acao_id')
            notas = request.POST.get('notas_organizador')
            # Garante que a ação pertence ao usuário logado
            acao = get_object_or_404(Acao, pk=acao_id, organizador=request.user)
            acao.notas_organizador = notas
            acao.save()
            messages.success(request, 'Suas notas sobre a ação foram salvas.')
            
        # --- CENÁRIO B: Voluntário salvando comentário na Inscrição ---
        elif 'inscricao_id' in request.POST:
            inscricao_id = request.POST.get('inscricao_id')
            comentario_texto = request.POST.get('comentario')
            inscricao = get_object_or_404(Inscricao, id=inscricao_id, voluntario=request.user)
            inscricao.comentario = comentario_texto
            inscricao.save()
            messages.success(request, 'Seu comentário foi salvo!')
        return redirect('acoes:historico')
    
    # --- Lógica de Exibição (GET) ---
    
    # 1. Histórico de PARTICIPAÇÃO (Todo mundo tem, inclusive organizadores)
    qs_participacao = Inscricao.objects.filter(
        voluntario=request.user, 
        status__in=['ACEITO', 'CANCELADO'], 
        acao__data__lt=hoje
    )
    # Aplica filtros
    qs_participacao = filtrar_acoes_queryset(request, qs_participacao).order_by('-acao__data')

    # Paginando com nome diferente 'page_part'
    page_participacoes = paginar_queryset(request, qs_participacao, 5, param_name='page_part')

    # 2. Histórico de ORGANIZAÇÃO (Apenas se for organizador)
    page_organizadas = None
    
    if is_organizador:
        qs_organizacao = Acao.objects.filter(organizador=request.user, data__lt=hoje)
        # Aplica filtros
        qs_organizacao = filtrar_acoes_queryset(request, qs_organizacao).order_by('-data')
        # Paginando com nome diferente 'page_org'
        page_organizadas = paginar_queryset(request, qs_organizacao, 5, param_name='page_org')
    context = {
        'historico_participacoes': page_participacoes,
        'historico_organizadas': page_organizadas, # Será None se não for organizador
        'is_organizador': is_organizador,
        'titulo_historico': "Meu Histórico",
        'categorias_choices': Acao.CATEGORIA_CHOICES,
        'filter_values': request.GET 
    }
    return render(request, 'acoes/historico.html', context)


@login_required
def inscricao_cancel(request, pk):
    """ Permite ao voluntário cancelar sua própria inscrição. """
    inscricao = get_object_or_404(Inscricao, pk=pk, voluntario=request.user)
    acao = inscricao.acao
    
    # Trava de segurança: não cancela se já passou
    if acao.ja_aconteceu:
        messages.error(request, 'Não é possível cancelar a inscrição em uma ação que já aconteceu.')
        return redirect('acoes:minhas_inscricoes')

    if request.method == 'POST':
        # Guardamos o status antes de mudar, para saber se precisamos apagar a notificação
        status_anterior = inscricao.status
        
        # Muda o status
        inscricao.status = 'CANCELADO'
        inscricao.save()
        
        messages.success(request, f"Sua inscrição em '{acao.titulo}' foi cancelada.")

        # --- LÓGICA DE APAGAR A NOTIFICAÇÃO DO ORGANIZADOR ---
        # Só apagamos se o organizador ainda não tinha aceito (ou seja, estava PENDENTE)
        if status_anterior == 'PENDENTE':
            # O link que foi enviado na notificação original
            link_alvo = reverse('acoes:acao_manage', args=[acao.pk])
            
            # Buscamos a notificação exata para deletar:
            # 1. Para o organizador dessa ação
            # 2. Que tenha o link de gerenciar essa ação específica
            # 3. Que contenha o nome do usuário que está cancelando (para não apagar notif de outros)
            Notificacao.objects.filter(
                destinatario=acao.organizador,
                link=link_alvo,
                mensagem__contains=request.user.username # Procura o nome do voluntário na mensagem
            ).delete() # <--- ISSO REMOVE A NOTIFICAÇÃO DO BANCO
        
        # (Opcional) Se você quiser avisar o organizador que ele cancelou
        # Apenas se ele JÁ TIVESSE SIDO ACEITO. Se estava pendente, melhor só sumir.
        elif status_anterior == 'ACEITO':
            Notificacao.objects.create(
                destinatario=acao.organizador,
                mensagem=f"{request.user.username} cancelou a inscrição confirmada na ação '{acao.titulo}'.",
                link=reverse('acoes:acao_manage', args=[acao.pk])
            )

    return redirect('acoes:minhas_inscricoes')