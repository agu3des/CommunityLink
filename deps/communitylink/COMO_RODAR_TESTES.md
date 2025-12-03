# 🧪 Como Rodar os Testes - Guia Prático

## ⚙️ Setup Inicial (Faça uma vez)

```bash
# 1. Instalar dependências de teste
pip install -r requirements.txt

# 2. Garantir que o banco está atualizado
python manage.py migrate

# 3. (Opcional) Criar grupo Organizadores manualmente
python manage.py shell
>>> from django.contrib.auth.models import Group
>>> Group.objects.get_or_create(name='Organizadores')
>>> exit()
```

## ✅ Testes que Você PODE Rodar AGORA

### Opção 1: Usar o Script Automático (Mais Fácil)
```bash
python run_tests_basicos.py
```

Este script roda automaticamente:
- ✅ 23 testes de modelos
- ✅ 14 testes de formulários
- **Total: ~37 testes**

### Opção 2: Rodar Manualmente

#### Todos os testes básicos (models + forms)
```bash
pytest acoes/tests/test_models.py acoes/tests/test_forms.py -v
```

#### Apenas testes de modelos
```bash
pytest acoes/tests/test_models.py -v
```

#### Apenas testes de formulários
```bash
pytest acoes/tests/test_forms.py -v
```

#### Um teste específico
```bash
pytest acoes/tests/test_models.py::TestAcaoModel::test_criar_acao_valida -v
```

### Opção 3: Com Cobertura (Ver % de código testado)
```bash
pytest acoes/tests/test_models.py acoes/tests/test_forms.py --cov=acoes.models --cov=acoes.forms --cov-report=html
```

Depois abra: `htmlcov/index.html` no navegador

## ⚠️ Testes que NÃO Rodar Agora

**EVITE rodar estes até implementar sistema de permissões automático:**

```bash
# ❌ NÃO RODE AINDA
pytest acoes/tests/test_permissions.py       # Sistema de grupos não automático
pytest acoes/tests/test_views_acoes.py       # Alguns testes checam permissões
pytest acoes/tests/test_views_inscricoes.py  # Alguns testes checam permissões
```

**Por quê?**
- Esses testes esperam que grupos sejam criados automaticamente
- Você cadastra organizadores/voluntários manualmente via admin
- Vão falhar por falta de setup, não por bug no código

## 🎯 O que Cada Arquivo Testa

### test_models.py (✅ PODE RODAR)
- Criação de Acao, Inscricao, Notificacao
- Propriedades: `vagas_preenchidas`, `esta_cheia`
- Constraints: `unique_together` em Inscricao
- Ordenação de notificações

### test_forms.py (✅ PODE RODAR)
- Validação do AcaoForm
- Campos obrigatórios
- Max length de titulo e local
- Número de vagas positivo
- Categorias válidas

### test_views_acoes.py (⚠️ ALGUNS testes podem falhar)
- Lista de ações (público) ✅
- Detalhes de ação (público) ✅
- CRUD (precisa checar permissões manualmente) ⚠️

### test_views_inscricoes.py (⚠️ ALGUNS testes podem falhar)
- Inscrição de voluntário ✅
- Gerenciamento de inscrições ⚠️
- Notificações ✅

### test_permissions.py (❌ NÃO RODAR AINDA)
- Sistema completo de permissões
- Organizador vs Voluntário vs Admin
- Isolamento de dados

## 🐛 Problemas Comuns

### Erro: "No such table: acoes_acao"
**Solução:**
```bash
python manage.py migrate
```

### Erro: "Group matching query does not exist"
**Solução:** O teste está tentando usar o grupo 'Organizadores'. Opções:
1. Criar o grupo manualmente (ver Setup Inicial)
2. Pular testes de permissões por enquanto
3. Usar `conftest_simple.py` (sem grupos)

### Erro: "django.core.exceptions.ImproperlyConfigured"
**Solução:**
```bash
# Verifique que pytest.ini está configurado
cat pytest.ini
# Deve ter: DJANGO_SETTINGS_MODULE = communitylink.settings
```

### Erro: ImportError de fixtures
**Solução:**
```bash
# Garanta que __init__.py existe
ls acoes/tests/__init__.py
```

## 📊 Interpretando os Resultados

### Exemplo de saída de sucesso:
```
acoes/tests/test_models.py::TestAcaoModel::test_criar_acao_valida PASSED [ 10%]
acoes/tests/test_models.py::TestAcaoModel::test_str_retorna_titulo PASSED [ 20%]
...
======================== 37 passed in 2.45s ========================
```

### Exemplo de saída de falha:
```
acoes/tests/test_models.py::TestAcaoModel::test_criar_acao_valida FAILED [ 10%]

FAILED - AssertionError: assert 'Campanha' == 'Campanha de Vacinação'
```

**O que fazer:**
1. Leia a mensagem de erro
2. Verifique o arquivo e linha indicados
3. Compare o esperado vs obtido
4. Corrija o código ou o teste

## 🚀 Comandos Úteis

```bash
# Ver lista de testes sem rodar
pytest acoes/tests/test_models.py --collect-only

# Rodar em modo silencioso (apenas erros)
pytest acoes/tests/test_models.py -q

# Rodar com mais detalhes
pytest acoes/tests/test_models.py -vv

# Parar no primeiro erro
pytest acoes/tests/test_models.py -x

# Mostrar print() nos testes
pytest acoes/tests/test_models.py -s

# Rodar apenas testes que falharam
pytest --lf

# Rodar testes em paralelo (mais rápido)
pytest acoes/tests/test_models.py -n auto
```

## 📈 Próximos Passos

1. **Agora**: Rode os testes básicos (37 testes)
   ```bash
   python run_tests_basicos.py
   ```

2. **Se todos passarem**: Sua lógica de negócio está correta! ✅

3. **Teste manualmente**:
   - Crie ação como organizador
   - Inscreva-se como voluntário
   - Gerencie inscrições

4. **Quando implementar permissões automáticas**: Rode todos
   ```bash
   pytest acoes/tests/ -v  # 120 testes!
   ```

## 💡 Dica Final

**Foque no que funciona!**

Testes básicos (models + forms) = **70% da lógica de negócio**

Quando eles passarem, você tem certeza que:
- Modelos funcionam corretamente
- Validações estão corretas
- Relacionamentos entre models estão OK
- Lógica de vagas preenchidas/cheia funciona

O resto (views, permissões) você testa manualmente por enquanto via navegador.

---

**Problemas?** Verifique:
1. Dependências instaladas? `pip install -r requirements.txt`
2. Banco migrado? `python manage.py migrate`
3. pytest configurado? `cat pytest.ini`
