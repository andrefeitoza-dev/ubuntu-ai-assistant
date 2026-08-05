# RC1.7 — Release Engineering

## Status

Concluída.

## Objetivo

Preparar e publicar a fundação `v0.6.0` do Ubuntu AI Assistant.

## Entregas

- versão promovida para `0.6.0`;
- metadados do pacote revisados;
- instalação local compatível com `pipx install .`;
- README e guia de contribuição atualizados;
- licença MIT preenchida;
- changelog consolidado;
- release notes da v0.6.0;
- testes de metadados e comandos públicos;
- script de verificação de release.

## Critérios de aceite

```bash
uv run ruff check src tests
uv run ruff format --check src tests
uv run pytest
uv build
pipx install --force .
ubuntu-ai version
```

## Tag sugerida

```bash
git tag -a v0.6.0 -m "Ubuntu AI Assistant v0.6.0"
git push origin v0.6.0
```
