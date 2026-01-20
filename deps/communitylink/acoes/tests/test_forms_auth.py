"""
Testes de Formulários de Autenticação e Perfil

Este arquivo testa os formulários:
- SignUpForm: Cadastro de usuário
- SignInForm: Login
- UserUpdateForm: Atualização de dados do User
- PerfilUpdateForm: Atualização de perfil com preferências
"""

from django.test import TestCase
from django.contrib.auth.models import User
from acoes.forms import SignUpForm, SignInForm, UserUpdateForm, PerfilUpdateForm
from acoes.models import Perfil
from .test_base import FullFixturesMixin


# ============================================
# SPRINT 2 - Formulários de Autenticação
# ============================================


class TestSignUpForm(TestCase):
    """
    CT-FA001: Testes do formulário de cadastro
    Referência: Documento de Casos de Teste - Formulários
    """

    def test_signup_form_valido_com_dados_completos(self):
        """
        CT-FA001.1: Form válido com todos os campos preenchidos
        Resultado Esperado: is_valid() == True
        """
        data = {
            'username': 'novo_usuario',
            'email': 'novo@test.com',
            'tipo_usuario': 'VOLUNTARIO',
            'password1': 'senhaSegura123!',
            'password2': 'senhaSegura123!'
        }

        form = SignUpForm(data=data)
        self.assertTrue(form.is_valid())

    def test_signup_form_campo_tipo_usuario_obrigatorio(self):
        """
        CT-FA001.2: Campo tipo_usuario é obrigatório
        Resultado Esperado: Erro se não fornecido
        """
        data = {
            'username': 'usuario',
            'email': 'email@test.com',
            # Falta tipo_usuario
            'password1': 'senha123',
            'password2': 'senha123'
        }

        form = SignUpForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('tipo_usuario', form.errors)

    def test_signup_form_tipo_usuario_choices_validos(self):
        """
        CT-FA001.3: Apenas VOLUNTARIO e ORGANIZADOR são válidos
        Resultado Esperado: Form aceita ambos
        """
        for tipo in ['VOLUNTARIO', 'ORGANIZADOR']:
            with self.subTest(tipo=tipo):
                data = {
                    'username': f'user_{tipo}',
                    'email': f'{tipo}@test.com',
                    'tipo_usuario': tipo,
                    'password1': 'senha123!',
                    'password2': 'senha123!'
                }

                form = SignUpForm(data=data)
                self.assertTrue(form.is_valid(), f"Tipo {tipo} deveria ser válido")

    def test_signup_form_email_obrigatorio(self):
        """
        CT-FA002: Email é obrigatório
        Resultado Esperado: Erro se não fornecido
        """
        data = {
            'username': 'usuario',
            'tipo_usuario': 'VOLUNTARIO',
            'password1': 'senha123',
            'password2': 'senha123'
        }

        form = SignUpForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_signup_form_email_invalido(self):
        """
        CT-FA003: Email inválido é rejeitado
        Resultado Esperado: Erro de validação
        """
        data = {
            'username': 'usuario',
            'email': 'email_invalido',  # Sem @
            'tipo_usuario': 'VOLUNTARIO',
            'password1': 'senha123',
            'password2': 'senha123'
        }

        form = SignUpForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_signup_form_email_duplicado(self):
        """
        CT-FA004: Email duplicado é rejeitado (clean_email)
        Resultado Esperado: Erro customizado
        """
        # Cria usuário com email
        User.objects.create_user('user1', 'existente@test.com', 'pass123')

        data = {
            'username': 'user2',
            'email': 'existente@test.com',  # Email já existe
            'tipo_usuario': 'VOLUNTARIO',
            'password1': 'senha123!',
            'password2': 'senha123!'
        }

        form = SignUpForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        self.assertIn('já está em uso', str(form.errors['email']))

    def test_signup_form_email_case_insensitive(self):
        """
        CT-FA005: Validação de email é case-insensitive
        Resultado Esperado: EMAIL@TEST.COM == email@test.com
        """
        # Cria usuário com email minúsculo
        User.objects.create_user('user1', 'email@test.com', 'pass123')

        data = {
            'username': 'user2',
            'email': 'EMAIL@TEST.COM',  # Maiúsculo mas é o mesmo
            'tipo_usuario': 'VOLUNTARIO',
            'password1': 'senha123!',
            'password2': 'senha123!'
        }

        form = SignUpForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_signup_form_senhas_diferentes(self):
        """
        CT-FA006: Senhas diferentes não validam
        Resultado Esperado: Erro de senha
        """
        data = {
            'username': 'usuario',
            'email': 'email@test.com',
            'tipo_usuario': 'VOLUNTARIO',
            'password1': 'senha123!',
            'password2': 'senha456!'  # Diferente
        }

        form = SignUpForm(data=data)
        self.assertFalse(form.is_valid())

    def test_signup_form_senha_muito_curta(self):
        """
        CT-FA007: Senha muito curta é rejeitada
        Resultado Esperado: Erro de validação
        """
        data = {
            'username': 'usuario',
            'email': 'email@test.com',
            'tipo_usuario': 'VOLUNTARIO',
            'password1': '123',  # Muito curta
            'password2': '123'
        }

        form = SignUpForm(data=data)
        self.assertFalse(form.is_valid())

    def test_signup_form_salva_usuario_corretamente(self):
        """
        CT-FA008: Form salva usuário no banco
        Resultado Esperado: User criado com dados corretos
        """
        data = {
            'username': 'novo_user',
            'email': 'novo@test.com',
            'tipo_usuario': 'VOLUNTARIO',
            'password1': 'senhaSegura123!',
            'password2': 'senhaSegura123!'
        }

        form = SignUpForm(data=data)
        self.assertTrue(form.is_valid())

        user = form.save()

        self.assertTrue(User.objects.filter(username='novo_user').exists())
        self.assertEqual(user.email, 'novo@test.com')
        self.assertTrue(user.check_password('senhaSegura123!'))  # Senha foi hasheada

    def test_signup_form_fields_corretos(self):
        """
        CT-FA009: Form possui campos corretos
        Resultado Esperado: username, email, tipo_usuario, password1, password2
        """
        form = SignUpForm()

        self.assertIn('username', form.fields)
        self.assertIn('email', form.fields)
        self.assertIn('tipo_usuario', form.fields)
        self.assertIn('password1', form.fields)
        self.assertIn('password2', form.fields)


