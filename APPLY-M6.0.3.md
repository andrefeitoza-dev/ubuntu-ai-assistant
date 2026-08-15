# Aplicação da M6.0.3

Na raiz do projeto:

```bash
unzip -o ~/Downloads/ubuntu-ai-m6.0.3-shell-skill-stabilization.zip -d .
uv run ruff check src tests
uv run pytest
```

Teste funcional:

```bash
ubuntu-ai tui
```

Objetivo sugerido:

```text
mostrar o diretório atual
```

Após confirmar, o comando `pwd` deve ser executado normalmente.

Commit sugerido:

```bash
git add .
git commit -m "fix(skills): stabilize shell executable validation"
```
