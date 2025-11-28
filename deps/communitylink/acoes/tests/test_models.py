"""
Testes dos Modelos do app 'acoes'

Este arquivo testa a lógica de negócio dos modelos:
- Acao: Criação, validações, propriedades calculadas
- Inscricao: Relacionamentos, constraints
- Notificacao: Criação e marcação de lida
"""

import pytest
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.utils import IntegrityError
from datetime import timedelta
from acoes.models import Acao, Inscricao, Notificacao


# ============================================
# SPRINT 1 - CRUD Ações + Inscrições
# ============================================


@pytest.mark.django_db
class TestAcaoModel:
    """
    CT-M001: Testes do modelo Acao
    Referência: Documento de Casos de Teste - Modelos
    """

    def test_criar_acao_valida(self, organizador_user):
        """
        CT-M001.1: Criar ação com todos os campos válidos
        Resultado Esperado: Ação criada com sucesso
        """
        acao = Acao.objects.create(
            titulo='Campanha de Vacinação',
            descricao='Vacinação gratuita para a comunidade',
            data=timezone.now() + timedelta(days=30),
            local='Centro de Saúde - Rua A, 123',
            numero_vagas=50,
            categoria='SAUDE',
            organizador=organizador_user
        )

        assert acao.titulo == 'Campanha de Vacinação'
        assert acao.numero_vagas == 50
        assert acao.categoria == 'SAUDE'
        assert acao.organizador == organizador_user

    def test_str_retorna_titulo(self, acao_futura):
        """
        CT-M001.2: Método __str__ retorna o título da ação
        Resultado Esperado: String igual ao título
        """
        assert str(acao_futura) == acao_futura.titulo

    def test_get_absolute_url(self, acao_futura):
        """
        CT-M001.3: get_absolute_url retorna URL correta
        Resultado Esperado: URL no formato /acoes/<pk>/
        """
        expected_url = f'/acoes/{acao_futura.pk}/'
        assert acao_futura.get_absolute_url() == expected_url

    def test_vagas_preenchidas_inicial_zero(self, acao_futura):
        """
        CT-M002.1: Ação nova tem 0 vagas preenchidas
        Resultado Esperado: vagas_preenchidas == 0
        """
        assert acao_futura.vagas_preenchidas == 0

    def test_vagas_preenchidas_conta_apenas_aceitos(self, acao_futura, voluntario_user):
        """
        CT-M002.2: vagas_preenchidas conta apenas inscrições ACEITAS
        Resultado Esperado: Apenas status='ACEITO' são contados
        """
        # Cria 3 inscrições aceitas
        for i in range(3):
            vol = User.objects.create_user(f'vol_aceito_{i}', f'vol{i}@test.com', 'pass')
            Inscricao.objects.create(acao=acao_futura, voluntario=vol, status='ACEITO')

        # Cria 2 inscrições pendentes
        for i in range(2):
            vol = User.objects.create_user(f'vol_pend_{i}', f'pend{i}@test.com', 'pass')
            Inscricao.objects.create(acao=acao_futura, voluntario=vol, status='PENDENTE')

        # Cria 1 inscrição rejeitada
        vol_rej = User.objects.create_user('vol_rej', 'rej@test.com', 'pass')
        Inscricao.objects.create(acao=acao_futura, voluntario=vol_rej, status='REJEITADO')

        assert acao_futura.vagas_preenchidas == 3

    def test_esta_cheia_false_com_vagas(self, acao_futura):
        """
        CT-M003.1: esta_cheia retorna False quando há vagas
        Resultado Esperado: esta_cheia == False
        """
        assert acao_futura.esta_cheia is False

    def test_esta_cheia_true_quando_lotada(self, acao_cheia):
        """
        CT-M003.2: esta_cheia retorna True quando todas vagas preenchidas
        Resultado Esperado: esta_cheia == True
        """
        assert acao_cheia.esta_cheia is True

    def test_categorias_validas(self, organizador_user):
        """
        CT-M004: Apenas categorias definidas em CATEGORIA_CHOICES são válidas
        Resultado Esperado: Ação aceita categorias válidas
        """
        categorias_validas = ['SAUDE', 'EDUCACAO', 'MEIO_AMBIENTE', 'ANIMAIS', 'OUTRO']

        for categoria in categorias_validas:
            acao = Acao.objects.create(
                titulo=f'Ação {categoria}',
                descricao='Teste',
                data=timezone.now() + timedelta(days=7),
                local='Local',
                numero_vagas=10,
                categoria=categoria,
                organizador=organizador_user
            )
            assert acao.categoria == categoria


