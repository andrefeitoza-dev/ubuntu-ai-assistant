# Arquitetura do Ubuntu AI Assistant

## Visão geral

```text
Usuário
  │
  ├── CLI / TUI
  │      │
  │      ▼
  │   Agent Loop
  │      │
  │      ▼
  │   Agent Runtime
  │      │
  │      ├── Context + Conversation
  │      ├── Planner
  │      │    ├── Rule Planner
  │      │    └── AI Planner → AI Provider → Ollama
  │      │              ├── Knowledge / RAG
  │      │              └── Learning Context
  │      ├── Reflection
  │      ├── Confirmation
  │      ├── Tool Selection
  │      ├── Skills
  │      ├── Execution Intelligence / Preflight
  │      └── Controlled Execution
  │               │
  │               ▼
  │            Ubuntu
  │
  └── Persistência local
         ├── Memory
         ├── Conversation
         ├── Knowledge
         ├── Semantic Index
         └── Learning
```

## Princípios

- segurança por padrão;
- planejamento antes da execução;
- preview sem efeitos colaterais;
- confirmação explícita;
- políticas e preflight obrigatórios;
- dependências compostas no Container;
- interfaces para provedores e repositórios;
- persistência local e operação offline quando possível;
- testes automatizados em cada subsistema.

## Fronteiras principais

### Apresentação

`cli/` e `tui/` apresentam dados e capturam decisões. Não executam comandos diretamente.

### Orquestração

`agent_loop/`, `agent/` e `pipeline/` coordenam casos de uso e estados.

### Inteligência

`planner/`, `ai/`, `reflection/`, `learning/`, `knowledge/` e `semantic/` produzem decisões e contexto, sem executar alterações diretamente.

### Segurança e execução

`tools/`, `skills/`, `execution_intelligence/` e `execution/` validam e executam planos aprovados.

### Infraestrutura

`services/`, repositórios SQLite, plugins e `container/` implementam detalhes externos e composição.

## Regras de dependência

- UI depende de casos de uso, nunca de SQLite ou shell diretamente.
- Planner depende de serviços de conhecimento e aprendizado, não de bancos concretos.
- Runtime depende de serviços e contratos, com implementações fornecidas pelo Container.
- Plugins recebem API pública limitada, não o Container interno.
- Políticas de segurança não podem ser ignoradas por IA, skill, plugin ou replanejamento.

## Dívida técnica documentada

- reduzir gradualmente o tamanho do Container;
- extrair responsabilidades do AgentRuntime;
- esclarecer a migração entre `executor/` e `execution/`;
- consolidar utilitários SQLite sem introduzir ORM;
- publicar política de compatibilidade do Plugin SDK.
