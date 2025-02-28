Ferramenta utilizada: https://editor.plantuml.com/uml/

```plantuml 
@startuml

left to right direction
skinparam classAttributeIconSize 0

'----------------- USUÁRIOS -----------------
class Usuario {
    + acessarPagina() -> void
    + acessarRegrasDePrivacidade() -> void
}

abstract class Assinante {
    - id : String
    + nome : String
    - email : String
    - senha : String
    + validarEmail() -> boolean
    + alterarSenha() -> void
    + validarSenha() -> boolean
    + editarNome() -> void
    + editarEmail() -> void
    + receberNotificacoesSobreAtualizacoesDoSistema() -> void
}

class AdministradorDoSistema {
    + notificarUsuariosSobreAtualizacoes() -> void
    + auditarAcessos() -> void
    + habilitarLoginComGoogle() -> void
    + manterPermissoesDeAcesso() -> void
    + realizarBackupDoSistema() -> void
    + agendarBackup() -> void
    + manterUsuario() -> void
}

class UsuarioComum {
    + foto : Image
    - status : String
    - preferencias : String
    + ativarAutenticacaoEmDoisFatores() -> void
    + reportarProblemas() -> void
    + acessarSistemaEmMultiplosIdiomas() -> void
    + cadastrar() -> void
    + realizarOauthGoogle() -> void
    + editarTelefone() -> void
    + editarImagemDePerfil() -> void
    + editarPreferencias() -> void
    + validarDados() -> boolean
    + salvarAlteracoes() -> void
}

class MembroDaComunidade {
    + buscarMembros() -> void
    + verRegrasDeParticipacao() -> void
}

class AdministradorDaComunidade {
    + realizarBackupDeDados() -> void
    + agendarBackup() -> void
    + enviarNotificacoes() -> void
    + manterUsuario() -> void
}

class PatrocinadorEParceiros {}

class Visitante {
    - ip : String
}

'----------------- EVENTOS -----------------
class Eventos {
    - id : String
    - titulo : String
    - dataInicial : String
    - dataFinal : String
    - horarioInicial : String
    - horarioFinal : String
    - local : String
    - listaDeParticipantes : List
    - listaDePatrocinadores : List
    - listaDeDoacoes : List
    - listaDeBeneficiados : List
    + criarEvento() -> void
    + listarEvento() -> List
    + buscarEvento() -> Object
    + removerEvento() -> void
    + adicionarParticipantes() -> void
    + adicionarPatrocinadores() -> void
    + notificarParticipantes() -> void
}

'----------------- RELATÓRIOS -----------------
class Relatorios {
    - id : String
    - filtro : String
    - formato : String
    - dataDeGeracao : String
    + baixarRelatorioPdf() -> void
    + baixarRelatorioCsv() -> void
    + gerarRelatorio() -> void
    + visualizarRelatorio() -> void
    + listarRelatorios() -> List
}

class RelatorioEventos {
    - tipo : String
    - data : String
    - participantes : List
    - doacoes : List
}

class RelatorioAnuncios {
    - numeroVisualizacoes : int
    - interacoes : int
    - listaDeAnuncios : List
    + calcularEstatisticas() -> double
}

'----------------- DOAÇÕES -----------------
class Doacao {
    - id : String
    - tipo : String
    - data : String
    - duracao : String
    - voluntarios : List
    - beneficiados : List
}

class DoacaoMonetaria {
    - valorTotal : float
    - destinoFundos : String
}

class DoacaoBens {
    - itens : List
    - quantidades : List
}

'----------------- ANÚNCIOS -----------------
class Anuncio {
    - id : String
    - titulo : String
    - descricao : String
    - imagem : Image
    - publicoAlvo : String
    - orcamento : double
    - duracao : String
    - status : String
    + buscarAnuncio() -> List
    + obterMetricas() -> void
    + criarAnuncio() -> void
    + pagarAnuncio() -> void
    + ativarAnuncio() -> void
    + editarAnuncio() -> void
    + removerAnuncio() -> void
    + validarInformacoes() -> boolean
    + compararAnuncios() -> int
}

'----------------- RELACIONAMENTOS -----------------
Usuario <|-- Assinante
Usuario <|-- Visitante
Assinante <|-- AdministradorDoSistema
Assinante <|-- UsuarioComum

UsuarioComum <|-- MembroDaComunidade
UsuarioComum <|-- AdministradorDaComunidade
UsuarioComum <|-- PatrocinadorEParceiros

Relatorios <|-- RelatorioEventos
Relatorios <|-- RelatorioAnuncios
Doacao <|-- DoacaoMonetaria
Doacao <|-- DoacaoBens

AdministradorDaComunidade "0..*" - "1..*" Eventos : acessa
UsuarioComum "0..*" - "1..*" Relatorios : gera
Eventos "0..*" - "0..*" UsuarioComum : listaDeParticipantes<>
Eventos "0..*" - "0..*" PatrocinadorEParceiros : listaDePatrocinadores<>
Eventos "0..*" - "0..*" Doacao : listaDeDoacoes<>
Eventos "0..*" - "0..*" Anuncio : possui
Eventos "0..*" - "0..*" RelatorioEventos : possui
Anuncio "0..*" - "0..*" RelatorioAnuncios : gera
Anuncio "0..*" - "0..*" PatrocinadorEParceiros : possui

@enduml
