"""
Testes de Permissões e Autorização

Este arquivo testa regras de acesso e permissões do sistema:
- Organizadores vs Voluntários
- Superusuários
- Acesso autenticado vs anônimo
"""

import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from acoes.models import Acao, Inscricao


# ============================================
# SPRINT 2 - Permissões
# ============================================


@pytest.mark.django_db
class TestPermissoesOrganizador:
    """
    CT-P001: Testes de permissões específicas de Organizadores
    Referência: Documento de Casos de Teste - Permissões
    """

    def test_organizador_pode_criar_acao(self, client_logged_organizador):
        """
        CT-P001.1: Organizador tem acesso à criação de ações
        Resultado Esperado: Status 200
        """
        url = reverse('acoes:acao_create')
        response = client_logged_organizador.get(url)
        assert response.status_code == 200

    def test_organizador_pode_editar_propria_acao(self, client_logged_organizador, acao_futura):
        """
        CT-P001.2: Organizador pode editar ações que criou
        Resultado Esperado: Status 200
        """
        url = reverse('acoes:acao_update', args=[acao_futura.pk])
        response = client_logged_organizador.get(url)
        assert response.status_code == 200

    def test_organizador_pode_deletar_propria_acao(self, client_logged_organizador, acao_futura):
        """
        CT-P001.3: Organizador pode deletar ações que criou
        Resultado Esperado: Status 200 na confirmação
        """
        url = reverse('acoes:acao_delete', args=[acao_futura.pk])
        response = client_logged_organizador.get(url)
        assert response.status_code == 200

    def test_organizador_pode_gerenciar_propria_acao(self, client_logged_organizador, acao_futura):
        """
        CT-P001.4: Organizador pode gerenciar inscrições de suas ações
        Resultado Esperado: Status 200
        """
        url = reverse('acoes:acao_manage', args=[acao_futura.pk])
        response = client_logged_organizador.get(url)
        assert response.status_code == 200

    def test_organizador_nao_pode_editar_acao_de_outro(self, client_logged_organizador, organizador_user):
        """
        CT-P002: Organizador NÃO pode editar ação de outro organizador
        Resultado Esperado: Redirect e mensagem de erro
        """
        # Cria ação de outro organizador
        outro_org = User.objects.create_user('outro_org', 'outro@test.com', 'pass')
        grupo_org = organizador_user.groups.first()
        outro_org.groups.add(grupo_org)

        acao_outro = Acao.objects.create(
            titulo='Ação de Outro',
            descricao='Teste',
            data='2025-12-31 10:00:00',
            local='Local',
            numero_vagas=10,
            organizador=outro_org
        )

        url = reverse('acoes:acao_update', args=[acao_outro.pk])
        response = client_logged_organizador.get(url)

        # Deve redirecionar (não tem permissão)
        assert response.status_code == 302

    def test_organizador_nao_pode_deletar_acao_de_outro(self, client_logged_organizador, organizador_user):
        """
        CT-P003: Organizador NÃO pode deletar ação de outro organizador
        Resultado Esperado: Redirect e mensagem de erro
        """
        outro_org = User.objects.create_user('outro_org2', 'outro2@test.com', 'pass')
        grupo_org = organizador_user.groups.first()
        outro_org.groups.add(grupo_org)

        acao_outro = Acao.objects.create(
            titulo='Ação de Outro 2',
            descricao='Teste',
            data='2025-12-31 10:00:00',
            local='Local',
            numero_vagas=10,
            organizador=outro_org
        )

        url = reverse('acoes:acao_delete', args=[acao_outro.pk])
        response = client_logged_organizador.post(url)

        # Deve redirecionar e ação deve continuar existindo
        assert response.status_code == 302
        assert Acao.objects.filter(pk=acao_outro.pk).exists()

    def test_organizador_nao_pode_gerenciar_acao_de_outro(self, client_logged_organizador, organizador_user):
        """
        CT-P004: Organizador NÃO pode gerenciar inscrições de ação de outro
        Resultado Esperado: Redirect e mensagem de erro
        """
        outro_org = User.objects.create_user('outro_org3', 'outro3@test.com', 'pass')
        grupo_org = organizador_user.groups.first()
        outro_org.groups.add(grupo_org)

        acao_outro = Acao.objects.create(
            titulo='Ação de Outro 3',
            descricao='Teste',
            data='2025-12-31 10:00:00',
            local='Local',
            numero_vagas=10,
            organizador=outro_org
        )

        url = reverse('acoes:acao_manage', args=[acao_outro.pk])
        response = client_logged_organizador.get(url)

        assert response.status_code == 302


