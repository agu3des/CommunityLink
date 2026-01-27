from .models import Acao, Inscricao, Notificacao, Perfil
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializers import AcaoSerializer, InscricaoSerializer, NotificacaoSerializer, PerfilSerializer
from .permissions import IsOrganizadorOrReadOnly

class AcaoViewSet(viewsets.ModelViewSet):
    queryset = Acao.objects.all()
    serializer_class = AcaoSerializer
    permission_classes = [IsOrganizadorOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(organizador=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def inscrever(self, request, pk=None):
        acao = self.get_object()
        inscricao, created = Inscricao.objects.get_or_create(
            acao=acao,
            voluntario=request.user,
            defaults={'status': 'PENDENTE'}
        )
        if not created:
            return Response({'detail': 'Já inscrito nesta ação.'}, status=400)
        serializer = InscricaoSerializer(inscricao)
        return Response(serializer.data)


class InscricaoViewSet(viewsets.ModelViewSet):
    queryset = Inscricao.objects.all()
    serializer_class = InscricaoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Inscricao.objects.filter(voluntario=self.request.user)

    def perform_create(self, serializer):
        serializer.save(voluntario=self.request.user)


class NotificacaoViewSet(viewsets.ModelViewSet):
    queryset = Notificacao.objects.all()
    serializer_class = NotificacaoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notificacao.objects.filter(destinatario=self.request.user)

    @action(detail=True, methods=['post'])
    def marcar_lida(self, request, pk=None):
        notificacao = self.get_object()
        notificacao.lida = True
        notificacao.save()
        serializer = self.get_serializer(notificacao)
        return Response(serializer.data)


class PerfilViewSet(viewsets.ModelViewSet):
    queryset = Perfil.objects.all()
    serializer_class = PerfilSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Perfil.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get', 'put', 'patch'])
    def meu_perfil(self, request):
        perfil = self.get_queryset().first()
        if not perfil:
            perfil = Perfil.objects.create(user=request.user)
        if request.method in ['PUT', 'PATCH']:
            serializer = self.get_serializer(perfil, data=request.data, partial=(request.method == 'PATCH'))
            serializer.is_valid(raise_exception=True)
            serializer.save()
        else:
            serializer = self.get_serializer(perfil)
        return Response(serializer.data)