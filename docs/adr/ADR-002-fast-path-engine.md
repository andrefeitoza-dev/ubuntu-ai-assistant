# ADR-002 — Fast Path Engine

- **Status:** Aceito
- **Data:** 2026-08-11
- **Versão:** Ubuntu AI Assistant v1.1

---

# Contexto

Durante a homologação da versão 1.0 foi identificado que todas as solicitações do usuário eram encaminhadas ao AI Planner (LLM), independentemente da complexidade da tarefa.

Mesmo comandos determinísticos e amplamente conhecidos, como:

- `pwd`
- `df -h`
- `free -h`
- `ls`
- `ip addr`

dependiam da geração de um plano pela IA antes da execução.

Em equipamentos com recursos limitados (CPU sem aceleração por GPU), esse fluxo aumentava significativamente o tempo de resposta, comprometendo a experiência do usuário.

Os testes de homologação mostraram que a maior parte da latência do sistema estava concentrada na etapa de planejamento realizada pelo modelo de linguagem.

---

# Problema

A utilização obrigatória do AI Planner para comandos simples provoca:

- aumento desnecessário da latência;
- maior consumo de CPU;
- maior utilização do modelo local;
- pior experiência de uso;
- sensação de lentidão mesmo em tarefas triviais.

---

# Decisão

Foi decidido introduzir uma nova camada denominada **Fast Path Engine** entre o Intent Analyzer e o AI Planner.

O Fast Path será responsável por identificar solicitações determinísticas e encaminhá-las diretamente ao Executor, sem necessidade de utilizar o modelo de linguagem.

Fluxo anterior:

```text
Usuário
    ↓
Intent
    ↓
AI Planner
    ↓
Executor
```

Novo fluxo:

```text
Usuário
    ↓
Intent
    ↓
Fast Path Router
   ↙           ↘
Conhecido   Desconhecido
    ↓            ↓
Executor    AI Planner
     ↓          ↓
      └────┬────┘
           ↓
Response Formatter
```

---

# Benefícios

A adoção do Fast Path proporciona:

- redução significativa da latência;
- menor utilização do Ollama;
- menor consumo de recursos computacionais;
- respostas praticamente instantâneas para comandos simples;
- preservação da arquitetura existente;
- separação clara entre tarefas determinísticas e tarefas que exigem raciocínio da IA.

---

# Escopo Inicial

Nesta primeira versão, o Fast Path contemplará comandos relacionados a:

## Sistema

- diretório atual (`pwd`)
- uso de disco (`df -h`)
- memória (`free -h`)
- kernel (`uname -r`)
- endereço IP (`ip addr`)
- listagem de arquivos (`ls`)

## Git

- status
- branch atual
- histórico

## Docker

- containers
- imagens

## Python

- pytest
- ruff

---

# Consequências

## Positivas

- melhora perceptível da experiência do usuário;
- redução do tempo de resposta para tarefas simples;
- menor dependência do modelo de linguagem;
- arquitetura preparada para expansão futura.

## Negativas

- necessidade de manter um catálogo de comandos rápidos;
- aumento da responsabilidade do roteador de execução;
- manutenção adicional do registro de comandos.

---

# Evoluções Futuras

O Fast Path poderá evoluir para:

- execução contextual baseada no projeto atual;
- cache de comandos recentes;
- cache de planos;
- seleção dinâmica entre Fast Path e AI Planner;
- aprendizagem automática de comandos frequentes.

---

# Motivação

Esta decisão foi tomada após a homologação completa da versão 1.0, quando foi observado que a principal limitação percebida pelos usuários não estava na arquitetura do sistema, mas na experiência de uso causada pela utilização desnecessária da IA em tarefas determinísticas.

O Fast Path torna o Ubuntu AI Assistant mais responsivo sem alterar sua arquitetura principal.