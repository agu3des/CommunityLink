### usuario
@startuml
start
:Clicar na opção de regras de privacidade;
:Aguardar carregamento da página;
:Visualizar regras de privacidade;
stop
@enduml

### assinante
@startuml
start
:Inserir e-mail para validação;
:Enviar solicitação para servidor;
if (E-mail válido?) then (Sim)
    :Exibir confirmação;
else (Não)
    :Exibir mensagem de erro;
endif
stop

start
:Inserir senha atual;
:Inserir nova senha;
:Confirmar nova senha;
if (Senha válida?) then (Sim)
    :Atualizar credenciais no sistema;
else (Não)
    :Exibir mensagem de erro;
endif
stop

start
:Editar nome;
:Confirmar alteração;
if (Nome válido?) then (Sim)
    :Salvar alterações;
else (Não)
    :Exibir mensagem de erro;
endif
stop

start
:Editar e-mail;
:Confirmar alteração;
if (E-mail válido?) then (Sim)
    :Salvar novas informações;
else (Não)
    :Exibir mensagem de erro;
endif
stop

start
:Receber notificações sobre atualizações;
:Exibir notificações ao usuário;
stop
@enduml

### adm sistema
@startuml
start
:Escrever notificação;
:Selecionar destinatários;
:Enviar notificações;
stop

start
:Selecionar logs de acessos;
:Filtrar por período e usuário;
:Gerar relatório de auditoria;
stop

start
:Acessar configurações de autenticação;
:Ativar login com Google;
:Confirmar integração;
stop

start
:Abrir painel de permissões;
:Selecionar usuário ou grupo;
:Alterar permissões;
:Salvar mudanças;
stop

start
:Selecionar opção de backup;
:Confirmar operação;
if (Backup realizado?) then (Sim)
    :Salvar log do backup;
else (Não)
    :Exibir mensagem de erro;
endif
stop

start
:Definir horário do backup;
:Configurar repetição automática;
:Confirmar agendamento;
stop

start
:Selecionar usuário;
:Alterar status ou permissões;
:Salvar modificações;
stop
@enduml

### usuario comum
@startuml
start
:Acessar configurações de segurança;
:Ativar autenticação em dois fatores;
:Confirmar via código enviado;
if (Código correto?) then (Sim)
    :Exibir mensagem de sucesso;
else (Não)
    :Exibir erro e solicitar novo código;
endif
stop

start
:Abrir suporte técnico;
:Descrever problema;
:Enviar relato;
:Aguardar resposta;
stop

start
:Selecionar idioma desejado;
:Ajustar configurações;
:Salvar preferências;
:Acessar sistema em múltiplos idiomas;
stop

start
:Acessar formulário de cadastro;
:Preencher dados;
:Confirmar e enviar;
if (Dados válidos?) then (Sim)
    :Criar conta;
else (Não)
    :Exibir mensagem de erro;
endif
stop

start
:Editar telefone;
:Confirmar alteração;
if (Telefone válido?) then (Sim)
    :Salvar mudanças;
else (Não)
    :Exibir mensagem de erro;
endif
stop
@enduml

### eventos
@startuml
start
:Acessar painel de eventos;
:Preencher formulário de criação;
:Confirmar dados;
if (Dados válidos?) then (Sim)
    :Salvar evento;
else (Não)
    :Exibir mensagem de erro;
endif
stop

start
:Listar eventos disponíveis;
:Exibir detalhes de cada evento;
stop

start
:Inserir critérios de busca;
:Filtrar eventos;
:Exibir resultados;
stop

start
:Selecionar evento;
:Confirmar remoção;
if (Evento encontrado?) then (Sim)
    :Remover evento da base de dados;
else (Não)
    :Exibir mensagem de erro;
endif
stop

start
:Selecionar evento;
:Adicionar participantes;
:Confirmar operação;
stop
@enduml

### relatorios
@startuml
start
:Selecionar tipo de relatório;
:Definir filtros;
:Gerar relatório;
:Baixar PDF;
stop

