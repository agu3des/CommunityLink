from .models import Notificacao

def auth_groups_processor(request):
    """
    Adiciona variáveis de grupo (is_organizador, is_voluntario) 
    e contagem de notificações ao contexto de todos os templates.
    """
    is_organizador = False
    is_voluntario = False
    unread_notification_count = 0 # Valor padrão

    # Precisamos checar se o usuário está logado
    # pois um AnonymousUser (usuário não logado) não tem .groups
    if request.user.is_authenticated:
        is_organizador = request.user.groups.filter(name='Organizadores').exists()
        is_voluntario = request.user.groups.filter(name='Voluntarios').exists()

        # --- Conta as notificações não lidas ---
        unread_notification_count = Notificacao.objects.filter(
            destinatario=request.user, 
            lida=False
        ).count()

    return {
        'is_organizador': is_organizador,
        'is_voluntario': is_voluntario,
        'unread_notification_count': unread_notification_count
    }