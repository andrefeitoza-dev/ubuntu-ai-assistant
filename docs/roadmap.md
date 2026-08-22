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

- Linha de desenvolvimento: `v1.3`
- Branch: `develop/v1.3`
- Versão do pacote: `1.2.0`
- Interface terminal: concluída
- Interface gráfica G1 e G2: concluídas
- Launcher desktop: funcional
- Testes automatizados: `530 passed`
- Qualidade estática: Ruff aprovado

> A versão `1.2.0` foi auditada e concluída.

## Visão geral das versões

| Versão | Tema | Estado |
|---|---|---|
| `v1.0` | Fundação, segurança e runtime do agente | Concluída |
| `v1.1` | Respostas rápidas, planners e evolução de UX | Concluída |
| `v1.2` | Aplicativo desktop e experiência gráfica | Concluída |
| `v1.3` | Inteligência, conversa e desempenho | Em desenvolvimento |
| `v1.4` | Administração remota segura | Planejada |
| `v1.5` | Automação e agentes especializados | Planejada |
| `v1.6` | Distribuição e integrações | Planejada |
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

## v1.3 — Inteligência, conversa e desempenho

### Objetivo

Tornar o aplicativo um assistente de IA completo para a apresentação do TCC,
sem transformar perguntas gerais em comandos e sem usar o Ollama quando uma
resposta determinística segura for suficiente.

### F1 — Roteamento e conversa

- [x] respostas locais instantâneas para consultas determinísticas;
- [x] cancelamento coerente entre GUI e Agent Loop;
- [x] proteção contra resultados antigos após cancelamento;
- [x] separação entre pergunta conversacional e ação no sistema;
- [x] canal Ollama textual independente do planejador JSON;
- [x] memória recente nas conversas gerais;
- [x] identificação da rota usada na GUI;
- [x] limite de resposta reduzido para computadores CPU-only.

### F2 — Fast Path adaptativo

- [x] ampliar vocabulário seguro e sinônimos;
- [x] reconhecer frases semelhantes por intenção;
- [x] priorizar correspondências específicas sobre termos genéricos;
- [x] usar histórico bem-sucedido como recomendação;
- [x] exigir aprovação antes de promover novos atalhos executáveis;
- [x] manter ações sensíveis fora do aprendizado automático.

### F3 — Desempenho e apresentação do TCC

- [x] medir latência por rota `local`, `action` e `chat`;
- [x] mostrar a estratégia selecionada de forma discreta;
- [x] preparar cenários reproduzíveis de demonstração;
- [x] validar operação em hardware CPU-only com 8 GB de RAM;
- [x] documentar arquitetura, segurança e resultados;
- [x] executar auditoria e preparar a release de apresentação.

### F4 — Contexto Local Inteligente

- [x] consultar configuração geral, CPU, memória e uso de disco sem Ollama;
- [x] consultar discos, partições, interfaces e rotas de rede;
- [x] consultar processos e estados de serviços em modo somente leitura;
- [x] listar diretórios, estruturas e arquivos ocultos com permissões do usuário;
- [x] adicionar busca dinâmica segura de arquivos e pastas;
- [x] abrir pastas e arquivos com caminhos validados;
- [x] abrir sites aceitando somente URLs HTTP/HTTPS;
- [x] iniciar aplicativos Ubuntu por identificadores confiáveis;
- [x] tratar pedidos ambíguos, como “abra meu e-mail”;
- [x] bloquear esquemas, caminhos e argumentos potencialmente perigosos;
- [x] explicar falhas de permissão sem tentar elevação automática;
- [x] consolidar perfil automático de saúde do computador;
- [x] validar consultas locais na GUI e documentar evidências.

---

## v1.4 — Administração remota segura

### Objetivo

Administrar computadores Ubuntu autorizados por SSH, preservando identificação
explícita do destino, autenticação segura, confirmação proporcional ao risco e
auditoria separada por host.

### R1 — Fundação SSH segura

