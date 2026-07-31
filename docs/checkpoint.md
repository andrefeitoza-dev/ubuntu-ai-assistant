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

## M5.1 — Tool Selection Engine

- Capacidades selecionadas por executável, intenção, prioridade e aprendizado.
- `PlanStep.tool_name` preserva a ferramenta escolhida até a execução.

## M5.2 — Execution Intelligence

- Discovery e preflight verificam disponibilidade, dependências, versão e elevação.
- Etapas incompatíveis são bloqueadas antes do executor.

## M5.3 — Skill System

- Última milestone concluída: ✅ M5.3 — Skill System.
- Skills registráveis passam a fornecer as capacidades do agente.
- `SkillManager` prepara e valida etapas antes do preflight.
- Skills nativas agrupam Apt/Snap, systemd, Docker, Git, Python, SSH e Shell.
- Próxima milestone: ➡ M5.4 — Self Reflection.

## M5.4 — Self Reflection

- Última milestone concluída: ✅ M5.4 — Self Reflection.
- Reflexão pré-execução avalia coerência, redundância, seleção de ferramentas e risco.
- Achados críticos bloqueiam a execução sem contornar confirmação ou preflight.
- Reflexão pós-execução diagnostica sucesso, bloqueio, falha e comandos indisponíveis.
- Relatórios estruturados ficam disponíveis no `AgentRuntime` e no histórico da sessão.
- Próxima milestone: ➡ M5.5 — Semantic Knowledge / Local RAG.

## M5.5 — Semantic Knowledge / Local RAG

- Última milestone concluída: ✅ M5.5 — Semantic Knowledge / Local RAG.
- Embeddings locais determinísticos adicionados sem dependências externas.
- Vetores persistidos no mesmo banco SQLite da base de conhecimento.
- Recuperação híbrida combina FTS5 e similaridade semântica.
- `RAGContextBuilder` injeta trechos relevantes e suas fontes no `AIPlanner`.
- Índice semântico é sincronizado automaticamente com alterações dos documentos.
- Próxima milestone: ➡ M5.6 — Plugin SDK.

## M5.6 — Plugin SDK

- Última milestone concluída: ✅ M5.6 — Plugin SDK.
- API pública v1 para plugins e manifesto TOML/JSON.
- Loader valida compatibilidade e permissões antes da inicialização.
- PluginManager oferece descoberta, instalação com rollback e remoção.
- Plugins podem fornecer Skills sem acesso direto ao Runtime interno.
- A política atual é uma barreira de capacidades, não isolamento de processo.
- Próxima milestone: ➡ M5.7 — Agent Loop.
