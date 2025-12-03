"""
Testes das Views de Inscrições e Notificações

Este arquivo testa:
- Inscrição de voluntários em ações
- Gerenciamento de inscrições pelo organizador
- Minhas inscrições (para voluntários)
- Notificações
"""

import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from acoes.models import Acao, Inscricao, Notificacao


# ============================================
# SPRINT 1 - Inscrições
# ============================================


@pytest.mark.django_db
class TestAcaoApplyView:
    """
    CT-V100: Testes da view de inscrição em ações
    """

    def test_inscricao_requer_login(self, client, acao_futura):
        """
        CT-V100.1: Inscrição requer autenticação
        Resultado Esperado: Redirect para login
        """
        url = reverse('acao_apply', args=[acao_futura.pk])
        response = client.post(url)
        assert response.status_code == 302

    def test_inscricao_requer_post(self, client_logged_voluntario, acao_futura):
        """
        CT-V100.2: Inscrição só aceita método POST
        Resultado Esperado: Redirect em GET
        """
        url = reverse('acao_apply', args=[acao_futura.pk])
        response = client_logged_voluntario.get(url)
        assert response.status_code == 302

    def test_voluntario_pode_se_inscrever(self, client_logged_voluntario, acao_futura, voluntario_user):
        """
        CT-V101: Voluntário se inscreve com sucesso em ação
        Resultado Esperado: Inscrição criada com status PENDENTE
        """
        url = reverse('acao_apply', args=[acao_futura.pk])
        response = client_logged_voluntario.post(url)

        # Verifica que a inscrição foi criada
        assert Inscricao.objects.filter(acao=acao_futura, voluntario=voluntario_user).exists()
        inscricao = Inscricao.objects.get(acao=acao_futura, voluntario=voluntario_user)
        assert inscricao.status == 'PENDENTE'

    def test_organizador_nao_pode_se_inscrever_propria_acao(self, client_logged_organizador, acao_futura, organizador_user):
        """
        CT-V102: Organizador não pode se inscrever na própria ação
        Resultado Esperado: Mensagem de aviso, sem inscrição criada
        """
        url = reverse('acao_apply', args=[acao_futura.pk])
        response = client_logged_organizador.post(url)

        # Verifica que NÃO criou inscrição
        assert not Inscricao.objects.filter(acao=acao_futura, voluntario=organizador_user).exists()

    def test_nao_pode_inscrever_em_acao_cheia(self, client_logged_voluntario, acao_cheia, voluntario_user):
        """
        CT-V103: Não é possível se inscrever em ação sem vagas
        Resultado Esperado: Mensagem de erro, sem inscrição criada
        """
        url = reverse('acao_apply', args=[acao_cheia.pk])
        response = client_logged_voluntario.post(url)

        # Verifica que NÃO criou inscrição
        assert not Inscricao.objects.filter(acao=acao_cheia, voluntario=voluntario_user).exists()

    def test_inscricao_duplicada_nao_cria_nova(self, client_logged_voluntario, acao_futura, voluntario_user):
        """
        CT-V104: Não é possível se inscrever 2x na mesma ação
        Resultado Esperado: Mensagem informativa, sem nova inscrição
        """
        # Primeira inscrição
        url = reverse('acao_apply', args=[acao_futura.pk])
        client_logged_voluntario.post(url)

        # Tenta segunda inscrição
        response = client_logged_voluntario.post(url)

        # Verifica que existe apenas 1 inscrição
        assert Inscricao.objects.filter(acao=acao_futura, voluntario=voluntario_user).count() == 1

    def test_inscricao_cria_notificacao_para_organizador(self, client_logged_voluntario, acao_futura, voluntario_user, organizador_user):
        """
        CT-V105: Inscrição cria notificação para o organizador
        Resultado Esperado: Notificação criada para o organizador
        """
        url = reverse('acao_apply', args=[acao_futura.pk])
        client_logged_voluntario.post(url)

        # Verifica que foi criada notificação para o organizador
        assert Notificacao.objects.filter(destinatario=organizador_user).exists()
        notificacao = Notificacao.objects.get(destinatario=organizador_user)
        assert voluntario_user.username in notificacao.mensagem
        assert acao_futura.titulo in notificacao.mensagem


