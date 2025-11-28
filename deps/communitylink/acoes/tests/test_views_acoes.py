"""
Testes das Views CRUD de Ações

Este arquivo testa as operações de:
- CREATE: Criação de ações
- READ: Listagem e detalhes de ações
- UPDATE: Edição de ações
- DELETE: Exclusão de ações
"""

import pytest
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from acoes.models import Acao


# ============================================
# SPRINT 1 - CRUD de Ações
# ============================================


@pytest.mark.django_db
class TestAcaoListView:
    """
    CT-V001: Testes da view de listagem de ações
    Referência: Documento de Casos de Teste - Views
    """

    def test_lista_acoes_acessivel_sem_login(self, client):
        """
        CT-V001.1: Lista de ações acessível sem autenticação
        Resultado Esperado: Status 200
        """
        url = reverse('acao_list')
        response = client.get(url)
        assert response.status_code == 200

    def test_lista_apenas_acoes_futuras(self, client, acao_futura, acao_passada):
        """
        CT-V001.2: Lista mostra apenas ações com data >= hoje
        Resultado Esperado: Ação passada não aparece na lista
        """
        url = reverse('acao_list')
        response = client.get(url)

        acoes = response.context['acoes']
        assert acao_futura in acoes
        assert acao_passada not in acoes

    def test_lista_ordenada_por_data(self, client, organizador_user):
        """
        CT-V001.3: Ações ordenadas por data (mais próximas primeiro)
        Resultado Esperado: Ordem crescente de data
        """
        # Cria 3 ações com datas diferentes
        acao1 = Acao.objects.create(
            titulo='Ação em 30 dias',
            descricao='Teste',
            data=timezone.now() + timedelta(days=30),
            local='Local',
            numero_vagas=10,
            organizador=organizador_user
        )
        acao2 = Acao.objects.create(
            titulo='Ação em 7 dias',
            descricao='Teste',
            data=timezone.now() + timedelta(days=7),
            local='Local',
            numero_vagas=10,
            organizador=organizador_user
        )
        acao3 = Acao.objects.create(
            titulo='Ação em 15 dias',
            descricao='Teste',
            data=timezone.now() + timedelta(days=15),
            local='Local',
            numero_vagas=10,
            organizador=organizador_user
        )

        url = reverse('acao_list')
        response = client.get(url)
        acoes = list(response.context['acoes'])

        # Verifica ordem: 7 dias, 15 dias, 30 dias
        assert acoes[0] == acao2
        assert acoes[1] == acao3
        assert acoes[2] == acao1

    def test_filtro_por_categoria(self, client, organizador_user):
        """
        CT-V002: Filtrar ações por categoria
        Resultado Esperado: Apenas ações da categoria filtrada
        """
        acao_saude = Acao.objects.create(
            titulo='Ação Saúde',
            descricao='Teste',
            data=timezone.now() + timedelta(days=7),
            local='Local',
            numero_vagas=10,
            categoria='SAUDE',
            organizador=organizador_user
        )
        acao_educacao = Acao.objects.create(
            titulo='Ação Educação',
            descricao='Teste',
            data=timezone.now() + timedelta(days=7),
            local='Local',
            numero_vagas=10,
            categoria='EDUCACAO',
            organizador=organizador_user
        )

        url = reverse('acao_list') + '?categoria=SAUDE'
        response = client.get(url)
        acoes = response.context['acoes']

        assert acao_saude in acoes
        assert acao_educacao not in acoes

    def test_filtro_por_local(self, client, organizador_user):
        """
        CT-V003: Filtrar ações por local (busca parcial)
        Resultado Esperado: Ações que contenham o termo no local
        """
        acao_sp = Acao.objects.create(
            titulo='Ação SP',
            descricao='Teste',
            data=timezone.now() + timedelta(days=7),
            local='São Paulo - Zona Sul',
            numero_vagas=10,
            organizador=organizador_user
        )
        acao_rj = Acao.objects.create(
            titulo='Ação RJ',
            descricao='Teste',
            data=timezone.now() + timedelta(days=7),
            local='Rio de Janeiro',
            numero_vagas=10,
            organizador=organizador_user
        )

        url = reverse('acao_list') + '?local=Paulo'
        response = client.get(url)
        acoes = response.context['acoes']

        assert acao_sp in acoes
        assert acao_rj not in acoes


