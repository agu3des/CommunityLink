from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib import messages
from .models import Acao, Inscricao, Notificacao
from .forms import AcaoForm
from django.db.models import Q # Importante para filtros complexos
import datetime # Importante para o filtro de data
from django.urls import reverse # Para criar links nas notificações

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
    acoes_list = Acao.objects.all() # Começa com todas as ações

    # --- MUDANÇA: Aplica o filtro ---
    acoes_list = filtrar_acoes_queryset(request, acoes_list)
    
    # Ordena DEPOIS de filtrar
    acoes_list = acoes_list.order_by('-data')

    context = {
        'acoes': acoes_list,
        'categorias_choices': Acao.CATEGORIA_CHOICES, # Passa as opções de categoria
        'filter_values': request.GET # Passa os valores do filtro (para preencher o form)
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
        'is_organizador': acao.organizador == request.user
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
        return redirect('acao_list')
    
    if request.method == 'POST':
        form = AcaoForm(request.POST)
        if form.is_valid():
            # Não salva no banco ainda, precisamos adicionar o organizador
            acao = form.save(commit=False) 
            acao.organizador = request.user # Define o organizador como o usuário logado
            acao.save()
            messages.success(request, 'Ação criada com sucesso!')
            return redirect(acao.get_absolute_url()) # Redireciona para os detalhes da ação
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

    if request.method == 'POST':
        form = AcaoForm(request.POST, instance=acao)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ação atualizada com sucesso!')
            return redirect(acao.get_absolute_url())
    else:
        form = AcaoForm(instance=acao)
        
    context = {'form': form, 'acao': acao, 'is_create': False}
    return render(request, 'acoes/acao_form.html', context)

# DELETE
@login_required
def acao_delete(request, pk):
    """ Deleta uma ação. """
    acao = get_object_or_404(Acao, pk=pk)
    
    # Superusuários também devem poder deletar
    if acao.organizador != request.user and not request.user.is_superuser:
        messages.error(request, 'Você não tem permissão para deletar esta ação.')
        return redirect(acao.get_absolute_url())

    if request.method == 'POST':
        acao.delete()
        messages.success(request, 'Ação deletada com sucesso.')
        return redirect('acao_list') # Redireciona para a lista de ações
        
    context = {'acao': acao}
    return render(request, 'acoes/acao_confirm_delete.html', context)

# --- Lógica de Inscrição ---

@login_required
def acao_apply(request, pk):
    """ View para um voluntário se inscrever em uma ação. """
    if request.method != 'POST':
        return redirect('acao_detail', pk=pk)

    acao = get_object_or_404(Acao, pk=pk)

    # Organizador não pode se inscrever na própria ação
    if acao.organizador == request.user:
        messages.warning(request, 'Você não pode se voluntariar na sua própria ação.')
        return redirect(acao.get_absolute_url())
        
    # Verifica se já está cheio
    if acao.esta_cheia:
        messages.error(request, 'Esta ação já atingiu o número máximo de voluntários.')
        return redirect(acao.get_absolute_url())

    # Cria a inscrição (ou informa se já existe)
    # o .get_or_create() retorna (objeto, foi_criado)
    inscricao, created = Inscricao.objects.get_or_create(
        acao=acao,
        voluntario=request.user
    )

    if created:
        messages.success(request, 'Sua solicitação foi enviada! O organizador irá analisá-la.')

        # --- Criar Notificação para o Organizador ---
        Notificacao.objects.create(
            destinatario=acao.organizador,
            mensagem=f"{request.user.username} solicitou participação em '{acao.titulo}'.",
            link=reverse('acao_manage', args=[acao.pk]) # Link para a página de gerenciamento
        )
    else:
        messages.info(request, f'Você já tem uma solicitação ({inscricao.get_status_display()}) para esta ação.')

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
            return redirect('acao_manage', pk=pk)
            
        try:
            inscricao = Inscricao.objects.get(id=inscricao_id, acao=acao)
            
            # Se for aceitar, verifica se ainda há vagas
            if novo_status == 'ACEITO' and acao.esta_cheia:
                messages.warning(request, 'Não foi possível aceitar. As vagas estão preenchidas.')
            else:
                inscricao.status = novo_status
                inscricao.save()
                messages.success(request, f'Solicitação de {inscricao.voluntario.username} foi atualizada.')

                # --- Criar Notificação para o Voluntário ---
                status_display = "Aceita" if novo_status == 'ACEITO' else "Rejeitada"
                Notificacao.objects.create(
                    destinatario=inscricao.voluntario,
                    mensagem=f"Sua inscrição para '{acao.titulo}' foi {status_display}.",
                    link=reverse('acao_detail', args=[acao.pk]) # Link para a página da ação
                )
                
        except Inscricao.DoesNotExist:
            messages.error(request, 'Solicitação não encontrada.')
            
        return redirect('acao_manage', pk=pk)


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
    
    context = {
        'inscricoes': inscricoes_list,
        'categorias_choices': Acao.CATEGORIA_CHOICES, # Passa as opções
        'filter_values': request.GET # Passa os valores
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
    
    context = {
        'acoes': acoes_list,
        'categorias_choices': Acao.CATEGORIA_CHOICES, # Passa as opções
        'filter_values': request.GET # Passa os valores
    }
    return render(request, 'acoes/minhas_acoes.html', context)

# --- VIEW PARA NOTIFICACOES ---

@login_required
def notificacoes_list(request):
    """ Mostra a lista de notificações do usuário e marca como lidas. """
    
    # Pega todas as notificações do usuário logado
    notificacoes = Notificacao.objects.filter(destinatario=request.user)
    
    # Pega as não lidas para atualizar
    nao_lidas = notificacoes.filter(lida=False)

    # Pega o número de lidas para o botão
    lidas_count = notificacoes.filter(lida=True).count()
    
    # Marca todas como lidas (ao visitar a página)
    nao_lidas.update(lida=True)
    
    context = {
        'notificacoes': notificacoes,
        'lidas_count': lidas_count # Passa a contagem para o template
    }
    return render(request, 'acoes/notificacoes_list.html', context)

@login_required
def notificacoes_clear(request):
    """ Deleta todas as notificações LIDAS do usuário. """
    
    # Só aceita POST para segurança
    if request.method != 'POST':
        return redirect('notificacoes_list')

    # Deleta apenas as notificações que já foram lidas
    Notificacao.objects.filter(destinatario=request.user, lida=True).delete()
    
    messages.success(request, 'Notificações lidas foram apagadas.')
    
    return redirect('notificacoes_list')