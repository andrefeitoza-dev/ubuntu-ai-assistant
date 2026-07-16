# UbuntuAI – Architecture Review 1.0

**Versão:** 1.0  
**Data:** Julho de 2026

---

# Objetivo

Este documento registra a primeira revisão completa da arquitetura do UbuntuAI após a consolidação da infraestrutura principal do projeto.

A partir desta versão, o UbuntuAI deixa de ser apenas um protótipo e passa a ser uma plataforma distribuível para automação inteligente de sistemas Ubuntu.

---

# Estado Atual

O projeto encontra-se estável e possui:

- Build reproduzível
- Wheel (.whl)
- Source Distribution (.tar.gz)
- CLI funcional
- SDK reutilizável
- Container de Injeção de Dependências
- Pipeline de execução
- Planejamento determinístico
- Planejamento baseado em IA
- Testes automatizados
- Distribuição via uv tool

---

# Arquitetura Geral

```
Usuário
    │
    ▼
CLI
    │
    ▼
SDK
    │
    ▼
Agent (futuro)
    │
    ▼
Planner
    │
 ┌──┴──────────────┐
 │                 │
 ▼                 ▼
RulePlanner    AIPlanner
                    │
                    ▼
              AIProvider
                    │
                    ▼
             OllamaProvider
                    │
                    ▼
             OllamaService
```

---

# Organização Atual

```
ubuntu_ai/

ai/
cli/
confirmation/
container/
core/
domain/
executor/
explainer/
memory/
pipeline/
planner/
renderer/
services/
tools/
```

Cada módulo possui responsabilidade única.

---

# Princípios Arquiteturais

O UbuntuAI adota os seguintes princípios:

- Clean Architecture (adaptada)
- SOLID
- Dependency Injection
- Composition over Inheritance
- Testabilidade
- Segurança por padrão
- Dry Run antes da execução
- Planejamento antes da execução

---

# Planejamento

O Planner atua como roteador de estratégias.

Fluxo:

```
Planner

↓

RulePlanner

↓

Encontrou regra?

↓

SIM
    retorna Plan

NÃO

↓

AIPlanner

↓

AIProvider

↓

Plan
```

---

# Pipeline

O Pipeline possui responsabilidade exclusiva de orquestrar:

- planejamento
- geração da prévia
- renderização

Nenhuma execução acontece nesta etapa.

---

# Segurança

Toda operação deve seguir:

Objetivo

↓

Plano

↓

Avaliação de risco

↓

Prévia

↓

Confirmação

↓

Execução

A execução direta de comandos sem confirmação não faz parte da arquitetura do UbuntuAI.

---

# Dependency Injection

Toda dependência é construída pelo Container.

O restante da aplicação não conhece implementações concretas.

Isso permite substituir:

- IA
- Serviços
- Ferramentas

sem alterar as regras de negócio.

---

# Inteligência Artificial

A IA nunca conversa diretamente com o restante da aplicação.

Toda comunicação acontece através de:

AIProvider

Isso permite suportar:

- Ollama
- OpenAI
- Claude
- Azure OpenAI
- outros modelos

sem alterar o núcleo.

---

# Distribuição

O projeto já suporta:

- uv build
- uv tool install
- wheel
- source distribution

---

# Qualidade

Estado atual:

- Ruff
- Pytest
- Build reproduzível
- CLI instalada
- SDK funcional

---

# Próxima Milestone

A próxima etapa do UbuntuAI será o desenvolvimento do Agent Runtime.

O objetivo é transformar o UbuntuAI em um agente inteligente especializado em administração de sistemas Ubuntu.

A arquitetura prevista é:

```
Agent Runtime

↓

Session

↓

Context

↓

Planner

↓

Pipeline

↓

Confirmation

↓

Executor

↓

Tools

↓

System
```

---

# Conclusão

A versão 1.0 da arquitetura estabelece a base definitiva do núcleo do UbuntuAI.

As próximas evoluções do projeto deverão preservar esta arquitetura, adicionando novas capacidades sem comprometer os princípios aqui definidos.