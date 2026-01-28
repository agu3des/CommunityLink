"""
Testes dos Modelos do app 'acoes'

Este arquivo testa a lógica de negócio dos modelos:
- Acao: Criação, validações, propriedades calculadas
- Inscricao: Relacionamentos, constraints
- Notificacao: Criação e marcação de lida
"""

from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.utils import IntegrityError
from datetime import timedelta
from acoes.models import Acao, Inscricao, Notificacao
from .test_base import FullFixturesMixin


# ============================================
# SPRINT 1 - CRUD Ações + Inscrições
# ============================================


class TestAcaoModel(FullFixturesMixin, TestCase):
    """
    CT-M001: Testes do modelo Acao
    Referência: Documento de Casos de Teste - Modelos
    """

    def test_criar_acao_valida(self):
        """
        CT-M001.1: Criar ação com todos os campos válidos
        Resultado Esperado: Ação criada com sucesso
        """
        acao = Acao.objects.create(
            titulo='Campanha de Vacinação',
            descricao='Vacinação gratuita para a comunidade',
            data=timezone.now() + timedelta(days=30),
            local='Centro de Saúde - Rua A, 123',
            numero_vagas=50,
            categoria='SAUDE',
            organizador=self.organizador_user
        )

        self.assertEqual(acao.titulo, 'Campanha de Vacinação')
        self.assertEqual(acao.numero_vagas, 50)
        self.assertEqual(acao.categoria, 'SAUDE')
        self.assertEqual(acao.organizador, self.organizador_user)

    def test_str_retorna_titulo(self):
        """
        CT-M001.2: Método __str__ retorna o título da ação
        Resultado Esperado: String igual ao título
        """
        self.assertEqual(str(self.acao_futura), self.acao_futura.titulo)

    def test_get_absolute_url(self):
        """
        CT-M001.3: get_absolute_url retorna URL correta
        Resultado Esperado: URL no formato /acoes/<pk>/
        """
        expected_url = f'/acoes/{self.acao_futura.pk}/'
        self.assertEqual(self.acao_futura.get_absolute_url(), expected_url)

    def test_vagas_preenchidas_inicial_zero(self):
        """
        CT-M002.1: Ação nova tem 0 vagas preenchidas
        Resultado Esperado: vagas_preenchidas == 0
        """
        self.assertEqual(self.acao_futura.vagas_preenchidas, 0)

    def test_vagas_preenchidas_conta_apenas_aceitos(self):
        """
        CT-M002.2: vagas_preenchidas conta apenas inscrições ACEITAS
        Resultado Esperado: Apenas status='ACEITO' são contados
        """
        # Cria 3 inscrições aceitas
        for i in range(3):
            vol = User.objects.create_user(f'vol_aceito_{i}', f'vol{i}@test.com', 'pass')
            Inscricao.objects.create(acao=self.acao_futura, voluntario=vol, status='ACEITO')

        # Cria 2 inscrições pendentes
        for i in range(2):
            vol = User.objects.create_user(f'vol_pend_{i}', f'pend{i}@test.com', 'pass')
            Inscricao.objects.create(acao=self.acao_futura, voluntario=vol, status='PENDENTE')

        # Cria 1 inscrição rejeitada
        vol_rej = User.objects.create_user('vol_rej', 'rej@test.com', 'pass')
        Inscricao.objects.create(acao=self.acao_futura, voluntario=vol_rej, status='REJEITADO')

        self.assertEqual(self.acao_futura.vagas_preenchidas, 3)

    def test_esta_cheia_false_com_vagas(self):
        """
        CT-M003.1: esta_cheia retorna False quando há vagas
        Resultado Esperado: esta_cheia == False
        """
        self.assertFalse(self.acao_futura.esta_cheia)

    def test_esta_cheia_true_quando_lotada(self):
        """
        CT-M003.2: esta_cheia retorna True quando todas vagas preenchidas
        Resultado Esperado: esta_cheia == True
        """
        self.assertTrue(self.acao_cheia.esta_cheia)

    def test_categorias_validas(self):
        """
        CT-M004: Apenas categorias definidas em CATEGORIA_CHOICES são válidas
        Resultado Esperado: Ação aceita categorias válidas
        """
        categorias_validas = ['SAUDE', 'EDUCACAO', 'MEIO_AMBIENTE', 'ANIMAIS', 'OUTRO']

        for categoria in categorias_validas:
            with self.subTest(categoria=categoria):
                acao = Acao.objects.create(
                    titulo=f'Ação {categoria}',
                    descricao='Teste',
                    data=timezone.now() + timedelta(days=7),
                    local='Local',
                    numero_vagas=10,
                    categoria=categoria,
                    organizador=self.organizador_user
                )
                self.assertEqual(acao.categoria, categoria)


