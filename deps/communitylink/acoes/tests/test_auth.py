"""
Testes de Autenticação

Este arquivo testa o sistema de autenticação:
- Cadastro de usuários (signup)
- Login (signin)
- Logout
- Atribuição de grupos (Organizadores/Voluntários)
"""

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User, Group
from .test_base import FullFixturesMixin


# ============================================
# SPRINT 2 - Autenticação
# ============================================


class TestSignupView(FullFixturesMixin, TestCase):
    """
    CT-A001: Testes de cadastro de usuário
    Referência: Documento de Casos de Teste - Autenticação
    """

    def test_signup_page_acessivel(self):
        """
        CT-A001.1: Página de signup acessível sem login
        Resultado Esperado: Status 200
        """
        url = reverse('acoes:signup')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_signup_cria_voluntario_com_grupo_correto(self):
        """
        CT-A001.2: Signup cria voluntário e adiciona ao grupo Voluntarios
        Resultado Esperado: Usuário criado e grupo atribuído
        """
        url = reverse('acoes:signup')
        data = {
            'username': 'novo_voluntario',
            'email': 'voluntario@test.com',
            'tipo_usuario': 'VOLUNTARIO',
            'password1': 'senhaSegura123!',
            'password2': 'senhaSegura123!'
        }

        response = self.client.post(url, data)

        # Verifica que usuário foi criado
        self.assertTrue(User.objects.filter(username='novo_voluntario').exists())
        user = User.objects.get(username='novo_voluntario')

        # Verifica que está no grupo Voluntarios
        self.assertTrue(user.groups.filter(name='Voluntarios').exists())

        # Verifica que foi logado automaticamente
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('acoes:acao_list'))

    def test_signup_cria_organizador_com_grupo_correto(self):
        """
        CT-A001.3: Signup cria organizador e adiciona ao grupo Organizadores
        Resultado Esperado: Usuário criado e grupo atribuído
        """
        url = reverse('acoes:signup')
        data = {
            'username': 'novo_organizador',
            'email': 'organizador@test.com',
            'tipo_usuario': 'ORGANIZADOR',
            'password1': 'senhaSegura123!',
            'password2': 'senhaSegura123!'
        }

        response = self.client.post(url, data)

        # Verifica que usuário foi criado
        self.assertTrue(User.objects.filter(username='novo_organizador').exists())
        user = User.objects.get(username='novo_organizador')

        # Verifica que está no grupo Organizadores
        self.assertTrue(user.groups.filter(name='Organizadores').exists())

        # Verifica redirect para minhas_acoes
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('acoes:minhas_acoes'))

    def test_signup_cria_grupo_se_nao_existir(self):
        """
        CT-A002: Signup cria grupos automaticamente se não existirem
        Resultado Esperado: Grupos criados com get_or_create
        """
        # Garante que grupos não existem
        Group.objects.filter(name__in=['Organizadores', 'Voluntarios']).delete()

        url = reverse('acoes:signup')
        data = {
            'username': 'usuario_teste',
            'email': 'teste@test.com',
            'tipo_usuario': 'VOLUNTARIO',
            'password1': 'senhaSegura123!',
            'password2': 'senhaSegura123!'
        }

        response = self.client.post(url, data)

        # Verifica que grupo foi criado
        self.assertTrue(Group.objects.filter(name='Voluntarios').exists())

    def test_signup_email_duplicado_falha(self):
        """
        CT-A003: Signup com email duplicado deve falhar
        Resultado Esperado: Erro de validação
        """
        # Cria usuário com email
        User.objects.create_user('user1', 'email@test.com', 'pass123')

        url = reverse('acoes:signup')
        data = {
            'username': 'user2',
            'email': 'email@test.com',  # Email duplicado
            'tipo_usuario': 'VOLUNTARIO',
            'password1': 'senhaSegura123!',
            'password2': 'senhaSegura123!'
        }

        response = self.client.post(url, data)

        # Não deve criar segundo usuário
        self.assertEqual(User.objects.filter(username='user2').count(), 0)
        # Deve mostrar erro no formulário
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)

    def test_signup_username_duplicado_falha(self):
        """
        CT-A004: Signup com username duplicado deve falhar
        Resultado Esperado: Erro de validação
        """
        # Cria usuário
        User.objects.create_user('usuario_existente', 'email1@test.com', 'pass123')

        url = reverse('acoes:signup')
        data = {
            'username': 'usuario_existente',  # Username duplicado
            'email': 'email2@test.com',
            'tipo_usuario': 'VOLUNTARIO',
            'password1': 'senhaSegura123!',
            'password2': 'senhaSegura123!'
        }

        response = self.client.post(url, data)

        # Deve ter apenas 1 usuário com esse username
        self.assertEqual(User.objects.filter(username='usuario_existente').count(), 1)

    def test_signup_senhas_diferentes_falha(self):
        """
        CT-A005: Signup com senhas diferentes deve falhar
        Resultado Esperado: Erro de validação
        """
        url = reverse('acoes:signup')
        data = {
            'username': 'novo_user',
            'email': 'novo@test.com',
            'tipo_usuario': 'VOLUNTARIO',
            'password1': 'senhaSegura123!',
            'password2': 'senhaSegura456!'  # Senha diferente
        }

        response = self.client.post(url, data)

        # Não deve criar usuário
        self.assertFalse(User.objects.filter(username='novo_user').exists())

    def test_signup_campos_obrigatorios(self):
        """
        CT-A006: Signup requer todos os campos obrigatórios
        Resultado Esperado: Erro se campos faltando
        """
        url = reverse('acoes:signup')
        data = {
            'username': 'user',
            # Falta email, tipo_usuario e senhas
        }

        response = self.client.post(url, data)

        # Não deve criar usuário
        self.assertFalse(User.objects.filter(username='user').exists())
        self.assertEqual(response.status_code, 200)


