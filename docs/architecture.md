# Ubuntu AI Assistant Architecture

**Versão:** 1.1  
**Status:** Em desenvolvimento  
**Arquitetura:** Clean Architecture + SOLID + Strategy + Dependency Injection

---

# Visão Geral

O Ubuntu AI Assistant é um assistente inteligente para administração de sistemas Ubuntu utilizando Inteligência Artificial Local (LLM) e planejamento seguro de execução.

Seu objetivo é permitir que o usuário interaja com o sistema operacional utilizando linguagem natural, mantendo segurança, previsibilidade e transparência durante todo o processo.

A arquitetura foi projetada para ser modular, extensível e independente da tecnologia utilizada pelo modelo de IA.

---

# Objetivos Arquiteturais

A arquitetura possui os seguintes objetivos:

- separação clara de responsabilidades;
- baixo acoplamento entre componentes;
- alta coesão;
- fácil manutenção;
- fácil evolução;
- suporte a múltiplos planejadores;
- suporte a múltiplos modelos de IA;
- execução segura baseada em planos;
- compatibilidade com ambientes locais e remotos.

---

# Componentes

## CLI / TUI

Responsável pela interação com o usuário.

Disponibiliza:

- comandos CLI;
- interface conversacional (TUI);
- visualização de planos;
- confirmação de execução;
- apresentação dos resultados.

---

## Agent Runtime

Responsável por coordenar todo o fluxo de execução.

Controla:

- contexto;
- planejamento;
- execução;
- reflexão;
- aprendizagem.

---

## Context Engine

Obtém informações relevantes do ambiente.

Exemplos:

- diretório atual;
- projeto ativo;
- sistema operacional;
- recursos disponíveis;
- contexto remoto.

---

## Intent Analyzer

Interpreta a solicitação do usuário.

Extrai:

- categoria;
- objetivo;
- entidades;
- nível de confiança.

---

# Planner

O Planner é o orquestrador responsável por selecionar a estratégia adequada para criação de um plano.

Ele delega o planejamento para um dos componentes especializados:

- BuiltinPlanner
- RulePlanner
- AIPlanner

---

## BuiltinPlanner

Responsável por comandos determinísticos do sistema operacional.

Não utiliza IA.

Gera diretamente objetos `Plan`.

Exemplos:

- pwd
- ls
- df
- free
- ip
- uname
- git status
- git branch

Objetivo principal:

reduzir a latência para operações simples.

---

## RulePlanner

Responsável por planos conhecidos compostos por múltiplas etapas.

Exemplos:

- instalar Docker;
- criar ambiente Python;
- instalar PostgreSQL;
- instalar Kubernetes.

Todos os planos são determinísticos.

---

## AIPlanner

Responsável por tarefas abertas que exigem raciocínio.

Exemplos:

- análise de projetos;
- planejamento complexo;
- arquitetura;
- automações;
- explicações.

Utiliza modelos locais através do Ollama.

---

## Tool Selection

Seleciona automaticamente as ferramentas necessárias para executar o plano.

Exemplos:

- Shell
- Git
- Docker
- Python
- SSH
- Remote Execution

---

## Executor

Executa cada etapa do plano.

Responsável por:

- execução segura;
- coleta do stdout;
- coleta do stderr;
- tempo de execução;
- códigos de retorno.

---

## Reflection

Analisa o resultado da execução.

Pode:

- identificar falhas;
- sugerir correções;
- acionar recuperação.

---

## Learning

Registra aprendizados obtidos durante a execução.

Permite evolução contínua do assistente.

---

## Memory

Armazena conhecimento persistente.

Exemplos:

- histórico;
- preferências;
- projetos;
- contexto recorrente.

---

## Response Formatter

Converte os resultados da execução em respostas amigáveis.

Exemplo:

Ao invés de apenas:

```
Comando executado com sucesso.
```

Pode apresentar:

```
Diretório atual

/home/usuario/projeto
```

ou

```
Uso de Disco

Total: 512 GB

Livre: 280 GB

Uso: 45%
```

Esse componente melhora significativamente a experiência do usuário.

---

# Fluxo de Execução

```text
Usuário
    │
    ▼
CLI / TUI
    │
    ▼
Agent Runtime
    │
    ▼
Context Engine
    │
    ▼
Intent Analyzer
    │
    ▼
Planner
    │
 ┌────────────┬────────────┬────────────┐
 │            │            │
 ▼            ▼            ▼
Builtin     Rule        AI
Planner    Planner     Planner
 │            │            │
 └────────────┴────────────┘
              │
              ▼
       Tool Selection
              │
              ▼
          Executor
              │
              ▼
         Reflection
              │
              ▼
          Learning
              │
              ▼
           Memory
              │
              ▼
    Response Formatter
              │
              ▼
          CLI / TUI
```

---

# Princípios Arquiteturais

A arquitetura segue os princípios:

- Clean Architecture;
- SOLID;
- Separation of Concerns;
- Strategy Pattern;
- Dependency Injection;
- Open/Closed Principle.

Cada componente possui uma única responsabilidade claramente definida.

---

# Extensibilidade

Novos planejadores podem ser adicionados sem modificar os existentes.

Exemplos futuros:

- CloudPlanner
- KubernetesPlanner
- DockerPlanner
- VSCodePlanner
- GitPlanner
- RemotePlanner

---

# Roadmap Arquitetural

## v1.0

- CLI
- TUI
- AI Planner
- Rule Planner
- Remote Execution
- Autonomous Loop

---

## v1.1

- Builtin Planner
- Response Formatter
- Fast Response
- UX Improvements
- Professional Installation

---

## v2.0

- GUI Desktop
- RAG Local
- Code Search
- Semantic Memory
- Plugin System
- Multi-Agent Collaboration
- Remote Infrastructure Management

---

# Conclusão

A arquitetura do Ubuntu AI Assistant foi concebida para permitir evolução contínua sem comprometer os princípios de modularidade, manutenção e extensibilidade.

A introdução do BuiltinPlanner na versão 1.1 reduz significativamente a latência para operações determinísticas, preservando o AIPlanner para tarefas que realmente exigem inteligência artificial.

Essa separação mantém a arquitetura limpa, melhora a experiência do usuário e prepara a plataforma para as próximas versões do projeto.