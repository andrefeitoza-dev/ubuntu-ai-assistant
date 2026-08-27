# Ubuntu AI Assistant — Development Checkpoint

> Última atualização: 2026-08-27

## Estado atual

- Última versão estável: `2.0.2`;
- Branch de desenvolvimento: `develop/v2.1`;
- Commit-base: `1ec6df8`;
- CI e Release da `v2.0.2`: aprovados;
- Artefatos da `v2.0.2`: publicados e verificados;
- Ciclo atual: `v2.1 — Qualidade arquitetural e manutenção`.

## Objetivo da v2.1

Reduzir dívida técnica e fortalecer a manutenção da plataforma sem alterar
comportamento, políticas de segurança ou compatibilidade da versão estável.

## Incremento atual

### V2.1-P1 — Contratos e dependências acíclicas

- separar contratos de contexto do pacote `agent`;
- eliminar a dependência `context -> agent`;
- separar `PlanningProfile` do pacote `planner`;
- eliminar a dependência `decision -> planner`;
- preservar os caminhos públicos anteriores;
- impedir regressões com verificações automatizadas.

## Linha de base

- 887 testes aprovados após o V2.1-P1;
- Ruff aprovado;
- verificações arquiteturais aprovadas;
- ciclos de alto nível reduzidos de um para zero;
- maior arquivo: `src/ubuntu_ai/gui/app.py`, com 2.213 linhas.

## Resultado do V2.1-P1

- contratos de contexto extraídos para área neutra;
- dependências `context -> agent` e `decision -> planner` removidas;
- imports públicos anteriores preservados por fachadas;
- regras arquiteturais automatizadas;
- 887 testes aprovados;
- zero ciclos entre pacotes de alto nível.

## Resultado do V2.1-P2-R1

- funções puras extraídas para `gui/presentation.py`;
- métodos anteriores preservados como fachadas;
- 50 testes específicos aprovados;
- suíte completa com 911 testes aprovados;
- `gui/app.py` reduzido de 2.213 para 2.151 linhas;
- comportamento visual e contratos do backend preservados;
- zero ciclos entre pacotes de alto nível.

## Resultado do V2.1-P2-R2

- tokens visuais centralizados em `gui/theme.py`;
- construção do painel extraída para `gui/capabilities_panel.py`;
- 57 testes específicos aprovados;
- suíte completa com 911 testes aprovados;
- `gui/app.py` reduzido de 2.151 para 2.065 linhas;
- redução acumulada de 2.213 para 2.065 linhas;
- zero ciclos entre pacotes de alto nível;
- layout, callbacks e backend preservados.

## Próximo incremento

- selecionar o próximo componente visual independente;
- manter coordenação e políticas em `UbuntuAIApp`;
- ampliar testes antes de cada nova extração.
