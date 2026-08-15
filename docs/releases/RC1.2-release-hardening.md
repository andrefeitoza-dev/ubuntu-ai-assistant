# RC1.2 — Release Hardening

## Objetivo

Preparar o Ubuntu AI Assistant para a versão `0.6.0rc1`, consolidando
versionamento, diagnóstico de runtime e tratamento de falhas da CLI.

## Entregas

- versão do pacote alterada para `0.6.0rc1`;
- módulo único de versionamento;
- comando `ubuntu-ai version`;
- opção global `--debug`;
- mensagens operacionais sem traceback no modo normal;
- preservação da exceção original no modo de depuração;
- testes de versão e tratamento de erros.

## Validação

```bash
uv run ruff check src tests
uv run pytest
uv build
ubuntu-ai version
```

O build depende de acesso às dependências declaradas no `build-system`.