class TestInscricaoModel(FullFixturesMixin, TestCase):
    """
    CT-M010: Testes do modelo Inscricao
    Referência: Documento de Casos de Teste - Inscrições
    """

    def test_criar_inscricao_valida(self):
        """
        CT-M010.1: Criar inscrição com ação e voluntário válidos
        Resultado Esperado: Inscrição criada com status PENDENTE
        """
        novo_vol = User.objects.create_user('novo_vol_inscr', 'novovol@test.com', 'pass')
        inscricao = Inscricao.objects.create(
            acao=self.acao_futura,
            voluntario=novo_vol
        )

        self.assertEqual(inscricao.status, 'PENDENTE')
        self.assertEqual(inscricao.acao, self.acao_futura)
        self.assertEqual(inscricao.voluntario, novo_vol)
        self.assertIsNotNone(inscricao.data_inscricao)

    def test_status_choices_validos(self):
        """
        CT-M010.2: Inscrição aceita status PENDENTE, ACEITO e REJEITADO
        Resultado Esperado: Status definido corretamente
        """
        status_validos = ['PENDENTE', 'ACEITO', 'REJEITADO']

        for i, status in enumerate(status_validos):
            with self.subTest(status=status):
                vol = User.objects.create_user(f'vol_{i}', f'vol{i}@test.com', 'pass')
                inscricao = Inscricao.objects.create(
                    acao=self.acao_futura,
                    voluntario=vol,
                    status=status
                )
                self.assertEqual(inscricao.status, status)

    def test_unique_together_impede_inscricao_duplicada(self):
        """
        CT-M011: Usuário não pode se inscrever 2x na mesma ação
        Resultado Esperado: IntegrityError ao tentar duplicar
        """
        # Primeira inscrição já existe via setUp (self.inscricao_pendente)
        # Segunda inscrição deve falhar
        with self.assertRaises(IntegrityError):
            Inscricao.objects.create(acao=self.acao_futura, voluntario=self.voluntario_user)

    def test_voluntario_pode_se_inscrever_em_multiplas_acoes(self):
        """
        CT-M012: Voluntário pode se inscrever em várias ações diferentes
        Resultado Esperado: Múltiplas inscrições criadas com sucesso
        """
        # Cria 3 ações diferentes
        acoes = []
        for i in range(3):
            acao = Acao.objects.create(
                titulo=f'Ação {i}',
                descricao='Teste',
                data=timezone.now() + timedelta(days=7 + i),
                local='Local',
                numero_vagas=10,
                organizador=self.organizador_user
            )
            acoes.append(acao)

        # Inscreve o mesmo voluntário nas 3 ações
        for acao in acoes:
            Inscricao.objects.create(acao=acao, voluntario=self.voluntario_user)

        # Verifica que o voluntário tem 3 novas inscrições + 1 do setUp
        self.assertEqual(Inscricao.objects.filter(voluntario=self.voluntario_user).count(), 4)

    def test_str_representation(self):
        """
        CT-M013: Método __str__ retorna formato legível
        Resultado Esperado: String com username, título da ação e status
        """
        expected = f'{self.inscricao_pendente.voluntario.username} em {self.inscricao_pendente.acao.titulo} ({self.inscricao_pendente.status})'
        self.assertEqual(str(self.inscricao_pendente), expected)


class TestNotificacaoModel(FullFixturesMixin, TestCase):
    """
    CT-M020: Testes do modelo Notificacao
    Referência: Documento de Casos de Teste - Notificações
    """

    def test_criar_notificacao_valida(self):
        """
        CT-M020.1: Criar notificação com destinatário e mensagem
        Resultado Esperado: Notificação criada com lida=False
        """
        notificacao = Notificacao.objects.create(
            destinatario=self.voluntario_user,
            mensagem='Sua inscrição foi aceita!'
        )

        self.assertEqual(notificacao.destinatario, self.voluntario_user)
        self.assertEqual(notificacao.mensagem, 'Sua inscrição foi aceita!')
        self.assertFalse(notificacao.lida)
        self.assertIsNotNone(notificacao.created_at)

    def test_notificacao_com_link(self):
        """
        CT-M020.2: Notificação pode ter link opcional
        Resultado Esperado: Link armazenado corretamente
        """
        notificacao = Notificacao.objects.create(
            destinatario=self.voluntario_user,
            mensagem='Nova ação disponível',
            link='http://example.com/acoes/1/'
        )

        self.assertEqual(notificacao.link, 'http://example.com/acoes/1/')

    def test_marcar_como_lida(self):
        """
        CT-M021: Marcar notificação como lida
        Resultado Esperado: lida muda de False para True
        """
        notificacao = Notificacao.objects.create(
            destinatario=self.voluntario_user,
            mensagem='Teste'
        )

        self.assertFalse(notificacao.lida)

        notificacao.lida = True
        notificacao.save()

        self.assertTrue(notificacao.lida)

    def test_ordering_por_created_at_desc(self):
        """
        CT-M022: Notificações ordenadas por created_at descendente (mais recentes primeiro)
        Resultado Esperado: Ordem correta ao buscar do banco
        """
        # Cria 3 notificações em momentos diferentes
        notif1 = Notificacao.objects.create(
            destinatario=self.voluntario_user,
            mensagem='Primeira'
        )

        notif2 = Notificacao.objects.create(
            destinatario=self.voluntario_user,
            mensagem='Segunda'
        )

        notif3 = Notificacao.objects.create(
            destinatario=self.voluntario_user,
            mensagem='Terceira'
        )

        # Busca todas as notificações (usando a ordenação padrão do Meta)
        notificacoes = list(Notificacao.objects.filter(destinatario=self.voluntario_user))

        # A mais recente deve vir primeiro
        self.assertEqual(notificacoes[0], notif3)
        self.assertEqual(notificacoes[1], notif2)
        self.assertEqual(notificacoes[2], notif1)

    def test_str_trunca_mensagem_longa(self):
        """
        CT-M023: __str__ trunca mensagens longas em 30 caracteres
        Resultado Esperado: String com mensagem truncada + '...'
        """
        mensagem_longa = 'Esta é uma mensagem muito longa que deve ser truncada no método __str__'
        notificacao = Notificacao.objects.create(
            destinatario=self.voluntario_user,
            mensagem=mensagem_longa
        )

        str_repr = str(notificacao)
        self.assertIn('...', str_repr)
        self.assertLessEqual(len(notificacao.mensagem[:30]), 30)
