"""
Fixtures compartilhadas para todos os testes do app 'acoes'

Fixtures são funções que criam dados de teste reutilizáveis.
Ao invés de repetir código de criação de usuários, ações, etc. em cada teste,
centralizamos aqui.
"""

import pytest
from django.contrib.auth.models import User, Group
from django.utils import timezone
from datetime import timedelta
from acoes.models import Acao, Inscricao, Notificacao


@pytest.fixture
def grupo_organizadores():
    """Cria o grupo 'Organizadores'"""
    grupo, created = Group.objects.get_or_create(name='Organizadores')
    return grupo


@pytest.fixture
def organizador_user(grupo_organizadores):
    """
    Cria um usuário organizador autenticado
    Uso: def test_algo(organizador_user):
    """
    user = User.objects.create_user(
        username='organizador',
        email='org@test.com',
        password='senha123'
    )
    user.groups.add(grupo_organizadores)
    return user


@pytest.fixture
def voluntario_user():
    """
    Cria um usuário voluntário (sem grupo especial)
    Uso: def test_algo(voluntario_user):
    """
    return User.objects.create_user(
        username='voluntario',
        email='vol@test.com',
        password='senha123'
    )


@pytest.fixture
def superuser():
    """
    Cria um superusuário para testes de admin
    Uso: def test_algo(superuser):
    """
    return User.objects.create_superuser(
        username='admin',
        email='admin@test.com',
        password='admin123'
    )


@pytest.fixture
def acao_futura(organizador_user):
    """
    Cria uma ação válida com data futura
    Uso: def test_algo(acao_futura):
    """
    return Acao.objects.create(
        titulo='Ação Teste',
        descricao='Descrição da ação de teste',
        data=timezone.now() + timedelta(days=7),
        local='São Paulo - SP',
        numero_vagas=10,
        categoria='SAUDE',
        organizador=organizador_user
    )


@pytest.fixture
def acao_passada(organizador_user):
    """
    Cria uma ação com data no passado (para testes de validação)
    Uso: def test_algo(acao_passada):
    """
    return Acao.objects.create(
        titulo='Ação Passada',
        descricao='Ação que já aconteceu',
        data=timezone.now() - timedelta(days=7),
        local='Rio de Janeiro - RJ',
        numero_vagas=5,
        categoria='EDUCACAO',
        organizador=organizador_user
    )


@pytest.fixture
def acao_cheia(organizador_user):
    """
    Cria uma ação com todas as vagas preenchidas
    Uso: def test_algo(acao_cheia):
    """
    acao = Acao.objects.create(
        titulo='Ação Lotada',
        descricao='Ação sem vagas disponíveis',
        data=timezone.now() + timedelta(days=7),
        local='Belo Horizonte - MG',
        numero_vagas=2,
        categoria='MEIO_AMBIENTE',
        organizador=organizador_user
    )

    # Cria 2 voluntários e aceita suas inscrições
    for i in range(2):
        vol = User.objects.create_user(
            username=f'vol_aceito_{i}',
            email=f'vol{i}@test.com',
            password='senha123'
        )
        Inscricao.objects.create(
            acao=acao,
            voluntario=vol,
            status='ACEITO'
        )

    return acao


@pytest.fixture
def inscricao_pendente(acao_futura, voluntario_user):
    """
    Cria uma inscrição com status PENDENTE
    Uso: def test_algo(inscricao_pendente):
    """
    return Inscricao.objects.create(
        acao=acao_futura,
        voluntario=voluntario_user,
        status='PENDENTE'
    )


@pytest.fixture
def inscricao_aceita(acao_futura):
    """
    Cria uma inscrição com status ACEITO
    Uso: def test_algo(inscricao_aceita):
    """
    voluntario = User.objects.create_user(
        username='vol_aceito',
        email='vol_aceito@test.com',
        password='senha123'
    )
    return Inscricao.objects.create(
        acao=acao_futura,
        voluntario=voluntario,
        status='ACEITO'
    )


@pytest.fixture
def client_logged_organizador(client, organizador_user):
    """
    Cliente HTTP já autenticado como organizador
    Uso: def test_algo(client_logged_organizador):
    """
    client.force_login(organizador_user)
    return client


@pytest.fixture
def client_logged_voluntario(client, voluntario_user):
    """
    Cliente HTTP já autenticado como voluntário
    Uso: def test_algo(client_logged_voluntario):
    """
    client.force_login(voluntario_user)
    return client