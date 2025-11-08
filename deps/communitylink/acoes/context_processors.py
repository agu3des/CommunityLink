def auth_groups_processor(request):
    """
    Adiciona variáveis de grupo (is_organizador, is_voluntario) 
    ao contexto de todos os templates.
    """
    is_organizador = False
    is_voluntario = False

    # Precisamos checar se o usuário está logado
    # pois um AnonymousUser (usuário não logado) não tem .groups
    if request.user.is_authenticated:
        is_organizador = request.user.groups.filter(name='Organizadores').exists()
        is_voluntario = request.user.groups.filter(name='Voluntarios').exists()

    return {
        'is_organizador': is_organizador,
        'is_voluntario': is_voluntario
    }