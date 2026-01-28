"""
Testes de Perfil de Usuário

Este arquivo testa:
- Criação automática de perfil via signal
- Atualização de dados pessoais
- Gerenciamento de preferências de categoria
- View de perfil
"""

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from acoes.models import Perfil, Acao
from .test_base import FullFixturesMixin


# ============================================
# SPRINT 2 - Perfil de Usuário
# ============================================


class TestPerfilSignal(TestCase):
    """
    CT-PR001: Testes de criação automática de perfil
    Referência: Documento de Casos de Teste - Perfil
    """

    def test_perfil_criado_automaticamente_ao_criar_usuario(self):
        """
        CT-PR001.1: Perfil é criado automaticamente via signal
        Resultado Esperado: Perfil existe após criar usuário
        """
        user = User.objects.create_user('novo_user', 'email@test.com', 'pass123')

        # Verifica que perfil foi criado automaticamente
        self.assertTrue(hasattr(user, 'perfil'))
        self.assertTrue(Perfil.objects.filter(user=user).exists())

    def test_perfil_criado_com_valores_padrao(self):
        """
        CT-PR001.2: Perfil criado tem valores padrão vazios
        Resultado Esperado: Endereco e preferencias são None/vazias
        """
        user = User.objects.create_user('user2', 'email2@test.com', 'pass123')

        perfil = user.perfil
        self.assertTrue(perfil.endereco is None or perfil.endereco == '')
        self.assertTrue(perfil.preferencias is None or perfil.preferencias == '')

    def test_perfil_relationship_one_to_one(self):
        """
        CT-PR001.3: Relacionamento OneToOne funciona corretamente
        Resultado Esperado: user.perfil retorna o perfil correto
        """
        user = User.objects.create_user('user3', 'email3@test.com', 'pass123')

        perfil = user.perfil
        self.assertEqual(perfil.user, user)
        self.assertIsInstance(perfil, Perfil)

    def test_deletar_usuario_deleta_perfil(self):
        """
        CT-PR002: Deletar usuário deleta perfil (CASCADE)
        Resultado Esperado: Perfil é removido ao deletar usuário
        """
        user = User.objects.create_user('user4', 'email4@test.com', 'pass123')
        perfil_id = user.perfil.id

        # Deleta usuário
        user.delete()

        # Verifica que perfil também foi deletado
        self.assertFalse(Perfil.objects.filter(id=perfil_id).exists())


class TestPerfilModel(FullFixturesMixin, TestCase):
    """
    CT-PR010: Testes do modelo Perfil
    """

    def test_perfil_str_retorna_username(self):
        """
        CT-PR010.1: __str__ retorna "Perfil de {username}"
        Resultado Esperado: String formatada corretamente
        """
        perfil = self.voluntario_user.perfil
        expected = f"Perfil de {self.voluntario_user.username}"
        self.assertEqual(str(perfil), expected)

    def test_perfil_pode_armazenar_endereco(self):
        """
        CT-PR010.2: Perfil pode armazenar endereço
        Resultado Esperado: Endereço salvo corretamente
        """
        perfil = self.voluntario_user.perfil
        perfil.endereco = "Rua ABC, 123 - Bairro - Cidade/UF"
        perfil.save()

        perfil.refresh_from_db()
        self.assertEqual(perfil.endereco, "Rua ABC, 123 - Bairro - Cidade/UF")

    def test_perfil_pode_armazenar_preferencias(self):
        """
        CT-PR010.3: Perfil pode armazenar preferências como string CSV
        Resultado Esperado: Preferências salvas como "SAUDE,EDUCACAO"
        """
        perfil = self.voluntario_user.perfil
        perfil.preferencias = "SAUDE,EDUCACAO,MEIO_AMBIENTE"
        perfil.save()

        perfil.refresh_from_db()
        self.assertEqual(perfil.preferencias, "SAUDE,EDUCACAO,MEIO_AMBIENTE")

    def test_get_preferencias_list_retorna_lista(self):
        """
        CT-PR011: get_preferencias_list() retorna lista de categorias
        Resultado Esperado: Lista ['SAUDE', 'EDUCACAO']
        """
        perfil = self.voluntario_user.perfil
        perfil.preferencias = "SAUDE,EDUCACAO"
        perfil.save()

        lista = perfil.get_preferencias_list()
        self.assertEqual(lista, ['SAUDE', 'EDUCACAO'])

    def test_get_preferencias_list_vazio_retorna_lista_vazia(self):
        """
        CT-PR011.2: get_preferencias_list() retorna [] se vazio
        Resultado Esperado: Lista vazia
        """
        perfil = self.voluntario_user.perfil
        perfil.preferencias = None
        perfil.save()

        lista = perfil.get_preferencias_list()
        self.assertEqual(lista, [])


