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
    usecase "Criar eventos" as UC01
    usecase "Realizar backup de dados" as UC02
    usecase "Enviar notificações" as UC03
    usecase "Gerenciar membros" as UC04
    usecase "Gerar relatórios" as UC05
    usecase "Cadastrar-se no sistema" as UC06
    usecase "Visualizar eventos ativos" as UC07
    usecase "Configurar perfil" as UC08
    usecase "Buscar eventos que já participou" as UC09
    usecase "Ver regras de participação" as UC10
    usecase "Baixar relatórios de participação" as UC11
    usecase "Buscar membros ou eventos" as UC12
    usecase "Visualizar informações públicas" as UC13
    usecase "Promover anúncios" as UC14
    usecase "Obter métricas de anúncios" as UC15
    usecase "Gerenciar login e acessos" as UC16
    usecase "Realizar backup do sistema" as UC17
    usecase "Habilitar login com Google" as UC18
    usecase "Notificar usuários sobre atualizações" as UC19
    usecase "Acessar regras de privacidade" as UC20
    usecase "Alterar e-mail" as UC21
    usecase "Alterar senha" as UC22
    usecase "Ativar autenticação em dois fatores" as UC23
    usecase "Reportar problemas" as UC24
    usecase "Receber notificações de manutenção" as UC25
    usecase "Acessar sistema em múltiplos idiomas" as UC26
}

AC --> UC01
AC --> UC02
AC --> UC03
AC --> UC04
AC --> UC05
AC --> UC09
AC --> UC12

MC --> UC09
MC --> UC10
MC --> UC11
MC --> UC12

V --> UC13

PP --> UC14
PP --> UC15

AS --> UC16
AS --> UC17
AS --> UC18
AS --> UC19

UC --> UC06
UC --> UC07
UC --> UC08
UC --> UC21
UC --> UC22
UC --> UC23
UC --> UC24
UC --> UC25
UC --> UC26

US --> UC20

UC06 <. UC08: <<extend>>
UC08 <. UC21: <<extend>>
UC08 <. UC22: <<extend>>
UC09 <. UC05: <<extend>>
UC09 <. UC11: <<extend>>

@enduml