@pytest.mark.django_db
class TestAcaoDetailView:
    """
    CT-V010: Testes da view de detalhes de ação
    """

    def test_detalhes_acessivel_sem_login(self, client, acao_futura):
        """
        CT-V010.1: Detalhes de ação acessíveis sem autenticação
        Resultado Esperado: Status 200
        """
        url = reverse('acao_detail', args=[acao_futura.pk])
        response = client.get(url)
        assert response.status_code == 200

    def test_detalhes_mostra_informacoes_corretas(self, client, acao_futura):
        """
        CT-V010.2: Detalhes mostram todas as informações da ação
        Resultado Esperado: Contexto contém a ação completa
        """
        url = reverse('acao_detail', args=[acao_futura.pk])
        response = client.get(url)

        assert response.context['acao'] == acao_futura
        assert acao_futura.titulo in response.content.decode()

    def test_detalhes_indica_se_usuario_ja_inscrito(self, client_logged_voluntario, acao_futura, voluntario_user):
        """
        CT-V010.3: Mostra se usuário logado já está inscrito
        Resultado Esperado: ja_inscrito=True quando há inscrição
        """
        from acoes.models import Inscricao

        # Cria inscrição
        Inscricao.objects.create(acao=acao_futura, voluntario=voluntario_user)

        url = reverse('acao_detail', args=[acao_futura.pk])
        response = client_logged_voluntario.get(url)

        assert response.context['ja_inscrito'] is True

    def test_detalhes_indica_organizador(self, client_logged_organizador, acao_futura):
        """
        CT-V010.4: Indica se usuário logado é o organizador
        Resultado Esperado: is_organizador=True para organizador da ação
        """
        url = reverse('acao_detail', args=[acao_futura.pk])
        response = client_logged_organizador.get(url)

        assert response.context['is_organizador'] is True


@pytest.mark.django_db
class TestAcaoCreateView:
    """
    CT-V020: Testes da view de criação de ação
    """

    def test_criacao_requer_login(self, client):
        """
        CT-V020.1: Criação de ação requer autenticação
        Resultado Esperado: Redirect para login
        """
        url = reverse('acao_create')
        response = client.get(url)
        assert response.status_code == 302  # Redirect

    def test_voluntario_nao_pode_criar_acao(self, client_logged_voluntario):
        """
        CT-V020.2: Voluntário (não-organizador) não pode criar ação
        Resultado Esperado: Mensagem de erro e redirect
        """
        url = reverse('acao_create')
        response = client_logged_voluntario.get(url)

        # Deve redirecionar para a lista de ações
        assert response.status_code == 302

    def test_organizador_pode_criar_acao(self, client_logged_organizador):
        """
        CT-V020.3: Organizador pode acessar formulário de criação
        Resultado Esperado: Status 200 e form no contexto
        """
        url = reverse('acao_create')
        response = client_logged_organizador.get(url)

        assert response.status_code == 200
        assert 'form' in response.context

    def test_criar_acao_com_dados_validos(self, client_logged_organizador, organizador_user):
        """
        CT-V021: Criar ação com dados válidos
        Resultado Esperado: Ação criada no banco e redirect
        """
        url = reverse('acao_create')
        data = {
            'titulo': 'Nova Ação',
            'descricao': 'Descrição da nova ação',
            'data': (timezone.now() + timedelta(days=10)).strftime('%Y-%m-%d %H:%M:%S'),
            'local': 'Centro Comunitário',
            'numero_vagas': 20,
            'categoria': 'EDUCACAO'
        }

        response = client_logged_organizador.post(url, data)

        # Verifica que foi criada
        assert Acao.objects.filter(titulo='Nova Ação').exists()
        acao = Acao.objects.get(titulo='Nova Ação')
        assert acao.organizador == organizador_user

    def test_criar_acao_com_data_passada_falha(self, client_logged_organizador):
        """
        CT-V022: Não é possível criar ação com data no passado
        Resultado Esperado: Erro de validação
        """
        url = reverse('acao_create')
        data = {
            'titulo': 'Ação Passada',
            'descricao': 'Teste',
            'data': (timezone.now() - timedelta(days=7)).strftime('%Y-%m-%d %H:%M:%S'),
            'local': 'Local',
            'numero_vagas': 10,
            'categoria': 'SAUDE'
        }

        response = client_logged_organizador.post(url, data)

        # Não deve criar a ação
        assert not Acao.objects.filter(titulo='Ação Passada').exists()
        # Deve mostrar erro no formulário
        assert 'form' in response.context
        assert response.context['form'].errors

    def test_superuser_pode_criar_acao(self, client, superuser):
        """
        CT-V023: Superusuário pode criar ação mesmo sem ser organizador
        Resultado Esperado: Ação criada com sucesso
        """
        client.force_login(superuser)
        url = reverse('acao_create')

        data = {
            'titulo': 'Ação Admin',
            'descricao': 'Teste',
            'data': (timezone.now() + timedelta(days=7)).strftime('%Y-%m-%d %H:%M:%S'),
            'local': 'Local',
            'numero_vagas': 10,
            'categoria': 'OUTRO'
        }

        response = client.post(url, data)
        assert Acao.objects.filter(titulo='Ação Admin').exists()


