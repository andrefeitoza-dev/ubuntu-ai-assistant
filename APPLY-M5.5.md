# Aplicação da M5.5

Na raiz do projeto:

```bash
unzip -o ~/Downloads/ubuntu-ai-m5.5-semantic-knowledge-local-rag.zip -d .
uv run ruff check src tests
uv run pytest
```

Resultado esperado dos testes:

```text
229 passed
```

Commit sugerido:

```bash
git add .
git commit -m "feat(knowledge): add local semantic retrieval and RAG"
```