@pytest.mark.django_db
class TestPermissoesVoluntario:
    """
    CT-P010: Testes de permissões de Voluntários
    """

    def test_voluntario_nao_pode_criar_acao(self, client_logged_voluntario):
        """
        CT-P010.1: Voluntário NÃO pode criar ações
        Resultado Esperado: Redirect com mensagem de erro
        """
        url = reverse('acoes:acao_create')
        response = client_logged_voluntario.get(url)
        assert response.status_code == 302

    def test_voluntario_nao_pode_editar_acao(self, client_logged_voluntario, acao_futura):
        """
        CT-P010.2: Voluntário NÃO pode editar ações
        Resultado Esperado: Redirect
        """
        url = reverse('acoes:acao_update', args=[acao_futura.pk])
        response = client_logged_voluntario.get(url)
        assert response.status_code == 302

    def test_voluntario_nao_pode_deletar_acao(self, client_logged_voluntario, acao_futura):
        """
        CT-P010.3: Voluntário NÃO pode deletar ações
        Resultado Esperado: Redirect e ação permanece
        """
        url = reverse('acoes:acao_delete', args=[acao_futura.pk])
        response = client_logged_voluntario.post(url)

        assert response.status_code == 302
        assert Acao.objects.filter(pk=acao_futura.pk).exists()

    def test_voluntario_nao_pode_gerenciar_inscricoes(self, client_logged_voluntario, acao_futura):
        """
        CT-P010.4: Voluntário NÃO pode gerenciar inscrições
        Resultado Esperado: Redirect
        """
        url = reverse('acoes:acao_manage', args=[acao_futura.pk])
        response = client_logged_voluntario.get(url)
        assert response.status_code == 302

    def test_voluntario_pode_se_inscrever(self, client_logged_voluntario, acao_futura, voluntario_user):
        """
        CT-P011: Voluntário PODE se inscrever em ações
        Resultado Esperado: Inscrição criada
        """
        url = reverse('acoes:acao_apply', args=[acao_futura.pk])
        response = client_logged_voluntario.post(url)

        assert Inscricao.objects.filter(acao=acao_futura, voluntario=voluntario_user).exists()

    def test_voluntario_pode_ver_lista_acoes(self, client_logged_voluntario):
        """
        CT-P012: Voluntário pode ver lista de ações
        Resultado Esperado: Status 200
        """
        url = reverse('acoes:acao_list')
        response = client_logged_voluntario.get(url)
        assert response.status_code == 200

    def test_voluntario_pode_ver_detalhes_acao(self, client_logged_voluntario, acao_futura):
        """
        CT-P013: Voluntário pode ver detalhes de ação
        Resultado Esperado: Status 200
        """
        url = reverse('acoes:acao_detail', args=[acao_futura.pk])
        response = client_logged_voluntario.get(url)
        assert response.status_code == 200

    def test_voluntario_pode_ver_minhas_inscricoes(self, client_logged_voluntario):
        """
        CT-P014: Voluntário pode ver suas inscrições
        Resultado Esperado: Status 200
        """
        url = reverse('acoes:minhas_inscricoes')
        response = client_logged_voluntario.get(url)
        assert response.status_code == 200


