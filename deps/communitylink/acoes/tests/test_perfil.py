"""
Testes de Perfil de Usuário

Este arquivo testa:
- Criação automática de perfil via signal
- Atualização de dados pessoais
- Gerenciamento de preferências de categoria
- View de perfil
"""

import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from acoes.models import Perfil, Acao


# ============================================
# SPRINT 2 - Perfil de Usuário
# ============================================


@pytest.mark.django_db
class TestPerfilSignal:
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
        assert hasattr(user, 'perfil')
        assert Perfil.objects.filter(user=user).exists()

    def test_perfil_criado_com_valores_padrao(self):
        """
        CT-PR001.2: Perfil criado tem valores padrão vazios
        Resultado Esperado: Endereco e preferencias são None/vazias
        """
        user = User.objects.create_user('user2', 'email2@test.com', 'pass123')

        perfil = user.perfil
        assert perfil.endereco is None or perfil.endereco == ''
        assert perfil.preferencias is None or perfil.preferencias == ''

    def test_perfil_relationship_one_to_one(self):
        """
        CT-PR001.3: Relacionamento OneToOne funciona corretamente
        Resultado Esperado: user.perfil retorna o perfil correto
        """
        user = User.objects.create_user('user3', 'email3@test.com', 'pass123')

        perfil = user.perfil
        assert perfil.user == user
        assert isinstance(perfil, Perfil)

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
        assert not Perfil.objects.filter(id=perfil_id).exists()


@pytest.mark.django_db
class TestPerfilModel:
    """
    CT-PR010: Testes do modelo Perfil
    """

    def test_perfil_str_retorna_username(self, voluntario_user):
        """
        CT-PR010.1: __str__ retorna "Perfil de {username}"
        Resultado Esperado: String formatada corretamente
        """
        perfil = voluntario_user.perfil
        expected = f"Perfil de {voluntario_user.username}"
        assert str(perfil) == expected

    def test_perfil_pode_armazenar_endereco(self, voluntario_user):
        """
        CT-PR010.2: Perfil pode armazenar endereço
        Resultado Esperado: Endereço salvo corretamente
        """
        perfil = voluntario_user.perfil
        perfil.endereco = "Rua ABC, 123 - Bairro - Cidade/UF"
        perfil.save()

        perfil.refresh_from_db()
        assert perfil.endereco == "Rua ABC, 123 - Bairro - Cidade/UF"

    def test_perfil_pode_armazenar_preferencias(self, voluntario_user):
        """
        CT-PR010.3: Perfil pode armazenar preferências como string CSV
        Resultado Esperado: Preferências salvas como "SAUDE,EDUCACAO"
        """
        perfil = voluntario_user.perfil
        perfil.preferencias = "SAUDE,EDUCACAO,MEIO_AMBIENTE"
        perfil.save()

        perfil.refresh_from_db()
        assert perfil.preferencias == "SAUDE,EDUCACAO,MEIO_AMBIENTE"

    def test_get_preferencias_list_retorna_lista(self, voluntario_user):
        """
        CT-PR011: get_preferencias_list() retorna lista de categorias
        Resultado Esperado: Lista ['SAUDE', 'EDUCACAO']
        """
        perfil = voluntario_user.perfil
        perfil.preferencias = "SAUDE,EDUCACAO"
        perfil.save()

        lista = perfil.get_preferencias_list()
        assert lista == ['SAUDE', 'EDUCACAO']

    def test_get_preferencias_list_vazio_retorna_lista_vazia(self, voluntario_user):
        """
        CT-PR011.2: get_preferencias_list() retorna [] se vazio
        Resultado Esperado: Lista vazia
        """
        perfil = voluntario_user.perfil
        perfil.preferencias = None
        perfil.save()

        lista = perfil.get_preferencias_list()
        assert lista == []


