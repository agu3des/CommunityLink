"""
Testes de Histórico

Este arquivo testa:
- Visualização de histórico de participação (voluntários)
- Visualização de histórico de ações organizadas (organizadores)
- Salvamento de comentários por voluntários
- Salvamento de notas privadas por organizadores
- Filtros no histórico
"""

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from acoes.models import Acao, Inscricao
from .test_base import FullFixturesMixin


# ============================================
# SPRINT 2 - Histórico
# ============================================


class TestHistoricoView(FullFixturesMixin, TestCase):
    """
    CT-H001: Testes de visualização de histórico
    Referência: Documento de Casos de Teste - Histórico
    """

    def test_historico_requer_login(self):
        """
        CT-H001.1: Página de histórico requer autenticação
        Resultado Esperado: Redirect para login
        """
        url = reverse('acoes:historico')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_historico_acessivel_quando_logado(self):
        """
        CT-H001.2: Usuário logado acessa histórico
        Resultado Esperado: Status 200
        """
        url = reverse('acoes:historico')
        response = self.client_logged_voluntario.get(url)
        self.assertEqual(response.status_code, 200)

    def test_historico_mostra_apenas_acoes_passadas(self):
        """
        CT-H002: Histórico mostra apenas ações com data < hoje
        Resultado Esperado: Ações futuras não aparecem
        """
        # Cria ação passada
        acao_passada = Acao.objects.create(
            titulo='Ação Passada',
            descricao='Teste',
            data=timezone.now() - timedelta(days=7),
            local='Local',
            numero_vagas=10,
            organizador=self.organizador_user
        )
        inscricao_passada = Inscricao.objects.create(
            acao=acao_passada,
            voluntario=self.voluntario_user,
            status='ACEITO'
        )

        # Cria ação futura
        acao_futura = Acao.objects.create(
            titulo='Ação Futura',
            descricao='Teste',
            data=timezone.now() + timedelta(days=7),
            local='Local',
            numero_vagas=10,
            organizador=self.organizador_user
        )
        inscricao_futura = Inscricao.objects.create(
            acao=acao_futura,
            voluntario=self.voluntario_user,
            status='ACEITO'
        )

        url = reverse('acoes:historico')
        response = self.client_logged_voluntario.get(url)

        historico = response.context['historico_participacoes']

        # Apenas ação passada deve aparecer
        self.assertIn(inscricao_passada, historico)
        self.assertNotIn(inscricao_futura, historico)

    def test_historico_mostra_apenas_aceitos_ou_cancelados(self):
        """
        CT-H003: Histórico mostra apenas inscrições ACEITO ou CANCELADO
        Resultado Esperado: PENDENTE e REJEITADO não aparecem
        """
        acao_passada = Acao.objects.create(
            titulo='Ação Passada',
            descricao='Teste',
            data=timezone.now() - timedelta(days=7),
            local='Local',
            numero_vagas=10,
            organizador=self.organizador_user
        )

        # Inscrição aceita (deve aparecer)
        inscr_aceita = Inscricao.objects.create(
            acao=acao_passada,
            voluntario=self.voluntario_user,
            status='ACEITO'
        )

        # Cria outra ação para testar outros status
        acao_passada2 = Acao.objects.create(
            titulo='Ação Passada 2',
            descricao='Teste',
            data=timezone.now() - timedelta(days=5),
            local='Local',
            numero_vagas=10,
            organizador=self.organizador_user
        )

        # Inscrição pendente (não deve aparecer)
        from django.contrib.auth.models import User
        outro_user = User.objects.create_user('outro', 'outro@test.com', 'pass')
        inscr_pendente = Inscricao.objects.create(
            acao=acao_passada2,
            voluntario=outro_user,
            status='PENDENTE'
        )

        url = reverse('acoes:historico')
        response = self.client_logged_voluntario.get(url)

        historico = list(response.context['historico_participacoes'])

        # Apenas aceita deve aparecer para o voluntario_user
        self.assertIn(inscr_aceita, historico)
        self.assertNotIn(inscr_pendente, historico)

    def test_historico_mostra_apenas_inscricoes_do_usuario(self):
        """
        CT-H004: Histórico mostra apenas inscrições do usuário logado
        Resultado Esperado: Inscrições de outros não aparecem
        """
        from django.contrib.auth.models import User

        acao_passada = Acao.objects.create(
            titulo='Ação Passada',
            descricao='Teste',
            data=timezone.now() - timedelta(days=7),
            local='Local',
            numero_vagas=10,
            organizador=self.organizador_user
        )

        # Inscrição do voluntário logado
        inscr_user = Inscricao.objects.create(
            acao=acao_passada,
            voluntario=self.voluntario_user,
            status='ACEITO'
        )

        # Inscrição de outro voluntário
        outro_vol = User.objects.create_user('outro_vol', 'outro@test.com', 'pass')
        inscr_outro = Inscricao.objects.create(
            acao=acao_passada,
            voluntario=outro_vol,
            status='ACEITO'
        )

        url = reverse('acoes:historico')
        response = self.client_logged_voluntario.get(url)

        historico = response.context['historico_participacoes']

        self.assertIn(inscr_user, historico)
        self.assertNotIn(inscr_outro, historico)

    def test_historico_ordenado_por_data_desc(self):
        """
        CT-H005: Histórico ordenado por data (mais recentes primeiro)
        Resultado Esperado: Ordem descendente
        """
        # Cria 3 ações em datas diferentes (todas no passado)
        acao1 = Acao.objects.create(
            titulo='Ação há 30 dias',
            descricao='Teste',
            data=timezone.now() - timedelta(days=30),
            local='Local',
            numero_vagas=10,
            organizador=self.organizador_user
        )
        acao2 = Acao.objects.create(
            titulo='Ação há 7 dias',
            descricao='Teste',
            data=timezone.now() - timedelta(days=7),
            local='Local',
            numero_vagas=10,
            organizador=self.organizador_user
        )
        acao3 = Acao.objects.create(
            titulo='Ação há 15 dias',
            descricao='Teste',
            data=timezone.now() - timedelta(days=15),
            local='Local',
            numero_vagas=10,
            organizador=self.organizador_user
        )

        # Inscreve em todas
        inscr1 = Inscricao.objects.create(acao=acao1, voluntario=self.voluntario_user, status='ACEITO')
        inscr2 = Inscricao.objects.create(acao=acao2, voluntario=self.voluntario_user, status='ACEITO')
        inscr3 = Inscricao.objects.create(acao=acao3, voluntario=self.voluntario_user, status='ACEITO')

        url = reverse('acoes:historico')
        response = self.client_logged_voluntario.get(url)

        historico = list(response.context['historico_participacoes'])

        # Mais recente primeiro: 7 dias, 15 dias, 30 dias
        self.assertEqual(historico[0], inscr2)
        self.assertEqual(historico[1], inscr3)
        self.assertEqual(historico[2], inscr1)