@pytest.mark.django_db
class TestPermissoesSuperuser:
    """
    CT-P020: Testes de permissões de Superusuário
    """

    def test_superuser_pode_criar_acao(self, client, superuser):
        """
        CT-P020.1: Superusuário pode criar ações
        Resultado Esperado: Status 200
        """
        client.force_login(superuser)
        url = reverse('acoes:acao_create')
        response = client.get(url)
        assert response.status_code == 200

    def test_superuser_pode_editar_qualquer_acao(self, client, superuser, acao_futura):
        """
        CT-P020.2: Superusuário pode editar qualquer ação
        Resultado Esperado: Status 200
        """
        client.force_login(superuser)
        url = reverse('acoes:acao_update', args=[acao_futura.pk])
        response = client.get(url)
        assert response.status_code == 200

    def test_superuser_pode_deletar_qualquer_acao(self, client, superuser, acao_futura):
        """
        CT-P020.3: Superusuário pode deletar qualquer ação
        Resultado Esperado: Ação deletada
        """
        client.force_login(superuser)
        url = reverse('acoes:acao_delete', args=[acao_futura.pk])
        acao_pk = acao_futura.pk

        response = client.post(url)

        assert not Acao.objects.filter(pk=acao_pk).exists()

    def test_superuser_pode_gerenciar_qualquer_acao(self, client, superuser, acao_futura):
        """
        CT-P020.4: Superusuário pode gerenciar qualquer ação
        Resultado Esperado: Status 200
        """
        client.force_login(superuser)
        url = reverse('acoes:acao_manage', args=[acao_futura.pk])
        response = client.get(url)
        assert response.status_code == 200


@pytest.mark.django_db
class TestPermissoesUsuarioAnonimo:
    """
    CT-P030: Testes de acesso para usuários não autenticados
    """

    def test_anonimo_pode_ver_lista_acoes(self, client):
        """
        CT-P030.1: Usuário anônimo pode ver lista de ações
        Resultado Esperado: Status 200
        """
        url = reverse('acoes:acao_list')
        response = client.get(url)
        assert response.status_code == 200

    def test_anonimo_pode_ver_detalhes_acao(self, client, acao_futura):
        """
        CT-P030.2: Usuário anônimo pode ver detalhes de ação
        Resultado Esperado: Status 200
        """
        url = reverse('acoes:acao_detail', args=[acao_futura.pk])
        response = client.get(url)
        assert response.status_code == 200

    def test_anonimo_nao_pode_criar_acao(self, client):
        """
        CT-P030.3: Usuário anônimo NÃO pode criar ação
        Resultado Esperado: Redirect para login
        """
        url = reverse('acoes:acao_create')
        response = client.get(url)
        assert response.status_code == 302
        assert '/login' in response.url or 'next=' in response.url

    def test_anonimo_nao_pode_editar_acao(self, client, acao_futura):
        """
        CT-P030.4: Usuário anônimo NÃO pode editar ação
        Resultado Esperado: Redirect para login
        """
        url = reverse('acoes:acao_update', args=[acao_futura.pk])
        response = client.get(url)
        assert response.status_code == 302

    def test_anonimo_nao_pode_deletar_acao(self, client, acao_futura):
        """
        CT-P030.5: Usuário anônimo NÃO pode deletar ação
        Resultado Esperado: Redirect para login
        """
        url = reverse('acoes:acao_delete', args=[acao_futura.pk])
        response = client.get(url)
        assert response.status_code == 302

    def test_anonimo_nao_pode_se_inscrever(self, client, acao_futura):
        """
        CT-P030.6: Usuário anônimo NÃO pode se inscrever
        Resultado Esperado: Redirect para login
        """
        url = reverse('acoes:acao_apply', args=[acao_futura.pk])
        response = client.post(url)
        assert response.status_code == 302

    def test_anonimo_nao_pode_gerenciar_acao(self, client, acao_futura):
        """
        CT-P030.7: Usuário anônimo NÃO pode gerenciar ação
        Resultado Esperado: Redirect para login
        """
        url = reverse('acoes:acao_manage', args=[acao_futura.pk])
        response = client.get(url)
        assert response.status_code == 302

    def test_anonimo_nao_pode_ver_minhas_inscricoes(self, client):
        """
        CT-P030.8: Usuário anônimo NÃO pode ver "minhas inscrições"
        Resultado Esperado: Redirect para login
        """
        url = reverse('acoes:minhas_inscricoes')
        response = client.get(url)
        assert response.status_code == 302

    def test_anonimo_nao_pode_ver_minhas_acoes(self, client):
        """
        CT-P030.9: Usuário anônimo NÃO pode ver "minhas ações"
        Resultado Esperado: Redirect para login
        """
        url = reverse('acoes:minhas_acoes')
        response = client.get(url)
        assert response.status_code == 302

    def test_anonimo_nao_pode_ver_notificacoes(self, client):
        """
        CT-P030.10: Usuário anônimo NÃO pode ver notificações
        Resultado Esperado: Redirect para login
        """
        url = reverse('acoes:notificacoes_list')
        response = client.get(url)
        assert response.status_code == 302


