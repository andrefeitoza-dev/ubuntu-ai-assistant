# Aplicação — Sprint 5.0

Extraia este pacote na raiz do repositório Ubuntu AI:

```bash
unzip -o ubuntu-ai-s5.0-architectural-consolidation.zip -d .
```

Valide:

```bash
uv run ruff check src tests
uv run pytest
```

Commit sugerido:

```bash
git add .
git commit -m "refactor(core): consolidate AI provider composition"
```
