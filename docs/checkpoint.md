# UbuntuAI Development Checkpoint

> Última atualização: 2026-07-26

## Versão do projeto

0.4.x

## Última milestone concluída

✅ M4.4 — Knowledge Engine

## Próxima milestone

➡ M4.5 — Learning Engine

## Estado do projeto

- Código: ✅ implementado
- Ruff: ✅ validado na entrega
- Pytest: ✅ validado na entrega
- Git: ⏳ commit local pendente

## Entregas da M4.4

- SQLiteKnowledgeRepository
- SQLite FTS5
- DocumentExtractor
- DocumentChunker
- KnowledgeEngine
- CLI Knowledge
- Container com backend padrão
- Integração do conhecimento com AIPlanner
- Testes e documentação

## Decisões arquiteturais

- `KnowledgeRepository` continua sendo o contrato central.
- O backend padrão é SQLite, mas pode ser substituído por DI.
- `KnowledgeService` mantém regras de negócio independentes da persistência.
- `KnowledgeEngine` concentra ingestão e manutenção.
- O Planner depende apenas de `KnowledgeService`, nunca de SQLite.
- Embeddings e busca vetorial ficam para evolução posterior.

## Próxima tarefa

Implementar M4.5 — Learning Engine para transformar resultados de execução, correções e feedback em conhecimento persistente controlado.

## Retomada

1. Ler `docs/checkpoint.md`.
2. Ler `docs/project-context.md` quando necessário.
3. Inspecionar apenas módulos afetados.
4. Continuar diretamente pela próxima milestone.