class TestHistoricoOrganizador(FullFixturesMixin, TestCase):
    """
    CT-H010: Testes de histórico para organizadores
    """

    def test_organizador_ve_historico_de_acoes_organizadas(self):
        """
        CT-H010.1: Organizador vê histórico de ações que organizou
        Resultado Esperado: historico_organizadas não é None
        """
        # Cria ação passada do organizador
        acao_passada = Acao.objects.create(
            titulo='Ação Organizada Passada',
            descricao='Teste',
            data=timezone.now() - timedelta(days=7),
            local='Local',
            numero_vagas=10,
            organizador=self.organizador_user
        )

        url = reverse('acoes:historico')
        response = self.client_logged_organizador.get(url)

        self.assertIsNotNone(response.context['historico_organizadas'])
        self.assertIn(acao_passada, response.context['historico_organizadas'])

    def test_organizador_nao_ve_acoes_de_outros(self):
        """
        CT-H010.2: Organizador vê apenas suas próprias ações
        Resultado Esperado: Ações de outros não aparecem
        """
        from django.contrib.auth.models import User

        # Ação do organizador logado
        acao_propria = Acao.objects.create(
            titulo='Ação Própria',
            descricao='Teste',
            data=timezone.now() - timedelta(days=7),
            local='Local',
            numero_vagas=10,
            organizador=self.organizador_user
        )

        # Ação de outro organizador
        outro_org = User.objects.create_user('outro_org', 'org@test.com', 'pass')
        acao_outro = Acao.objects.create(
            titulo='Ação de Outro',
            descricao='Teste',
            data=timezone.now() - timedelta(days=7),
            local='Local',
            numero_vagas=10,
            organizador=outro_org
        )

        url = reverse('acoes:historico')
        response = self.client_logged_organizador.get(url)

        historico_org = response.context['historico_organizadas']

        self.assertIn(acao_propria, historico_org)
        self.assertNotIn(acao_outro, historico_org)

    def test_voluntario_nao_ve_historico_organizadas(self):
        """
        CT-H011: Voluntário não vê seção de histórico organizadas
        Resultado Esperado: historico_organizadas é None
        """
        url = reverse('acoes:historico')
        response = self.client_logged_voluntario.get(url)

        # Voluntário não deve ter seção de organizadas
        self.assertIsNone(response.context['historico_organizadas'])

    def test_organizador_ve_ambos_historicos(self):
        """
        CT-H012: Organizador vê histórico de participação E organização
        Resultado Esperado: Ambas seções preenchidas
        """
        # Cria ação organizada por ele
        acao_organizada = Acao.objects.create(
            titulo='Ação Organizada',
            descricao='Teste',
            data=timezone.now() - timedelta(days=7),
            local='Local',
            numero_vagas=10,
            organizador=self.organizador_user
        )

        # Cria ação de outro e organizador se inscreve como voluntário
        acao_participou = Acao.objects.create(
            titulo='Ação que Participou',
            descricao='Teste',
            data=timezone.now() - timedelta(days=5),
            local='Local',
            numero_vagas=10,
            organizador=self.voluntario_user
        )
        inscr = Inscricao.objects.create(
            acao=acao_participou,
            voluntario=self.organizador_user,
            status='ACEITO'
        )

        url = reverse('acoes:historico')
        response = self.client_logged_organizador.get(url)

        # Deve ter ambos
        self.assertIn(acao_organizada, response.context['historico_organizadas'])
        self.assertIn(inscr, response.context['historico_participacoes'])


