from rest_framework import serializers
from .models import Acao, Inscricao, Notificacao, Perfil
from django.contrib.auth.models import User
from django.utils import timezone


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class PerfilSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Perfil
        fields = ['user', 'endereco', 'preferencias']


class InscricaoSerializer(serializers.ModelSerializer):
    voluntario = UserSerializer(read_only=True)
    acao_titulo = serializers.CharField(source='acao.titulo', read_only=True)

    class Meta:
        model = Inscricao
        fields = ['id', 'acao', 'voluntario', 'status', 'data_inscricao', 'comentario', 'acao_titulo']
        read_only_fields = ['data_inscricao']


class AcaoSerializer(serializers.ModelSerializer):
    organizador = UserSerializer(read_only=True)
    inscricoes = InscricaoSerializer(many=True, read_only=True)
    vagas_preenchidas = serializers.ReadOnlyField()
    esta_cheia = serializers.ReadOnlyField()
    ja_aconteceu = serializers.ReadOnlyField()

    class Meta:
        model = Acao
        fields = [
            'id', 'titulo', 'descricao', 'data', 'local', 'numero_vagas',
            'categoria', 'organizador', 'notas_organizador', 'inscricoes',
            'vagas_preenchidas', 'esta_cheia', 'ja_aconteceu'
        ]
        read_only_fields = ['organizador']

    def validate_data(self, value):
        if value and timezone.is_naive(value):
            value = timezone.make_aware(value)
        return value

    def validate_numero_vagas(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "O número de vagas deve ser maior que zero"
            )
        return value


class NotificacaoSerializer(serializers.ModelSerializer):
    destinatario = UserSerializer(read_only=True)

    class Meta:
        model = Notificacao
        fields = ['id', 'destinatario', 'mensagem', 'lida', 'created_at', 'link']
        read_only_fields = ['created_at']