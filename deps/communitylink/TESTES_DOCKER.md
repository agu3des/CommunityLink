#  Rodando Testes no Docker - Guia Completo

## Onde Rodar os Comandos

**No seu terminal (Windows/PowerShell ou Git Bash)**, na pasta:
```
C:\Users\Angelica\Documents\GitHub\CommunityLink\deps\communitylink\
```

## Comandos para Rodar AGORA

### Método 1: Serviço Dedicado (Mais Rápido) RECOMENDADO

```bash
# Rode apenas testes básicos (models + forms)
docker-compose run --rm tests-basic
```

**O que acontece:**
- Container inicia
- Roda pytest nos arquivos test_models.py e test_forms.py
- Mostra resultados
- Container é removido automaticamente (--rm)

### Método 2: Usando o Container Web

```bash
# 1. Garanta que o web está rodando
docker-compose up -d web

# 2. Execute os testes no container
docker-compose exec web pytest acoes/tests/test_models.py acoes/tests/test_forms.py -v
```

### Método 3: Entrar no Container (Para Explorar)

```bash
# 1. Entre no container
docker-compose exec web bash

# 2. Dentro do container, rode:
pytest acoes/tests/test_models.py -v
pytest acoes/tests/test_forms.py -v
python run_tests_basicos.py

# 3. Saia
exit
```

## Comandos por Necessidade

### Rodar Testes Específicos

```bash
# Apenas modelos
docker-compose exec web pytest acoes/tests/test_models.py -v

# Apenas formulários
docker-compose exec web pytest acoes/tests/test_forms.py -v

# Um teste específico
docker-compose exec web pytest acoes/tests/test_models.py::TestAcaoModel::test_criar_acao_valida -v

# Uma classe de testes
docker-compose exec web pytest acoes/tests/test_models.py::TestAcaoModel -v
```

### Rodar com Cobertura

```bash
# Com relatório HTML
docker-compose exec web pytest acoes/tests/test_models.py acoes/tests/test_forms.py --cov=acoes --cov-report=html

# Ver o relatório (arquivo será criado em htmlcov/index.html)
# Abra no navegador: C:\Users\Angelica\Documents\GitHub\CommunityLink\deps\communitylink\htmlcov\index.html
```

### Rodar Todos os Testes (Quando Implementar Permissões)

```bash
# Este vai tentar rodar TODOS os 120 testes
docker-compose run --rm tests
```

## Comandos Úteis Docker

### Gerenciamento de Containers

```bash
# Ver containers rodando
docker-compose ps

# Iniciar todos os serviços
docker-compose up -d

# Parar todos os serviços
docker-compose down

# Reiniciar o serviço web
docker-compose restart web

# Ver logs do web
docker-compose logs web

# Ver logs em tempo real
docker-compose logs -f web
```

### Comandos Django no Docker

```bash
# Migrations
docker-compose exec web python manage.py migrate

# Criar superuser
docker-compose exec web python manage.py createsuperuser

# Shell Django
docker-compose exec web python manage.py shell

# Coletar arquivos estáticos
docker-compose exec web python manage.py collectstatic
```

##  Troubleshooting

### Erro: "Cannot connect to the Docker daemon"
**Solução:** Docker Desktop não está rodando
```bash
# Inicie o Docker Desktop e aguarde inicializar
```

### Erro: "service 'web' is not running"
**Solução:** Container não está ativo
```bash
# Inicie o serviço
docker-compose up -d web

# Tente novamente
docker-compose exec web pytest acoes/tests/test_models.py -v
```

### Erro: "No such file or directory: pytest"
**Solução:** Dependências não instaladas no container
```bash
# Reconstrua a imagem
docker-compose build web

# Ou entre no container e instale manualmente
docker-compose exec web bash
pip install -r requirements.txt
exit
```

