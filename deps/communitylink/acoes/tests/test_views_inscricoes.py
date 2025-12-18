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
# SPRINT 1 e 3 - Inscrições
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
        url = reverse('acoes:acao_apply', args=[acao_futura.pk])
        response = client.post(url)
        assert response.status_code == 302

    def test_inscricao_requer_post(self, client_logged_voluntario, acao_futura):
        """
        CT-V100.2: Inscrição só aceita método POST
        Resultado Esperado: Redirect em GET
        """
        url = reverse('acoes:acao_apply', args=[acao_futura.pk])
        response = client_logged_voluntario.get(url)
        assert response.status_code == 302

    def test_voluntario_pode_se_inscrever(self, client_logged_voluntario, acao_futura, voluntario_user):
        """
        CT-V101: Voluntário se inscreve com sucesso em ação
        Resultado Esperado: Inscrição criada com status PENDENTE
        """
        url = reverse('acoes:acao_apply', args=[acao_futura.pk])
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
        url = reverse('acoes:acao_apply', args=[acao_futura.pk])
        response = client_logged_organizador.post(url)

        # Verifica que NÃO criou inscrição
        assert not Inscricao.objects.filter(acao=acao_futura, voluntario=organizador_user).exists()

    def test_nao_pode_inscrever_em_acao_cheia(self, client_logged_voluntario, acao_cheia, voluntario_user):
        """
        CT-V103: Não é possível se inscrever em ação sem vagas
        Resultado Esperado: Mensagem de erro, sem inscrição criada
        """
        url = reverse('acoes:acao_apply', args=[acao_cheia.pk])
        response = client_logged_voluntario.post(url)

        # Verifica que NÃO criou inscrição
        assert not Inscricao.objects.filter(acao=acao_cheia, voluntario=voluntario_user).exists()

    def test_inscricao_duplicada_nao_cria_nova(self, client_logged_voluntario, acao_futura, voluntario_user):
        """
        CT-V104: Não é possível se inscrever 2x na mesma ação
        Resultado Esperado: Mensagem informativa, sem nova inscrição
        """
        # Primeira inscrição
        url = reverse('acoes:acao_apply', args=[acao_futura.pk])
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
        url = reverse('acoes:acao_apply', args=[acao_futura.pk])
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
        url = reverse('acoes:acao_manage', args=[acao_futura.pk])
        response = client.get(url)
        assert response.status_code == 302

    def test_apenas_organizador_pode_gerenciar(self, client_logged_voluntario, acao_futura):
        """
        CT-V110.2: Apenas organizador pode gerenciar inscrições
        Resultado Esperado: Mensagem de erro e redirect
        """
        url = reverse('acoes:acao_manage', args=[acao_futura.pk])
        response = client_logged_voluntario.get(url)
        assert response.status_code == 302

    def test_organizador_acessa_gerenciamento(self, client_logged_organizador, acao_futura):
        """
        CT-V110.3: Organizador acessa página de gerenciamento
        Resultado Esperado: Página renderizada com listas de inscrições
        """
        url = reverse('acoes:acao_manage', args=[acao_futura.pk])
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
        url = reverse('acoes:acao_manage', args=[inscricao_pendente.acao.pk])
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
        url = reverse('acoes:acao_manage', args=[inscricao_pendente.acao.pk])
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

        url = reverse('acoes:acao_manage', args=[acao_cheia.pk])
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

        url = reverse('acoes:acao_manage', args=[inscricao_pendente.acao.pk])
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
        url = reverse('acoes:acao_manage', args=[inscricao_pendente.acao.pk])
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
        url = reverse('acoes:acao_manage', args=[inscricao_pendente.acao.pk])
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
        url = reverse('acoes:minhas_inscricoes')
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

        url = reverse('acoes:minhas_inscricoes')
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

        url = reverse('acoes:minhas_inscricoes')
        response = client_logged_voluntario.get(url)
        inscricoes = list(response.context['inscricoes'])

        # Ação mais próxima deve vir primeiro
        assert inscricoes[0] == inscr2
        assert inscricoes[1] == inscr1


