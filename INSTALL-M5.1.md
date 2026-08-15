# Instalação — M5.1 Tool Selection Engine

Na raiz do repositório, extraia este pacote preservando a estrutura de diretórios.

```bash
unzip -o ubuntu-ai-m5.1-tool-selection-engine.zip -d .
```

Valide:

```bash
uv run ruff check src tests
uv run pytest
```

Resultado obtido durante a preparação do pacote:

```text
205 passed
```

Commit sugerido:

```bash
git add .
git commit -m "feat(tools): implement tool selection engine"
```
