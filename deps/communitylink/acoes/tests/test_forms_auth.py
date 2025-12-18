"""
Testes de Formulários de Autenticação e Perfil

Este arquivo testa os formulários:
- SignUpForm: Cadastro de usuário
- SignInForm: Login
- UserUpdateForm: Atualização de dados do User
- PerfilUpdateForm: Atualização de perfil com preferências
"""

import pytest
from django.contrib.auth.models import User
from acoes.forms import SignUpForm, SignInForm, UserUpdateForm, PerfilUpdateForm
from acoes.models import Perfil


# ============================================
# SPRINT 2 - Formulários de Autenticação
# ============================================


@pytest.mark.django_db
class TestSignUpForm:
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
        assert form.is_valid()

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
        assert not form.is_valid()
        assert 'tipo_usuario' in form.errors

    def test_signup_form_tipo_usuario_choices_validos(self):
        """
        CT-FA001.3: Apenas VOLUNTARIO e ORGANIZADOR são válidos
        Resultado Esperado: Form aceita ambos
        """
        for tipo in ['VOLUNTARIO', 'ORGANIZADOR']:
            data = {
                'username': f'user_{tipo}',
                'email': f'{tipo}@test.com',
                'tipo_usuario': tipo,
                'password1': 'senha123!',
                'password2': 'senha123!'
            }

            form = SignUpForm(data=data)
            assert form.is_valid(), f"Tipo {tipo} deveria ser válido"

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
        assert not form.is_valid()
        assert 'email' in form.errors

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
        assert not form.is_valid()
        assert 'email' in form.errors

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
        assert not form.is_valid()
        assert 'email' in form.errors
        assert 'já está em uso' in str(form.errors['email'])

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
        assert not form.is_valid()
        assert 'email' in form.errors

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
        assert not form.is_valid()

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
        assert not form.is_valid()

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
        assert form.is_valid()

        user = form.save()

        assert User.objects.filter(username='novo_user').exists()
        assert user.email == 'novo@test.com'
        assert user.check_password('senhaSegura123!')  # Senha foi hasheada

    def test_signup_form_fields_corretos(self):
        """
        CT-FA009: Form possui campos corretos
        Resultado Esperado: username, email, tipo_usuario, password1, password2
        """
        form = SignUpForm()

        assert 'username' in form.fields
        assert 'email' in form.fields
        assert 'tipo_usuario' in form.fields
        assert 'password1' in form.fields
        assert 'password2' in form.fields


@pytest.mark.django_db
class TestSignInForm:
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
        assert form.is_valid()

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
        assert not form.is_valid()

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
        assert not form.is_valid()

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
        assert not form.is_valid()
        assert 'username' in form.errors or '__all__' in form.errors
        assert 'password' in form.errors or '__all__' in form.errors


@pytest.mark.django_db
class TestUserUpdateForm:
    """
    CT-FA020: Testes do formulário de atualização de User
    """

    def test_user_update_form_valido(self, voluntario_user):
        """
        CT-FA020.1: Form válido com dados corretos
        Resultado Esperado: is_valid() == True
        """
        data = {
            'first_name': 'João',
            'last_name': 'Silva',
            'email': 'joao@test.com'
        }

        form = UserUpdateForm(data=data, instance=voluntario_user)
        assert form.is_valid()

    def test_user_update_form_atualiza_dados(self, voluntario_user):
        """
        CT-FA020.2: Form atualiza dados do usuário
        Resultado Esperado: Dados salvos no banco
        """
        data = {
            'first_name': 'Maria',
            'last_name': 'Santos',
            'email': 'maria@test.com'
        }

        form = UserUpdateForm(data=data, instance=voluntario_user)
        assert form.is_valid()

        user = form.save()

        assert user.first_name == 'Maria'
        assert user.last_name == 'Santos'
        assert user.email == 'maria@test.com'

    def test_user_update_form_email_invalido(self, voluntario_user):
        """
        CT-FA021: Email inválido é rejeitado
        Resultado Esperado: Erro de validação
        """
        data = {
            'first_name': 'João',
            'last_name': 'Silva',
            'email': 'email_invalido'  # Sem @
        }

        form = UserUpdateForm(data=data, instance=voluntario_user)
        assert not form.is_valid()
        assert 'email' in form.errors

    def test_user_update_form_campos_opcionais(self, voluntario_user):
        """
        CT-FA022: first_name e last_name são opcionais
        Resultado Esperado: Form válido sem esses campos
        """
        data = {
            'first_name': '',
            'last_name': '',
            'email': voluntario_user.email
        }

        form = UserUpdateForm(data=data, instance=voluntario_user)
        assert form.is_valid()

    def test_user_update_form_fields_corretos(self):
        """
        CT-FA023: Form possui apenas campos esperados
        Resultado Esperado: first_name, last_name, email
        """
        form = UserUpdateForm()

        assert 'first_name' in form.fields
        assert 'last_name' in form.fields
        assert 'email' in form.fields
        assert 'username' not in form.fields  # Não deve permitir mudar username
        assert 'password' not in form.fields


