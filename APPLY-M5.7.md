# Aplicação da M5.7

```bash
unzip -o ubuntu-ai-m5.7-agent-loop.zip -d .
uv run ruff check src tests
uv run pytest
```

Commit sugerido:

```bash
git add .
git commit -m "feat(agent-loop): add iterative planning and safe replanning"
```
