# Aplicação da M5.4

Na raiz do repositório:

```bash
unzip -o ~/Downloads/ubuntu-ai-m5.4-self-reflection.zip -d .
uv run ruff check src tests
uv run pytest
```

Resultado de referência da entrega: `223 passed`.

Commit sugerido:

```bash
git add .
git commit -m "feat(reflection): add pre and post execution self reflection"
```