- [x] validar nomes, endereços, usuários, portas e argumentos;
- [x] persistir inventário de hosts com permissão `0600`;
- [x] aceitar somente caminhos absolutos para chaves e `known_hosts`;
- [x] exigir verificação da identidade do servidor;
- [x] desabilitar autenticação interativa por senha;
- [x] limitar timeouts de conexão e execução;
- [x] bloquear elevação automática e shells intermediários;
- [x] validar a fundação com testes automatizados.

### R2 — Contexto e execução remota

- [x] cadastrar, listar, editar e remover hosts autorizados;
- [x] testar conectividade e apresentar diagnóstico amigável;
- [x] consultar sistema, CPU, memória, disco, rede e serviços;
- [x] aplicar classificação de risco aos comandos remotos;
- [x] implementar confirmação, cancelamento e timeout;
- [x] separar contexto local e contexto remoto.

### R3 — GUI e auditoria

- [x] selecionar explicitamente o computador de destino;
- [x] manter o destino visível durante toda a operação;
- [x] impedir execução quando o destino estiver indefinido;
- [x] apresentar conexão, diagnóstico, resultado e falhas na GUI;
- [x] manter histórico e logs separados por host;
- [x] proteger contra execução acidental no computador errado.

### R4 — Integração e release v1.4.0

- [x] preparar ambiente SSH isolado;
- [x] validar conexão, identidade, timeout e falhas;
- [x] validar políticas `LOW`, `MEDIUM`, `HIGH` e `CRITICAL`;
- [x] atualizar documentação e evidências;
- [x] executar auditoria, build e instalação limpa;
- [x] preparar e criar a tag `v1.4.0`.

---

## v1.5 — Automação e agentes especializados

### Objetivo

Executar automações longas de forma observável, retomável e segura, usando
agentes especializados com limites operacionais explícitos.

### A1 — Tarefas longas e progresso

- [x] formalizar estados de tarefas longas;
- [x] publicar progresso incremental para observadores;
- [x] implementar pausa, retomada e cancelamento cooperativos;
- [x] limitar duração de tarefas;
- [x] impedir retrocesso e extrapolação do progresso;
- [x] integrar o gerenciador ao runtime autônomo;
- [x] validar concorrência, limites e transições com testes automatizados.

### A2 — Persistência, retomada e agendamento

- [x] persistir tarefas e checkpoints sem armazenar segredos;
- [x] recuperar tarefas interrompidas de forma segura;
- [x] agendar execuções locais com política de risco;
- [x] manter histórico de automações e tentativas.

### A3 — Agentes especializados

- [x] especializar agentes de sistema, rede, armazenamento e serviços;
- [x] aplicar limites operacionais por agente e ambiente;
- [x] replanejar tarefas com base em falhas observadas;
- [x] impedir que agentes contornem confirmação ou política de risco.

### A4 — Observabilidade e release v1.5.0

- [x] emitir eventos e métricas estruturadas;
- [x] integrar progresso, automações e agentes à GUI;
- [x] validar tarefas longas, retomada e agentes especializados;
- [x] executar auditoria, build e instalação limpa;
- [x] preparar e criar a tag `v1.5.0`.

---

## v1.6 — Distribuição e integrações

### Objetivo

Transformar o Ubuntu AI Assistant em um produto distribuível, atualizável,
extensível e documentado, preservando segurança, compatibilidade e
reprodutibilidade.

### D1 — Instalação e ciclo de vida

- [x] consolidar instalação pelo wheel e por ferramenta isolada;
- [x] implementar atualização controlada com validação de versão;
- [x] implementar desinstalação completa e segura;
- [x] preservar configurações e dados durante atualizações;
- [x] validar launcher, ícone e comandos após instalação;
- [x] testar instalação, atualização e remoção em ambiente limpo.

### D2 — Configurações, perfis e plugins

- [x] importar e exportar configurações sem incluir segredos;
- [x] criar perfis de agentes com limites e políticas explícitas;
- [x] formalizar catálogo local de plugins;
- [x] validar versão, manifesto e compatibilidade dos plugins;
- [x] impedir carregamento de plugins inválidos ou não confiáveis;
- [x] documentar estabilidade e depreciação da API pública.

