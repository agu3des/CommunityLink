"""
Testes dos Formulários

Este arquivo testa a validação e comportamento dos formulários:
- AcaoForm: Criação e edição de ações
"""

from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from acoes.forms import AcaoForm
from acoes.models import Acao
from .test_base import FullFixturesMixin


# ============================================
# SPRINT 1 - Formulário de Ações
# ============================================


class TestAcaoForm(FullFixturesMixin, TestCase):
    """
    CT-F001: Testes do formulário AcaoForm
    Referência: Documento de Casos de Teste - Formulários
    """

    def test_form_valido_com_dados_completos(self):
        """
        CT-F001.1: Form válido com todos os dados corretos
        Resultado Esperado: is_valid() == True
        """
        data = {
            'titulo': 'Campanha de Doação',
            'descricao': 'Descrição da campanha',
            'data': (timezone.now() + timedelta(days=7)).strftime('%Y-%m-%dT%H:%M'),
            'local': 'Centro Comunitário',
            'numero_vagas': 20,
            'categoria': 'SAUDE'
        }

        form = AcaoForm(data=data)
        self.assertTrue(form.is_valid())

    def test_form_invalido_sem_titulo(self):
        """
        CT-F001.2: Form inválido sem título
        Resultado Esperado: is_valid() == False, erro no campo 'titulo'
        """
        data = {
            'descricao': 'Descrição',
            'data': (timezone.now() + timedelta(days=7)).strftime('%Y-%m-%dT%H:%M'),
            'local': 'Local',
            'numero_vagas': 10,
            'categoria': 'EDUCACAO'
        }

        form = AcaoForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('titulo', form.errors)

    def test_form_invalido_sem_data(self):
        """
        CT-F001.3: Form inválido sem data
        Resultado Esperado: is_valid() == False, erro no campo 'data'
        """
        data = {
            'titulo': 'Título',
            'descricao': 'Descrição',
            'local': 'Local',
            'numero_vagas': 10,
            'categoria': 'EDUCACAO'
        }

        form = AcaoForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('data', form.errors)

    def test_form_invalido_sem_local(self):
        """
        CT-F001.4: Form inválido sem local
        Resultado Esperado: is_valid() == False, erro no campo 'local'
        """
        data = {
            'titulo': 'Título',
            'descricao': 'Descrição',
            'data': (timezone.now() + timedelta(days=7)).strftime('%Y-%m-%dT%H:%M'),
            'numero_vagas': 10,
            'categoria': 'EDUCACAO'
        }

        form = AcaoForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('local', form.errors)

    def test_form_invalido_sem_numero_vagas(self):
        """
        CT-F001.5: Form inválido sem número de vagas
        Resultado Esperado: is_valid() == False, erro no campo 'numero_vagas'
        """
        data = {
            'titulo': 'Título',
            'descricao': 'Descrição',
            'data': (timezone.now() + timedelta(days=7)).strftime('%Y-%m-%dT%H:%M'),
            'local': 'Local',
            'categoria': 'EDUCACAO'
        }

        form = AcaoForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('numero_vagas', form.errors)

    def test_form_invalido_numero_vagas_negativo(self):
        """
        CT-F002: Form inválido com número de vagas negativo
        Resultado Esperado: is_valid() == False
        """
        data = {
            'titulo': 'Título',
            'descricao': 'Descrição',
            'data': (timezone.now() + timedelta(days=7)).strftime('%Y-%m-%dT%H:%M'),
            'local': 'Local',
            'numero_vagas': -5,
            'categoria': 'EDUCACAO'
        }

        form = AcaoForm(data=data)
        self.assertFalse(form.is_valid())

    def test_form_invalido_numero_vagas_zero(self):
        """
        CT-F003: Form inválido com número de vagas zero
        Resultado Esperado: is_valid() == False
        """
        data = {
            'titulo': 'Título',
            'descricao': 'Descrição',
            'data': (timezone.now() + timedelta(days=7)).strftime('%Y-%m-%dT%H:%M'),
            'local': 'Local',
            'numero_vagas': 0,
            'categoria': 'EDUCACAO'
        }

        form = AcaoForm(data=data)
        self.assertFalse(form.is_valid())

    def test_form_aceita_todas_categorias_validas(self):
        """
        CT-F004: Form aceita todas as categorias definidas em CATEGORIA_CHOICES
        Resultado Esperado: Form válido para cada categoria
        """
        categorias = ['SAUDE', 'EDUCACAO', 'MEIO_AMBIENTE', 'ANIMAIS', 'OUTRO']

        for categoria in categorias:
            with self.subTest(categoria=categoria):
                data = {
                    'titulo': f'Ação {categoria}',
                    'descricao': 'Descrição',
                    'data': (timezone.now() + timedelta(days=7)).strftime('%Y-%m-%dT%H:%M'),
                    'local': 'Local',
                    'numero_vagas': 10,
                    'categoria': categoria
                }

                form = AcaoForm(data=data)
                self.assertTrue(form.is_valid(), f"Categoria {categoria} deveria ser válida")

    def test_form_invalido_categoria_inexistente(self):
        """
        CT-F005: Form inválido com categoria não definida
        Resultado Esperado: is_valid() == False
        """
        data = {
            'titulo': 'Título',
            'descricao': 'Descrição',
            'data': (timezone.now() + timedelta(days=7)).strftime('%Y-%m-%dT%H:%M'),
            'local': 'Local',
            'numero_vagas': 10,
            'categoria': 'CATEGORIA_INVALIDA'
        }

        form = AcaoForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('categoria', form.errors)

    def test_form_data_campo_usa_datetime_local_widget(self):
        """
        CT-F006: Campo data usa widget datetime-local
        Resultado Esperado: Widget correto configurado
        """
        form = AcaoForm()
        data_widget = form.fields['data'].widget

        self.assertEqual(data_widget.input_type, 'datetime-local')

    def test_form_salva_acao_corretamente(self):
        """
        CT-F007: Form salva ação no banco corretamente
        Resultado Esperado: Ação criada com dados corretos
        """
        data = {
            'titulo': 'Ação para Salvar',
            'descricao': 'Descrição completa',
            'data': (timezone.now() + timedelta(days=10)).strftime('%Y-%m-%dT%H:%M'),
            'local': 'Rua ABC, 123',
            'numero_vagas': 25,
            'categoria': 'MEIO_AMBIENTE'
        }

        form = AcaoForm(data=data)
        self.assertTrue(form.is_valid())

        # Salva a ação (sem commit para adicionar organizador)
        acao = form.save(commit=False)
        acao.organizador = self.organizador_user
        acao.save()

        # Verifica que foi salva corretamente
        self.assertTrue(Acao.objects.filter(titulo='Ação para Salvar').exists())
        acao_db = Acao.objects.get(titulo='Ação para Salvar')
        self.assertEqual(acao_db.numero_vagas, 25)
        self.assertEqual(acao_db.categoria, 'MEIO_AMBIENTE')
        self.assertEqual(acao_db.organizador, self.organizador_user)

    def test_form_edicao_mantem_dados_existentes(self):
        """
        CT-F008: Form de edição carrega dados existentes da ação
        Resultado Esperado: Campos preenchidos com dados atuais
        """
        form = AcaoForm(instance=self.acao_futura)

        self.assertEqual(form.instance, self.acao_futura)
        self.assertEqual(form.initial['titulo'], self.acao_futura.titulo)
        self.assertEqual(form.initial['numero_vagas'], self.acao_futura.numero_vagas)

    def test_form_campos_obrigatorios_corretos(self):
        """
        CT-F009: Verifica quais campos são obrigatórios
        Resultado Esperado: Todos os campos exceto descricao são required
        """
        form = AcaoForm()

        # Campos obrigatórios
        self.assertTrue(form.fields['titulo'].required)
        self.assertTrue(form.fields['data'].required)
        self.assertTrue(form.fields['local'].required)
        self.assertTrue(form.fields['numero_vagas'].required)
        self.assertTrue(form.fields['categoria'].required)

    def test_form_titulo_longo_invalido(self):
        """
        CT-F010: Título maior que max_length é inválido
        Resultado Esperado: is_valid() == False
        """
        titulo_longo = 'A' * 201  # Limite é 200

        data = {
            'titulo': titulo_longo,
            'descricao': 'Descrição',
            'data': (timezone.now() + timedelta(days=7)).strftime('%Y-%m-%dT%H:%M'),
            'local': 'Local',
            'numero_vagas': 10,
            'categoria': 'SAUDE'
        }

        form = AcaoForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('titulo', form.errors)

    def test_form_local_longo_invalido(self):
        """
        CT-F011: Local maior que max_length é inválido
        Resultado Esperado: is_valid() == False
        """
        local_longo = 'A' * 256  # Limite é 255

        data = {
            'titulo': 'Título',
            'descricao': 'Descrição',
            'data': (timezone.now() + timedelta(days=7)).strftime('%Y-%m-%dT%H:%M'),
            'local': local_longo,
            'numero_vagas': 10,
            'categoria': 'SAUDE'
        }

        form = AcaoForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('local', form.errors)

    def test_form_data_formato_correto(self):
        """
        CT-F012: Form aceita data no formato correto
        Resultado Esperado: is_valid() == True
        """
        data = {
            'titulo': 'Título',
            'descricao': 'Descrição',
            'data': '2025-12-31T14:30',  # Formato datetime-local
            'local': 'Local',
            'numero_vagas': 10,
            'categoria': 'SAUDE'
        }

        form = AcaoForm(data=data)
        self.assertTrue(form.is_valid())
