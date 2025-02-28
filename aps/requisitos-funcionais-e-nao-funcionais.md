# Capa

---

<h1>Requisitos de Software</h1>

<h2>CommunityLink</h2>

<small>Versão 1.0</small>

---

## Histórico de revisões

|    Data    | Versão |          Descrição          |      Autor       |
| :--------: | :----: | :-------------------------: | :--------------: |
| 16/01/2025 |  1.0   |    Criação do documento     | Ananda Guedes, Angélica Araújo, Letícia Leite e Maira Fernandes |


---

## Sumário

- [Capa](#capa)
  - [Histórico de revisões](#histórico-de-revisões)
  - [Sumário](#sumário)
- [Introdução](#introdução)
  - [Definições, Acrônimos e Abreviações](#definições-acrônimos-e-abreviações)
- [Usuários identificados](#usuários-identificados)
- [Requisitos funcionais](#requisitos-funcionais)
- [Requisitos não-funcionais](#requisitos-não-funcionais)
  - [Disponibilidade](#disponibilidade)
  - [Privacidade e segurança](#privacidade-e-segurança)
  - [Usabilidade](#usabilidade)
  - [Suportabilidade](#suportabilidade)
  - [Interoperabilidade](#interoperabilidade)
  - [Manutenibilidade](#manutenibilidade)
  - [Desempenho](#desempenho)
  - [Implementação](#implementação)
  - [Implantação](#implantação)
- [Matriz de rastreabilidade](#matriz-de-rastreabilidade)
  - [Rastreabilidade entre NFs e RNFs](#rastreabilidade-entre-nfs-e-rnfs)

---

# Introdução

O objetivo deste documento é apresentar os requisitos de software do produto **Sistema de Voluntariado para Ações Comunitárias - CommunityLink**

## Definições, Acrônimos e Abreviações

Esta subseção fornece as definições de todos os termos, acrônimos e abreviações necessárias para a interpretação adequada deste Documento de Requisitos, incluindo suas prioridades de acordo com a matriz GUT (Gravidade, Urgência, Tendência).

Identificação dos requisitos: os **requisitos funcionais** estão divididos em módulos enumerados. Os **requisitos não funcionais** estão dividos por categoria, quais sejam: Disponibilidade, Privacidade e segurança, Usabilidade, Suportabilidade, Interoperabilidade, Manutenibilidade, Desempenho e Implementação. Ambos (funcionais ou não) são identificados com o prefixo referente ao tipo de requisito e um número sequencial. A estrutura do identificador é a seguinte:

[IDENTIFICADOR DO TIPO DE REQUISITOS]-[IDENTIFICADOR NUMÉRICO]

Onde o identificador do tipo de requisito é uma sigla conforme abaixo:

**RF** – Requisito Funcional

**RNF** – Requisito Não-Funcional

**NR** – Não-Requisito

O identificador numérico será sequencial e único para todo o conjunto de requisitos.
Exemplo: RF0001, RF1234, RNF1234, NR1212

Atributos dos Requisitos: os requisitos são classificados e possuem os seguintes atributos essenciais para sua gestão:
Prioridade (GUT):

**Gravidade (G):** Define o impacto do requisito caso não seja atendido:

1 - Sem gravidade

2 - Pouco grave

3 - Grave

4 - Muito grave

5 - Os prejuízos ou dificuldade são extremamente graves


**Urgência (U):** Determina a necessidade de implementação do requisito dentro de um prazo específico. A urgência é classificada em 3 níveis:

1 - Não tem pressa

2 - Pode esperar um pouco

3 - O mais cedo possível

4 - Com alguma urgência

5 - É necessária uma ação imediata

**Tendência (T):** Avalia o risco do requisito se tornar mais crítico com o tempo. A tendência é classificada em 3 níveis:

1 - Não vai piorar

2 - Vai piorar a longo prazo

3 - Vai piorar a médio prazo

4 - Vai piorar em pouco tempo

5 - Se nada for feito, a situação irá piorar rapidamente

<u>Complexidade:</u> Nível de dificuldade para implementar o requisito, classificado como Complexo, Alto, Médio ou Baixo.
<u>Risco:</u> Nível de risco associado à implementação do requisito, classificado como Alto, Médio ou Baixo.

# Usuários identificados

Os seguintes usuários foram identificados para o sistema **Community Link**:  
- Usuário do sistema
  - Usuários comuns
    - **Administrador da Comunidade**  
    - **Membro da Comunidade**  
    - **Visitante**  
    - **Patrocinadores/Parceiros** 
  - Administrador do sistema

---

# Requisitos funcionais

Os requisitos funcionais são descritos a seguir.

## Módulo 1 - Administrador da Comunidade

| ID    | Requisitos Funcionais                                                                 | G | U | T | P   |
|-------|----------------------------------------------------------------------------------------|---|---|---|-----|
| RF001 | Como um administrador da comunidade, eu gostaria de criar eventos, fornecendo informações como título, data, descrição, local e lista de participantes, para organizar atividades comunitárias. | 5 | 5 | 5 | 125 |
| RF002 | Como um administrador da comunidade, eu gostaria de realizar backup de todos os dados, para garantir a segurança da informação. | 5 | 5 | 5 | 125 |
| RF003 | Como um administrador da comunidade, eu gostaria de enviar notificações aos membros, para informá-los sobre atualizações importantes ou eventos futuros, como também chamar atenção caso a conduta do mesmo esteja em desacordo com os termos da aplicação. | 4 | 4 | 3 | 48  |
| RF004 | Como um administrador da comunidade, eu gostaria de gerenciar os membros, remover usuários para manter a organização da comunidade. Para tal, eu teria os seguintes campos: nome, status, data de cadastro. A exclusão seria lógica. | 3 | 3 | 3 | 27  |
| RF005 | Como um administrador da comunidade, eu gostaria de gerar relatórios sobre a participação, ou seja, a quantidade de pessoas que participaram como voluntários, a quantidade das pessoas que foram beneficiadas, a data em que ocorreu, bem como sua duração. A depender do tipo de ação. No caso de doações monetárias: o total arrecadado e onde este dinheiro foi escoado. No caso de doações bens materiais: (objetos de casa, vestuário, comida, itens de higiene) também devem ser listadas e quantificadas. Estes relários são importaras na tomada de decisões e noções de impactos sociais baseadas em dados. | 2 | 3 | 3 | 18  |

## Módulo 2 - Membro da Comunidade

| ID    | Requisitos Funcionais                                                                 | G | U | T | P   |
|-------|----------------------------------------------------------------------------------------|---|---|---|-----|
| RF200 | Como um membro da comunidade, eu gostaria de me cadastrar no sistema, fornecendo informações como nome, e-mail e uma senha, para que eu possa acessar as funcionalidades da plataforma. | 5 | 5 | 5 | 125 |
| RF201 | Como um membro da comunidade, eu gostaria de visualizar os eventos criados e me inscrever nos que forem do meu interesse, para participar das atividades da comunidade. | 5 | 5 | 5 | 125 |
| RF202 | Como um membro da comunidade, eu gostaria de configurar meu perfil com informações pessoais e interesses, para personalizar minha experiência na plataforma. | 4 | 3 | 4 | 48  |
| RF203 | Como membro da comunidade, gostaria de realizar a busca pelos eventos que já participei . A busca deve ser feita por nome do evento, data ou local. | 4 | 4 | 3 | 48  |
| RF204 | Como membro da comunidade, gostaria de verificar quais as regras de participação de cada ação. | 4 | 4 | 3 | 48  |
| RF205 | Como membro da comunidade, gostaria de realizar o download dos relatórios de participação, para que eu possa comprovar minha participação e ter uma cópia dos dados em caso de falha no sistema. | 4 | 4 | 3 | 48  |
| RF206 | Como um membro da comunidade, eu gostaria de buscar por outros membros ou eventos usando palavras-chave, para encontrar informações específicas de maneira eficiente. | 2 | 2 | 2 | 8   |

## Módulo 3 - Visitante

| ID    | Requisitos Funcionais                                                                 | G | U | T | P   |
|-------|----------------------------------------------------------------------------------------|---|---|---|-----|
| RF300 | Como um visitante, eu gostaria de visualizar informações públicas sobre a comunidade, como uma lista de eventos e iniciativas, para decidir se quero participar da plataforma. | 4 | 4 | 4 | 64  |

## Módulo 4 - Patrocinadores/Parceiros

| ID    | Requisitos Funcionais                                                                 | G | U | T | P   |
|-------|----------------------------------------------------------------------------------------|---|---|---|-----|
| RF400 | Como um patrocinador/parceiro, eu gostaria de promover anúncios na plataforma, segmentados com base no interesse dos membros, para divulgar meus produtos e serviços. | 5 | 5 | 5 | 125 |
| RF401 | Como patrocinador/parceiro, eu gostaria de ter a informação sobre o alcance dos anúncios promovidos na plataforma que divulgam meus produtos e serviços | 4 | 4 | 4 | 64  |

## Módulo 5 - Administrador do Sistema

| ID    | Requisitos Funcionais                                                                 | G | U | T | P   |
|-------|----------------------------------------------------------------------------------------|---|---|---|-----|
| RF500 | Como administrador, gostaria que todos os usuários realizassem login no sistema, para que eu possa ter controle sobre os acessos e possa realizar auditorias de acesso. | 5 | 5 | 5 | 125 |
| RF501 | Como administrador, gostaria de realizar o backup dos dados dos usuários, para que eu possa recuperar os dados em caso de falha no sistema. | 5 | 5 | 5 | 125 |
| RF502 | Como administrador, gostaria de oferecer aos usuários a possibilidade de realizar o login com o Google, para que eles possam ter uma experiência mais rápida e segura. | 4 | 4 | 4 | 64  |
| RF503 | Como administrador, gostaria que os usuários fossem comunicados sobre as atualizações do sistema, para que eles possam ter uma experiência mais segura e atualizada. | 3 | 3 | 3 | 27  |

## Módulo 6 - Usuário Comum

| ID    | Requisitos Funcionais                                                                 | G | U | T | P   |
|-------|----------------------------------------------------------------------------------------|---|---|---|-----|
| RF600 | Como usuário comum, gostaria de verificar quais as regras de privacidade e uso de dados de maneira resumida e simplificada, para que eu possa ter uma experiência mais segura. As regras de privacidade e uso de dados também devem ser apresentadas em uma página de termos de uso e política de privacidade, que deve ser acessível a partir do rodapé do site, a partir da página de cadastro e da página de regras simplificadas. | 5 | 4 | 4 | 80  |
| RF601 | Como usuário comum, gostaria de poder alterar o meu e-mail, para que eu possa ter uma experiência mais segura. A alteração de e-mail somente poderá ser realizada por meio de um e-mail de confirmação para acesso a uma página de alteração de e-mail. | 4 | 4 | 4 | 64  |
| RF602 | Como usuário comum, gostaria de poder alterar a minha senha, para que eu possa ter uma experiência mais segura. A alteração de senha somente poderá ser realizada por meio de um e-mail de confirmação para acesso a uma página de alteração de senha. | 4 | 4 | 4 | 64  |
| RF603 | Como usuário comum, gostaria de poder ativar acesso por dois fatores, para que eu possa ter uma experiência mais segura. | 4 | 4 | 4 | 64  |
| RF604 | Como usuário comum, gostaria que minha senha fosse criptografada, para que eu possa ter uma experiência mais segura. A troca de senha somente poderá ser realizada por meio de um e-mail de confirmação para acesso a uma página de troca de senha. | 4 | 4 | 4 | 64  |
| RF605 | Como usuário comum, gostaria de reportar problemas no sistema, para que eu possa ajudar a melhorar a experiência dos usuários. | 3 | 2 | 3 | 18  |
| RF606 | Como usuário comum, gostaria de receber notificações sobre manutenções agendadas no sistema, para que eu possa ter uma experiência mais segura e atualizada. | 3 | 2 | 3 | 18  |
| RF607 | Como usuário gostaria de ler informações em meu idioma, para que eu possa ter uma experiência mais agradável. O sistema deve ser desenvolvido de forma que possa ser traduzido para outros idiomas, priorizando o inglês, o espanhol e o português do Brasil. | 2 | 2 | 2 | 8   |

# Requisitos não-funcionais

Os requisitos não-funcionais são descritos a seguir.

## Disponibilidade

| ID    | Requisitos Não Funcionais                                                                 | G | U | T | P   |
|-------|--------------------------------------------------------------------------------------------|---|---|---|-----|
| RNF001 | O sistema deve ser desenvolvido de forma que possa ser implantado em plataformas web. | 5 | 5 | 5 | 125 |
| RNF002 | O sistema deve estar disponível 24 horas por dia, 7 dias por semana, 365 dias por ano.    | 5 | 5 | 5 | 125 |
| RNF003 | O sistema deve ser desenvolvido de forma que possa ser escalável, ou seja, deve ser possível aumentar a capacidade de armazenamento de dados e de processamento de requisições sem que haja perda de desempenho. | 5 | 5 | 5 | 125 |
| RNF004 | O sistema deve ser desenvolvido de forma que possa ser executado em qualquer dispositivo com conexão offline conforme RNF 401. | 4 | 3 | 3 | 36  |

## Privacidade e segurança

| ID    | Requisitos Não Funcionais                                                                 | G | U | T | P   |
|-------|--------------------------------------------------------------------------------------------|---|---|---|-----|
| RNF200 | O sistema deve ser desenvolvido de forma que os dados dos clientes sejam protegidos e não sejam acessíveis por terceiros. | 5 | 5 | 5 | 125 |
| RNF201 | O sistema deve atender aos requisitos de privacidade da LGPD (Lei Geral de Proteção de Dados). | 5 | 5 | 5 | 125 |
| RNF202 | O sistema deve ser desenvolvido de forma que os dados pessoais dos clientes sejam criptografados, como endereço de e-mail, senha, nome completo, cidade e estado. A criptografia deverá ser realizada com o algoritmo SHA-512, e deve impossibilitar a recuperação dos dados originais. | 5 | 5 | 5 | 125 |

## Usabilidade

| ID    | Requisitos Não Funcionais                                                                 | G | U | T | P   |
|-------|--------------------------------------------------------------------------------------------|---|---|---|-----|
| RNF300 | O sistema deve ser desenvolvido de forma que possa ser acessado por pessoas com deficiência visual, auditiva e física. | 5 | 5 | 5 | 125 |
| RNF301 | O sistema deve ser desenvolvido de forma que seja fácil de usar e de fácil aprendizado, de forma que os usuários não precisem de treinamento para utilizá-lo. | 4 | 5 | 5 | 100 |

## Suportabilidade

| ID    | Requisitos Não Funcionais                                                                 | G | U | T | P   |
|-------|--------------------------------------------------------------------------------------------|---|---|---|-----|
| RNF400 | O sistema deve ser desenvolvido de forma que possa ser executado em aplicativos nativos para Android e iOS, conforme a RNF 400. | 5 | 5 | 5 | 125 |
| RNF401 | O sistema deve ser desenvolvido de forma que possa ser executado nos três principais navegadores da web: Google Chrome, Mozilla Firefox e Microsoft Edge através de um computador com sistema operacional Windows, Linux ou Mac OS, bem como tablets e smartphones com sistema operacional Android ou iOS. | 4 | 3 | 3 | 36  |

## Interoperabilidade

| ID    | Requisitos Não Funcionais                                                                 | G | U | T | P   |
|-------|--------------------------------------------------------------------------------------------|---|---|---|-----|
| RNF500 | O sistema deve ser desenvolvido de forma que possa ser integrado com a API do Google para autenticação de usuários. | 4 | 4 | 4 | 64  |

## Manutenibilidade

| ID    | Requisitos Não Funcionais                                                                 | G | U | T | P   |
|-------|--------------------------------------------------------------------------------------------|---|---|---|-----|
| RNF600 | O sistema deve ser desenvolvido de forma que possa ser facilmente atualizado e mantido, preferencialmente, de maneira automatizada. | 5 | 5 | 5 | 125 |
| RNF601 | O sistema deve ser desenvolvido de forma que possa ser facilmente testado e validado, de forma manual e automatizada. | 5 | 5 | 5 | 125 |
| RNF602 | O sistema deve ser documentado de forma que possa ser facilmente compreendido por terceiros e para facilitar a manutenção do sistema. | 5 | 5 | 5 | 125 |

## Desempenho

| ID    | Requisitos Não Funcionais                                                                 | G | U | T | P   |
|-------|--------------------------------------------------------------------------------------------|---|---|---|-----|
| RNF700 | O sistema deve ser desenvolvido de forma que possa ser executado em qualquer dispositivo com conexão à internet, com velocidade de conexão de no mínimo 1 Mbps com tempo de resposta de no máximo 5 segundos. | 4 | 4 | 4 | 64  |

## Implementação

| ID    | Requisitos Não Funcionais                                                                 | G | U | T | P   |
|-------|--------------------------------------------------------------------------------------------|---|---|---|-----|
| RNF800 | O sistema deve ser desenvolvido com APIs de acesso aos dados, para que possa ser integrado com outros sistemas. | 4 | 4 | 4 | 64  |



Referencia: _Maxwell Anderson_ Abril de 2023.
