# Ubuntu AI Assistant — Roadmap

## Visão do produto

O Ubuntu AI Assistant é um agente local para administração segura de sistemas
Linux. Ele transforma solicitações em linguagem natural em planos auditáveis,
avalia riscos, solicita confirmação quando necessário e executa ações de forma
controlada.

O objetivo é oferecer no Ubuntu uma experiência semelhante aos assistentes
modernos, preservando controle humano, privacidade local, rastreabilidade e
segurança operacional.

## Estado atual

- Linha de desenvolvimento: `v1.2`
- Branch: `develop/v1.2`
- Versão do pacote: `1.2.0`
- Interface terminal: concluída
- Interface gráfica G1 e G2: concluídas
- Launcher desktop: funcional
- Testes automatizados: `482 passed`
- Qualidade estática: Ruff aprovado

> A versão `1.2.0` foi auditada e concluída.

## Visão geral das versões

| Versão | Tema | Estado |
|---|---|---|
| `v1.0` | Fundação, segurança e runtime do agente | Concluída |
| `v1.1` | Respostas rápidas, planners e evolução de UX | Concluída |
| `v1.2` | Aplicativo desktop e experiência gráfica | Concluída |
| `v1.3` | Administração remota segura | Planejada |
| `v1.4` | Automação e agentes especializados | Planejada |
| `v1.5` | Distribuição e integrações | Planejada |
| `v2.0` | Plataforma inteligente multiagente | Visão futura |

---

## v1.0 — Fundação segura

### Concluído

- Clean Architecture, SOLID e separação por domínios;
- CLI, Doctor e diagnóstico do runtime;
- integração local com Ollama;
- Rule Planner e AI Planner;
- planos, preview e classificação de risco;
- confirmação humana e política de execução;
- executor controlado;
- contexto, memória e histórico de conversa;
- base de conhecimento e RAG local;
- aprendizado baseado no histórico;
- skills e Plugin SDK;
- reflexão, preflight e recuperação;
- Agent Loop com limites e watchdog;
- TUI interativa;
- logging, benchmark e hardening;
- SDK Python;
- suíte automatizada de regressão.

---

## v1.1 — Inteligência rápida e UX

### Concluído

- Builtin Planner para operações determinísticas;
- Fast Path para respostas sem uso desnecessário do modelo;
- roteamento entre Builtin, Rule e AI Planner;
- Response Formatter;
- melhoria das respostas rápidas;
- refinamento da experiência no terminal;
- evolução das políticas de execução;
- base para instalação profissional;
- ADRs da arquitetura de planejamento rápido.

---

## v1.2 — Ubuntu AI Assistant Desktop

### Objetivo

Transformar o framework em um aplicativo Ubuntu utilizável no dia a dia, sem
depender do terminal ou do VS Code.

### G1 — Fundação da GUI

- [x] interface moderna em Tkinter;
- [x] identidade visual escura;
- [x] cabeçalho, status e área de conversa;
- [x] entrada de solicitações;
- [x] integração da GUI com o backend;
- [x] apresentação de planos e riscos;
- [x] confirmação de ações sensíveis;
- [x] apresentação dos resultados de execução.

### G2 — Launcher e execução por risco

- [x] launcher no menu de aplicativos do Ubuntu;
- [x] abertura independente do terminal;
- [x] execução automática para risco `LOW`;
- [x] confirmação obrigatória para `HIGH` e `CRITICAL`;
- [x] resultado no card “Execução concluída”;
- [x] ícone próprio do Ubuntu AI Assistant;
- [x] logo no cabeçalho e na tela inicial;
- [x] composer central na apresentação;
- [x] composer inferior após o início da conversa;
- [x] validação com `482 passed`.

### G3 — Estabilização da aplicação desktop

- [x] versionar o instalador do launcher;
- [x] empacotar corretamente os assets da GUI;
- [x] adicionar testes específicos da interface;
- [x] validar associação da janela com o Dock;
- [x] tratar ausência ou corrupção do ícone;
- [x] melhorar mensagens de falha do backend;
- [x] adicionar cancelamento visual de tarefas;
- [x] revisar acessibilidade, foco e navegação por teclado;
### G4 — Preparação da release v1.2.0

- [x] validar os fluxos `LOW`, `HIGH` e `CRITICAL`;
- [x] testar instalação e desinstalação em ambiente limpo;
- [x] atualizar README, arquitetura e checkpoint;
- [x] preparar notas da release `v1.2.0`;
- [x] atualizar a versão do pacote para `1.2.0`;
- [x] executar auditoria final e criar a tag da release.

### Critério de conclusão da v1.2

A versão será concluída quando o aplicativo puder ser instalado, aberto pelo
menu do Ubuntu, executar o fluxo completo com segurança e ser reproduzido em
uma instalação limpa.

---

## v1.3 — Administração remota segura

### Planejado

- cadastro de hosts Ubuntu remotos;
- conexão SSH com validação de identidade;
- diagnóstico remoto;
- planejamento com contexto do host selecionado;
- execução remota usando a mesma política de risco;
- confirmação explícita para ações remotas;
- logs separados por host;
- timeout, cancelamento e recuperação de conexão;
- inventário básico dos servidores;
- testes de integração com ambiente SSH isolado.

---

## v1.4 — Automação e agentes especializados

### Planejado

- tarefas longas com progresso;
- retomada segura após interrupção;
- agendamento local de tarefas;
- agentes especializados em sistema, rede, armazenamento e serviços;
- replanejamento baseado em falhas;
- observabilidade estruturada;
- histórico de automações;
- limites operacionais por agente;
- políticas específicas por ambiente.

---

## v1.5 — Distribuição e integrações

### Planejado

- pacote instalável para Ubuntu;
- atualização e desinstalação controladas;
- integração com VS Code;
- catálogo de plugins;
- perfis de agente;
- importação e exportação de configurações;
- documentação pública;
- guia de contribuição;
- pipeline de release;
- distribuição assinada.

---

## v2.0 — Plataforma inteligente multiagente

### Visão futura

- colaboração entre múltiplos agentes especializados;
- gerenciamento de infraestrutura local e remota;
- memória semântica evoluída;
- busca de código e configuração;
- interface gráfica extensível;
- interface web opcional;
- políticas organizacionais;
- execução distribuída;
- painel de observabilidade;
- ecossistema público de plugins;
- suporte a múltiplas distribuições Linux.

---

## Próximos passos imediatos

1. concluir a personalização e persistência do launcher;
2. versionar o instalador e os assets;
3. adicionar testes da GUI e do carregamento do ícone;
4. validar o fluxo `LOW`, `HIGH` e `CRITICAL` pela GUI;
5. atualizar README, arquitetura e checkpoint;
6. preparar a release `v1.2.0`.

## Princípios permanentes

- segurança antes da autonomia;
- confirmação proporcional ao risco;
- nenhuma tentativa de contornar bloqueios;
- execução auditável;
- funcionamento local por padrão;
- baixo consumo de recursos;
- arquitetura incremental;
- testes obrigatórios para cada evolução.
