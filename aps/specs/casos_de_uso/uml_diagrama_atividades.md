## Administrador da Comunidade
@startuml
|Administrador da Comunidade|
start
:Criar Evento;
|Sistema|
:Exibir formulário;
|Administrador da Comunidade|
:Preencher os campos;
|Sistema|
if (Todos os campos obrigatórios foram preenchidos?) then (Sim)
    :Validar dados;
    if (Erro de conexão?) then (Sim)
        :Exibir mensagem de erro;
        stop
    else (Não)
        :Armazenar informações;
        :Confirmar criação;
        :Notificar participantes;
    endif
else (Não)
    :Exibir mensagem de erro;
    stop
endif
stop
@enduml

@startuml
|Administrador da Comunidade|
start
:Realizar Backup;
|Sistema|
if (Há espaço disponível?) then (Sim)
    :Gerar arquivo de backup;
    :Verificar integridade dos dados;
    if (Erro de conexão?) then (Sim)
        :Exibir mensagem de erro;
        stop
    else (Não)
        :Disponibilizar para download;
        :Armazenar backup;
        :Exibir confirmação;
    endif
else (Não)
    :Exibir mensagem de erro sobre espaço;
    stop
endif
stop
@enduml

@startuml
|Administrador da Comunidade|
start
:Enviar Notificação;
|Sistema|
:Exibir formulário;
|Administrador da Comunidade|
:Preencher mensagem e destinatários;
|Sistema|
if (Mensagem e destinatários válidos?) then (Sim)
    :Enviar notificações;
    :Exibir resumo do envio;
else (Não)
    :Exibir mensagem de erro;
    stop
endif
stop
@enduml

@startuml
|Administrador da Comunidade|
start
:Manter Usuário;
|Sistema|
:Exibir lista de usuários;
|Administrador da Comunidade|
:Adicionar, editar ou excluir usuário;
|Sistema|
if (Dados válidos?) then (Sim)
    :Armazenar alterações;
    :Exibir confirmação;
else (Não)
    :Exibir mensagem de erro;
    stop
endif
stop
@enduml

@startuml
|Administrador da Comunidade|
start
:Gerar Relatórios;
|Sistema|
:Exibir opções de filtros;
|Administrador da Comunidade|
:Selecionar filtros;
|Sistema|
if (Dados disponíveis?) then (Sim)
    :Gerar relatório;
    :Disponibilizar para visualização e download;
else (Não)
    :Exibir mensagem de erro;
    stop
endif
stop
@enduml

## Usuário Comum
@startuml
|Usuário Comum|
start
:Cadastrar-se;
|Sistema|
:Exibir formulário de cadastro;
|Usuário Comum|
:Preencher os campos obrigatórios;
|Sistema|
if (E-mail já cadastrado?) then (Sim)
    :Exibir mensagem de erro;
    stop
else (Não)
    if (Senha forte?) then (Sim)
        :Validar dados;
        :Criar conta;
        :Enviar e-mail de confirmação;
        |Usuário Comum|
        :Confirmar cadastro via e-mail;
        |Sistema|
        :Ativar conta;
    else (Não)
        :Solicitar senha mais forte;
        stop
    endif
endif
stop
@enduml


@startuml
|Usuário Comum|
start
:Visualizar Eventos;
|Sistema|
:Exibir lista de eventos;
|Usuário Comum|
:Aplicar filtros (categoria, data, local);
|Sistema|
if (Eventos disponíveis?) then (Sim)
    :Exibir eventos filtrados;
else (Não)
    :Exibir mensagem de erro;
    stop
endif
stop
@enduml

@startuml
|Usuário Comum|
start
:Configurar Perfil;
|Sistema|
:Exibir formulário de edição;
|Usuário Comum|
:Editar informações (nome, e-mail, telefone, imagem de perfil, preferências);
|Sistema|
if (Dados válidos?) then (Sim)
    :Salvar alterações;
else (Não)
    :Exibir mensagem de erro;
    stop
endif
stop
@enduml


@startuml
|Usuário Comum|
start
:Alterar E-mail;
|Sistema|
:Exibir opção para alterar e-mail;
|Usuário Comum|
:Inserir novo e-mail e confirmar;
|Sistema|
if (E-mail inválido?) then (Sim)
    :Exibir erro;
    stop
