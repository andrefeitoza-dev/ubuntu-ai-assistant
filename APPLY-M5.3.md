# Aplicação da M5.3

Na raiz do repositório:

```bash
unzip -o ~/Downloads/ubuntu-ai-m5.3-skill-system.zip -d .
uv run ruff check src tests
uv run pytest
```

Commit sugerido:

```bash
git add .
git commit -m "feat(skills): add extensible skill system"
```
