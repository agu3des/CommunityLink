from django.urls import path
from . import views

urlpatterns = [
    # READ
    path('', views.acao_list, name='acao_list'),
    path('<int:pk>/', views.acao_detail, name='acao_detail'),
    
    # CREATE
    path('nova/', views.acao_create, name='acao_create'),
    
    # UPDATE
    path('<int:pk>/editar/', views.acao_update, name='acao_update'),
    
    # DELETE
    path('<int:pk>/deletar/', views.acao_delete, name='acao_delete'),
    
    # Inscrição
    path('<int:pk>/inscrever/', views.acao_apply, name='acao_apply'),
    path('<int:pk>/gerenciar/', views.acao_manage, name='acao_manage'),
    path('minhas-inscricoes/', views.minhas_inscricoes, name='minhas_inscricoes'),
]