else (Não)
    if (E-mail já cadastrado?) then (Sim)
        :Informar erro e solicitar novo endereço;
        stop
    else (Não)
        :Validar e salvar alteração;
        :Enviar e-mail de confirmação;
        |Usuário Comum|
        :Confirmar alteração através do link recebido;
    endif
endif
stop
@enduml

@startuml
|Usuário Comum|
start
:Alterar Senha;
|Sistema|
:Exibir opção para alterar senha;
|Usuário Comum|
:Inserir senha atual e nova senha;
|Sistema|
if (Senha inválida?) then (Sim)
    :Exibir erro;
    stop
else (Não)
    if (Senha incorreta?) then (Sim)
        :Exibir erro e solicitar nova tentativa;
        stop
    else (Não)
        :Validar e salvar alteração;
        :Exibir mensagem de confirmação;
    endif
endif
stop
@enduml

@startuml
|Usuário Comum|
start
:Ativar Autenticação em Dois Fatores;
|Sistema|
:Exibir opção para ativar 2FA;
|Usuário Comum|
:Escolher método de autenticação;
|Sistema|
:Gerar e exibir código de verificação;
|Usuário Comum|
:Inserir código e confirmar ativação;
|Sistema|
if (Código inválido?) then (Sim)
    :Exibir erro e solicitar novo código;
    stop
else (Não)
    if (Falha na configuração?) then (Sim)
        :Exibir mensagem e sugerir nova tentativa;
        stop
    else (Não)
        :Exibir mensagem de sucesso;
    endif
endif
stop
@enduml

@startuml
|Usuário Comum|
start
:Reportar Problema;
|Sistema|
:Exibir formulário para preenchimento;
|Usuário Comum|
:Preencher informações e enviar;
|Sistema|
if (Dados incompletos?) then (Sim)
    :Exibir erro e solicitar correção;
    stop
else (Não)
    :Validar e registrar problema;
    :Exibir confirmação de envio;
endif
stop
@enduml


@startuml
|Usuário Comum|
start
:Acessar Sistema em Múltiplos Idiomas;
|Sistema|
:Exibir opção para selecionar idioma;
|Usuário Comum|
:Escolher idioma;
|Sistema|
if (Idioma disponível?) then (Sim)
    :Exibir interface no idioma selecionado;
else (Não)
    :Exibir mensagem de indisponibilidade e manter idioma padrão;
endif
stop
@enduml


## Membro da Comunidade
@startuml
|Membro da Comunidade|
start
:Ver Regras de Participação;
|Sistema|
:Exibir diretrizes e regras;
|Membro da Comunidade|
:Pesquisar por palavras-chave ou categorias;
stop
@enduml

@startuml
|Membro da Comunidade|
start
:Baixar Relatórios de Participação;
|Sistema|
:Exibir lista de eventos participados;
|Membro da Comunidade|
:Selecionar evento e solicitar relatório;
|Sistema|
if (Erro na geração do relatório?) then (Sim)
    :Exibir mensagem de erro;
    stop
else (Não)
    :Gerar relatório em PDF ou CSV;
    :Disponibilizar para download;
endif
stop
@enduml


@startuml
|Visitante|
start
:Visualizar Informações Públicas;
|Sistema|
:Exibir eventos abertos e regras gerais;
|Visitante|
:Navegar pelas informações;
stop
@enduml

## Patrocinadores/Parceiros

@startuml
|Patrocinadores/Parceiros|
start
:Promover Anúncios;
|Sistema|
:Exibir formulário de criação;
|Patrocinadores/Parceiros|
:Preencher detalhes do anúncio;
|Sistema|
if (Dados válidos?) then (Sim)
    |Patrocinadores/Parceiros|
    :Confirmar pagamento;
    |Sistema|
    if (Pagamento autorizado?) then (Sim)
        :Ativar anúncio;
        :Exibir métricas de desempenho;
    else (Não)
        :Exibir mensagem de erro;
        stop
    endif
else (Não)
    :Exibir mensagem de erro;
    stop
endif
stop
@enduml

@startuml
|Patrocinadores/Parceiros|
start
:Obter Métricas de Anúncios;
|Sistema|
:Exibir lista de anúncios promovidos;
|Patrocinadores/Parceiros|
:Selecionar anúncio para visualizar métricas;
|Sistema|
if (Métricas disponíveis?) then (Sim)
    :Exibir dados de visualizações, cliques e conversões;
    |Patrocinadores/Parceiros|
    :Exportar dados para relatório;