class TestSignInForm(TestCase):
    """
    CT-FA010: Testes do formulário de login
    """

    def test_signin_form_valido_com_credenciais_corretas(self):
        """
        CT-FA010.1: Form válido com username e senha corretos
        Resultado Esperado: is_valid() == True
        """
        # Cria usuário
        User.objects.create_user('testuser', 'test@test.com', 'password123')

        # Simula request (necessário para AuthenticationForm)
        from django.test import RequestFactory
        factory = RequestFactory()
        request = factory.post('/login/')

        data = {
            'username': 'testuser',
            'password': 'password123'
        }

        form = SignInForm(request=request, data=data)
        self.assertTrue(form.is_valid())

    def test_signin_form_invalido_com_senha_errada(self):
        """
        CT-FA010.2: Form inválido com senha incorreta
        Resultado Esperado: is_valid() == False
        """
        User.objects.create_user('testuser', 'test@test.com', 'password123')

        from django.test import RequestFactory
        factory = RequestFactory()
        request = factory.post('/login/')

        data = {
            'username': 'testuser',
            'password': 'senhaErrada'
        }

        form = SignInForm(request=request, data=data)
        self.assertFalse(form.is_valid())

    def test_signin_form_invalido_com_usuario_inexistente(self):
        """
        CT-FA011: Form inválido com usuário que não existe
        Resultado Esperado: is_valid() == False
        """
        from django.test import RequestFactory
        factory = RequestFactory()
        request = factory.post('/login/')

        data = {
            'username': 'usuario_inexistente',
            'password': 'qualquersenha'
        }

        form = SignInForm(request=request, data=data)
        self.assertFalse(form.is_valid())

    def test_signin_form_campos_obrigatorios(self):
        """
        CT-FA012: Username e password são obrigatórios
        Resultado Esperado: Erro se campos vazios
        """
        from django.test import RequestFactory
        factory = RequestFactory()
        request = factory.post('/login/')

        data = {
            'username': '',
            'password': ''
        }

        form = SignInForm(request=request, data=data)
        self.assertFalse(form.is_valid())
        self.assertTrue('username' in form.errors or '__all__' in form.errors)
        self.assertTrue('password' in form.errors or '__all__' in form.errors)