start
:Selecionar relatório;
:Definir formato CSV;
:Baixar arquivo;
stop

start
:Selecionar relatório;
:Visualizar informações detalhadas;
stop

start
:Listar relatórios disponíveis;
:Exibir opções de filtro;
stop
@enduml

### anuncio
@startuml
start
:Acessar painel de anúncios;
:Preencher detalhes do anúncio;
:Confirmar criação;
if (Informações válidas?) then (Sim)
    :Criar anúncio;
else (Não)
    :Exibir mensagem de erro;
endif
stop

start
:Definir critérios de busca;
:Filtrar anúncios;
:Exibir lista de anúncios encontrados;
stop

start
:Coletar dados de desempenho;
:Gerar relatório de métricas;
:Exibir estatísticas;
stop

start
:Selecionar método de pagamento;
:Confirmar pagamento;
if (Pagamento aprovado?) then (Sim)
    :Ativar anúncio;
else (Não)
    :Exibir erro e solicitar nova tentativa;
endif
stop

start
:Selecionar anúncio;
:Editar detalhes;
:Salvar mudanças;
stop

start
:Selecionar anúncio;
:Confirmar remoção;
if (Anúncio existente?) then (Sim)
    :Remover da base de dados;
else (Não)
    :Exibir erro;
endif
stop
@enduml

### membro comunidade
@startuml
start
:Acessar painel de membros;
:Inserir critérios de busca;
:Filtrar lista de membros;
:Exibir resultados;
stop

start
:Abrir regras de participação;
:Exibir documento;
stop
@enduml

###  adm comunidade
@startuml
start
:Acessar painel de administração;
:Selecionar opção de backup;
:Definir configurações;
:Executar backup;
if (Backup concluído?) then (Sim)
    :Exibir mensagem de sucesso;
else (Não)
    :Exibir erro e registrar falha;
endif
stop

start
:Acessar painel de administração;
:Definir cronograma de backup;
:Confirmar agendamento;
stop

start
:Escrever notificação;
:Selecionar destinatários;
:Enviar notificação;
stop

start
:Selecionar usuário;
:Modificar status ou permissões;
:Salvar mudanças;
stop
@enduml

### patrocinadores e parceiros
@startuml
start
:Navegar até painel de patrocínios;
:Visualizar oportunidades disponíveis;
:Selecionar evento ou campanha;
:Confirmar participação;
stop
@enduml

### visitante
@startuml
start
:Acessar página inicial;
:Navegar pelo site;
:Visualizar informações públicas;
stop
@enduml

### relatorios eventos
@startuml
start
:Acessar painel de relatórios;
:Selecionar relatório de eventos;
:Filtrar por data ou tipo;
:Exibir lista de participantes e doações;
stop
@enduml

### relatorios anuncios
@startuml
start
:Acessar painel de relatórios;
:Selecionar relatório de anúncios;
:Filtrar por período;
:Calcular estatísticas de visualização e interação;
:Exibir resultados;
stop
@enduml

### doacao
@startuml
start
:Abrir painel de doações;
:Selecionar tipo de doação;
:Preencher informações;
:Confirmar doação;
if (Dados válidos?) then (Sim)
    :Registrar doação no sistema;
else (Não)
    :Exibir mensagem de erro;
endif
stop
@enduml

### doacao monetaria
@startuml
start
:Selecionar opção de doação monetária;
:Inserir valor;
:Selecionar destino dos fundos;
:Confirmar pagamento;
if (Pagamento aprovado?) then (Sim)
    :Registrar doação;
else (Não)
    :Exibir erro e solicitar nova tentativa;
endif
stop
@enduml

### doacao bens
@startuml
start
:Abrir painel de doações;
:Selecionar opção de doação de bens;
:Listar itens e quantidades;
:Confirmar envio;
if (Itens aceitos?) then (Sim)
    :Registrar doação no sistema;
else (Não)
    :Exibir mensagem de erro;
endif
stop
@enduml