@pytest.mark.django_db
class TestPerfilUpdateForm:
    """
    CT-FA030: Testes do formulário de atualização de Perfil
    """

    def test_perfil_update_form_valido(self, voluntario_user):
        """
        CT-FA030.1: Form válido com dados corretos
        Resultado Esperado: is_valid() == True
        """
        data = {
            'endereco': 'Rua ABC, 123',
            'preferencias': ['SAUDE', 'EDUCACAO']
        }

        form = PerfilUpdateForm(data=data, instance=voluntario_user.perfil)
        assert form.is_valid()

    def test_perfil_update_form_converte_preferencias_para_csv(self, voluntario_user):
        """
        CT-FA030.2: Form converte lista de preferências em CSV
        Resultado Esperado: ['SAUDE', 'EDUCACAO'] → 'SAUDE,EDUCACAO'
        """
        data = {
            'endereco': 'Rua ABC, 123',
            'preferencias': ['SAUDE', 'EDUCACAO', 'ANIMAIS']
        }

        form = PerfilUpdateForm(data=data, instance=voluntario_user.perfil)
        assert form.is_valid()

        # Verifica que clean_preferencias converteu para CSV
        assert form.cleaned_data['preferencias'] == 'SAUDE,EDUCACAO,ANIMAIS'

    def test_perfil_update_form_salva_preferencias_corretamente(self, voluntario_user):
        """
        CT-FA031: Form salva preferências no banco como CSV
        Resultado Esperado: Perfil.preferencias == 'SAUDE,EDUCACAO'
        """
        data = {
            'endereco': 'Rua XYZ',
            'preferencias': ['SAUDE', 'MEIO_AMBIENTE']
        }

        form = PerfilUpdateForm(data=data, instance=voluntario_user.perfil)
        assert form.is_valid()

        perfil = form.save()

        assert perfil.preferencias == 'SAUDE,MEIO_AMBIENTE'

    def test_perfil_update_form_carrega_preferencias_existentes(self, voluntario_user):
        """
        CT-FA032: Form carrega preferências existentes como lista
        Resultado Esperado: 'SAUDE,EDUCACAO' → ['SAUDE', 'EDUCACAO'] no initial
        """
        # Define preferências no perfil
        voluntario_user.perfil.preferencias = 'SAUDE,EDUCACAO'
        voluntario_user.perfil.save()

        form = PerfilUpdateForm(instance=voluntario_user.perfil)

        # Verifica que preferências foram carregadas como lista
        assert form.initial['preferencias'] == ['SAUDE', 'EDUCACAO']

    def test_perfil_update_form_preferencias_vazias(self, voluntario_user):
        """
        CT-FA033: Form aceita preferências vazias
        Resultado Esperado: Lista vazia → string vazia
        """
        data = {
            'endereco': 'Rua ABC',
            'preferencias': []  # Nenhuma selecionada
        }

        form = PerfilUpdateForm(data=data, instance=voluntario_user.perfil)
        assert form.is_valid()
        assert form.cleaned_data['preferencias'] == ''

    def test_perfil_update_form_categorias_validas(self, voluntario_user):
        """
        CT-FA034: Form aceita todas categorias definidas em CATEGORIA_CHOICES
        Resultado Esperado: Todas as 5 categorias são válidas
        """
        categorias = ['SAUDE', 'EDUCACAO', 'MEIO_AMBIENTE', 'ANIMAIS', 'OUTRO']

        data = {
            'endereco': 'Rua ABC',
            'preferencias': categorias
        }

        form = PerfilUpdateForm(data=data, instance=voluntario_user.perfil)
        assert form.is_valid()

    def test_perfil_update_form_categoria_invalida(self, voluntario_user):
        """
        CT-FA035: Form rejeita categoria não definida
        Resultado Esperado: Erro de validação
        """
        data = {
            'endereco': 'Rua ABC',
            'preferencias': ['CATEGORIA_INVALIDA']
        }

        form = PerfilUpdateForm(data=data, instance=voluntario_user.perfil)
        assert not form.is_valid()
        assert 'preferencias' in form.errors

    def test_perfil_update_form_campos_corretos(self):
        """
        CT-FA036: Form possui campos corretos
        Resultado Esperado: endereco, preferencias
        """
        form = PerfilUpdateForm()

        assert 'endereco' in form.fields
        assert 'preferencias' in form.fields

    def test_perfil_update_form_campos_opcionais(self, voluntario_user):
        """
        CT-FA037: Todos os campos são opcionais
        Resultado Esperado: Form válido com campos vazios
        """
        data = {
            'endereco': '',
            'preferencias': []
        }

        form = PerfilUpdateForm(data=data, instance=voluntario_user.perfil)
        assert form.is_valid()

    def test_perfil_update_form_widget_checkbox(self):
        """
        CT-FA038: Preferências usam CheckboxSelectMultiple
        Resultado Esperado: Widget correto configurado
        """
        form = PerfilUpdateForm()

        from django import forms
        assert isinstance(form.fields['preferencias'].widget, forms.CheckboxSelectMultiple)
