# ADR-003 — Builtin Planner

- **Status:** Aceito
- **Data:** 2026-08-11
- **Versão:** Ubuntu AI Assistant v1.1

---

# Contexto

Durante a evolução da versão 1.1 foi identificada a necessidade de reduzir a latência do sistema para solicitações determinísticas, como:

- mostrar uso de disco;
- mostrar memória;
- listar arquivos;
- mostrar diretório atual;
- mostrar endereço IP.

Na versão 1.0 todas as solicitações desconhecidas pelo RulePlanner eram encaminhadas ao AIPlanner.

Embora essa estratégia preserve a flexibilidade do sistema, ela introduz uma latência desnecessária para comandos simples, uma vez que a geração de planos depende da inferência do modelo de linguagem.

---

# Problema

Existem três categorias distintas de planejamento:

1. comandos determinísticos do sistema operacional;
2. planos compostos conhecidos;
3. planejamento por IA.

Na arquitetura da versão 1.0 apenas as categorias (2) e (3) estavam explicitamente representadas.

A tentativa inicial de criar um módulo FastPath separado introduziu sobreposição de responsabilidades com o RulePlanner.

---

# Decisão

Foi decidido introduzir um novo componente denominado **BuiltinPlanner**.

Esse componente será responsável exclusivamente pelo planejamento de comandos determinísticos do sistema operacional.

Fluxo atualizado:

```text
                Planner
                   │
        ┌──────────┼──────────┐
        │          │          │
        ▼          ▼          ▼
BuiltinPlanner RulePlanner AIPlanner
        │          │          │
        └──────────┴──────────┘
                   │
                   ▼
               Executor
                   │
                   ▼
          Response Formatter
```

---

# Responsabilidades

## BuiltinPlanner

Responsável por:

- pwd
- ls
- df
- free
- ip
- uname
- git status
- git branch
- docker ps
- docker images

Não utiliza IA.

Retorna diretamente um objeto `Plan`.

---

## RulePlanner

Responsável por planos compostos conhecidos.

Exemplos:

- instalar Docker;
- configurar PostgreSQL;
- criar ambiente Python;
- instalar Kubernetes.

Pode conter múltiplas etapas.

---

## AIPlanner

Responsável por solicitações abertas.

Exemplos:

- analisar projeto;
- montar arquitetura;
- criar ambiente complexo;
- explicar erros;
- planejamento contextual.

Utiliza LLM.

---

# Benefícios

A separação das responsabilidades proporciona:

- redução significativa da latência;
- menor consumo do modelo local;
- preservação do princípio da responsabilidade única (SRP);
- maior clareza arquitetural;
- facilidade de expansão futura.

---

# Consequências

## Positivas

- comandos administrativos passam a responder quase instantaneamente;
- RulePlanner permanece responsável apenas por regras de negócio;
- AIPlanner permanece responsável apenas por raciocínio.

## Negativas

- aumento de um componente na arquitetura;
- necessidade de manter o catálogo de comandos internos.

---

# Evoluções Futuras

O BuiltinPlanner poderá evoluir para:

- detecção automática do sistema operacional;
- comandos específicos por distribuição Linux;
- cache de resultados;
- execução paralela;
- descoberta dinâmica de capacidades.

---

# Motivação

Esta decisão foi tomada após a homologação completa da versão 1.0.

Os testes demonstraram que o maior gargalo percebido pelos usuários não estava na arquitetura nem na execução dos comandos, mas na utilização do modelo de linguagem para tarefas determinísticas que poderiam ser resolvidas localmente.

O BuiltinPlanner elimina essa limitação preservando toda a arquitetura existente.