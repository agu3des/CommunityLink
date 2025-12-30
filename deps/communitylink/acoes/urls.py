from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from . import views

app_name = "acoes"

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
    path('inscricao/<int:pk>/cancelar/', views.inscricao_cancel, name='inscricao_cancel'),

    #Páginas de usuário
    path('minhas-inscricoes/', views.minhas_inscricoes, name='minhas_inscricoes'),
    path('minhas-acoes/', views.minhas_acoes, name='minhas_acoes'),

    # Notificações
    path('notificacoes/', views.notificacoes_list, name='notificacoes_list'),
    path('notificacoes/limpar/', views.notificacoes_clear, name='notificacoes_clear'),

    #Auth
    path('signup/', views.signup_view, name='signup'), #Registrar usuário
    path('signin/', views.signin_view, name='signin'), #Login do usuário
    path('logout/', views.logout_view, name='logout'), #Logout do usuário

    # Perfil
    path('perfil/', views.perfil_view, name='perfil'), #Ver/editar perfil
    path('historico/', views.historico_view, name='historico'),


   # --- RECUPERAÇÃO DE SENHA (PASSWORD RESET) ---
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(
             template_name='acoes/password_reset.html',
             email_template_name='acoes/password_reset_email.html',
             subject_template_name='acoes/password_reset_subject.txt',
             success_url=reverse_lazy('acoes:password_reset_done') # CORREÇÃO AQUI
         ),
         name='password_reset'),

    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(
             template_name='acoes/password_reset_done.html'
         ),
         name='password_reset_done'),

    path('password-reset-confirm/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             template_name='acoes/password_reset_confirm.html',
             success_url=reverse_lazy('acoes:password_reset_complete') # CORREÇÃO AQUI
         ),
         name='password_reset_confirm'),

    path('password-reset-complete/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name='acoes/password_reset_complete.html'
         ),
         name='password_reset_complete'),
]