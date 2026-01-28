"""
Testes das Views de Inscrições e Notificações

Este arquivo testa:
- Inscrição de voluntários em ações
- Gerenciamento de inscrições pelo organizador
- Minhas inscrições (para voluntários)
- Notificações
"""

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from acoes.models import Acao, Inscricao, Notificacao
from .test_base import FullFixturesMixin


# ============================================
# SPRINT 1 e 3 - Inscrições
# ============================================


class TestAcaoApplyView(FullFixturesMixin, TestCase):
    """
    CT-V100: Testes da view de inscrição em ações
    """

    def test_inscricao_requer_login(self):
        """
        CT-V100.1: Inscrição requer autenticação
        Resultado Esperado: Redirect para login
        """
        url = reverse('acoes:acao_apply', args=[self.acao_futura.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)

    def test_inscricao_requer_post(self):
        """
        CT-V100.2: Inscrição só aceita método POST
        Resultado Esperado: Redirect em GET
        """
        url = reverse('acoes:acao_apply', args=[self.acao_futura.pk])
        response = self.client_logged_voluntario.get(url)
        self.assertEqual(response.status_code, 302)

    def test_voluntario_pode_se_inscrever(self):
        """
        CT-V101: Voluntário se inscreve com sucesso em ação
        Resultado Esperado: Inscrição criada com status PENDENTE
        """
        # Remove inscrição existente do setUp para testar criação nova
        self.inscricao_pendente.delete()

        url = reverse('acoes:acao_apply', args=[self.acao_futura.pk])
        response = self.client_logged_voluntario.post(url)

        # Verifica que a inscrição foi criada
        self.assertTrue(Inscricao.objects.filter(acao=self.acao_futura, voluntario=self.voluntario_user).exists())
        inscricao = Inscricao.objects.get(acao=self.acao_futura, voluntario=self.voluntario_user)
        self.assertEqual(inscricao.status, 'PENDENTE')

    def test_organizador_nao_pode_se_inscrever_propria_acao(self):
        """
        CT-V102: Organizador não pode se inscrever na própria ação
        Resultado Esperado: Mensagem de aviso, sem inscrição criada
        """
        url = reverse('acoes:acao_apply', args=[self.acao_futura.pk])
        response = self.client_logged_organizador.post(url)

        # Verifica que NÃO criou inscrição
        self.assertFalse(Inscricao.objects.filter(acao=self.acao_futura, voluntario=self.organizador_user).exists())

    def test_nao_pode_inscrever_em_acao_cheia(self):
        """
        CT-V103: Não é possível se inscrever em ação sem vagas
        Resultado Esperado: Mensagem de erro, sem inscrição criada
        """
        url = reverse('acoes:acao_apply', args=[self.acao_cheia.pk])
        response = self.client_logged_voluntario.post(url)

        # Verifica que NÃO criou inscrição
        self.assertFalse(Inscricao.objects.filter(acao=self.acao_cheia, voluntario=self.voluntario_user).exists())

    def test_inscricao_duplicada_nao_cria_nova(self):
        """
        CT-V104: Não é possível se inscrever 2x na mesma ação
        Resultado Esperado: Mensagem informativa, sem nova inscrição
        """
        # Primeira inscrição
        url = reverse('acoes:acao_apply', args=[self.acao_futura.pk])
        self.client_logged_voluntario.post(url)

        # Tenta segunda inscrição
        response = self.client_logged_voluntario.post(url)

        # Verifica que existe apenas 1 inscrição
        self.assertEqual(Inscricao.objects.filter(acao=self.acao_futura, voluntario=self.voluntario_user).count(), 1)

    def test_inscricao_cria_notificacao_para_organizador(self):
        """
        CT-V105: Inscrição cria notificação para o organizador
        Resultado Esperado: Notificação criada para o organizador
        """
        # Remove inscrição existente do setUp para testar criação nova
        self.inscricao_pendente.delete()

        url = reverse('acoes:acao_apply', args=[self.acao_futura.pk])
        self.client_logged_voluntario.post(url)

        # Verifica que foi criada notificação para o organizador
        self.assertTrue(Notificacao.objects.filter(destinatario=self.organizador_user).exists())
        notificacao = Notificacao.objects.get(destinatario=self.organizador_user)
        self.assertIn(self.voluntario_user.username, notificacao.mensagem)
        self.assertIn(self.acao_futura.titulo, notificacao.mensagem)


class TestAcaoManageView(FullFixturesMixin, TestCase):
    """
    CT-V110: Testes da view de gerenciamento de inscrições
    """

    def test_gerenciamento_requer_login(self):
        """
        CT-V110.1: Gerenciamento requer autenticação
        Resultado Esperado: Redirect para login
        """
        url = reverse('acoes:acao_manage', args=[self.acao_futura.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_apenas_organizador_pode_gerenciar(self):
        """
        CT-V110.2: Apenas organizador pode gerenciar inscrições
        Resultado Esperado: Mensagem de erro e redirect
        """
        url = reverse('acoes:acao_manage', args=[self.acao_futura.pk])
        response = self.client_logged_voluntario.get(url)
        self.assertEqual(response.status_code, 302)

    def test_organizador_acessa_gerenciamento(self):
        """
        CT-V110.3: Organizador acessa página de gerenciamento
        Resultado Esperado: Página renderizada com listas de inscrições
        """
        url = reverse('acoes:acao_manage', args=[self.acao_futura.pk])
        response = self.client_logged_organizador.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertIn('pendentes', response.context)
        self.assertIn('aceitas', response.context)
        self.assertIn('rejeitadas', response.context)

    def test_organizador_aceita_inscricao(self):
        """
        CT-V111: Organizador aceita inscrição pendente
        Resultado Esperado: Status muda para ACEITO
        """
        url = reverse('acoes:acao_manage', args=[self.inscricao_pendente.acao.pk])
        data = {
            'inscricao_id': self.inscricao_pendente.id,
            'status': 'ACEITO'
        }

        response = self.client_logged_organizador.post(url, data)

        self.inscricao_pendente.refresh_from_db()
        self.assertEqual(self.inscricao_pendente.status, 'ACEITO')

    def test_organizador_rejeita_inscricao(self):
        """
        CT-V112: Organizador rejeita inscrição pendente
        Resultado Esperado: Status muda para REJEITADO
        """
        url = reverse('acoes:acao_manage', args=[self.inscricao_pendente.acao.pk])
        data = {
            'inscricao_id': self.inscricao_pendente.id,
            'status': 'REJEITADO'
        }

        response = self.client_logged_organizador.post(url, data)

        self.inscricao_pendente.refresh_from_db()
        self.assertEqual(self.inscricao_pendente.status, 'REJEITADO')

    def test_nao_pode_aceitar_quando_acao_cheia(self):
        """
        CT-V113: Não pode aceitar inscrição se ação já está cheia
        Resultado Esperado: Status permanece PENDENTE
        """
        # Cria nova inscrição pendente na ação cheia
        voluntario = User.objects.create_user('novo_vol', 'novo@test.com', 'pass')
        inscricao = Inscricao.objects.create(
            acao=self.acao_cheia,
            voluntario=voluntario,
            status='PENDENTE'
        )

        url = reverse('acoes:acao_manage', args=[self.acao_cheia.pk])
        data = {
            'inscricao_id': inscricao.id,
            'status': 'ACEITO'
        }

        response = self.client_logged_organizador.post(url, data)

        inscricao.refresh_from_db()
        self.assertEqual(inscricao.status, 'PENDENTE')  # Não foi aceita

    def test_mudanca_status_cria_notificacao_para_voluntario(self):
        """
        CT-V114: Mudança de status cria notificação para o voluntário
        Resultado Esperado: Notificação criada para o voluntário
        """
        voluntario = self.inscricao_pendente.voluntario

        url = reverse('acoes:acao_manage', args=[self.inscricao_pendente.acao.pk])
        data = {
            'inscricao_id': self.inscricao_pendente.id,
            'status': 'ACEITO'
        }

        self.client_logged_organizador.post(url, data)

        # Verifica que foi criada notificação para o voluntário
        self.assertTrue(Notificacao.objects.filter(destinatario=voluntario).exists())
        notificacao = Notificacao.objects.get(destinatario=voluntario)
        self.assertIn('Aceita', notificacao.mensagem)

    def test_status_invalido_nao_aceito(self):
        """
        CT-V115: Status inválido não é aceito
        Resultado Esperado: Erro e status permanece inalterado
        """
        url = reverse('acoes:acao_manage', args=[self.inscricao_pendente.acao.pk])
        data = {
            'inscricao_id': self.inscricao_pendente.id,
            'status': 'STATUS_INVALIDO'
        }

        response = self.client_logged_organizador.post(url, data)

        self.inscricao_pendente.refresh_from_db()
        self.assertEqual(self.inscricao_pendente.status, 'PENDENTE')

    def test_superuser_pode_gerenciar_qualquer_acao(self):
        """
        CT-V116: Superusuário pode gerenciar qualquer ação
        Resultado Esperado: Acesso permitido
        """
        self.client.force_login(self.superuser)
        url = reverse('acoes:acao_manage', args=[self.inscricao_pendente.acao.pk])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)


class TestMinhasInscricoesView(FullFixturesMixin, TestCase):
    """
    CT-V120: Testes da view "Minhas Inscrições" (para voluntários)
    """

    def test_minhas_inscricoes_requer_login(self):
        """
        CT-V120.1: View requer autenticação
        Resultado Esperado: Redirect para login
        """
        url = reverse('acoes:minhas_inscricoes')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_mostra_apenas_inscricoes_do_voluntario(self):
        """
        CT-V120.2: Mostra apenas inscrições do voluntário logado
        Resultado Esperado: Apenas inscrições do usuário na lista
        """
        # inscricao_pendente já existe via setUp para (acao_futura, voluntario_user)

        # Cria inscrição de outro voluntário
        outro_vol = User.objects.create_user('outro_vol', 'outro@test.com', 'pass')
        inscricao2 = Inscricao.objects.create(acao=self.acao_futura, voluntario=outro_vol)

        url = reverse('acoes:minhas_inscricoes')
        response = self.client_logged_voluntario.get(url)
        inscricoes = response.context['inscricoes']

        self.assertIn(self.inscricao_pendente, inscricoes)
        self.assertNotIn(inscricao2, inscricoes)

    def test_inscricoes_ordenadas_por_data_acao(self):
        """
        CT-V120.3: Inscrições ordenadas por data da ação
        Resultado Esperado: Ações mais próximas primeiro
        """
        from django.utils import timezone
        from datetime import timedelta

        # Remove inscrição existente para teste limpo de ordenação
        self.inscricao_pendente.delete()

        # Cria 2 ações com datas diferentes
        acao1 = Acao.objects.create(
            titulo='Ação em 30 dias',
            descricao='Teste',
            data=timezone.now() + timedelta(days=30),
            local='Local',
            numero_vagas=10,
            organizador=self.organizador_user
        )
        acao2 = Acao.objects.create(
            titulo='Ação em 7 dias',
            descricao='Teste',
            data=timezone.now() + timedelta(days=7),
            local='Local',
            numero_vagas=10,
            organizador=self.organizador_user
        )

        # Inscreve o voluntário nas 2 ações
        inscr1 = Inscricao.objects.create(acao=acao1, voluntario=self.voluntario_user)
        inscr2 = Inscricao.objects.create(acao=acao2, voluntario=self.voluntario_user)

        url = reverse('acoes:minhas_inscricoes')
        response = self.client_logged_voluntario.get(url)
        inscricoes = list(response.context['inscricoes'])

        # Ação mais próxima deve vir primeiro
        self.assertEqual(inscricoes[0], inscr2)
        self.assertEqual(inscricoes[1], inscr1)


# ============================================
# SPRINT 3 - Notificações
# ============================================


class TestNotificacoesListView(FullFixturesMixin, TestCase):
    """
    CT-V130: Testes da view de listagem de notificações
    """

    def test_notificacoes_requer_login(self):
        """
        CT-V130.1: View requer autenticação
        Resultado Esperado: Redirect para login
        """
        url = reverse('acoes:notificacoes_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_mostra_apenas_notificacoes_do_usuario(self):
        """
        CT-V130.2: Mostra apenas notificações do usuário logado
        Resultado Esperado: Apenas notificações do usuário na lista
        """
        # Notificação do voluntário logado
        notif1 = Notificacao.objects.create(
            destinatario=self.voluntario_user,
            mensagem='Notificação para voluntário'
        )

        # Notificação de outro usuário
        notif2 = Notificacao.objects.create(
            destinatario=self.organizador_user,
            mensagem='Notificação para organizador'
        )

        url = reverse('acoes:notificacoes_list')
        response = self.client_logged_voluntario.get(url)
        notificacoes = response.context['notificacoes']

        self.assertIn(notif1, notificacoes)
        self.assertNotIn(notif2, notificacoes)

    def test_visualizar_marca_como_lidas(self):
        """
        CT-V131: Ao visualizar, notificações são marcadas como lidas
        Resultado Esperado: lida=True após acesso
        """
        # Cria notificações não lidas
        notif1 = Notificacao.objects.create(
            destinatario=self.voluntario_user,
            mensagem='Notificação 1'
        )
        notif2 = Notificacao.objects.create(
            destinatario=self.voluntario_user,
            mensagem='Notificação 2'
        )

        self.assertFalse(notif1.lida)
        self.assertFalse(notif2.lida)

        # Acessa a página de notificações
        url = reverse('acoes:notificacoes_list')
        self.client_logged_voluntario.get(url)

        # Verifica que foram marcadas como lidas
        notif1.refresh_from_db()
        notif2.refresh_from_db()
        self.assertTrue(notif1.lida)
        self.assertTrue(notif2.lida)

    def test_notificacoes_ordenadas_por_data_desc(self):
        """
        CT-V132: Notificações ordenadas por data (mais recentes primeiro)
        Resultado Esperado: Ordem descendente
        """
        notif1 = Notificacao.objects.create(
            destinatario=self.voluntario_user,
            mensagem='Primeira'
        )
        notif2 = Notificacao.objects.create(
            destinatario=self.voluntario_user,
            mensagem='Segunda'
        )

        url = reverse('acoes:notificacoes_list')
        response = self.client_logged_voluntario.get(url)
        notificacoes = list(response.context['notificacoes'])

        # Mais recente primeiro
        self.assertEqual(notificacoes[0], notif2)
        self.assertEqual(notificacoes[1], notif1)

    def test_notificacoes_paginadas(self):
        """
        CT-V133: Notificações são paginadas (10 por página)
        Resultado Esperado: Paginação funciona
        """
        # Cria 15 notificações
        for i in range(15):
            Notificacao.objects.create(
                destinatario=self.voluntario_user,
                mensagem=f'Notificação {i}'
            )

        url = reverse('acoes:notificacoes_list')
        response = self.client_logged_voluntario.get(url)

        # Primeira página deve ter 10 notificações
        notificacoes = response.context['notificacoes']
        self.assertEqual(len(list(notificacoes)), 10)

        # Segunda página deve ter 5
        url_page2 = reverse('acoes:notificacoes_list') + '?page=2'
        response2 = self.client_logged_voluntario.get(url_page2)
        notificacoes2 = response2.context['notificacoes']
        self.assertEqual(len(list(notificacoes2)), 5)

    def test_notificacao_com_link_funciona(self):
        """
        CT-V134: Notificações podem ter links opcionais
        Resultado Esperado: Link é armazenado e exibido
        """
        link_acao = reverse('acoes:acao_detail', args=[self.acao_futura.pk])
        notif = Notificacao.objects.create(
            destinatario=self.voluntario_user,
            mensagem='Nova ação disponível',
            link=link_acao
        )

        url = reverse('acoes:notificacoes_list')
        response = self.client_logged_voluntario.get(url)

        # Verifica que notificação está no contexto
        self.assertIn(notif, response.context['notificacoes'])
        self.assertEqual(notif.link, link_acao)

    def test_contagem_notificacoes_nao_lidas(self):
        """
        CT-V135: Context mostra contagem de notificações não lidas
        Resultado Esperado: Contador correto
        """
        # Cria 3 não lidas e 2 lidas
        for i in range(3):
            Notificacao.objects.create(
                destinatario=self.voluntario_user,
                mensagem=f'Não lida {i}',
                lida=False
            )
        for i in range(2):
            Notificacao.objects.create(
                destinatario=self.voluntario_user,
                mensagem=f'Lida {i}',
                lida=True
            )

        url = reverse('acoes:notificacoes_list')
        response = self.client_logged_voluntario.get(url)

        # Verifica que tem informação de lidas no contexto
        self.assertIn('lidas_count', response.context)


class TestNotificacoesClearView(FullFixturesMixin, TestCase):
    """
    CT-V140: Testes da view de limpar notificações
    """

    def test_limpar_requer_login(self):
        """
        CT-V140.1: View requer autenticação
        Resultado Esperado: Redirect para login
        """
        url = reverse('acoes:notificacoes_clear')
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)

    def test_limpar_requer_post(self):
        """
        CT-V140.2: Limpar só aceita método POST
        Resultado Esperado: Redirect em GET
        """
        url = reverse('acoes:notificacoes_clear')
        response = self.client_logged_voluntario.get(url)
        self.assertEqual(response.status_code, 302)

    def test_limpar_deleta_apenas_lidas(self):
        """
        CT-V141: Limpar deleta apenas notificações lidas
        Resultado Esperado: Não lidas permanecem no banco
        """
        # Notificação lida
        notif_lida = Notificacao.objects.create(
            destinatario=self.voluntario_user,
            mensagem='Lida',
            lida=True
        )

        # Notificação não lida
        notif_nao_lida = Notificacao.objects.create(
            destinatario=self.voluntario_user,
            mensagem='Não lida',
            lida=False
        )

        url = reverse('acoes:notificacoes_clear')
        self.client_logged_voluntario.post(url)

        # Verifica que apenas a lida foi deletada
        self.assertFalse(Notificacao.objects.filter(id=notif_lida.id).exists())
        self.assertTrue(Notificacao.objects.filter(id=notif_nao_lida.id).exists())

    def test_limpar_deleta_apenas_do_usuario_logado(self):
        """
        CT-V142: Limpar deleta apenas notificações do usuário logado
        Resultado Esperado: Notificações de outros usuários permanecem
        """
        # Notificação lida do voluntário
        notif_vol = Notificacao.objects.create(
            destinatario=self.voluntario_user,
            mensagem='Voluntário',
            lida=True
        )

        # Notificação lida do organizador
        notif_org = Notificacao.objects.create(
            destinatario=self.organizador_user,
            mensagem='Organizador',
            lida=True
        )

        url = reverse('acoes:notificacoes_clear')
        self.client_logged_voluntario.post(url)

        # Verifica que apenas a do voluntário foi deletada
        self.assertFalse(Notificacao.objects.filter(id=notif_vol.id).exists())
        self.assertTrue(Notificacao.objects.filter(id=notif_org.id).exists())


class TestNotificacoesAutomaticas(FullFixturesMixin, TestCase):
    """
    CT-V145: Testes de criação automática de notificações em eventos
    """

    def test_edicao_de_acao_notifica_inscritos(self):
        """
        CT-V145.1: Editar ação cria notificação para inscritos
        Resultado Esperado: Inscritos aceitos e pendentes são notificados
        """
        # Atualiza inscrição existente do setUp para status ACEITO
        self.inscricao_pendente.status = 'ACEITO'
        self.inscricao_pendente.save()

        from django.contrib.auth.models import User
        vol2 = User.objects.create_user('vol2', 'vol2@test.com', 'pass')
        inscr_pendente = Inscricao.objects.create(acao=self.acao_futura, voluntario=vol2, status='PENDENTE')

        # Conta notificações antes
        count_antes = Notificacao.objects.filter(destinatario=self.voluntario_user).count()

        # Edita ação
        url = reverse('acoes:acao_update', args=[self.acao_futura.pk])
        data = {
            'titulo': 'Título Editado',
            'descricao': self.acao_futura.descricao,
            'data': self.acao_futura.data.strftime('%Y-%m-%d %H:%M:%S'),
            'local': self.acao_futura.local,
            'numero_vagas': self.acao_futura.numero_vagas,
            'categoria': self.acao_futura.categoria
        }
        response = self.client_logged_organizador.post(url, data)

        # Verifica que notificação foi criada
        count_depois = Notificacao.objects.filter(destinatario=self.voluntario_user).count()
        self.assertEqual(count_depois, count_antes + 1)

        # Verifica conteúdo
        notif = Notificacao.objects.filter(destinatario=self.voluntario_user).latest('created_at')
        self.assertTrue('alterações' in notif.mensagem.lower() or 'sofreu' in notif.mensagem.lower())

    def test_delecao_de_acao_notifica_inscritos(self):
        """
        CT-V145.2: Deletar ação cria notificação para inscritos
        Resultado Esperado: Todos inscritos são notificados
        """
        # Atualiza inscrição existente do setUp para status ACEITO
        self.inscricao_pendente.status = 'ACEITO'
        self.inscricao_pendente.save()

        count_antes = Notificacao.objects.filter(destinatario=self.voluntario_user).count()

        # Deleta ação
        url = reverse('acoes:acao_delete', args=[self.acao_futura.pk])
        response = self.client_logged_organizador.post(url)

        # Verifica notificação
        count_depois = Notificacao.objects.filter(destinatario=self.voluntario_user).count()
        self.assertEqual(count_depois, count_antes + 1)

        notif = Notificacao.objects.filter(destinatario=self.voluntario_user).latest('created_at')
        self.assertTrue('cancelada' in notif.mensagem.lower() or 'excluída' in notif.mensagem.lower())

    def test_inscricao_rejeitada_nao_recebe_notificacao_de_edicao(self):
        """
        CT-V145.3: Inscrição rejeitada não recebe notificação de edição
        Resultado Esperado: Apenas ACEITO e PENDENTE são notificados
        """
        # Atualiza inscrição existente do setUp para status REJEITADO
        self.inscricao_pendente.status = 'REJEITADO'
        self.inscricao_pendente.save()

        count_antes = Notificacao.objects.filter(destinatario=self.voluntario_user).count()

        # Edita ação
        url = reverse('acoes:acao_update', args=[self.acao_futura.pk])
        data = {
            'titulo': 'Título Editado',
            'descricao': self.acao_futura.descricao,
            'data': self.acao_futura.data.strftime('%Y-%m-%d %H:%M:%S'),
            'local': self.acao_futura.local,
            'numero_vagas': self.acao_futura.numero_vagas,
            'categoria': self.acao_futura.categoria
        }
        self.client_logged_organizador.post(url, data)

        # Verifica que NÃO foi criada notificação
        count_depois = Notificacao.objects.filter(destinatario=self.voluntario_user).count()
        self.assertEqual(count_depois, count_antes)

    def test_reinscricao_apos_cancelamento_notifica_organizador_novamente(self):
        """
        CT-V145.4: Reinscrever após cancelamento cria nova notificação
        Resultado Esperado: Organizador é notificado novamente
        """
        # Atualiza inscrição existente do setUp para status CANCELADO
        self.inscricao_pendente.status = 'CANCELADO'
        self.inscricao_pendente.save()

        count_antes = Notificacao.objects.filter(destinatario=self.organizador_user).count()

        # Se inscreve novamente
        url = reverse('acoes:acao_apply', args=[self.acao_futura.pk])
        response = self.client_logged_voluntario.post(url)

        # Verifica que organizador foi notificado
        count_depois = Notificacao.objects.filter(destinatario=self.organizador_user).count()
        self.assertEqual(count_depois, count_antes + 1)

        notif = Notificacao.objects.filter(destinatario=self.organizador_user).latest('created_at')
        self.assertIn('novamente', notif.mensagem.lower())


class TestInscricaoCancelView(FullFixturesMixin, TestCase):
    """
    CT-V150: Testes de cancelamento de inscrição
    """

    def test_cancelamento_requer_login(self):
        """
        CT-V150.1: Cancelamento requer autenticação
        Resultado Esperado: Redirect para login
        """
        url = reverse('acoes:inscricao_cancel', args=[self.inscricao_pendente.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)

    def test_cancelamento_requer_post(self):
        """
        CT-V150.2: Cancelamento requer método POST
        Resultado Esperado: Redirect em GET (deve mostrar confirmação)
        """
        # Usa inscricao_pendente do setUp
        url = reverse('acoes:inscricao_cancel', args=[self.inscricao_pendente.pk])
        response = self.client_logged_voluntario.get(url)

        # Como não há template de confirmação, provavelmente vai dar erro ou redirect
        # Se a view exigir POST, deve retornar erro
        self.assertIn(response.status_code, [302, 405])

    def test_voluntario_cancela_inscricao_pendente(self):
        """
        CT-V151: Voluntário cancela inscrição com status PENDENTE
        Resultado Esperado: Status muda para CANCELADO
        """
        # Usa inscricao_pendente do setUp (já é PENDENTE)
        url = reverse('acoes:inscricao_cancel', args=[self.inscricao_pendente.pk])
        response = self.client_logged_voluntario.post(url)

        # Verifica redirect
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('acoes:minhas_inscricoes'))

        # Verifica que status mudou
        self.inscricao_pendente.refresh_from_db()
        self.assertEqual(self.inscricao_pendente.status, 'CANCELADO')

    def test_voluntario_cancela_inscricao_aceita(self):
        """
        CT-V152: Voluntário cancela inscrição com status ACEITO
        Resultado Esperado: Status muda para CANCELADO
        """
        # Atualiza inscrição existente do setUp para ACEITO
        self.inscricao_pendente.status = 'ACEITO'
        self.inscricao_pendente.save()

        url = reverse('acoes:inscricao_cancel', args=[self.inscricao_pendente.pk])
        response = self.client_logged_voluntario.post(url)

        self.inscricao_pendente.refresh_from_db()
        self.assertEqual(self.inscricao_pendente.status, 'CANCELADO')

    def test_cancelamento_remove_notificacao_do_organizador_se_pendente(self):
        """
        CT-V153: Cancelar inscrição PENDENTE remove notificação do organizador
        Resultado Esperado: Notificação é deletada
        """
        # Usa inscricao_pendente do setUp (já é PENDENTE)

        # Cria notificação para o organizador (como se tivesse sido criada na inscrição)
        Notificacao.objects.create(
            destinatario=self.organizador_user,
            mensagem=f"{self.voluntario_user.username} solicitou participação em '{self.acao_futura.titulo}'.",
            link=reverse('acoes:acao_manage', args=[self.acao_futura.pk])
        )

        # Verifica que notificação existe
        self.assertTrue(Notificacao.objects.filter(
            destinatario=self.organizador_user,
            mensagem__contains=self.voluntario_user.username
        ).exists())

        # Cancela inscrição
        url = reverse('acoes:inscricao_cancel', args=[self.inscricao_pendente.pk])
        self.client_logged_voluntario.post(url)

        # Verifica que notificação foi deletada
        self.assertFalse(Notificacao.objects.filter(
            destinatario=self.organizador_user,
            mensagem__contains=self.voluntario_user.username,
            link=reverse('acoes:acao_manage', args=[self.acao_futura.pk])
        ).exists())

    def test_cancelamento_cria_notificacao_para_organizador_se_aceito(self):
        """
        CT-V154: Cancelar inscrição ACEITO cria notificação para organizador
        Resultado Esperado: Nova notificação criada
        """
        # Atualiza inscrição existente do setUp para ACEITO
        self.inscricao_pendente.status = 'ACEITO'
        self.inscricao_pendente.save()

        # Conta notificações antes
        count_antes = Notificacao.objects.filter(destinatario=self.organizador_user).count()

        # Cancela inscrição
        url = reverse('acoes:inscricao_cancel', args=[self.inscricao_pendente.pk])
        self.client_logged_voluntario.post(url)

        # Verifica que nova notificação foi criada
        count_depois = Notificacao.objects.filter(destinatario=self.organizador_user).count()
        self.assertEqual(count_depois, count_antes + 1)

        # Verifica conteúdo da notificação
        notif = Notificacao.objects.filter(destinatario=self.organizador_user).latest('created_at')
        self.assertIn('cancelou', notif.mensagem.lower())
        self.assertIn(self.voluntario_user.username, notif.mensagem)

    def test_nao_pode_cancelar_inscricao_de_acao_passada(self):
        """
        CT-V155: Não é possível cancelar inscrição em ação passada
        Resultado Esperado: Mensagem de erro, status não muda
        """
        inscricao = Inscricao.objects.create(
            acao=self.acao_passada,
            voluntario=self.voluntario_user,
            status='ACEITO'
        )

        url = reverse('acoes:inscricao_cancel', args=[inscricao.pk])
        response = self.client_logged_voluntario.post(url)

        # Verifica redirect
        self.assertEqual(response.status_code, 302)

        # Verifica que status NÃO mudou
        inscricao.refresh_from_db()
        self.assertEqual(inscricao.status, 'ACEITO')

    def test_apenas_proprio_voluntario_pode_cancelar(self):
        """
        CT-V156: Voluntário só pode cancelar própria inscrição
        Resultado Esperado: Erro 404 ao tentar cancelar de outro
        """
        # Cria outro voluntário e inscrição dele
        outro_vol = User.objects.create_user('outro_vol', 'outro@test.com', 'pass')
        inscricao_outro = Inscricao.objects.create(
            acao=self.acao_futura,
            voluntario=outro_vol,
            status='PENDENTE'
        )

        url = reverse('acoes:inscricao_cancel', args=[inscricao_outro.pk])

        # Deve dar erro 404 (get_object_or_404 com voluntario=request.user)
        response = self.client_logged_voluntario.post(url)
        self.assertEqual(response.status_code, 404)

    def test_cancelamento_exibe_mensagem_sucesso(self):
        """
        CT-V157: Cancelamento exibe mensagem de sucesso
        Resultado Esperado: Mensagem no sistema de messages
        """
        # Usa inscricao_pendente do setUp
        url = reverse('acoes:inscricao_cancel', args=[self.inscricao_pendente.pk])
        response = self.client_logged_voluntario.post(url, follow=True)

        # Verifica que tem mensagem
        messages = list(response.context['messages'])
        self.assertGreater(len(messages), 0)
        self.assertIn('cancelada', str(messages[0]).lower())

    def test_cancelamento_redireciona_para_minhas_inscricoes(self):
        """
        CT-V158: Cancelamento redireciona para minhas inscrições
        Resultado Esperado: Redirect correto
        """
        # Usa inscricao_pendente do setUp
        url = reverse('acoes:inscricao_cancel', args=[self.inscricao_pendente.pk])
        response = self.client_logged_voluntario.post(url)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('acoes:minhas_inscricoes'))

    def test_cancelar_inscricao_rejeitada_tambem_funciona(self):
        """
        CT-V159: É possível cancelar inscrição rejeitada (para limpar histórico)
        Resultado Esperado: Status muda para CANCELADO
        """
        # Atualiza inscrição existente do setUp para REJEITADO
        self.inscricao_pendente.status = 'REJEITADO'
        self.inscricao_pendente.save()

        url = reverse('acoes:inscricao_cancel', args=[self.inscricao_pendente.pk])
        response = self.client_logged_voluntario.post(url)

        self.inscricao_pendente.refresh_from_db()
        self.assertEqual(self.inscricao_pendente.status, 'CANCELADO')