class TestComentariosNotasView(FullFixturesMixin, TestCase):
    """
    CT-H020: Testes de salvamento de comentários e notas
    """

    def test_voluntario_salva_comentario_em_inscricao(self):
        """
        CT-H020.1: Voluntário pode salvar comentário em inscrição passada
        Resultado Esperado: Comentário salvo na inscrição
        """
        acao_passada = Acao.objects.create(
            titulo='Ação Passada',
            descricao='Teste',
            data=timezone.now() - timedelta(days=7),
            local='Local',
            numero_vagas=10,
            organizador=self.organizador_user
        )
        inscricao = Inscricao.objects.create(
            acao=acao_passada,
            voluntario=self.voluntario_user,
            status='ACEITO'
        )

        url = reverse('acoes:historico')
        data = {
            'inscricao_id': inscricao.id,
            'comentario': 'Foi uma experiência incrível! Aprendi muito.'
        }

        response = self.client_logged_voluntario.post(url, data)

        # Verifica redirect
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('acoes:historico'))

        # Verifica que comentário foi salvo
        inscricao.refresh_from_db()
        self.assertEqual(inscricao.comentario, 'Foi uma experiência incrível! Aprendi muito.')

    def test_voluntario_atualiza_comentario_existente(self):
        """
        CT-H020.2: Voluntário pode atualizar comentário existente
        Resultado Esperado: Comentário sobrescrito
        """
        acao_passada = Acao.objects.create(
            titulo='Ação Passada',
            descricao='Teste',
            data=timezone.now() - timedelta(days=7),
            local='Local',
            numero_vagas=10,
            organizador=self.organizador_user
        )
        inscricao = Inscricao.objects.create(
            acao=acao_passada,
            voluntario=self.voluntario_user,
            status='ACEITO',
            comentario='Comentário antigo'
        )

        url = reverse('acoes:historico')
        data = {
            'inscricao_id': inscricao.id,
            'comentario': 'Comentário atualizado'
        }

        response = self.client_logged_voluntario.post(url, data)

        inscricao.refresh_from_db()
        self.assertEqual(inscricao.comentario, 'Comentário atualizado')

    def test_organizador_salva_notas_em_acao(self):
        """
        CT-H021: Organizador pode salvar notas privadas em ação
        Resultado Esperado: Notas salvas na ação
        """
        acao_passada = Acao.objects.create(
            titulo='Ação Passada',
            descricao='Teste',
            data=timezone.now() - timedelta(days=7),
            local='Local',
            numero_vagas=10,
            organizador=self.organizador_user
        )

        url = reverse('acoes:historico')
        data = {
            'acao_id': acao_passada.id,
            'notas_organizador': 'Ação foi um sucesso. Tivemos ótima participação.'
        }

        response = self.client_logged_organizador.post(url, data)

        # Verifica redirect
        self.assertEqual(response.status_code, 302)

        # Verifica que notas foram salvas
        acao_passada.refresh_from_db()
        self.assertEqual(acao_passada.notas_organizador, 'Ação foi um sucesso. Tivemos ótima participação.')

    def test_organizador_atualiza_notas_existentes(self):
        """
        CT-H021.2: Organizador pode atualizar notas existentes
        Resultado Esperado: Notas sobrescritas
        """
        acao_passada = Acao.objects.create(
            titulo='Ação Passada',
            descricao='Teste',
            data=timezone.now() - timedelta(days=7),
            local='Local',
            numero_vagas=10,
            organizador=self.organizador_user,
            notas_organizador='Notas antigas'
        )

        url = reverse('acoes:historico')
        data = {
            'acao_id': acao_passada.id,
            'notas_organizador': 'Notas atualizadas com mais detalhes.'
        }

        response = self.client_logged_organizador.post(url, data)

        acao_passada.refresh_from_db()
        self.assertEqual(acao_passada.notas_organizador, 'Notas atualizadas com mais detalhes.')

    def test_organizador_nao_pode_salvar_notas_de_acao_de_outro(self):
        """
        CT-H022: Organizador não pode salvar notas em ação de outro
        Resultado Esperado: Erro 404
        """
        from django.contrib.auth.models import User

        outro_org = User.objects.create_user('outro', 'outro@test.com', 'pass')
        acao_outro = Acao.objects.create(
            titulo='Ação de Outro',
            descricao='Teste',
            data=timezone.now() - timedelta(days=7),
            local='Local',
            numero_vagas=10,
            organizador=outro_org
        )

        url = reverse('acoes:historico')
        data = {
            'acao_id': acao_outro.id,
            'notas_organizador': 'Tentando hackear'
        }

        # Deve dar erro 404 (get_object_or_404 com organizador=request.user)
        with self.assertRaises(Exception):  # Pode ser Http404
            response = self.client_logged_organizador.post(url, data)

    def test_voluntario_nao_pode_salvar_comentario_de_inscricao_de_outro(self):
        """
        CT-H023: Voluntário não pode salvar comentário em inscrição de outro
        Resultado Esperado: Erro 404
        """
        from django.contrib.auth.models import User

        outro_vol = User.objects.create_user('outro_vol', 'outro@test.com', 'pass')
        acao_passada = Acao.objects.create(
            titulo='Ação Passada',
            descricao='Teste',
            data=timezone.now() - timedelta(days=7),
            local='Local',
            numero_vagas=10,
            organizador=self.organizador_user
        )
        inscricao_outro = Inscricao.objects.create(
            acao=acao_passada,
            voluntario=outro_vol,
            status='ACEITO'
        )

        url = reverse('acoes:historico')
        data = {
            'inscricao_id': inscricao_outro.id,
            'comentario': 'Tentando hackear'
        }

        # Deve dar erro 404
        with self.assertRaises(Exception):
            response = self.client_logged_voluntario.post(url, data)


