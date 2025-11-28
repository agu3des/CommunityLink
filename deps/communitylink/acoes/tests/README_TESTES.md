# Guia de Testes - Sprint 1

## Status Atual da Implementação

- Models (Acao, Inscricao, Notificacao)
- CRUD de Ações
- Inscrições
- Formulários
- Permissões (cadastro manual via Django Admin)


### 1. Testes de Modelos (100% Prontos)
```bash
pytest acoes/tests/test_models.py -v
```

**Todos os 23 testes devem passar!**

### 2. Testes de Formulários (100% Prontos)
```bash
pytest acoes/tests/test_forms.py -v
```

**Todos os 14 testes devem passar!**

### 3. Testes de Views - Listagem e Detalhes
```bash
# Lista de ações (pública)
pytest acoes/tests/test_views_acoes.py::TestAcaoListView -v

# Detalhes de ação (pública)
pytest acoes/tests/test_views_acoes.py::TestAcaoDetailView -v
```

### 4. Testes de Inscrições (Parcial)
```bash
# Testes básicos de inscrição
pytest acoes/tests/test_views_inscricoes.py::TestAcaoApplyView::test_voluntario_pode_se_inscrever -v
pytest acoes/tests/test_views_inscricoes.py::TestAcaoApplyView::test_inscricao_duplicada_nao_cria_nova -v
```

### Testes que Dependem de Sistema de Permissões Automático

- `test_permissions.py` - TODO (sistema de grupos não implementado automaticamente)
- Testes de criação/edição/deleção que verificam permissões automáticas
- Testes que usam `grupo_organizadores` fixture

## Como Rodar Apenas Testes Funcionais

### Comando Simplificado (Recomendado)
```bash
# Roda apenas models e forms (100% prontos)
pytest acoes/tests/test_models.py acoes/tests/test_forms.py -v
```

### Ver Cobertura dos Testes Funcionais
```bash
pytest acoes/tests/test_models.py acoes/tests/test_forms.py --cov=acoes.models --cov=acoes.forms --cov-report=html
```

## Ajustes Necessários para Rodar Todos os Testes

### 1. Fixtures Problemáticas

Se rodar testes de views e encontrar erro no `grupo_organizadores`, você pode:

**Opção A: Criar o grupo manualmente antes dos testes**
```bash
python manage.py shell
>>> from django.contrib.auth.models import Group
>>> Group.objects.get_or_create(name='Organizadores')
>>> exit()
```

## Workflow Recomendado para Agora

1. **Rode os testes de models e forms**:
```bash
pytest acoes/tests/test_models.py acoes/tests/test_forms.py -v
```

2. **Quando implementar sistema de permissões automático**, rode todos os testes:
```bash
pytest acoes/tests/ -v
```

## Estatísticas

- **Testes 100% prontos**: 37 (models + forms)
- **Testes parcialmente prontos**: 28 (views CRUD - depende de setup manual)
- **Testes para depois**: 55 (permissões + views com auth)
- **Total**: 120 testes

## Próximo Sprint

Quando implementar:
- Sistema de grupos automático (Organizadores)
- Permissões programáticas
- Middleware de autorização

Então rodar:
```bash
pytest acoes/tests/ -v  # Todos os 120 testes!
```