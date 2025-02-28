Ferramenta utilizada: https://editor.plantuml.com/uml/

```plantuml 
@startuml

' left to right direction
skinparam classAttributeIconSize 0

class UsuarioDoSistema {
    + acessarRegrasDePrivacidade() -> void
    + receberNotificacoesSobreAtualizacoesDoSistema() -> void
}

class AdministradorDoSistema {
    - nome : String
    - email : String
    - senha : String
    + notificarUsuariosSobreAtualizacoes() -> void
    + auditarAcessos() -> void
    + habilitarLoginComGoogle() -> void
    + manterPermissoesDeAcesso() -> void
    + realizarBackupDoSistema() -> void
    + agendarBackup() -> void
    + manterUsuario() -> void
    + alterarEmail() -> void
    + validarEmail() -> boolean
    + alterarSenha() -> void
    + validarSenha() -> boolean
}

class UsuarioComum {
    - status : String
    - nome : String
    - email : String
    - senha : String
    + ativarAutenticacaoEmDoisFatores() -> void
    + reportarProblemas() -> void
    + acessarSistemaEmMultiplosIdiomas() -> void
    + cadastrar() -> void
    + configurarPerfil() -> void
    + realizarOauthGoogle() -> void
    + visualizarEventos() -> void
    + alterarEmail() -> void
    + validarEmail() -> boolean
    + alterarSenha() -> void
    + validarSenha() -> boolean
    + baixarRelatoriosDeParticipacao() -> void
}

class Perfil {
    - nome : String
    - email : String
    - telefone : String
    - imagemDePerfil : String
    - preferencias : String
    + editarNome() -> void
    + editarEmail() -> void
    + editarTelefone() -> void
    + editarImagemDePerfil() -> void
    + editarPreferencias() -> void
    + validarDados() -> boolean
    + salvarAlteracoes() -> void
}

class MembroDaComunidade {
    + buscarEventosQueJaParticipou() -> void
    + buscarMembrosOuEventos() -> void
    + verRegrasDeParticipacao() -> void
}

class AdministradorDaComunidade {
    + gerarRelatorios() -> void
    + criarEventos() -> void
    + realizarBackupDeDados() -> void
    + agendarBackup() -> void
    + enviarNotificacoes() -> void
    + buscarEventosQueJaParticipou() -> void
    + manterUsuario() -> void
}

class PatrocinadorEParceiros {
    + promoverAnuncios() -> void
    + obterMetricas() -> void
}

class Visitante {
    + visualizarInformacoesPublicas() -> void
}

class Eventos {
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
    + exibirFormulario() -> void
    + validarFormulario() -> void
    + armazenarInformacao() -> void
    + adicionarParticipantes() -> void
    + adicionarPatrocinadores() -> void
    + notificarParticipantes() -> void
}

class Relatorios {
    - filtro : String
    - formato : String
    - dataDeGeracao : String
    + baixarRelatorioPdf() -> void
    + baixarRelatorioCsv() -> void
    + gerarRelatorio() -> void
    + visualizarRelatorio() -> void
}

class RelatorioEventos {
    - tipo : String
    - data : String
    - participantes : List
    - doacoes : List
    + filtrarEventos() -> void
}

class RelatorioAnuncios {
    - numeroVisualizacoes : int
    - interacoes : int
    - listaDeAnuncios : List
    + calcularEstatisticas() -> void
    + selecionarAnuncios() -> void
    + compararAnuncios() -> void
    + filtrarAnuncios() -> void
    + exibirMetricas() -> void
}

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

class Anuncio {
    - titulo : String
    - descricao : String
    - imagem : String
    - publicoAlvo : String
    - orcamento : float
    - duracao : String
    - status : String
    + criarAnuncio() -> void
    + pagarAnuncio() -> void
    + ativarAnuncio() -> void
    + editarAnuncio() -> void
    + validarInformacoes() -> boolean
}

UsuarioDoSistema <|-- AdministradorDoSistema
UsuarioDoSistema <|-- UsuarioComum
UsuarioComum *-- Perfil : possui
UsuarioComum <|-- MembroDaComunidade
UsuarioComum <|-- AdministradorDaComunidade
UsuarioComum <|-- PatrocinadorEParceiros
Visitante -- UsuarioDoSistema : associado a
UsuarioComum -- Eventos : associado a
Eventos -- Doacao : associado a
Anuncio -- Eventos : associado a
Relatorios -- Eventos : associado a
Relatorios -- Anuncio : associado a

Relatorios <|-- RelatorioEventos
Relatorios <|-- RelatorioAnuncios
Doacao <|-- DoacaoMonetaria
Doacao <|-- DoacaoBens

@enduml
