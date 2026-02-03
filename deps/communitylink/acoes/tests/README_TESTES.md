# Guia de Testes - Unittest (Django TestCase)

- Models (Acao, Inscricao, Notificacao)
- CRUD de Ações
- Inscrições e Notificações
- Formulários
- Autenticação e Permissões
- Histórico e Perfil

**Tecnologia:** Unittest nativo do Django (django.test.TestCase)

## Resumo de Testes Unitários por Módulo

| Módulo | Testes Unitários |
|--------|------------------|
| **1. Módulo Usuário (Voluntários e Organizadores)** | **76 testes** |
| **2. Módulo Ações Comunitárias** | **62 testes** |
| **3. Módulo Comunicação Básica** | **63 testes** |
| **TOTAL** | **201 testes** |

### Detalhamento por Módulo

**Módulo 1 - Usuário (76 testes)**
- `test_auth.py`: 16 testes (Signup, Signin, Logout)
- `test_forms_auth.py`: 28 testes (Formulários de autenticação e perfil)
- `test_perfil.py`: 21 testes (Model, Signal, View de perfil)
- `test_permissions.py`: 30 testes (Permissões de organizador, voluntário, superuser, anônimo)

**Módulo 2 - Ações Comunitárias (62 testes)**
- `test_forms.py`: 16 testes (Formulário de ação)
- `test_views_acoes.py`: 23 testes (CRUD de ações)
- `test_models.py`: 16 testes (Models Acao, Inscricao, Notificacao)
- `test_historico.py`: 17 testes (Histórico e comentários)

**Módulo 3 - Comunicação Básica (63 testes)**
- `test_views_inscricoes.py`: 41 testes (Inscrições, notificações, cancelamentos)
- Testes de notificações automáticas incluídos

## Estrutura dos Testes

### Arquivos de Teste

```
acoes/tests/
├── test_base.py              # Mixins com fixtures reutilizáveis
├── test_models.py            # Testes dos modelos (23 testes)
├── test_forms.py             # Testes dos formulários (14 testes)
├── test_auth.py              # Testes de autenticação (25 testes)
├── test_perfil.py            # Testes de perfil (21 testes)
├── test_forms_auth.py        # Testes de formulários de auth (38 testes)
├── test_permissions.py       # Testes de permissões (34 testes)
├── test_views_acoes.py       # Testes de views CRUD (28 testes)
├── test_historico.py         # Testes de histórico (19 testes)
└── test_views_inscricoes.py  # Testes de inscrições (51 testes)
```

**Total:** ~253 testes em 10 arquivos

## Como Rodar os Testes

### Todos os testes
```bash
python manage.py test acoes.tests
```

### Com verbosidade
```bash
python manage.py test acoes.tests -v 2
```

### Arquivo específico
```bash
python manage.py test acoes.tests.test_models
python manage.py test acoes.tests.test_forms
python manage.py test acoes.tests.test_views_acoes
```

### Classe específica
```bash
python manage.py test acoes.tests.test_models.TestAcaoModel
```

### Teste específico
```bash
python manage.py test acoes.tests.test_models.TestAcaoModel.test_criar_acao_valida
```

## Coverage (Cobertura de Código)

### Rodar testes com coverage
```bash
coverage run --source='acoes' manage.py test acoes.tests
```

### Ver relatório no terminal
```bash
coverage report
```

### Gerar relatório HTML
```bash
coverage html
```

### Abrir relatório HTML (navegador)
```bash
# Mac/Linux
open htmlcov/index.html

# Windows
start htmlcov/index.html
```

### Arquivo de configuração
O arquivo `.coveragerc` na raiz do projeto configura:
- Source: `acoes`
- Omitir: `tests/`, `migrations/`, `__init__.py`, `admin.py`, `apps.py`
- Relatórios HTML em: `htmlcov/`

## Estrutura dos Mixins (test_base.py)

### Mixins Disponíveis

**UserFixturesMixin:**
- `cls.grupo_organizadores` - Grupo "Organizadores"
- `cls.organizador_user` - Usuário organizador
- `cls.voluntario_user` - Usuário voluntário
- `cls.superuser` - Superusuário