class TestHistoricoFiltros(FullFixturesMixin, TestCase):
    """
    CT-H030: Testes de filtros no histórico
    """

    def test_historico_filtro_por_categoria(self):
        """
        CT-H030.1: Filtro por categoria funciona no histórico
        Resultado Esperado: Apenas ações da categoria filtrada
        """
        # Cria ação de SAUDE
        acao_saude = Acao.objects.create(
            titulo='Ação Saúde',
            descricao='Teste',
            data=timezone.now() - timedelta(days=7),
            local='Local',
            numero_vagas=10,
            categoria='SAUDE',
            organizador=self.organizador_user
        )
        inscr_saude = Inscricao.objects.create(acao=acao_saude, voluntario=self.voluntario_user, status='ACEITO')

        # Cria ação de EDUCACAO
        acao_educacao = Acao.objects.create(
            titulo='Ação Educação',
            descricao='Teste',
            data=timezone.now() - timedelta(days=7),
            local='Local',
            numero_vagas=10,
            categoria='EDUCACAO',
            organizador=self.organizador_user
        )
        inscr_educacao = Inscricao.objects.create(acao=acao_educacao, voluntario=self.voluntario_user, status='ACEITO')

        url = reverse('acoes:historico') + '?categoria=SAUDE'
        response = self.client_logged_voluntario.get(url)

        historico = response.context['historico_participacoes']

        self.assertIn(inscr_saude, historico)
        self.assertNotIn(inscr_educacao, historico)

    def test_historico_paginacao_separada(self):
        """
        CT-H031: Paginação usa parâmetros separados (page_part e page_org)
        Resultado Esperado: Paginações independentes
        """
        # Cria várias ações organizadas (mais de 5 para forçar paginação)
        for i in range(7):
            Acao.objects.create(
                titulo=f'Ação Organizada {i}',
                descricao='Teste',
                data=timezone.now() - timedelta(days=7+i),
                local='Local',
                numero_vagas=10,
                organizador=self.organizador_user
            )

        # Acessa página 2 de organizadas
        url = reverse('acoes:historico') + '?page_org=2'
        response = self.client_logged_organizador.get(url)

        # Deve funcionar sem erro
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context['historico_organizadas'])