# ============================================
# SPRINT 3 - Notificações
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
        url = reverse('acoes:notificacoes_list')
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

        url = reverse('acoes:notificacoes_list')
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
        url = reverse('acoes:notificacoes_list')
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

        url = reverse('acoes:notificacoes_list')
        response = client_logged_voluntario.get(url)
        notificacoes = list(response.context['notificacoes'])

        # Mais recente primeiro
        assert notificacoes[0] == notif2
        assert notificacoes[1] == notif1

    def test_notificacoes_paginadas(self, client_logged_voluntario, voluntario_user):
        """
        CT-V133: Notificações são paginadas (10 por página)
        Resultado Esperado: Paginação funciona
        """
        # Cria 15 notificações
        for i in range(15):
            Notificacao.objects.create(
                destinatario=voluntario_user,
                mensagem=f'Notificação {i}'
            )

        url = reverse('acoes:notificacoes_list')
        response = client_logged_voluntario.get(url)

        # Primeira página deve ter 10 notificações
        notificacoes = response.context['notificacoes']
        assert len(list(notificacoes)) == 10

        # Segunda página deve ter 5
        url_page2 = reverse('acoes:notificacoes_list') + '?page=2'
        response2 = client_logged_voluntario.get(url_page2)
        notificacoes2 = response2.context['notificacoes']
        assert len(list(notificacoes2)) == 5

    def test_notificacao_com_link_funciona(self, client_logged_voluntario, voluntario_user, acao_futura):
        """
        CT-V134: Notificações podem ter links opcionais
        Resultado Esperado: Link é armazenado e exibido
        """
        link_acao = reverse('acoes:acao_detail', args=[acao_futura.pk])
        notif = Notificacao.objects.create(
            destinatario=voluntario_user,
            mensagem='Nova ação disponível',
            link=link_acao
        )

        url = reverse('acoes:notificacoes_list')
        response = client_logged_voluntario.get(url)

        # Verifica que notificação está no contexto
        assert notif in response.context['notificacoes']
        assert notif.link == link_acao

    def test_contagem_notificacoes_nao_lidas(self, client_logged_voluntario, voluntario_user):
        """
        CT-V135: Context mostra contagem de notificações não lidas
        Resultado Esperado: Contador correto
        """
        # Cria 3 não lidas e 2 lidas
        for i in range(3):
            Notificacao.objects.create(
                destinatario=voluntario_user,
                mensagem=f'Não lida {i}',
                lida=False
            )
        for i in range(2):
            Notificacao.objects.create(
                destinatario=voluntario_user,
                mensagem=f'Lida {i}',
                lida=True
            )

        url = reverse('acoes:notificacoes_list')
        response = client_logged_voluntario.get(url)

        # Verifica que tem informação de lidas no contexto
        assert 'lidas_count' in response.context


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
        url = reverse('acoes:notificacoes_clear')
        response = client.post(url)
        assert response.status_code == 302

    def test_limpar_requer_post(self, client_logged_voluntario):
        """
        CT-V140.2: Limpar só aceita método POST
        Resultado Esperado: Redirect em GET
        """
        url = reverse('acoes:notificacoes_clear')
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

        url = reverse('acoes:notificacoes_clear')
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

        url = reverse('acoes:notificacoes_clear')
        client_logged_voluntario.post(url)

        # Verifica que apenas a do voluntário foi deletada
        assert not Notificacao.objects.filter(id=notif_vol.id).exists()
        assert Notificacao.objects.filter(id=notif_org.id).exists()