**AcaoFixturesMixin:**
- `cls.acao_futura` - Ação com data futura (+7 dias)
- `cls.acao_passada` - Ação no passado (-7 dias)
- `cls.acao_cheia` - Ação lotada (todas vagas preenchidas)

**InscricaoFixturesMixin:**
- `cls.inscricao_pendente` - Inscrição com status PENDENTE
- `cls.inscricao_aceita` - Inscrição com status ACEITO

**ClientFixturesMixin:**
- `self.client` - Cliente HTTP básico
- `self.client_logged_organizador` - Cliente com organizador logado
- `self.client_logged_voluntario` - Cliente com voluntário logado

**FullFixturesMixin:**
- Combina todos os mixins acima

### Exemplo de Uso

```python
from django.test import TestCase
from .test_base import FullFixturesMixin

class TestMinhaFeature(FullFixturesMixin, TestCase):
    """
    CT-XXX: Descrição do caso de teste
    """

    def test_algo(self):
        """
        CT-XXX.1: Descrição específica
        Resultado Esperado: O que deve acontecer
        """
        # Acessa fixtures via self.*
        self.assertEqual(self.voluntario_user.username, 'voluntario')

        # Usa client autenticado
        response = self.client_logged_organizador.get('/url/')
        self.assertEqual(response.status_code, 200)

        # Usa ações e inscrições
        self.assertTrue(self.acao_futura.vagas_preenchidas == 0)
```

## Padrões de Teste

### Asserções Comuns

```python
# Igualdade
self.assertEqual(a, b)
self.assertNotEqual(a, b)

# Booleanos
self.assertTrue(condition)
self.assertFalse(condition)

# Existência
self.assertIsNone(value)
self.assertIsNotNone(value)

# Contenção
self.assertIn(item, lista)
self.assertNotIn(item, lista)

# Comparação
self.assertGreater(a, b)
self.assertLess(a, b)
self.assertGreaterEqual(a, b)
self.assertLessEqual(a, b)

# Exceções
with self.assertRaises(IntegrityError):
    Model.objects.create(...)

# Existência no banco
self.assertTrue(Model.objects.filter(...).exists())
```

### Testes Parametrizados (subTest)

```python
def test_multiplos_valores(self):
    """Testa múltiplos valores usando subTest"""
    categorias = ['SAUDE', 'EDUCACAO', 'MEIO_AMBIENTE']

    for categoria in categorias:
        with self.subTest(categoria=categoria):
            acao = Acao.objects.create(..., categoria=categoria)
            self.assertEqual(acao.categoria, categoria)
```

### Testes de Views

```python
def test_lista_acoes(self):
    """Testa listagem de ações"""
    url = reverse('acoes:acao_list')
    response = self.client.get(url)

    self.assertEqual(response.status_code, 200)
    self.assertIn(self.acao_futura, response.context['acoes'])
```

### Testes de Formulários

```python
def test_form_valido(self):
    """Testa formulário com dados válidos"""
    data = {
        'titulo': 'Ação Teste',
        'data': (timezone.now() + timedelta(days=7)).strftime('%Y-%m-%dT%H:%M'),
        'local': 'São Paulo',
        'numero_vagas': 10,
        'categoria': 'SAUDE'
    }

    form = AcaoForm(data=data)
    self.assertTrue(form.is_valid())
```
## Comandos Úteis

```bash
# Rodar todos os testes
python manage.py test acoes.tests

# Rodar com coverage
coverage run --source='acoes' manage.py test acoes.tests
coverage report
coverage html

# Rodar testes específicos
python manage.py test acoes.tests.test_models
python manage.py test acoes.tests.test_models.TestAcaoModel
python manage.py test acoes.tests.test_models.TestAcaoModel.test_criar_acao_valida

# Rodar com verbosidade
python manage.py test acoes.tests -v 2

# Rodar em paralelo (mais rápido)
python manage.py test acoes.tests --parallel

# Rodar apenas testes que falharam na última execução
python manage.py test acoes.tests --failed

# Ver detalhes de cada teste
python manage.py test acoes.tests -v 3
```

## Referências

- [Django Testing Documentation](https://docs.djangoproject.com/en/5.2/topics/testing/)
- [Python unittest Documentation](https://docs.python.org/3/library/unittest.html)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)
