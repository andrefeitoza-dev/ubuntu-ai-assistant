# RC1.6 — UX

## Objetivo

Melhorar a experiência do terminal sem alterar o contrato de execução segura.

## Entregas

- Banner e painéis Rich mais claros.
- Spinners durante planejamento e execução confirmada.
- Tabela de resultados com símbolos visuais e quebra de conteúdo.
- Resumo de benchmark ao final de cada ciclo.
- Configuração de UX pelo `TerminalAppConfig`.
- Integração do `BenchmarkService` ao `TerminalApp` pelo `Container`.
- Testes para o resumo de desempenho e validação da configuração.

## Validação

```bash
uv run ruff check src tests
uv run pytest
ubuntu-ai tui
```