@pytest.mark.django_db
class TestNotificacoesAutomaticas:
    """
    CT-V145: Testes de criação automática de notificações em eventos
    """

    def test_edicao_de_acao_notifica_inscritos(self, client_logged_organizador, acao_futura, voluntario_user):
        """
        CT-V145.1: Editar ação cria notificação para inscritos
        Resultado Esperado: Inscritos aceitos e pendentes são notificados
        """
        # Cria inscrições
        inscr_aceita = Inscricao.objects.create(acao=acao_futura, voluntario=voluntario_user, status='ACEITO')

        from django.contrib.auth.models import User
        vol2 = User.objects.create_user('vol2', 'vol2@test.com', 'pass')
        inscr_pendente = Inscricao.objects.create(acao=acao_futura, voluntario=vol2, status='PENDENTE')

        # Conta notificações antes
        count_antes = Notificacao.objects.filter(destinatario=voluntario_user).count()

        # Edita ação
        url = reverse('acoes:acao_update', args=[acao_futura.pk])
        data = {
            'titulo': 'Título Editado',
            'descricao': acao_futura.descricao,
            'data': acao_futura.data.strftime('%Y-%m-%d %H:%M:%S'),
            'local': acao_futura.local,
            'numero_vagas': acao_futura.numero_vagas,
            'categoria': acao_futura.categoria
        }
        response = client_logged_organizador.post(url, data)

        # Verifica que notificação foi criada
        count_depois = Notificacao.objects.filter(destinatario=voluntario_user).count()
        assert count_depois == count_antes + 1

        # Verifica conteúdo
        notif = Notificacao.objects.filter(destinatario=voluntario_user).latest('created_at')
        assert 'alterações' in notif.mensagem.lower() or 'sofreu' in notif.mensagem.lower()

    def test_delecao_de_acao_notifica_inscritos(self, client_logged_organizador, acao_futura, voluntario_user):
        """
        CT-V145.2: Deletar ação cria notificação para inscritos
        Resultado Esperado: Todos inscritos são notificados
        """
        # Cria inscrição
        inscricao = Inscricao.objects.create(acao=acao_futura, voluntario=voluntario_user, status='ACEITO')

        count_antes = Notificacao.objects.filter(destinatario=voluntario_user).count()

        # Deleta ação
        url = reverse('acoes:acao_delete', args=[acao_futura.pk])
        response = client_logged_organizador.post(url)

        # Verifica notificação
        count_depois = Notificacao.objects.filter(destinatario=voluntario_user).count()
        assert count_depois == count_antes + 1

        notif = Notificacao.objects.filter(destinatario=voluntario_user).latest('created_at')
        assert 'cancelada' in notif.mensagem.lower() or 'excluída' in notif.mensagem.lower()

    def test_inscricao_rejeitada_nao_recebe_notificacao_de_edicao(self, client_logged_organizador, acao_futura, voluntario_user):
        """
        CT-V145.3: Inscrição rejeitada não recebe notificação de edição
        Resultado Esperado: Apenas ACEITO e PENDENTE são notificados
        """
        # Cria inscrição rejeitada
        inscricao = Inscricao.objects.create(acao=acao_futura, voluntario=voluntario_user, status='REJEITADO')

        count_antes = Notificacao.objects.filter(destinatario=voluntario_user).count()

        # Edita ação
        url = reverse('acoes:acao_update', args=[acao_futura.pk])
        data = {
            'titulo': 'Título Editado',
            'descricao': acao_futura.descricao,
            'data': acao_futura.data.strftime('%Y-%m-%d %H:%M:%S'),
            'local': acao_futura.local,
            'numero_vagas': acao_futura.numero_vagas,
            'categoria': acao_futura.categoria
        }
        client_logged_organizador.post(url, data)

        # Verifica que NÃO foi criada notificação
        count_depois = Notificacao.objects.filter(destinatario=voluntario_user).count()
        assert count_depois == count_antes

    def test_reinscricao_apos_cancelamento_notifica_organizador_novamente(self, client_logged_voluntario, voluntario_user, acao_futura, organizador_user):
        """
        CT-V145.4: Reinscrever após cancelamento cria nova notificação
        Resultado Esperado: Organizador é notificado novamente
        """
        # Cria e cancela inscrição
        inscricao = Inscricao.objects.create(acao=acao_futura, voluntario=voluntario_user, status='CANCELADO')

        count_antes = Notificacao.objects.filter(destinatario=organizador_user).count()

        # Se inscreve novamente
        url = reverse('acoes:acao_apply', args=[acao_futura.pk])
        response = client_logged_voluntario.post(url)

        # Verifica que organizador foi notificado
        count_depois = Notificacao.objects.filter(destinatario=organizador_user).count()
        assert count_depois == count_antes + 1

        notif = Notificacao.objects.filter(destinatario=organizador_user).latest('created_at')
        assert 'novamente' in notif.mensagem.lower()