### Erro: "django.core.exceptions.ImproperlyConfigured"
**Solução:** Variável de ambiente DJANGO_SETTINGS_MODULE
```bash
# Verifique o pytest.ini
docker-compose exec web cat pytest.ini

# Ou rode com variável explícita
docker-compose exec web bash -c "DJANGO_SETTINGS_MODULE=communitylink.settings pytest acoes/tests/test_models.py -v"
```

### Erro: "No such table: acoes_acao"
**Solução:** Banco não está migrado
```bash
# Rode as migrations
docker-compose exec web python manage.py migrate
```

### Erro: Testes falhando com problemas de timezone
**Solução:** Configure USE_TZ no settings
```bash
# Verifique o settings.py
docker-compose exec web cat communitylink/settings.py | grep USE_TZ

# Deve ter: USE_TZ = True
```

##  Interpretando Resultados

### Sucesso 
```
acoes/tests/test_models.py::TestAcaoModel::test_criar_acao_valida PASSED [ 10%]
acoes/tests/test_models.py::TestAcaoModel::test_str_retorna_titulo PASSED [ 20%]
...
======================== 37 passed in 2.45s ========================
```

### Falha
```
acoes/tests/test_models.py::TestAcaoModel::test_criar_acao_valida FAILED [ 10%]

FAILED acoes/tests/test_models.py::TestAcaoModel::test_criar_acao_valida - AssertionError: ...
```

**O que fazer:**
1. Leia a mensagem de erro completa
2. Use `-vv` para mais detalhes:
   ```bash
   docker-compose exec web pytest acoes/tests/test_models.py::TestAcaoModel::test_criar_acao_valida -vv
   ```
3. Entre no container para investigar:
   ```bash
   docker-compose exec web bash
   python manage.py shell
   # Teste manualmente o código
   ```

##  Workflow Recomendado

### Desenvolvimento Diário

1. **Inicie os serviços**
   ```bash
   docker-compose up -d
   ```

2. **Trabalhe no código normalmente**

3. **Rode os testes básicos frequentemente**
   ```bash
   docker-compose run --rm tests-basic
   ```

4. **Se tudo passar, commit!**

5. **Ao final do dia**
   ```bash
   docker-compose down
   ```

### Antes de Commitar

```bash
# 1. Rode os testes
docker-compose run --rm tests-basic

# 2. Se passou, veja cobertura
docker-compose exec web pytest acoes/tests/test_models.py acoes/tests/test_forms.py --cov=acoes --cov-report=term

# 3. Se cobertura > 80%, está ok!
```

## Aliases Úteis (Opcional)

Adicione ao seu `.bashrc` ou `.zshrc` (se usar Linux/Mac) ou crie um script .bat (Windows):

```bash
# Aliases para facilitar
alias dtest='docker-compose run --rm tests-basic'
alias dtest-all='docker-compose run --rm tests'
alias dshell='docker-compose exec web python manage.py shell'
alias dmigrate='docker-compose exec web python manage.py migrate'
```

**No Windows**, crie um arquivo `test.bat`:
```batch
@echo off
docker-compose run --rm tests-basic
```

Depois rode apenas:
```bash
test.bat
```

## Comando Mais Simples Possível

**Para rodar os testes básicos agora:**

```bash
docker-compose run --rm tests-basic
```

**Isso é tudo que você precisa!** 

---

## Resumo dos Comandos

| O que fazer | Comando |
|-------------|---------|
| **Rodar testes básicos** | `docker-compose run --rm tests-basic` |
| Rodar todos os testes | `docker-compose run --rm tests` |
| Rodar teste específico | `docker-compose exec web pytest acoes/tests/test_models.py -v` |
| Ver cobertura | `docker-compose exec web pytest acoes/tests/test_models.py acoes/tests/test_forms.py --cov=acoes` |
| Entrar no container | `docker-compose exec web bash` |
| Ver logs | `docker-compose logs web` |
| Rodar migrations | `docker-compose exec web python manage.py migrate` |

---

**Dúvidas?** Comece com:
```bash
docker-compose run --rm tests-basic
```