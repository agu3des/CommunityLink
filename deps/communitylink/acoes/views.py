from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib import messages
from .models import Acao, Inscricao
from .forms import AcaoForm

# --- CRUD Views ---

# READ (List)
def acao_list(request):
    """ Mostra a lista de todas as ações. """
    acoes = Acao.objects.all().order_by('-data') # Mais recentes primeiro
    context = {'acoes': acoes}
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

    # --- MUDANÇA AQUI ---
    # Verifica se o usuário logado NÃO está no grupo 'Organizadores'
    if not request.user.groups.filter(name='Organizadores').exists():
        messages.error(request, 'Apenas organizadores podem criar ações.')
        return redirect('acao_list')
    # --- FIM DA MUDANÇA ---

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
    if acao.organizador != request.user:
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
    
    if acao.organizador != request.user:
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
    else:
        messages.info(request, f'Você já tem uma solicitação ({inscricao.get_status_display()}) para esta ação.')

    return redirect(acao.get_absolute_url())


@login_required
def acao_manage(request, pk):
    """ Página para o organizador gerenciar as solicitações. """
    acao = get_object_or_404(Acao, pk=pk)

    if acao.organizador != request.user:
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
    inscricoes = Inscricao.objects.filter(voluntario=request.user).order_by('acao__data')
    
    context = {
        'inscricoes': inscricoes
    }
    return render(request, 'acoes/minhas_inscricoes.html', context)