else (Não)
    :Exibir mensagem de erro;
    stop
endif
stop
@enduml


## Administrador do Sistema

@startuml
|Administrador do Sistema|
start
:Manter Permissões de Acesso;
|Sistema|
:Exibir lista de usuários cadastrados;
|Administrador do Sistema|
:Ativar, desativar ou redefinir acessos;
|Sistema|
if (Erro na atualização?) then (Sim)
    :Exibir mensagem de erro;
    stop
else (Não)
    :Aplicar mudanças;
    :Notificar usuários afetados;
endif
stop
@enduml

@startuml
|Administrador do Sistema|
start
:Realizar Backup do Sistema;
|Sistema|
:Exibir opções de backup disponíveis;
|Administrador do Sistema|
:Selecionar opção e iniciar backup;
|Sistema|
if (Falha no backup?) then (Sim)
    :Exibir mensagem de erro e sugerir nova tentativa;
    stop
else (Não)
    :Processar e armazenar backup;
    :Notificar sucesso da operação;
endif
stop
@enduml

@startuml
|Administrador do Sistema|
start
:Habilitar login com Google;
|Sistema|
:Exibir opção para ativar login com Google;
|Administrador do Sistema|
:Habilitar opção e fornecer credenciais;
|Sistema|
:Configurar autenticação e salvar alterações;
:Exibir mensagem de sucesso;
stop
@enduml

@startuml
|Administrador do Sistema|
start
:Notificar Usuários sobre Atualizações;
|Sistema|
:Exibir formulário de envio de notificação;
|Administrador do Sistema|
:Redigir mensagem e selecionar público-alvo;
|Sistema|
if (Destinatários inválidos?) then (Sim)
    :Exibir alerta e sugerir correção;
    stop
else (Não)
    :Exibir resumo da notificação;
    |Administrador do Sistema|
    :Confirmar envio;
    |Sistema|
    if (Falha no envio?) then (Sim)
        :Exibir erro e permitir nova tentativa;
        stop
    else (Não)
        :Enviar notificação;
    endif
endif
stop
@enduml


@startuml
|Administrador do Sistema|
start
:Auditar Acessos;
|Sistema|
:Exibir opção "Auditoria de Acessos";
|Administrador do Sistema|
:Selecionar filtros para busca;
|Sistema|
if (Falha na consulta?) then (Sim)
    :Exibir mensagem de erro e sugerir nova tentativa;
    stop
else (Não)
    :Exibir registros de acesso;
    |Administrador do Sistema|
    :Exportar dados, se necessário;
endif
stop
@enduml


## Usuário do Sistema
@startuml
|Usuário do Sistema|
start
:Acessar Regras de Privacidade;
|Sistema|
:Exibir diretrizes de privacidade;
|Usuário do Sistema|
:Pesquisar ou filtrar regras;
|Sistema|
if (Falha no carregamento?) then (Sim)
    :Exibir mensagem de erro e sugerir nova tentativa;
    stop
else (Não)
    :Apresentar resultados;
endif
stop
@enduml

@startuml
|Usuário do Sistema|
start
:Receber Notificações de Manutenção;
|Sistema|
:Detectar manutenção programada;
:Enviar notificação;
|Usuário do Sistema|
:Consultar detalhes, se necessário;
|Sistema|
if (Falha ao enviar notificação?) then (Sim)
    :Registrar falha e tentar reenviar;
    :Gerar alerta para administradores;
endif
stop
@enduml


## Administrador da Comunidade, Membro da Comunidade
@startuml
|Administrador da Comunidade, Membro da Comunidade|
start
:Buscar Eventos Participados;
|Sistema|
:Exibir lista de eventos já participados;
|Administrador da Comunidade, Membro da Comunidade|
:Filtrar eventos por data, nome ou categoria;
|Sistema|
if (Eventos encontrados?) then (Sim)
    :Exibir eventos filtrados;
else (Não)
    :Exibir mensagem de erro;
    stop
endif
stop
@enduml

@startuml
|Administrador da Comunidade, Membro da Comunidade|
start
:Buscar Membros ou Eventos;
|Sistema|
:Exibir campo de pesquisa e filtros;
|Administrador da Comunidade, Membro da Comunidade|
:Escolher categoria e aplicar filtros;
|Sistema|
if (Resultados encontrados?) then (Sim)
    :Exibir resultados;
else (Não)
    :Exibir mensagem de erro;
    stop
endif
stop
@enduml