class TestSigninView(FullFixturesMixin, TestCase):
    """
    CT-A010: Testes de login
    """

    def test_signin_page_acessivel(self):
        """
        CT-A010.1: Página de login acessível sem autenticação
        Resultado Esperado: Status 200
        """
        url = reverse('acoes:signin')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_signin_com_credenciais_validas(self):
        """
        CT-A010.2: Login com credenciais válidas autentica usuário
        Resultado Esperado: Usuário logado e redirecionado
        """
        # Cria usuário
        user = User.objects.create_user('testuser', 'test@test.com', 'password123')

        url = reverse('acoes:signin')
        data = {
            'username': 'testuser',
            'password': 'password123'
        }

        response = self.client.post(url, data)

        # Verifica redirect
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('acoes:acao_list'))

        # Verifica que está autenticado
        # (força uma request para verificar session)
        response2 = self.client.get(reverse('acoes:acao_list'))
        self.assertTrue(response2.wsgi_request.user.is_authenticated)
        self.assertEqual(response2.wsgi_request.user.username, 'testuser')

    def test_signin_com_credenciais_invalidas(self):
        """
        CT-A011: Login com credenciais inválidas falha
        Resultado Esperado: Permanece na página de login com erro
        """
        # Cria usuário
        User.objects.create_user('testuser', 'test@test.com', 'password123')

        url = reverse('acoes:signin')
        data = {
            'username': 'testuser',
            'password': 'senhaErrada'
        }

        response = self.client.post(url, data)

        # Deve permanecer na página de login
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)

        # Não deve estar autenticado
        response2 = self.client.get(reverse('acoes:acao_list'))
        self.assertFalse(response2.wsgi_request.user.is_authenticated)

    def test_signin_redirect_para_next_url(self):
        """
        CT-A012: Login redireciona para URL 'next' se fornecida
        Resultado Esperado: Redirect para URL especificada
        """
        # Cria usuário
        User.objects.create_user('testuser', 'test@test.com', 'password123')

        # URL de destino
        next_url = reverse('acoes:minhas_inscricoes')
        url = reverse('acoes:signin') + f'?next={next_url}'

        data = {
            'username': 'testuser',
            'password': 'password123',
            'next': next_url
        }

        response = self.client.post(url, data)

        # Verifica redirect para next
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, next_url)

    def test_signin_next_url_invalida_redireciona_para_lista(self):
        """
        CT-A013: Login com URL 'next' inválida redireciona para lista
        Resultado Esperado: Redirect seguro para acao_list
        """
        # Cria usuário
        User.objects.create_user('testuser', 'test@test.com', 'password123')

        url = reverse('acoes:signin')
        data = {
            'username': 'testuser',
            'password': 'password123',
            'next': 'https://site-malicioso.com/phishing'  # URL externa
        }

        response = self.client.post(url, data)

        # Deve redirecionar para lista (URL segura)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('acoes:acao_list'))

    def test_signin_usuario_nao_existente(self):
        """
        CT-A014: Login com usuário inexistente falha
        Resultado Esperado: Erro de autenticação
        """
        url = reverse('acoes:signin')
        data = {
            'username': 'usuario_inexistente',
            'password': 'qualquersenha'
        }

        response = self.client.post(url, data)

        # Deve permanecer na página de login
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(self.client.session.get('_auth_user_id'))


class TestLogoutView(FullFixturesMixin, TestCase):
    """
    CT-A020: Testes de logout
    """

    def test_logout_requer_post(self):
        """
        CT-A020.1: Logout requer método POST (segurança CSRF)
        Resultado Esperado: GET retorna erro 405
        """
        url = reverse('acoes:logout')
        response = self.client_logged_voluntario.get(url)

        # Deve retornar método não permitido
        self.assertEqual(response.status_code, 405)

    def test_logout_desloga_usuario(self):
        """
        CT-A020.2: Logout remove autenticação do usuário
        Resultado Esperado: Usuário não está mais autenticado
        """
        # Verifica que está logado
        response = self.client_logged_voluntario.get(reverse('acoes:acao_list'))
        self.assertTrue(response.wsgi_request.user.is_authenticated)

        # Faz logout
        url = reverse('acoes:logout')
        response = self.client_logged_voluntario.post(url)

        # Verifica redirect
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('acoes:signin'))

        # Verifica que não está mais autenticado
        response2 = self.client_logged_voluntario.get(reverse('acoes:acao_list'))
        self.assertFalse(response2.wsgi_request.user.is_authenticated)

    def test_logout_redireciona_para_signin(self):
        """
        CT-A020.3: Logout redireciona para página de login
        Resultado Esperado: Redirect para signin
        """
        url = reverse('acoes:logout')
        response = self.client_logged_organizador.post(url)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('acoes:signin'))

    def test_logout_usuario_nao_autenticado(self):
        """
        CT-A020.4: Logout funciona mesmo se usuário não está autenticado
        Resultado Esperado: Redirect sem erro
        """
        url = reverse('acoes:logout')
        response = self.client.post(url)

        # Deve redirecionar normalmente
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('acoes:signin'))


# ============================================
# SPRINT 2 - Placeholder para novos recursos
# ============================================

# Quando implementar recuperação de senha:
# class TestPasswordResetView(FullFixturesMixin, TestCase):
#     """CT-A030: Testes de recuperação de senha - Sprint 2"""
#     pass
