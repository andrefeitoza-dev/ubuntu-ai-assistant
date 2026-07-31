# UbuntuAI Development Checkpoint

> Última atualização: 2026-07-31

## Versão do projeto

0.4.x

## Última milestone concluída

✅ M4.5 — Learning Engine

## Próxima milestone

➡ M4.6 — Autonomous Decision Engine

## Estado do projeto

- Código: ✅ implementado
- Ruff: ✅ validado na entrega
- Pytest: ✅ validado na entrega
- Git: ⏳ commit local pendente

## Entregas da M4.5

- LearningPattern e LearningRecommendation
- SQLiteLearningRepository
- LearningService e LearningEngine
- Aprendizado automático após execuções
- Recomendações por similaridade e confiança
- Integração com AIPlanner
- Feedback positivo e negativo
- Testes e documentação

## Decisões arquiteturais

- `LearningRepository` é o contrato de persistência do aprendizado.
- O backend padrão é SQLite e pode ser substituído por DI.
- O runtime observa resultados; não altera políticas de segurança.
- O Planner depende apenas de `LearningService`, nunca de SQLite.
- Recomendações são contexto, não autorização de execução.
- Embeddings ficam para evolução posterior.

## Próxima tarefa

Implementar M4.6 — Autonomous Decision Engine usando memória, conhecimento e aprendizado sob políticas controladas.

## Retomada

1. Ler `docs/checkpoint.md`.
2. Ler `docs/project-context.md` quando necessário.
3. Inspecionar apenas módulos afetados.
4. Continuar diretamente pela próxima milestone.

## Sprint 5.0 — Consolidação arquitetural

- Auditoria concluiu que Brain facade e Result genérico seriam abstrações prematuras.
- Adicionado registro configurável de provedores de IA.
- Container ganhou seleção de provider e recomposição segura via `reset()`.
- Compatibilidade com Ollama e fluxo atual preservada.