@pytest.mark.django_db
class TestInscricaoCancelView:
    """
    CT-V150: Testes de cancelamento de inscrição
    """

    def test_cancelamento_requer_login(self, client, inscricao_pendente):
        """
        CT-V150.1: Cancelamento requer autenticação
        Resultado Esperado: Redirect para login
        """
        url = reverse('acoes:inscricao_cancel', args=[inscricao_pendente.pk])
        response = client.post(url)
        assert response.status_code == 302

    def test_cancelamento_requer_post(self, client_logged_voluntario, voluntario_user, acao_futura):
        """
        CT-V150.2: Cancelamento requer método POST
        Resultado Esperado: Redirect em GET (deve mostrar confirmação)
        """
        inscricao = Inscricao.objects.create(acao=acao_futura, voluntario=voluntario_user)
        url = reverse('acoes:inscricao_cancel', args=[inscricao.pk])
        response = client_logged_voluntario.get(url)

        # Como não há template de confirmação, provavelmente vai dar erro ou redirect
        # Se a view exigir POST, deve retornar erro
        assert response.status_code in [302, 405]

    def test_voluntario_cancela_inscricao_pendente(self, client_logged_voluntario, voluntario_user, acao_futura):
        """
        CT-V151: Voluntário cancela inscrição com status PENDENTE
        Resultado Esperado: Status muda para CANCELADO
        """
        inscricao = Inscricao.objects.create(
            acao=acao_futura,
            voluntario=voluntario_user,
            status='PENDENTE'
        )

        url = reverse('acoes:inscricao_cancel', args=[inscricao.pk])
        response = client_logged_voluntario.post(url)

        # Verifica redirect
        assert response.status_code == 302
        assert response.url == reverse('acoes:minhas_inscricoes')

        # Verifica que status mudou
        inscricao.refresh_from_db()
        assert inscricao.status == 'CANCELADO'

    def test_voluntario_cancela_inscricao_aceita(self, client_logged_voluntario, voluntario_user, acao_futura):
        """
        CT-V152: Voluntário cancela inscrição com status ACEITO
        Resultado Esperado: Status muda para CANCELADO
        """
        inscricao = Inscricao.objects.create(
            acao=acao_futura,
            voluntario=voluntario_user,
            status='ACEITO'
        )

        url = reverse('acoes:inscricao_cancel', args=[inscricao.pk])
        response = client_logged_voluntario.post(url)

        inscricao.refresh_from_db()
        assert inscricao.status == 'CANCELADO'

    def test_cancelamento_remove_notificacao_do_organizador_se_pendente(self, client_logged_voluntario, voluntario_user, acao_futura, organizador_user):
        """
        CT-V153: Cancelar inscrição PENDENTE remove notificação do organizador
        Resultado Esperado: Notificação é deletada
        """
        inscricao = Inscricao.objects.create(
            acao=acao_futura,
            voluntario=voluntario_user,
            status='PENDENTE'
        )

        # Cria notificação para o organizador (como se tivesse sido criada na inscrição)
        Notificacao.objects.create(
            destinatario=organizador_user,
            mensagem=f"{voluntario_user.username} solicitou participação em '{acao_futura.titulo}'.",
            link=reverse('acoes:acao_manage', args=[acao_futura.pk])
        )

        # Verifica que notificação existe
        assert Notificacao.objects.filter(
            destinatario=organizador_user,
            mensagem__contains=voluntario_user.username
        ).exists()

        # Cancela inscrição
        url = reverse('acoes:inscricao_cancel', args=[inscricao.pk])
        client_logged_voluntario.post(url)

        # Verifica que notificação foi deletada
        assert not Notificacao.objects.filter(
            destinatario=organizador_user,
            mensagem__contains=voluntario_user.username,
            link=reverse('acoes:acao_manage', args=[acao_futura.pk])
        ).exists()

    def test_cancelamento_cria_notificacao_para_organizador_se_aceito(self, client_logged_voluntario, voluntario_user, acao_futura, organizador_user):
        """
        CT-V154: Cancelar inscrição ACEITO cria notificação para organizador
        Resultado Esperado: Nova notificação criada
        """
        inscricao = Inscricao.objects.create(
            acao=acao_futura,
            voluntario=voluntario_user,
            status='ACEITO'
        )

        # Conta notificações antes
        count_antes = Notificacao.objects.filter(destinatario=organizador_user).count()

        # Cancela inscrição
        url = reverse('acoes:inscricao_cancel', args=[inscricao.pk])
        client_logged_voluntario.post(url)

        # Verifica que nova notificação foi criada
        count_depois = Notificacao.objects.filter(destinatario=organizador_user).count()
        assert count_depois == count_antes + 1

        # Verifica conteúdo da notificação
        notif = Notificacao.objects.filter(destinatario=organizador_user).latest('created_at')
        assert 'cancelou' in notif.mensagem.lower()
        assert voluntario_user.username in notif.mensagem

    def test_nao_pode_cancelar_inscricao_de_acao_passada(self, client_logged_voluntario, voluntario_user, acao_passada):
        """
        CT-V155: Não é possível cancelar inscrição em ação passada
        Resultado Esperado: Mensagem de erro, status não muda
        """
        inscricao = Inscricao.objects.create(
            acao=acao_passada,
            voluntario=voluntario_user,
            status='ACEITO'
        )

        url = reverse('acoes:inscricao_cancel', args=[inscricao.pk])
        response = client_logged_voluntario.post(url)

        # Verifica redirect
        assert response.status_code == 302

        # Verifica que status NÃO mudou
        inscricao.refresh_from_db()
        assert inscricao.status == 'ACEITO'

    def test_apenas_proprio_voluntario_pode_cancelar(self, client_logged_voluntario, voluntario_user, acao_futura):
        """
        CT-V156: Voluntário só pode cancelar própria inscrição
        Resultado Esperado: Erro 404 ao tentar cancelar de outro
        """
        # Cria outro voluntário e inscrição dele
        outro_vol = User.objects.create_user('outro_vol', 'outro@test.com', 'pass')
        inscricao_outro = Inscricao.objects.create(
            acao=acao_futura,
            voluntario=outro_vol,
            status='PENDENTE'
        )

        url = reverse('acoes:inscricao_cancel', args=[inscricao_outro.pk])

        # Deve dar erro 404 (get_object_or_404 com voluntario=request.user)
        with pytest.raises(Exception):
            response = client_logged_voluntario.post(url)

    def test_cancelamento_exibe_mensagem_sucesso(self, client_logged_voluntario, voluntario_user, acao_futura):
        """
        CT-V157: Cancelamento exibe mensagem de sucesso
        Resultado Esperado: Mensagem no sistema de messages
        """
        inscricao = Inscricao.objects.create(
            acao=acao_futura,
            voluntario=voluntario_user,
            status='PENDENTE'
        )

        url = reverse('acoes:inscricao_cancel', args=[inscricao.pk])
        response = client_logged_voluntario.post(url, follow=True)

        # Verifica que tem mensagem
        messages = list(response.context['messages'])
        assert len(messages) > 0
        assert 'cancelada' in str(messages[0]).lower()

    def test_cancelamento_redireciona_para_minhas_inscricoes(self, client_logged_voluntario, voluntario_user, acao_futura):
        """
        CT-V158: Cancelamento redireciona para minhas inscrições
        Resultado Esperado: Redirect correto
        """
        inscricao = Inscricao.objects.create(
            acao=acao_futura,
            voluntario=voluntario_user,
            status='PENDENTE'
        )

        url = reverse('acoes:inscricao_cancel', args=[inscricao.pk])
        response = client_logged_voluntario.post(url)

        assert response.status_code == 302
        assert response.url == reverse('acoes:minhas_inscricoes')

    def test_cancelar_inscricao_rejeitada_tambem_funciona(self, client_logged_voluntario, voluntario_user, acao_futura):
        """
        CT-V159: É possível cancelar inscrição rejeitada (para limpar histórico)
        Resultado Esperado: Status muda para CANCELADO
        """
        inscricao = Inscricao.objects.create(
            acao=acao_futura,
            voluntario=voluntario_user,
            status='REJEITADO'
        )

        url = reverse('acoes:inscricao_cancel', args=[inscricao.pk])
        response = client_logged_voluntario.post(url)

        inscricao.refresh_from_db()
        assert inscricao.status == 'CANCELADO'