@pytest.mark.django_db
class TestAcaoManageView:
    """
    CT-V110: Testes da view de gerenciamento de inscrições
    """

    def test_gerenciamento_requer_login(self, client, acao_futura):
        """
        CT-V110.1: Gerenciamento requer autenticação
        Resultado Esperado: Redirect para login
        """
        url = reverse('acao_manage', args=[acao_futura.pk])
        response = client.get(url)
        assert response.status_code == 302

    def test_apenas_organizador_pode_gerenciar(self, client_logged_voluntario, acao_futura):
        """
        CT-V110.2: Apenas organizador pode gerenciar inscrições
        Resultado Esperado: Mensagem de erro e redirect
        """
        url = reverse('acao_manage', args=[acao_futura.pk])
        response = client_logged_voluntario.get(url)
        assert response.status_code == 302

    def test_organizador_acessa_gerenciamento(self, client_logged_organizador, acao_futura):
        """
        CT-V110.3: Organizador acessa página de gerenciamento
        Resultado Esperado: Página renderizada com listas de inscrições
        """
        url = reverse('acao_manage', args=[acao_futura.pk])
        response = client_logged_organizador.get(url)

        assert response.status_code == 200
        assert 'pendentes' in response.context
        assert 'aceitas' in response.context
        assert 'rejeitadas' in response.context

    def test_organizador_aceita_inscricao(self, client_logged_organizador, inscricao_pendente):
        """
        CT-V111: Organizador aceita inscrição pendente
        Resultado Esperado: Status muda para ACEITO
        """
        url = reverse('acao_manage', args=[inscricao_pendente.acao.pk])
        data = {
            'inscricao_id': inscricao_pendente.id,
            'status': 'ACEITO'
        }

        response = client_logged_organizador.post(url, data)

        inscricao_pendente.refresh_from_db()
        assert inscricao_pendente.status == 'ACEITO'

    def test_organizador_rejeita_inscricao(self, client_logged_organizador, inscricao_pendente):
        """
        CT-V112: Organizador rejeita inscrição pendente
        Resultado Esperado: Status muda para REJEITADO
        """
        url = reverse('acao_manage', args=[inscricao_pendente.acao.pk])
        data = {
            'inscricao_id': inscricao_pendente.id,
            'status': 'REJEITADO'
        }

        response = client_logged_organizador.post(url, data)

        inscricao_pendente.refresh_from_db()
        assert inscricao_pendente.status == 'REJEITADO'

    def test_nao_pode_aceitar_quando_acao_cheia(self, client_logged_organizador, acao_cheia):
        """
        CT-V113: Não pode aceitar inscrição se ação já está cheia
        Resultado Esperado: Status permanece PENDENTE
        """
        # Cria nova inscrição pendente na ação cheia
        voluntario = User.objects.create_user('novo_vol', 'novo@test.com', 'pass')
        inscricao = Inscricao.objects.create(
            acao=acao_cheia,
            voluntario=voluntario,
            status='PENDENTE'
        )

        url = reverse('acao_manage', args=[acao_cheia.pk])
        data = {
            'inscricao_id': inscricao.id,
            'status': 'ACEITO'
        }

        response = client_logged_organizador.post(url, data)

        inscricao.refresh_from_db()
        assert inscricao.status == 'PENDENTE'  # Não foi aceita

    def test_mudanca_status_cria_notificacao_para_voluntario(self, client_logged_organizador, inscricao_pendente):
        """
        CT-V114: Mudança de status cria notificação para o voluntário
        Resultado Esperado: Notificação criada para o voluntário
        """
        voluntario = inscricao_pendente.voluntario

        url = reverse('acao_manage', args=[inscricao_pendente.acao.pk])
        data = {
            'inscricao_id': inscricao_pendente.id,
            'status': 'ACEITO'
        }

        client_logged_organizador.post(url, data)

        # Verifica que foi criada notificação para o voluntário
        assert Notificacao.objects.filter(destinatario=voluntario).exists()
        notificacao = Notificacao.objects.get(destinatario=voluntario)
        assert 'Aceita' in notificacao.mensagem

    def test_status_invalido_nao_aceito(self, client_logged_organizador, inscricao_pendente):
        """
        CT-V115: Status inválido não é aceito
        Resultado Esperado: Erro e status permanece inalterado
        """
        url = reverse('acao_manage', args=[inscricao_pendente.acao.pk])
        data = {
            'inscricao_id': inscricao_pendente.id,
            'status': 'STATUS_INVALIDO'
        }

        response = client_logged_organizador.post(url, data)

        inscricao_pendente.refresh_from_db()
        assert inscricao_pendente.status == 'PENDENTE'

    def test_superuser_pode_gerenciar_qualquer_acao(self, client, superuser, inscricao_pendente):
        """
        CT-V116: Superusuário pode gerenciar qualquer ação
        Resultado Esperado: Acesso permitido
        """
        client.force_login(superuser)
        url = reverse('acao_manage', args=[inscricao_pendente.acao.pk])
        response = client.get(url)

        assert response.status_code == 200


