# Aplicação da M6.0 — Terminal UI

Na raiz do projeto, extraia este pacote preservando os caminhos:

```bash
unzip -o ubuntu-ai-m6.0-terminal-ui.zip -d .
```

Valide:

```bash
uv run ruff check src tests
uv run pytest
```

Resultado de referência da suíte:

```text
247 passed
```

Inicie a interface:

```bash
ubuntu-ai tui
```

Commit sugerido:

```bash
git add .
git commit -m "feat(tui): add interactive terminal interface"
```
