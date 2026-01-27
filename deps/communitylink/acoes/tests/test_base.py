"""
Base de testes com fixtures completas para o app acoes.

Este arquivo contém o FullFixturesMixin que cria usuários e ações
para serem usados nos testes.
"""

from django.test import TestCase
from django.contrib.auth.models import User, Group
from django.utils import timezone
from datetime import timedelta
from acoes.models import Acao, Inscricao


class FullFixturesMixin:
    """
    Mixin que cria fixtures completas para testes:
    - Usuários organizador, voluntário e superusuário
    - Grupos de permissões
    - Ações (futura, cheia, passada)
    - Inscrições
    - Clientes de teste já logados
    """

    def setUp(self):
        super().setUp()

        # Criar grupos
        organizadores_group, _ = Group.objects.get_or_create(name='Organizadores')
        voluntarios_group, _ = Group.objects.get_or_create(name='Voluntários')

        # Criar usuários
        self.organizador_user = User.objects.create_user(
            username='organizador',
            email='org@test.com',
            password='test123',
            first_name='João',
            last_name='Organizador'
        )
        self.organizador_user.groups.add(organizadores_group)

        self.voluntario_user = User.objects.create_user(
            username='voluntario',
            email='vol@test.com',
            password='test123',
            first_name='Maria',
            last_name='Voluntária'
        )
        self.voluntario_user.groups.add(voluntarios_group)

        # Criar ação futura
        self.acao_futura = Acao.objects.create(
            titulo='Ação Futura de Teste',
            descricao='Descrição da ação futura para testes',
            data=timezone.now() + timedelta(days=30),
            local='Local de Teste',
            numero_vagas=10,
            categoria='EDUCACAO',
            organizador=self.organizador_user
        )

        # Criar ação cheia (com inscrições aceitas preenchendo todas as vagas)
        self.acao_cheia = Acao.objects.create(
            titulo='Ação Cheia de Teste',
            descricao='Descrição da ação cheia para testes',
            data=timezone.now() + timedelta(days=15),
            local='Local Cheio de Teste',
            numero_vagas=2,
            categoria='SAUDE',
            organizador=self.organizador_user
        )

        # Preencher a ação cheia com inscrições aceitas
        for i in range(self.acao_cheia.numero_vagas):
            voluntario = User.objects.create_user(
                username=f'voluntario_cheio_{i}',
                email=f'volcheio{i}@test.com',
                password='test123'
            )
            Inscricao.objects.create(
                acao=self.acao_cheia,
                voluntario=voluntario,
                status='ACEITO'
            )

        # Criar ação passada
        self.acao_passada = Acao.objects.create(
            titulo='Ação Passada de Teste',
            descricao='Descrição da ação passada para testes',
            data=timezone.now() - timedelta(days=30),
            local='Local Passado de Teste',
            numero_vagas=5,
            categoria='MEIO_AMBIENTE',
            organizador=self.organizador_user
        )

        # Criar inscrição pendente para testes
        self.inscricao_pendente = Inscricao.objects.create(
            acao=self.acao_futura,
            voluntario=self.voluntario_user,
            status='PENDENTE'
        )

        # Configurar clientes de teste já logados
        from django.test import Client
        self.client_logged_voluntario = Client()
        self.client_logged_voluntario.login(username='voluntario', password='test123')

        self.client_logged_organizador = Client()
        self.client_logged_organizador.login(username='organizador', password='test123')

        # Criar superusuário
        self.superuser = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='test123'
        )