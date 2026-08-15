# RC1.4 — Logging Foundation

Este bloco introduz uma infraestrutura de logging baseada exclusivamente na
biblioteca padrão do Python.

## Entregas

- configuração validada do runtime de logs;
- formatter padronizado;
- arquivo rotativo por tamanho;
- console opcional;
- serviço central com loggers por componente;
- encerramento explícito dos handlers;
- testes isolados sem integração com módulos de produção.

## Próximo bloco

Integrar `LoggingService` ao `Container` e, gradualmente, ao Planner, Runtime,
Ollama e Executor.