class TestPerfilView(FullFixturesMixin, TestCase):
    """
    CT-PR020: Testes da view de perfil
    """

    def test_perfil_view_requer_login(self):
        """
        CT-PR020.1: View de perfil requer autenticação
        Resultado Esperado: Redirect para login
        """
        url = reverse('acoes:perfil')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_perfil_view_acessivel_quando_logado(self):
        """
        CT-PR020.2: Usuário logado acessa página de perfil
        Resultado Esperado: Status 200 com formulários no contexto
        """
        url = reverse('acoes:perfil')
        response = self.client_logged_voluntario.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertIn('u_form', response.context)  # Formulário de User
        self.assertIn('p_form', response.context)  # Formulário de Perfil

    def test_perfil_view_formularios_preenchidos_com_dados_atuais(self):
        """
        CT-PR020.3: Formulários vêm preenchidos com dados atuais
        Resultado Esperado: Initial values corretos
        """
        # Define dados no perfil
        self.voluntario_user.first_name = 'João'
        self.voluntario_user.last_name = 'Silva'
        self.voluntario_user.email = 'joao@test.com'
        self.voluntario_user.save()

        self.voluntario_user.perfil.endereco = 'Rua ABC, 123'
        self.voluntario_user.perfil.save()

        url = reverse('acoes:perfil')
        response = self.client_logged_voluntario.get(url)

        # Verifica valores iniciais
        u_form = response.context['u_form']
        self.assertEqual(u_form.initial['first_name'], 'João')
        self.assertEqual(u_form.initial['last_name'], 'Silva')
        self.assertEqual(u_form.initial['email'], 'joao@test.com')

        p_form = response.context['p_form']
        self.assertEqual(p_form.initial['endereco'], 'Rua ABC, 123')

    def test_perfil_atualizar_dados_user_com_sucesso(self):
        """
        CT-PR021: Atualizar first_name, last_name e email
        Resultado Esperado: Dados atualizados no banco
        """
        url = reverse('acoes:perfil')
        data = {
            'first_name': 'Maria',
            'last_name': 'Santos',
            'email': 'maria@test.com',
            'endereco': '',
        }

        response = self.client_logged_voluntario.post(url, data)

        # Verifica redirect
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('acoes:perfil'))

        # Verifica que dados foram atualizados
        self.voluntario_user.refresh_from_db()
        self.assertEqual(self.voluntario_user.first_name, 'Maria')
        self.assertEqual(self.voluntario_user.last_name, 'Santos')
        self.assertEqual(self.voluntario_user.email, 'maria@test.com')

    def test_perfil_atualizar_endereco_com_sucesso(self):
        """
        CT-PR022: Atualizar endereço
        Resultado Esperado: Endereço atualizado no perfil
        """
        url = reverse('acoes:perfil')
        data = {
            'first_name': self.voluntario_user.first_name or '',
            'last_name': self.voluntario_user.last_name or '',
            'email': self.voluntario_user.email,
            'endereco': 'Nova Rua, 456',
        }

        response = self.client_logged_voluntario.post(url, data)

        # Verifica que endereço foi atualizado
        self.voluntario_user.perfil.refresh_from_db()
        self.assertEqual(self.voluntario_user.perfil.endereco, 'Nova Rua, 456')

    def test_perfil_atualizar_preferencias_multiplas(self):
        """
        CT-PR023: Atualizar preferências múltiplas (checkboxes)
        Resultado Esperado: Preferências salvas como CSV
        """
        url = reverse('acoes:perfil')
        data = {
            'first_name': '',
            'last_name': '',
            'email': self.voluntario_user.email,
            'endereco': '',
            'preferencias': ['SAUDE', 'EDUCACAO', 'ANIMAIS']  # Lista de selecionados
        }

        response = self.client_logged_voluntario.post(url, data)

        # Verifica que preferências foram salvas como CSV
        self.voluntario_user.perfil.refresh_from_db()
        self.assertEqual(self.voluntario_user.perfil.preferencias, 'SAUDE,EDUCACAO,ANIMAIS')

    def test_perfil_atualizar_sem_preferencias(self):
        """
        CT-PR024: Atualizar sem selecionar preferências
        Resultado Esperado: Preferências ficam vazias
        """
        url = reverse('acoes:perfil')
        data = {
            'first_name': '',
            'last_name': '',
            'email': self.voluntario_user.email,
            'endereco': '',
            'preferencias': []  # Nenhuma selecionada
        }

        response = self.client_logged_voluntario.post(url, data)

        # Verifica que preferências ficaram vazias
        self.voluntario_user.perfil.refresh_from_db()
        self.assertEqual(self.voluntario_user.perfil.preferencias, '')

    def test_perfil_atualizar_apenas_alguns_campos(self):
        """
        CT-PR025: Atualizar apenas alguns campos mantém outros intactos
        Resultado Esperado: Apenas campos enviados são alterados
        """
        # Define valores iniciais
        self.voluntario_user.first_name = 'Nome Original'
        self.voluntario_user.save()
        self.voluntario_user.perfil.endereco = 'Endereco Original'
        self.voluntario_user.perfil.save()

        url = reverse('acoes:perfil')
        data = {
            'first_name': 'Nome Atualizado',  # Muda isso
            'last_name': '',
            'email': self.voluntario_user.email,
            'endereco': 'Endereco Original',  # Mantém
        }

        response = self.client_logged_voluntario.post(url, data)

        self.voluntario_user.refresh_from_db()
        self.assertEqual(self.voluntario_user.first_name, 'Nome Atualizado')
        self.assertEqual(self.voluntario_user.perfil.endereco, 'Endereco Original')

    def test_perfil_formulario_invalido_nao_salva(self):
        """
        CT-PR026: Formulário inválido não salva dados
        Resultado Esperado: Erro e dados não alterados
        """
        email_original = self.voluntario_user.email

        url = reverse('acoes:perfil')
        data = {
            'first_name': '',
            'last_name': '',
            'email': 'email_invalido',  # Email inválido
            'endereco': '',
        }

        response = self.client_logged_voluntario.post(url, data)

        # Deve permanecer na página com erro
        self.assertEqual(response.status_code, 200)

        # Email não deve ter mudado
        self.voluntario_user.refresh_from_db()
        self.assertEqual(self.voluntario_user.email, email_original)

    def test_perfil_organizador_tambem_pode_atualizar(self):
        """
        CT-PR027: Organizador também pode atualizar seu perfil
        Resultado Esperado: Atualização bem-sucedida
        """
        url = reverse('acoes:perfil')
        data = {
            'first_name': 'Organizador Atualizado',
            'last_name': '',
            'email': self.organizador_user.email,
            'endereco': 'Endereco Org',
            'preferencias': ['SAUDE']
        }

        response = self.client_logged_organizador.post(url, data)

        self.assertEqual(response.status_code, 302)
        self.organizador_user.refresh_from_db()
        self.assertEqual(self.organizador_user.first_name, 'Organizador Atualizado')
        self.assertEqual(self.organizador_user.perfil.endereco, 'Endereco Org')
