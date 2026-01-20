#  Rodando Testes no Docker - Guia Completo

## Onde Rodar os Comandos

**No seu terminal (Windows/PowerShell ou Git Bash)**, na pasta:
```
C:\Users\Angelica\Documents\GitHub\CommunityLink\deps\communitylink\
```

## Comandos para Rodar AGORA

### Método 1: Serviço Dedicado (Mais Rápido) RECOMENDADO

```bash
# Rode todos os testes
docker-compose run --rm tests
```

**O que acontece:**
- Container inicia
- Roda testes usando Django unittest (manage.py test)
- Gera relatórios de cobertura
- Container é removido automaticamente (--rm)

### Método 2: Usando o Container Web

```bash
# 1. Garanta que o web está rodando
docker-compose up -d web

# 2. Execute os testes no container
docker-compose exec web python manage.py test acoes.tests -v 2
```

### Método 3: Entrar no Container (Para Explorar)

```bash
# 1. Entre no container
docker-compose exec web bash

# 2. Dentro do container, rode:
python manage.py test acoes.tests.test_models -v 2
python manage.py test acoes.tests.test_forms -v 2
python manage.py test acoes.tests

# 3. Saia
exit
```

## Comandos por Necessidade

### Rodar Testes Específicos

```bash
# Apenas modelos
docker-compose exec web python manage.py test acoes.tests.test_models

# Apenas formulários
docker-compose exec web python manage.py test acoes.tests.test_forms

# Um teste específico
docker-compose exec web python manage.py test acoes.tests.test_models.TestAcaoModel.test_criar_acao_valida

# Uma classe de testes
docker-compose exec web python manage.py test acoes.tests.test_models.TestAcaoModel
```

### Rodar com Cobertura

```bash
# Com relatório HTML
docker-compose exec web sh -c "coverage run --source='acoes' manage.py test acoes.tests && coverage html"

# Ver o relatório (arquivo será criado em htmlcov/index.html)
# Abra no navegador: C:\Users\Angelica\Documents\GitHub\CommunityLink\deps\communitylink\htmlcov\index.html
```

### Rodar Todos os Testes

```bash
# Roda todos os testes com cobertura
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
docker-compose exec web python manage.py test acoes.tests.test_models
```

### Erro: "coverage: command not found"
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
**Solução:** Verifique o settings.py
```bash
# Verifique o settings.py
docker-compose exec web cat communitylink/settings.py

# Rode com variável explícita se necessário
docker-compose exec web bash -c "DJANGO_SETTINGS_MODULE=communitylink.settings python manage.py test acoes.tests"
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
test_criar_acao_valida (acoes.tests.test_models.TestAcaoModel) ... ok
test_str_retorna_titulo (acoes.tests.test_models.TestAcaoModel) ... ok
...
----------------------------------------------------------------------
Ran 253 tests in 12.345s

OK
```

### Falha
```
test_criar_acao_valida (acoes.tests.test_models.TestAcaoModel) ... FAIL

======================================================================
FAIL: test_criar_acao_valida (acoes.tests.test_models.TestAcaoModel)
----------------------------------------------------------------------
AssertionError: ...
```

**O que fazer:**
1. Leia a mensagem de erro completa
2. Use `-v 3` para mais detalhes:
   ```bash
   docker-compose exec web python manage.py test acoes.tests.test_models.TestAcaoModel.test_criar_acao_valida -v 3
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

3. **Rode os testes frequentemente**
   ```bash
   docker-compose exec web python manage.py test acoes.tests
   ```

4. **Se tudo passar, commit!**

5. **Ao final do dia**
   ```bash
   docker-compose down
   ```

### Antes de Commitar

```bash
# 1. Rode os testes
docker-compose exec web python manage.py test acoes.tests

# 2. Se passou, veja cobertura
docker-compose exec web sh -c "coverage run --source='acoes' manage.py test acoes.tests && coverage report"

# 3. Se cobertura > 80%, está ok!
```

## Resumo dos Comandos

| O que fazer | Comando |
|-------------|---------|
| **Rodar testes** | `docker-compose exec web python manage.py test acoes.tests` |
| Rodar todos os testes com cobertura | `docker-compose run --rm tests` |
| Rodar teste específico | `docker-compose exec web python manage.py test acoes.tests.test_models` |
| Ver cobertura | `docker-compose exec web sh -c "coverage run --source='acoes' manage.py test acoes.tests && coverage report"` |
| Entrar no container | `docker-compose exec web bash` |
| Ver logs | `docker-compose logs web` |
| Rodar migrations | `docker-compose exec web python manage.py migrate` |

---