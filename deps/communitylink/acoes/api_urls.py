from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .viewset import AcaoViewSet, InscricaoViewSet, NotificacaoViewSet, PerfilViewSet

router = SimpleRouter()
router.register(r'acoes', AcaoViewSet)
router.register(r'inscricoes', InscricaoViewSet)
router.register(r'notificacoes', NotificacaoViewSet)
router.register(r'perfis', PerfilViewSet)

#app_name = 'api'

urlpatterns = [
    path('', include(router.urls)),
]