@pytest.mark.django_db
class TestMinhasInscricoesView:
    """
    CT-V120: Testes da view "Minhas Inscrições" (para voluntários)
    """

    def test_minhas_inscricoes_requer_login(self, client):
        """
        CT-V120.1: View requer autenticação
        Resultado Esperado: Redirect para login
        """
        url = reverse('minhas_inscricoes')
        response = client.get(url)
        assert response.status_code == 302

    def test_mostra_apenas_inscricoes_do_voluntario(self, client_logged_voluntario, acao_futura, voluntario_user):
        """
        CT-V120.2: Mostra apenas inscrições do voluntário logado
        Resultado Esperado: Apenas inscrições do usuário na lista
        """
        # Cria inscrição do voluntário logado
        inscricao1 = Inscricao.objects.create(acao=acao_futura, voluntario=voluntario_user)

        # Cria inscrição de outro voluntário
        outro_vol = User.objects.create_user('outro_vol', 'outro@test.com', 'pass')
        inscricao2 = Inscricao.objects.create(acao=acao_futura, voluntario=outro_vol)

        url = reverse('minhas_inscricoes')
        response = client_logged_voluntario.get(url)
        inscricoes = response.context['inscricoes']

        assert inscricao1 in inscricoes
        assert inscricao2 not in inscricoes

    def test_inscricoes_ordenadas_por_data_acao(self, client_logged_voluntario, organizador_user, voluntario_user):
        """
        CT-V120.3: Inscrições ordenadas por data da ação
        Resultado Esperado: Ações mais próximas primeiro
        """
        from django.utils import timezone
        from datetime import timedelta

        # Cria 3 ações com datas diferentes
        acao1 = Acao.objects.create(
            titulo='Ação em 30 dias',
            descricao='Teste',
            data=timezone.now() + timedelta(days=30),
            local='Local',
            numero_vagas=10,
            organizador=organizador_user
        )
        acao2 = Acao.objects.create(
            titulo='Ação em 7 dias',
            descricao='Teste',
            data=timezone.now() + timedelta(days=7),
            local='Local',
            numero_vagas=10,
            organizador=organizador_user
        )

        # Inscreve o voluntário nas 2 ações
        inscr1 = Inscricao.objects.create(acao=acao1, voluntario=voluntario_user)
        inscr2 = Inscricao.objects.create(acao=acao2, voluntario=voluntario_user)

        url = reverse('minhas_inscricoes')
        response = client_logged_voluntario.get(url)
        inscricoes = list(response.context['inscricoes'])

        # Ação mais próxima deve vir primeiro
        assert inscricoes[0] == inscr2
        assert inscricoes[1] == inscr1


# ============================================
# SPRINT 1 - Notificações
# ============================================


