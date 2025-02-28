Ferramenta utilizada:
https://editor.plantuml.com/uml/
---

- Código UML:
  
```plantuml
@startuml

left to right direction

actor "Usuário do Sistema" as US
actor "Usuário Comum" as UC
actor "Administrador da Comunidade" as AC
actor "Membro da Comunidade" as MC
actor "Visitante" as V
actor "Patrocinadores/Parceiros" as PP
actor "Administrador do Sistema" as AS

US <|-- UC
US <|-- AS
UC <|-- AC
UC <|-- MC
UC <|-- V
UC <|-- PP

rectangle CommunityLink {
    usecase "Criar eventos" as uc_criar_evento
    usecase "Realizar backup de dados" as uc_realizar_backup
    usecase "Enviar notificações" as uc_enviar_notificações
    usecase "Manter usuario" as uc_manter_usuario
    usecase "Gerar relatórios" as uc_gerar_relatórios
    usecase "Cadastrar-se no sistema" as uc_cadastrar_no_sistema
    usecase "Visualizar eventos" as uc_visualizar_eventos
    usecase "Configurar perfil" as uc_configurar_perfil
    usecase "Buscar eventos que já participou" as uc_buscar_eventos_que_ja_participou
    usecase "Ver regras de participação" as uc_ver_regras_de_participação
    usecase "Baixar relatórios de participação" as uc_baixar_relatorios_de_participação
    usecase "Buscar membros ou eventos" as uc_buscar_membros_ou_eventos
    usecase "Visualizar informações públicas" as uc_visualizar_informações_publicas
    usecase "Promover anúncios" as uc_promover_anúncios
    usecase "Obter métricas de anúncios" as uc_obter_metricas_de_anúncios
    usecase "Manter permissões de acesso" as uc_manter_permissões_de_acesso
    usecase "Auditar acessos" as uc_auditar_acessos
    usecase "Habilitar login com google" as uc_habilitar_login_com_google
    usecase "Realizar backup do sistema" as uc_realizar_backup_do_sistema
    usecase "Auditar acessos" as uc_auditar_acessos
    usecase "Realizar oauth google" as uc_realizar_oauth_google
    usecase "Notificar usuários sobre atualizações" as uc_notificar_usuarios_sobre_atualizações
    usecase "Acessar regras de privacidade" as uc_acessar_regras_de_privacidade
    usecase "Alterar e-mail" as uc_alterar_email
    usecase "Alterar senha" as uc_alterar_senha
    usecase "Ativar autenticação em dois fatores" as uc_ativar_autenticacação_em_dois_fatores
    usecase "Reportar problemas" as uc_reportar_problemas
    usecase "Receber notificações sobre atualizações do sistema" as uc_receber_notificações_sobre_atualizações_do_sistema
    usecase "Acessar sistema em múltiplos idiomas" as uc_acessar_sistema_em_multiplos_idiomas
}

AC -- uc_criar_evento
AC -- uc_realizar_backup
AC -- uc_enviar_notificações
AC -- uc_manter_usuario
AC -- uc_gerar_relatórios
AC -- uc_buscar_eventos_que_ja_participou
AC -- uc_buscar_membros_ou_eventos

MC -- uc_buscar_eventos_que_ja_participou
MC -- uc_ver_regras_de_participação
MC -- uc_baixar_relatorios_de_participação
MC -- uc_buscar_membros_ou_eventos

V -- uc_visualizar_informações_publicas

PP -- uc_promover_anúncios
PP -- uc_obter_metricas_de_anúncios

AS -- uc_manter_permissões_de_acesso
AS -- uc_auditar_acessos
AS -- uc_notificar_usuarios_sobre_atualizações
AS -- uc_realizar_backup_do_sistema
AS -- uc_manter_usuario
AS -- uc_habilitar_login_com_google

UC -- uc_realizar_oauth_google
UC -- uc_cadastrar_no_sistema
UC -- uc_visualizar_eventos
UC -- uc_configurar_perfil
UC -- uc_alterar_email
UC -- uc_alterar_senha
UC -- uc_ativar_autenticacação_em_dois_fatores
UC -- uc_reportar_problemas
UC -- uc_acessar_sistema_em_multiplos_idiomas


US -- uc_acessar_regras_de_privacidade
US -- uc_receber_notificações_sobre_atualizações_do_sistema

uc_cadastrar_no_sistema <. uc_configurar_perfil: <<extend>>
uc_cadastrar_no_sistema <. uc_realizar_oauth_google: <<extend>>
uc_configurar_perfil <. uc_alterar_email: <<extend>>
uc_configurar_perfil <. uc_alterar_senha: <<extend>>
uc_buscar_eventos_que_ja_participou <. uc_gerar_relatórios: <<extend>>
uc_buscar_eventos_que_ja_participou <. uc_baixar_relatorios_de_participação: <<extend>>
uc_visualizar_eventos <. uc_criar_evento: <<extend>>
@enduml