@pytest.mark.django_db
class TestPerfilView:
    """
    CT-PR020: Testes da view de perfil
    """

    def test_perfil_view_requer_login(self, client):
        """
        CT-PR020.1: View de perfil requer autenticação
        Resultado Esperado: Redirect para login
        """
        url = reverse('acoes:perfil')
        response = client.get(url)
        assert response.status_code == 302

    def test_perfil_view_acessivel_quando_logado(self, client_logged_voluntario):
        """
        CT-PR020.2: Usuário logado acessa página de perfil
        Resultado Esperado: Status 200 com formulários no contexto
        """
        url = reverse('acoes:perfil')
        response = client_logged_voluntario.get(url)

        assert response.status_code == 200
        assert 'u_form' in response.context  # Formulário de User
        assert 'p_form' in response.context  # Formulário de Perfil

    def test_perfil_view_formularios_preenchidos_com_dados_atuais(self, client_logged_voluntario, voluntario_user):
        """
        CT-PR020.3: Formulários vêm preenchidos com dados atuais
        Resultado Esperado: Initial values corretos
        """
        # Define dados no perfil
        voluntario_user.first_name = 'João'
        voluntario_user.last_name = 'Silva'
        voluntario_user.email = 'joao@test.com'
        voluntario_user.save()

        voluntario_user.perfil.endereco = 'Rua ABC, 123'
        voluntario_user.perfil.save()

        url = reverse('acoes:perfil')
        response = client_logged_voluntario.get(url)

        # Verifica valores iniciais
        u_form = response.context['u_form']
        assert u_form.initial['first_name'] == 'João'
        assert u_form.initial['last_name'] == 'Silva'
        assert u_form.initial['email'] == 'joao@test.com'

        p_form = response.context['p_form']
        assert p_form.initial['endereco'] == 'Rua ABC, 123'

    def test_perfil_atualizar_dados_user_com_sucesso(self, client_logged_voluntario, voluntario_user):
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
            'preferencias': ''
        }

        response = client_logged_voluntario.post(url, data)

        # Verifica redirect
        assert response.status_code == 302
        assert response.url == reverse('acoes:perfil')

        # Verifica que dados foram atualizados
        voluntario_user.refresh_from_db()
        assert voluntario_user.first_name == 'Maria'
        assert voluntario_user.last_name == 'Santos'
        assert voluntario_user.email == 'maria@test.com'

    def test_perfil_atualizar_endereco_com_sucesso(self, client_logged_voluntario, voluntario_user):
        """
        CT-PR022: Atualizar endereço
        Resultado Esperado: Endereço atualizado no perfil
        """
        url = reverse('acoes:perfil')
        data = {
            'first_name': voluntario_user.first_name or '',
            'last_name': voluntario_user.last_name or '',
            'email': voluntario_user.email,
            'endereco': 'Nova Rua, 456',
            'preferencias': ''
        }

        response = client_logged_voluntario.post(url, data)

        # Verifica que endereço foi atualizado
        voluntario_user.perfil.refresh_from_db()
        assert voluntario_user.perfil.endereco == 'Nova Rua, 456'

    def test_perfil_atualizar_preferencias_multiplas(self, client_logged_voluntario, voluntario_user):
        """
        CT-PR023: Atualizar preferências múltiplas (checkboxes)
        Resultado Esperado: Preferências salvas como CSV
        """
        url = reverse('acoes:perfil')
        data = {
            'first_name': '',
            'last_name': '',
            'email': voluntario_user.email,
            'endereco': '',
            'preferencias': ['SAUDE', 'EDUCACAO', 'ANIMAIS']  # Lista de selecionados
        }

        response = client_logged_voluntario.post(url, data)

        # Verifica que preferências foram salvas como CSV
        voluntario_user.perfil.refresh_from_db()
        assert voluntario_user.perfil.preferencias == 'SAUDE,EDUCACAO,ANIMAIS'

    def test_perfil_atualizar_sem_preferencias(self, client_logged_voluntario, voluntario_user):
        """
        CT-PR024: Atualizar sem selecionar preferências
        Resultado Esperado: Preferências ficam vazias
        """
        url = reverse('acoes:perfil')
        data = {
            'first_name': '',
            'last_name': '',
            'email': voluntario_user.email,
            'endereco': '',
            'preferencias': []  # Nenhuma selecionada
        }

        response = client_logged_voluntario.post(url, data)

        # Verifica que preferências ficaram vazias
        voluntario_user.perfil.refresh_from_db()
        assert voluntario_user.perfil.preferencias == ''

    def test_perfil_atualizar_apenas_alguns_campos(self, client_logged_voluntario, voluntario_user):
        """
        CT-PR025: Atualizar apenas alguns campos mantém outros intactos
        Resultado Esperado: Apenas campos enviados são alterados
        """
        # Define valores iniciais
        voluntario_user.first_name = 'Nome Original'
        voluntario_user.save()
        voluntario_user.perfil.endereco = 'Endereco Original'
        voluntario_user.perfil.save()

        url = reverse('acoes:perfil')
        data = {
            'first_name': 'Nome Atualizado',  # Muda isso
            'last_name': '',
            'email': voluntario_user.email,
            'endereco': 'Endereco Original',  # Mantém
            'preferencias': ''
        }

        response = client_logged_voluntario.post(url, data)

        voluntario_user.refresh_from_db()
        assert voluntario_user.first_name == 'Nome Atualizado'
        assert voluntario_user.perfil.endereco == 'Endereco Original'

    def test_perfil_formulario_invalido_nao_salva(self, client_logged_voluntario, voluntario_user):
        """
        CT-PR026: Formulário inválido não salva dados
        Resultado Esperado: Erro e dados não alterados
        """
        email_original = voluntario_user.email

        url = reverse('acoes:perfil')
        data = {
            'first_name': '',
            'last_name': '',
            'email': 'email_invalido',  # Email inválido
            'endereco': '',
            'preferencias': ''
        }

        response = client_logged_voluntario.post(url, data)

        # Deve permanecer na página com erro
        assert response.status_code == 200

        # Email não deve ter mudado
        voluntario_user.refresh_from_db()
        assert voluntario_user.email == email_original

    def test_perfil_organizador_tambem_pode_atualizar(self, client_logged_organizador, organizador_user):
        """
        CT-PR027: Organizador também pode atualizar seu perfil
        Resultado Esperado: Atualização bem-sucedida
        """
        url = reverse('acoes:perfil')
        data = {
            'first_name': 'Organizador Atualizado',
            'last_name': '',
            'email': organizador_user.email,
            'endereco': 'Endereco Org',
            'preferencias': 'SAUDE'
        }

        response = client_logged_organizador.post(url, data)

        assert response.status_code == 302
        organizador_user.refresh_from_db()
        assert organizador_user.first_name == 'Organizador Atualizado'
        assert organizador_user.perfil.endereco == 'Endereco Org'


# ============================================
# SPRINT 2 - Placeholder para novos recursos
# ============================================

# Quando adicionar foto de perfil ou outras configurações:
# @pytest.mark.django_db
# class TestPerfilFoto:
#     """CT-PR030: Testes de foto de perfil - Sprint 2"""
#     pass