@pytest.mark.django_db
class TestInscricaoModel:
    """
    CT-M010: Testes do modelo Inscricao
    Referência: Documento de Casos de Teste - Inscrições
    """

    def test_criar_inscricao_valida(self, acao_futura, voluntario_user):
        """
        CT-M010.1: Criar inscrição com ação e voluntário válidos
        Resultado Esperado: Inscrição criada com status PENDENTE
        """
        inscricao = Inscricao.objects.create(
            acao=acao_futura,
            voluntario=voluntario_user
        )

        assert inscricao.status == 'PENDENTE'
        assert inscricao.acao == acao_futura
        assert inscricao.voluntario == voluntario_user
        assert inscricao.data_inscricao is not None

    def test_status_choices_validos(self, acao_futura, voluntario_user):
        """
        CT-M010.2: Inscrição aceita status PENDENTE, ACEITO e REJEITADO
        Resultado Esperado: Status definido corretamente
        """
        status_validos = ['PENDENTE', 'ACEITO', 'REJEITADO']

        for i, status in enumerate(status_validos):
            vol = User.objects.create_user(f'vol_{i}', f'vol{i}@test.com', 'pass')
            inscricao = Inscricao.objects.create(
                acao=acao_futura,
                voluntario=vol,
                status=status
            )
            assert inscricao.status == status

    def test_unique_together_impede_inscricao_duplicada(self, acao_futura, voluntario_user):
        """
        CT-M011: Usuário não pode se inscrever 2x na mesma ação
        Resultado Esperado: IntegrityError ao tentar duplicar
        """
        # Primeira inscrição
        Inscricao.objects.create(acao=acao_futura, voluntario=voluntario_user)

        # Segunda inscrição deve falhar
        with pytest.raises(IntegrityError):
            Inscricao.objects.create(acao=acao_futura, voluntario=voluntario_user)

    def test_voluntario_pode_se_inscrever_em_multiplas_acoes(self, organizador_user, voluntario_user):
        """
        CT-M012: Voluntário pode se inscrever em várias ações diferentes
        Resultado Esperado: Múltiplas inscrições criadas com sucesso
        """
        # Cria 3 ações diferentes
        acoes = []
        for i in range(3):
            acao = Acao.objects.create(
                titulo=f'Ação {i}',
                descricao='Teste',
                data=timezone.now() + timedelta(days=7 + i),
                local='Local',
                numero_vagas=10,
                organizador=organizador_user
            )
            acoes.append(acao)

        # Inscreve o mesmo voluntário nas 3 ações
        for acao in acoes:
            Inscricao.objects.create(acao=acao, voluntario=voluntario_user)

        # Verifica que o voluntário tem 3 inscrições
        assert Inscricao.objects.filter(voluntario=voluntario_user).count() == 3

    def test_str_representation(self, inscricao_pendente):
        """
        CT-M013: Método __str__ retorna formato legível
        Resultado Esperado: String com username, título da ação e status
        """
        expected = f'{inscricao_pendente.voluntario.username} em {inscricao_pendente.acao.titulo} ({inscricao_pendente.status})'
        assert str(inscricao_pendente) == expected


@pytest.mark.django_db
class TestNotificacaoModel:
    """
    CT-M020: Testes do modelo Notificacao
    Referência: Documento de Casos de Teste - Notificações
    """

    def test_criar_notificacao_valida(self, voluntario_user):
        """
        CT-M020.1: Criar notificação com destinatário e mensagem
        Resultado Esperado: Notificação criada com lida=False
        """
        notificacao = Notificacao.objects.create(
            destinatario=voluntario_user,
            mensagem='Sua inscrição foi aceita!'
        )

        assert notificacao.destinatario == voluntario_user
        assert notificacao.mensagem == 'Sua inscrição foi aceita!'
        assert notificacao.lida is False
        assert notificacao.created_at is not None

    def test_notificacao_com_link(self, voluntario_user):
        """
        CT-M020.2: Notificação pode ter link opcional
        Resultado Esperado: Link armazenado corretamente
        """
        notificacao = Notificacao.objects.create(
            destinatario=voluntario_user,
            mensagem='Nova ação disponível',
            link='http://example.com/acoes/1/'
        )

        assert notificacao.link == 'http://example.com/acoes/1/'

    def test_marcar_como_lida(self, voluntario_user):
        """
        CT-M021: Marcar notificação como lida
        Resultado Esperado: lida muda de False para True
        """
        notificacao = Notificacao.objects.create(
            destinatario=voluntario_user,
            mensagem='Teste'
        )

        assert notificacao.lida is False

        notificacao.lida = True
        notificacao.save()

        assert notificacao.lida is True

    def test_ordering_por_created_at_desc(self, voluntario_user):
        """
        CT-M022: Notificações ordenadas por created_at descendente (mais recentes primeiro)
        Resultado Esperado: Ordem correta ao buscar do banco
        """
        # Cria 3 notificações em momentos diferentes
        notif1 = Notificacao.objects.create(
            destinatario=voluntario_user,
            mensagem='Primeira'
        )

        notif2 = Notificacao.objects.create(
            destinatario=voluntario_user,
            mensagem='Segunda'
        )

        notif3 = Notificacao.objects.create(
            destinatario=voluntario_user,
            mensagem='Terceira'
        )

        # Busca todas as notificações (usando a ordenação padrão do Meta)
        notificacoes = list(Notificacao.objects.filter(destinatario=voluntario_user))

        # A mais recente deve vir primeiro
        assert notificacoes[0] == notif3
        assert notificacoes[1] == notif2
        assert notificacoes[2] == notif1

    def test_str_trunca_mensagem_longa(self, voluntario_user):
        """
        CT-M023: __str__ trunca mensagens longas em 30 caracteres
        Resultado Esperado: String com mensagem truncada + '...'
        """
        mensagem_longa = 'Esta é uma mensagem muito longa que deve ser truncada no método __str__'
        notificacao = Notificacao.objects.create(
            destinatario=voluntario_user,
            mensagem=mensagem_longa
        )

        str_repr = str(notificacao)
        assert '...' in str_repr
        assert len(notificacao.mensagem[:30]) <= 30


# ============================================
# SPRINT 2 - Placeholder para futuras funcionalidades
# ============================================

# Quando implementar avaliações, adicione aqui:
# @pytest.mark.django_db
# class TestAvaliacaoModel:
#     """CT-M030: Testes do modelo Avaliacao - Sprint 2"""
#     pass