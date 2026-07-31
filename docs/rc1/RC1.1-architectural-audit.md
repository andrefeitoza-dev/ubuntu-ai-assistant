# RC1.1 — Auditoria Arquitetural

**Projeto:** Ubuntu AI Assistant  
**Alvo de release:** v0.6.0 RC1  
**Data:** 31 de julho de 2026

## Resumo executivo

A base está funcional e madura o bastante para entrar em estabilização de release. A reconstrução auditada contém 151 arquivos Python em `src`, 130 arquivos Python em `tests` e uma suíte com **266 testes aprovados**.

Foi identificado **um ciclo entre pacotes de primeiro nível** (`agent → pipeline → planner → ai → context → agent`). Ele não impede a execução atual, mas deve ser reduzido de forma incremental. O fluxo completo TUI → planejamento → confirmação → preflight → execução → memória foi validado no ambiente do usuário.

A recomendação é **não realizar uma reorganização ampla de diretórios antes da RC1**. Os riscos relevantes podem ser tratados de forma incremental e compatível.

## Pontos fortes confirmados

- Separação entre domínio, planejamento, execução, persistência e apresentação.
- Injeção de dependências centralizada.
- Provedor de IA abstraído e substituível.
- Confirmação humana obrigatória antes da execução.
- Políticas, preflight, skills e reflexão preservados no caminho de execução.
- Persistência local independente de serviços externos.
- Suíte de regressão ampla e rápida.
- Ausência de falhas de importação ou ciclos que impeçam a inicialização.

## Achados prioritários

### P0 — Nenhum bloqueador arquitetural aberto

Os bugs encontrados durante a validação da TUI foram corrigidos nas fronteiras apropriadas: confiabilidade do Ollama, validação da skill shell e normalização de `Path` antes do SQLite.

### P1 — ciclo entre pacotes de orquestração e inteligência

A análise de imports identificou o ciclo:

```text
agent → pipeline → planner → ai → context → agent
```

A principal causa é o compartilhamento de modelos e serviços entre pacotes de orquestração. O ciclo ainda não causa falha de importação, porém dificulta evolução e testes isolados.

**Ação recomendada na Fase 7:** mover contratos compartilhados (`ContextSnapshot`, resultados e protocolos) para uma camada neutra de aplicação ou domínio, sem migrar implementações em massa.

### P1 — `Container` concentra composição demais

`src/ubuntu_ai/container/container.py` possui aproximadamente 486 linhas e conhece quase todos os subsistemas. Isso não quebra o produto, mas aumenta o custo de manutenção e o risco de conflitos.

**Ação recomendada após a RC1:** dividir a composição em módulos internos, por exemplo `AIComposition`, `PersistenceComposition`, `AgentComposition` e `UIComposition`, mantendo `Container` como fachada pública.

### P1 — `AgentRuntime` acumula responsabilidades

`src/ubuntu_ai/agent/runtime.py` possui aproximadamente 352 linhas e coordena contexto, conversa, confirmação, execução, memória, aprendizado e reflexão.

**Ação recomendada na Fase 7:** extrair colaboradores de aplicação, sem mudar a API pública:

- `ExecutionCoordinator`;
- `ExecutionRecorder`;
- `PostExecutionProcessor`.

### P1 — coexistência de `execution/` e `executor/`

Os dois pacotes têm responsabilidades diferentes hoje:

- `executor/`: preview e componentes legados;
- `execution/`: execução controlada real, política e relatórios.

A nomenclatura é ambígua, mas uma renomeação agora quebraria muitos imports.

**Decisão RC1:** preservar ambos. Marcar componentes legados e planejar migração compatível para uma versão posterior.

### P1 — versão do pacote ainda está em `0.1.0`

O `pyproject.toml` não representa o estágio atual do produto.

**Ação recomendada para RC1:** atualizar para `0.6.0rc1` somente no pacote de release, junto com changelog e tag.

### P1 — documentação principal estava desatualizada

O README estava vazio, o diagrama em `docs/architecture.md` descrevia apenas o núcleo inicial e o roadmap ainda marcava componentes concluídos como pendentes.

**Correção incluída neste pacote:** README, arquitetura, roadmap, changelog e ADR de estabilização.

### P2 — repositórios SQLite grandes e repetitivos

Há repetição de conexão, criação de schema e serialização entre memória, conhecimento, conversa, aprendizado e semântica.

**Ação recomendada após a RC1:** criar utilitários pequenos para conexão e migração. Não introduzir ORM agora.

### P2 — observabilidade ainda é parcial

O comando `diagnose-ai` resolve o diagnóstico do provedor, mas ainda faltam logs estruturados para execução completa.

**Ação recomendada na Fase 7:** eventos estruturados com correlação por sessão e iteração, mantendo saída Rich separada da telemetria.

### P2 — política de compatibilidade de plugins precisa ser publicada

A API de plugins está versionada, mas a política de estabilidade e depreciação ainda deve ser documentada antes de plugins de terceiros.

## Decisões da auditoria

1. Não realizar reorganização em massa antes da RC1.
2. Não introduzir ORM, framework de eventos ou fachada `Brain` nesta etapa.
3. Manter APIs públicas e imports existentes.
4. Tratar `Container` e `AgentRuntime` por extrações incrementais na Fase 7.
5. Fechar a RC1 com documentação, cenários de aceitação, build e versão coerente.

## Critérios para v0.6.0 RC1

- `ruff check src tests` aprovado;
- suíte completa do Pytest aprovada;
- `uv build` aprovado;
- `ubuntu-ai doctor` aprovado;
- `ubuntu-ai diagnose-ai` aprovado;
- cenário TUI `mostrar o diretório atual` aprovado;
- cenários somente leitura aprovados;
- documentação principal atualizada;
- versão ajustada para `0.6.0rc1`;
- tag de release criada somente após validação local.

## Próxima entrega recomendada

**RC1.2 — Release Hardening**

- atualizar versão;
- adicionar comando `version`;
- criar testes de aceitação de CLI/TUI sem efeitos destrutivos;
- revisar tratamento de exceções na CLI;
- executar build e validar instalação via `pipx` ou `uv tool`.