@pytest.mark.django_db
class TestAcaoUpdateView:
    """
    CT-V030: Testes da view de edição de ação
    """

    def test_edicao_requer_login(self, client, acao_futura):
        """
        CT-V030.1: Edição requer autenticação
        Resultado Esperado: Redirect para login
        """
        url = reverse('acao_update', args=[acao_futura.pk])
        response = client.get(url)
        assert response.status_code == 302

    def test_apenas_organizador_pode_editar(self, client_logged_voluntario, acao_futura):
        """
        CT-V030.2: Apenas organizador da ação pode editá-la
        Resultado Esperado: Mensagem de erro e redirect
        """
        url = reverse('acao_update', args=[acao_futura.pk])
        response = client_logged_voluntario.get(url)

        assert response.status_code == 302

    def test_organizador_pode_editar_propria_acao(self, client_logged_organizador, acao_futura):
        """
        CT-V030.3: Organizador pode editar sua própria ação
        Resultado Esperado: Form preenchido com dados da ação
        """
        url = reverse('acao_update', args=[acao_futura.pk])
        response = client_logged_organizador.get(url)

        assert response.status_code == 200
        assert response.context['form'].instance == acao_futura

    def test_atualizar_acao_com_sucesso(self, client_logged_organizador, acao_futura):
        """
        CT-V031: Atualizar ação com dados válidos
        Resultado Esperado: Ação atualizada no banco
        """
        url = reverse('acao_update', args=[acao_futura.pk])
        data = {
            'titulo': 'Título Atualizado',
            'descricao': acao_futura.descricao,
            'data': acao_futura.data.strftime('%Y-%m-%d %H:%M:%S'),
            'local': acao_futura.local,
            'numero_vagas': acao_futura.numero_vagas,
            'categoria': acao_futura.categoria
        }

        response = client_logged_organizador.post(url, data)

        acao_futura.refresh_from_db()
        assert acao_futura.titulo == 'Título Atualizado'

    def test_superuser_pode_editar_qualquer_acao(self, client, superuser, acao_futura):
        """
        CT-V032: Superusuário pode editar qualquer ação
        Resultado Esperado: Edição permitida
        """
        client.force_login(superuser)
        url = reverse('acao_update', args=[acao_futura.pk])
        response = client.get(url)

        assert response.status_code == 200


@pytest.mark.django_db
class TestAcaoDeleteView:
    """
    CT-V040: Testes da view de exclusão de ação
    """

    def test_delecao_requer_login(self, client, acao_futura):
        """
        CT-V040.1: Exclusão requer autenticação
        Resultado Esperado: Redirect para login
        """
        url = reverse('acao_delete', args=[acao_futura.pk])
        response = client.get(url)
        assert response.status_code == 302

    def test_apenas_organizador_pode_deletar(self, client_logged_voluntario, acao_futura):
        """
        CT-V040.2: Apenas organizador pode deletar a ação
        Resultado Esperado: Mensagem de erro e redirect
        """
        url = reverse('acao_delete', args=[acao_futura.pk])
        response = client_logged_voluntario.post(url)

        assert response.status_code == 302
        assert Acao.objects.filter(pk=acao_futura.pk).exists()

    def test_organizador_pode_deletar_propria_acao(self, client_logged_organizador, acao_futura):
        """
        CT-V040.3: Organizador pode deletar sua própria ação
        Resultado Esperado: Ação removida do banco
        """
        url = reverse('acao_delete', args=[acao_futura.pk])
        acao_pk = acao_futura.pk

        response = client_logged_organizador.post(url)

        assert not Acao.objects.filter(pk=acao_pk).exists()

    def test_delecao_exibe_confirmacao(self, client_logged_organizador, acao_futura):
        """
        CT-V041: GET na view de deleção exibe página de confirmação
        Resultado Esperado: Página de confirmação renderizada
        """
        url = reverse('acao_delete', args=[acao_futura.pk])
        response = client_logged_organizador.get(url)

        assert response.status_code == 200
        assert 'acao' in response.context


@pytest.mark.django_db
class TestMinhasAcoesView:
    """
    CT-V050: Testes da view "Minhas Ações" (para organizadores)
    """

    def test_minhas_acoes_requer_login(self, client):
        """
        CT-V050.1: View requer autenticação
        Resultado Esperado: Redirect para login
        """
        url = reverse('minhas_acoes')
        response = client.get(url)
        assert response.status_code == 302

    def test_mostra_apenas_acoes_do_organizador(self, client_logged_organizador, acao_futura, organizador_user):
        """
        CT-V050.2: Mostra apenas ações criadas pelo organizador logado
        Resultado Esperado: Apenas ações do organizador na lista
        """
        # Cria ação de outro organizador
        from django.contrib.auth.models import User
        outro_org = User.objects.create_user('outro_org', 'outro@test.com', 'pass')
        acao_outro = Acao.objects.create(
            titulo='Ação de Outro',
            descricao='Teste',
            data=timezone.now() + timedelta(days=7),
            local='Local',
            numero_vagas=10,
            organizador=outro_org
        )

        url = reverse('minhas_acoes')
        response = client_logged_organizador.get(url)
        acoes = response.context['acoes']

        assert acao_futura in acoes
        assert acao_outro not in acoes


# ============================================
# SPRINT 2 - Placeholder para novas views
# ============================================

# Quando adicionar avaliações, adicione aqui:
# @pytest.mark.django_db
# class TestAvaliacaoCreateView:
#     """CT-V060: Testes de criação de avaliação - Sprint 2"""
#     pass