### D3 — Integração e documentação pública

- [x] integrar comandos e tarefas seguras ao VS Code;
- [x] manter a integração opcional e desacoplada da aplicação;
- [x] publicar documentação de instalação, uso e solução de problemas;
- [x] atualizar guia de contribuição e desenvolvimento;
- [x] documentar plugins, perfis e configurações;
- [x] preparar exemplos reproduzíveis para usuários e contribuidores.

### D4 — Pipeline e release v1.6.0

- [x] automatizar qualidade, testes, arquitetura e build;
- [x] validar integridade e conteúdo dos artefatos;
- [x] gerar checksums verificáveis da distribuição;
- [x] preparar assinatura sem armazenar chaves no repositório;
- [x] executar instalação, atualização e desinstalação limpas;
- [x] atualizar documentação e evidências da release;
- [x] preparar e criar a tag `v1.6.0`.

---

## v2.0 — Plataforma inteligente multiagente

### Objetivo

Transformar o Ubuntu AI Assistant em uma plataforma multiagente capaz de
compreender objetivos, consultar o contexto real do computador, orientar o
usuário, coordenar especialistas e executar tarefas locais ou remotas com
segurança, confirmação proporcional ao risco e auditoria completa.

A v2.0 não fornecerá autonomia irrestrita. Políticas de risco, destino
explícito, limites operacionais e confirmação humana continuarão centralizados.

### V2-P1 — Contexto, comandos e descoberta de recursos

- [x] responder com dados reais do computador selecionado;
- [x] consultar Ubuntu, kernel, arquitetura, hostname, CPU e memória;
- [x] consultar discos, rede, bateria, processos e serviços;
- [x] separar explicitamente contexto local e contexto SSH;
- [x] impedir que perguntas factuais do sistema sejam enviadas à conversa;
- [x] listar os principais comandos Linux por categoria;
- [x] explicar comandos, argumentos e exemplos seguros;
- [x] localizar comandos pela finalidade informada pelo usuário;
- [x] listar ou pesquisar comandos instalados no computador selecionado;
- [x] sinalizar comandos destrutivos ou dependentes de privilégios;
- [x] apresentar um catálogo completo das capacidades do assistente;
- [x] adicionar acesso visível a recursos, ajuda e exemplos na GUI;
- [x] validar roteamento, segurança e respostas com testes automatizados.

### V2-P2 — Orquestração multiagente

- [x] formalizar objetivos, tarefas, dependências e resultados;
- [x] selecionar agentes especializados conforme a solicitação;
- [x] coordenar agentes de sistema, rede, armazenamento e serviços;
- [x] compartilhar somente o contexto necessário entre agentes;
- [x] impedir ciclos, duplicações e execução fora do escopo;
- [x] manter confirmação e política de risco centralizadas;
- [x] acompanhar progresso e resultados de cada agente.

### V2-P3 — Replanejamento, memória e recuperação

- [x] analisar falhas e resultados parciais;
- [x] gerar alternativas seguras sem ampliar silenciosamente o escopo;
- [x] retomar tarefas usando checkpoints persistidos;
- [x] incorporar histórico e conhecimento local às decisões;
- [x] registrar justificativas para seleção e replanejamento;
- [x] medir qualidade, tentativas, duração e taxa de sucesso;
- [x] impedir aprendizado automático não aprovado.

### V2-P4 — Experiência integrada e release v2.0.0

- [ ] integrar plano, agentes, progresso e controles à GUI;
- [ ] permitir pausa, retomada e cancelamento;
- [ ] manter computador e ambiente de destino sempre visíveis;
- [ ] consolidar eventos, métricas, histórico e auditoria;
- [ ] validar operação local, remota e multiagente;
- [ ] atualizar documentação e evidências;
- [ ] executar auditoria, build e instalação limpa;
- [ ] preparar e criar a tag `v2.0.0`.