@pytest.mark.django_db
class TestNotificacoesListView:
    """
    CT-V130: Testes da view de listagem de notificações
    """

    def test_notificacoes_requer_login(self, client):
        """
        CT-V130.1: View requer autenticação
        Resultado Esperado: Redirect para login
        """
        url = reverse('notificacoes_list')
        response = client.get(url)
        assert response.status_code == 302

    def test_mostra_apenas_notificacoes_do_usuario(self, client_logged_voluntario, voluntario_user, organizador_user):
        """
        CT-V130.2: Mostra apenas notificações do usuário logado
        Resultado Esperado: Apenas notificações do usuário na lista
        """
        # Notificação do voluntário logado
        notif1 = Notificacao.objects.create(
            destinatario=voluntario_user,
            mensagem='Notificação para voluntário'
        )

        # Notificação de outro usuário
        notif2 = Notificacao.objects.create(
            destinatario=organizador_user,
            mensagem='Notificação para organizador'
        )

        url = reverse('notificacoes_list')
        response = client_logged_voluntario.get(url)
        notificacoes = response.context['notificacoes']

        assert notif1 in notificacoes
        assert notif2 not in notificacoes

    def test_visualizar_marca_como_lidas(self, client_logged_voluntario, voluntario_user):
        """
        CT-V131: Ao visualizar, notificações são marcadas como lidas
        Resultado Esperado: lida=True após acesso
        """
        # Cria notificações não lidas
        notif1 = Notificacao.objects.create(
            destinatario=voluntario_user,
            mensagem='Notificação 1'
        )
        notif2 = Notificacao.objects.create(
            destinatario=voluntario_user,
            mensagem='Notificação 2'
        )

        assert notif1.lida is False
        assert notif2.lida is False

        # Acessa a página de notificações
        url = reverse('notificacoes_list')
        client_logged_voluntario.get(url)

        # Verifica que foram marcadas como lidas
        notif1.refresh_from_db()
        notif2.refresh_from_db()
        assert notif1.lida is True
        assert notif2.lida is True

    def test_notificacoes_ordenadas_por_data_desc(self, client_logged_voluntario, voluntario_user):
        """
        CT-V132: Notificações ordenadas por data (mais recentes primeiro)
        Resultado Esperado: Ordem descendente
        """
        notif1 = Notificacao.objects.create(
            destinatario=voluntario_user,
            mensagem='Primeira'
        )
        notif2 = Notificacao.objects.create(
            destinatario=voluntario_user,
            mensagem='Segunda'
        )

        url = reverse('notificacoes_list')
        response = client_logged_voluntario.get(url)
        notificacoes = list(response.context['notificacoes'])

        # Mais recente primeiro
        assert notificacoes[0] == notif2
        assert notificacoes[1] == notif1


@pytest.mark.django_db
class TestNotificacoesClearView:
    """
    CT-V140: Testes da view de limpar notificações
    """

    def test_limpar_requer_login(self, client):
        """
        CT-V140.1: View requer autenticação
        Resultado Esperado: Redirect para login
        """
        url = reverse('notificacoes_clear')
        response = client.post(url)
        assert response.status_code == 302

    def test_limpar_requer_post(self, client_logged_voluntario):
        """
        CT-V140.2: Limpar só aceita método POST
        Resultado Esperado: Redirect em GET
        """
        url = reverse('notificacoes_clear')
        response = client_logged_voluntario.get(url)
        assert response.status_code == 302

    def test_limpar_deleta_apenas_lidas(self, client_logged_voluntario, voluntario_user):
        """
        CT-V141: Limpar deleta apenas notificações lidas
        Resultado Esperado: Não lidas permanecem no banco
        """
        # Notificação lida
        notif_lida = Notificacao.objects.create(
            destinatario=voluntario_user,
            mensagem='Lida',
            lida=True
        )

        # Notificação não lida
        notif_nao_lida = Notificacao.objects.create(
            destinatario=voluntario_user,
            mensagem='Não lida',
            lida=False
        )

        url = reverse('notificacoes_clear')
        client_logged_voluntario.post(url)

        # Verifica que apenas a lida foi deletada
        assert not Notificacao.objects.filter(id=notif_lida.id).exists()
        assert Notificacao.objects.filter(id=notif_nao_lida.id).exists()

    def test_limpar_deleta_apenas_do_usuario_logado(self, client_logged_voluntario, voluntario_user, organizador_user):
        """
        CT-V142: Limpar deleta apenas notificações do usuário logado
        Resultado Esperado: Notificações de outros usuários permanecem
        """
        # Notificação lida do voluntário
        notif_vol = Notificacao.objects.create(
            destinatario=voluntario_user,
            mensagem='Voluntário',
            lida=True
        )

        # Notificação lida do organizador
        notif_org = Notificacao.objects.create(
            destinatario=organizador_user,
            mensagem='Organizador',
            lida=True
        )

        url = reverse('notificacoes_clear')
        client_logged_voluntario.post(url)

        # Verifica que apenas a do voluntário foi deletada
        assert not Notificacao.objects.filter(id=notif_vol.id).exists()
        assert Notificacao.objects.filter(id=notif_org.id).exists()


# ============================================
# SPRINT 2 - Placeholder para novas funcionalidades
# ============================================

# Quando adicionar chat ou mensagens diretas:
# @pytest.mark.django_db
# class TestChatView:
#     """CT-V150: Testes de chat - Sprint 2"""
#     pass