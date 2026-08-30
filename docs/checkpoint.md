# Ubuntu AI Assistant — Development Checkpoint

> Última atualização: 2026-08-30

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

## Resultado do V2.1-P2-R3

- painel visual extraído para `gui/automation_panel.py`;
- apresentação de tarefas e métricas extraída;
- consultas e controles preservados no coordenador;
- 31 testes específicos aprovados;
- suíte completa com 913 testes aprovados;
- `gui/app.py` reduzido de 2.065 para 1.995 linhas;
- redução acumulada de 2.213 para 1.995 linhas;
- zero ciclos entre pacotes de alto nível.

## Resultado do V2.1-P2-R4

- controles visuais extraídos para `gui/remote_controls.py`;
- destino selecionado permanece sempre visível;
- cadastro, seleção e diagnóstico preservados no coordenador;
- validações e segurança preservadas no backend remoto;
- 35 testes específicos aprovados;
- suíte completa com 915 testes aprovados;
- `gui/app.py` reduzido de 1.995 para 1.942 linhas;
- redução acumulada de 2.213 para 1.942 linhas;
- zero ciclos entre pacotes de alto nível.

## Último incremento concluído

### V2.1-P2-R5 — Cartões de plano e execução

- construção visual delegada a `gui/execution_cards.py`;
- confirmação, cancelamento e coordenação preservados em `UbuntuAIApp`;
- contrato público das constantes do tema preservado;
- testes específicos e suíte completa aprovados;
- auditoria arquitetural permaneceu com zero ciclos;
- `gui/app.py` reduzido para 1.614 linhas.

## Último incremento concluído

### V2.1-P2-R6 — Estrutura visual e conversa

- estrutura principal delegada a `gui/interface.py`;
- conversa e boas-vindas delegadas a `gui/conversation_view.py`;
- apresentação do estado ocupado isolada;
- backend e coordenação preservados em `UbuntuAIApp`;
- contratos tipográficos preservados;
- suíte completa e arquitetura aprovadas.

## Pacote atual

### V2.1-P3-R1 — CI moderno e proteção arquitetural

- atualizar actions para runtimes Node.js 24;
- preservar checkout, uv, testes, artefatos e provenance;
- impedir que `gui/app.py` ultrapasse 1.400 linhas;
- verificar automaticamente os componentes visuais obrigatórios;
- executar testes, documentação e arquitetura antes da publicação.

## Validação remota concluída

- CI aprovado no commit `e4d8572`;
- CodeQL aprovado no commit `e4d8572`;
- actions Node.js 24 confirmadas no GitHub;
- proteção arquitetural da GUI ativa.

## Pacote atual

### V2.1-P4-R1 — Matriz de homologação

- 20 recursos catalogados;
- 39 perguntas anunciadas identificadas;
- 8 casos negativos complementares definidos;
- 47 casos aguardando execução funcional;
- matriz protegida contra divergência pelo CI.

## Próxima etapa

Executar os casos pela interface, registrar evidências e corrigir qualquer
diferença entre o comportamento observado e o recurso anunciado.

## V2.1-P4-R5 — Consultas e coordenação operacional

- H16, H20, H27–H32, H35 e H36 alinhados às APIs reais;
- consultas de tarefas, agendamentos, perfis e plugins executadas localmente;
- diagnóstico SSH e cancelamento mantidos sob seleção explícita na GUI;
- rede e armazenamento integrados ao planejamento multiagente;
- consulta ao APT limitada ao cache local e sem alterações;
- recorrência semanal retirada dos exemplos até possuir implementação completa;
- arquitetura permanece sem ciclos;
- evidência: `docs/releases/v2.1-p4-r5-operational-queries-validation.md`.

## V2.1-P4-R6 — Entrega assíncrona e ações anunciadas

- fila segura criada entre workers e a thread principal do Tkinter;
- chamadas diretas `root.after(0, ...)` removidas dos workers;
- entrega corrigida para ações, chat, SSH, multiagente e confirmação;
- H09, H10, H11 e H18 receberam planos determinísticos corretos;
- variações naturais mantêm rota segura e independente do Ollama;
- homologação visual confirmou cartões, resultados e retorno ao estado Pronto;
- evidência: `docs/releases/v2.1-p4-r6-thread-delivery-actions-validation.md`.

## V2.1-P4-R7 — Homologação funcional local

- 38 casos anunciados aprovados pela GUI;
- 6 casos negativos complementares aprovados;
- 44 aprovações, nenhuma falha e três pendências SSH;
- Ollama, automação, confirmação, cancelamento e bloqueio crítico validados;
- resultados persistidos separadamente do catálogo;
- `capability_matrix.py --write` preserva resultados e evidências;
- evidência: `docs/releases/v2.1-p4-r7-local-homologation-validation.md`.

## Próxima evolução — Ações naturais seguras

A v2.2.0 deverá ampliar o assistente de consultas para operação cotidiana do
Ubuntu por linguagem natural, incluindo aplicativos instalados, sites e pastas
XDG. A execução continuará subordinada à política de risco, confirmação,
bloqueios críticos e auditoria.

Especificação: `docs/natural-actions-roadmap.md`.

## Candidata v2.1.0

- metadados promovidos de `2.0.2` para `2.1.0`;
- changelog e notas da release preparados;
- roadmap histórico corrigido para o estado atual;
- 44 de 47 casos homologados, sem falhas;
- H16, N07 e N08 aguardam um segundo computador SSH;
- próxima etapa: suíte, build, auditoria e instalação;
- nenhuma tag deve ser criada antes da validação final.

## RC2 instalada e homologada

- 992 testes aprovados;
- quatro artefatos construídos e auditados;
- atualização real de 2.0.2 para 2.1.0 aprovada;
- RC2 reinstalada após correção das consultas de versão;
- homologação visual e preservação do histórico aprovadas;
- próxima etapa: commit da candidata e validação pelo CI.
