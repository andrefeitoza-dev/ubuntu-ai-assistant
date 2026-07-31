# Aplicação da M5.6

Na raiz do repositório:

```bash
unzip -o ubuntu-ai-m5.6-plugin-sdk.zip -d .
uv run ruff check src tests
uv run pytest
```

Commit sugerido:

```bash
git add .
git commit -m "feat(plugins): add versioned plugin SDK"
```