@pytest.mark.django_db
class TestPermissoesEspeciais:
    """
    CT-P040: Testes de regras de negócio específicas
    """

    def test_organizador_nao_pode_se_inscrever_propria_acao(self, client_logged_organizador, acao_futura, organizador_user):
        """
        CT-P040.1: Organizador NÃO pode se inscrever na própria ação
        Resultado Esperado: Inscrição não criada, mensagem de aviso
        """
        url = reverse('acoes:acao_apply', args=[acao_futura.pk])
        response = client_logged_organizador.post(url)

        assert not Inscricao.objects.filter(acao=acao_futura, voluntario=organizador_user).exists()

    def test_usuario_pode_ver_apenas_proprias_inscricoes(self, client_logged_voluntario, acao_futura, voluntario_user):
        """
        CT-P041: Usuário vê apenas suas próprias inscrições
        Resultado Esperado: Apenas inscrições do usuário logado
        """
        # Cria inscrição do voluntário logado
        Inscricao.objects.create(acao=acao_futura, voluntario=voluntario_user)

        # Cria inscrição de outro voluntário
        outro_vol = User.objects.create_user('outro_vol', 'outro@test.com', 'pass')
        Inscricao.objects.create(acao=acao_futura, voluntario=outro_vol)

        url = reverse('acoes:minhas_inscricoes')
        response = client_logged_voluntario.get(url)
        inscricoes = response.context['inscricoes']

        # Deve ter apenas 1 inscrição (do usuário logado)
        assert inscricoes.count() == 1
        assert inscricoes.first().voluntario == voluntario_user

    def test_usuario_pode_ver_apenas_proprias_acoes(self, client_logged_organizador, acao_futura, organizador_user):
        """
        CT-P042: Organizador vê apenas ações que criou
        Resultado Esperado: Apenas ações do organizador logado
        """
        # Cria ação de outro organizador
        outro_org = User.objects.create_user('outro_org_final', 'outrofinal@test.com', 'pass')
        grupo_org = organizador_user.groups.first()
        outro_org.groups.add(grupo_org)

        from django.utils import timezone
        from datetime import timedelta

        acao_outro = Acao.objects.create(
            titulo='Ação de Outro Organizador',
            descricao='Teste',
            data=timezone.now() + timedelta(days=7),
            local='Local',
            numero_vagas=10,
            organizador=outro_org
        )

        url = reverse('acoes:minhas_acoes')
        response = client_logged_organizador.get(url)
        acoes = response.context['acoes']

        # Deve conter apenas a ação do organizador logado
        assert acao_futura in acoes
        assert acao_outro not in acoes

    def test_usuario_pode_ver_apenas_proprias_notificacoes(self, client_logged_voluntario, voluntario_user, organizador_user):
        """
        CT-P043: Usuário vê apenas suas próprias notificações
        Resultado Esperado: Apenas notificações do usuário logado
        """
        from acoes.models import Notificacao

        # Notificação do voluntário
        notif_vol = Notificacao.objects.create(
            destinatario=voluntario_user,
            mensagem='Para voluntário'
        )

        # Notificação do organizador
        notif_org = Notificacao.objects.create(
            destinatario=organizador_user,
            mensagem='Para organizador'
        )

        url = reverse('acoes:notificacoes_list')
        response = client_logged_voluntario.get(url)
        notificacoes = response.context['notificacoes']

        assert notif_vol in notificacoes
        assert notif_org not in notificacoes