class TestUserUpdateForm(FullFixturesMixin, TestCase):
    """
    CT-FA020: Testes do formulário de atualização de User
    """

    def test_user_update_form_valido(self):
        """
        CT-FA020.1: Form válido com dados corretos
        Resultado Esperado: is_valid() == True
        """
        data = {
            'first_name': 'João',
            'last_name': 'Silva',
            'email': 'joao@test.com'
        }

        form = UserUpdateForm(data=data, instance=self.voluntario_user)
        self.assertTrue(form.is_valid())

    def test_user_update_form_atualiza_dados(self):
        """
        CT-FA020.2: Form atualiza dados do usuário
        Resultado Esperado: Dados salvos no banco
        """
        data = {
            'first_name': 'Maria',
            'last_name': 'Santos',
            'email': 'maria@test.com'
        }

        form = UserUpdateForm(data=data, instance=self.voluntario_user)
        self.assertTrue(form.is_valid())

        user = form.save()

        self.assertEqual(user.first_name, 'Maria')
        self.assertEqual(user.last_name, 'Santos')
        self.assertEqual(user.email, 'maria@test.com')

    def test_user_update_form_email_invalido(self):
        """
        CT-FA021: Email inválido é rejeitado
        Resultado Esperado: Erro de validação
        """
        data = {
            'first_name': 'João',
            'last_name': 'Silva',
            'email': 'email_invalido'  # Sem @
        }

        form = UserUpdateForm(data=data, instance=self.voluntario_user)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_user_update_form_campos_opcionais(self):
        """
        CT-FA022: first_name e last_name são opcionais
        Resultado Esperado: Form válido sem esses campos
        """
        data = {
            'first_name': '',
            'last_name': '',
            'email': self.voluntario_user.email
        }

        form = UserUpdateForm(data=data, instance=self.voluntario_user)
        self.assertTrue(form.is_valid())

    def test_user_update_form_fields_corretos(self):
        """
        CT-FA023: Form possui apenas campos esperados
        Resultado Esperado: first_name, last_name, email
        """
        form = UserUpdateForm()

        self.assertIn('first_name', form.fields)
        self.assertIn('last_name', form.fields)
        self.assertIn('email', form.fields)
        self.assertNotIn('username', form.fields)  # Não deve permitir mudar username
        self.assertNotIn('password', form.fields)


