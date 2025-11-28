# 🚀 COMECE AQUI - Rodando Testes

## 📍 Você Está Usando: DOCKER

### 1️⃣ Abra o Terminal na Pasta do Projeto

```
C:\Users\Angelica\Documents\GitHub\CommunityLink\deps\communitylink\
```

### 2️⃣ Rode Este Comando:

```bash
docker-compose run --rm tests-basic
```

### 3️⃣ O que Vai Acontecer?

```
✅ 37 testes vão rodar (models + forms)
⏱️  Leva ~5-10 segundos
📊 Mostra quantos passaram/falharam
```

### 4️⃣ Se Todos Passarem ✅

**Parabéns!** Sua lógica de negócio está correta:
- ✅ Modelos funcionando
- ✅ Validações OK
- ✅ Relacionamentos OK
- ✅ Formulários validando

### 5️⃣ Se Algum Falhar ❌

**Não se preocupe!** Pode ser:
1. Banco não migrado → rode: `docker-compose exec web python manage.py migrate`
2. Container não rodando → rode: `docker-compose up -d web`
3. Bug real no código → analise a mensagem de erro

---

## 🔥 Comando Único

```bash
docker-compose run --rm tests-basic
```

**Isso é tudo!** 🎉

---

## 📚 Quer Mais Detalhes?

- **Docker**: Veja `TESTES_DOCKER.md`
- **Geral**: Veja `COMO_RODAR_TESTES.md`
- **Detalhes dos Testes**: Veja `acoes/tests/README_TESTES.md`