class TestPerfilUpdateForm(FullFixturesMixin, TestCase):
    """
    CT-FA030: Testes do formulário de atualização de Perfil
    """

    def test_perfil_update_form_valido(self):
        """
        CT-FA030.1: Form válido com dados corretos
        Resultado Esperado: is_valid() == True
        """
        data = {
            'endereco': 'Rua ABC, 123',
            'preferencias': ['SAUDE', 'EDUCACAO']
        }

        form = PerfilUpdateForm(data=data, instance=self.voluntario_user.perfil)
        self.assertTrue(form.is_valid())

    def test_perfil_update_form_converte_preferencias_para_csv(self):
        """
        CT-FA030.2: Form converte lista de preferências em CSV
        Resultado Esperado: ['SAUDE', 'EDUCACAO'] → 'SAUDE,EDUCACAO'
        """
        data = {
            'endereco': 'Rua ABC, 123',
            'preferencias': ['SAUDE', 'EDUCACAO', 'ANIMAIS']
        }

        form = PerfilUpdateForm(data=data, instance=self.voluntario_user.perfil)
        self.assertTrue(form.is_valid())

        # Verifica que clean_preferencias converteu para CSV
        self.assertEqual(form.cleaned_data['preferencias'], 'SAUDE,EDUCACAO,ANIMAIS')

    def test_perfil_update_form_salva_preferencias_corretamente(self):
        """
        CT-FA031: Form salva preferências no banco como CSV
        Resultado Esperado: Perfil.preferencias == 'SAUDE,EDUCACAO'
        """
        data = {
            'endereco': 'Rua XYZ',
            'preferencias': ['SAUDE', 'MEIO_AMBIENTE']
        }

        form = PerfilUpdateForm(data=data, instance=self.voluntario_user.perfil)
        self.assertTrue(form.is_valid())

        perfil = form.save()

        self.assertEqual(perfil.preferencias, 'SAUDE,MEIO_AMBIENTE')

    def test_perfil_update_form_carrega_preferencias_existentes(self):
        """
        CT-FA032: Form carrega preferências existentes como lista
        Resultado Esperado: 'SAUDE,EDUCACAO' → ['SAUDE', 'EDUCACAO'] no initial
        """
        # Define preferências no perfil
        self.voluntario_user.perfil.preferencias = 'SAUDE,EDUCACAO'
        self.voluntario_user.perfil.save()

        form = PerfilUpdateForm(instance=self.voluntario_user.perfil)

        # Verifica que preferências foram carregadas como lista
        self.assertEqual(form.initial['preferencias'], ['SAUDE', 'EDUCACAO'])

    def test_perfil_update_form_preferencias_vazias(self):
        """
        CT-FA033: Form aceita preferências vazias
        Resultado Esperado: Lista vazia → string vazia
        """
        data = {
            'endereco': 'Rua ABC',
            'preferencias': []  # Nenhuma selecionada
        }

        form = PerfilUpdateForm(data=data, instance=self.voluntario_user.perfil)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['preferencias'], '')

    def test_perfil_update_form_categorias_validas(self):
        """
        CT-FA034: Form aceita todas categorias definidas em CATEGORIA_CHOICES
        Resultado Esperado: Todas as 5 categorias são válidas
        """
        categorias = ['SAUDE', 'EDUCACAO', 'MEIO_AMBIENTE', 'ANIMAIS', 'OUTRO']

        data = {
            'endereco': 'Rua ABC',
            'preferencias': categorias
        }

        form = PerfilUpdateForm(data=data, instance=self.voluntario_user.perfil)
        self.assertTrue(form.is_valid())

    def test_perfil_update_form_categoria_invalida(self):
        """
        CT-FA035: Form rejeita categoria não definida
        Resultado Esperado: Erro de validação
        """
        data = {
            'endereco': 'Rua ABC',
            'preferencias': ['CATEGORIA_INVALIDA']
        }

        form = PerfilUpdateForm(data=data, instance=self.voluntario_user.perfil)
        self.assertFalse(form.is_valid())
        self.assertIn('preferencias', form.errors)

    def test_perfil_update_form_campos_corretos(self):
        """
        CT-FA036: Form possui campos corretos
        Resultado Esperado: endereco, preferencias
        """
        form = PerfilUpdateForm()

        self.assertIn('endereco', form.fields)
        self.assertIn('preferencias', form.fields)

    def test_perfil_update_form_campos_opcionais(self):
        """
        CT-FA037: Todos os campos são opcionais
        Resultado Esperado: Form válido com campos vazios
        """
        data = {
            'endereco': '',
            'preferencias': []
        }

        form = PerfilUpdateForm(data=data, instance=self.voluntario_user.perfil)
        self.assertTrue(form.is_valid())

    def test_perfil_update_form_widget_checkbox(self):
        """
        CT-FA038: Preferências usam CheckboxSelectMultiple
        Resultado Esperado: Widget correto configurado
        """
        form = PerfilUpdateForm()

        from django import forms
        self.assertIsInstance(form.fields['preferencias'].widget, forms.CheckboxSelectMultiple)
