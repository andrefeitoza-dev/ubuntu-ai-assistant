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

- Última versão estável: `v2.0.2`
- Branch atual: `develop/v2.1`
- Candidata em preparação: `v2.1.0`
- Interface terminal e gráfica: funcionais
- Arquitetura: zero ciclos entre pacotes
- GUI: 1.374 linhas e oito componentes
- Homologação: 44 aprovações e nenhuma falha
- Casos SSH pendentes: H16, N07 e N08
- Qualidade estática, CI e CodeQL: aprovados

> A versão `v2.1.0` está em preparação para validação final.

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

- [x] integrar plano, agentes, progresso e controles à GUI;
- [x] permitir pausa, retomada e cancelamento;
- [x] manter computador e ambiente de destino sempre visíveis;
- [x] consolidar eventos, métricas, histórico e auditoria;
- [x] validar operação local, remota e multiagente;
- [x] atualizar documentação e evidências;
- [x] executar auditoria, build e instalação limpa;
- [x] preparar e criar a tag `v2.0.0`.

### V2-P5 — Distribuição simplificada e release v2.0.1

- [x] incorporar os hotfixes de desktop e roteamento temporal;
- [x] construir um pacote Debian único para Ubuntu `amd64`;
- [x] incluir aplicação, dependências Python, comandos, ícone e entrada no menu;
- [x] orientar a configuração inicial do Ollama e do modelo local;
- [x] auditar conteúdo, metadados e dependências do pacote;
- [x] publicar o `.deb` junto aos demais artefatos da release;
- [x] validar instalação e funcionamento em um segundo notebook Ubuntu;
- [x] validar remoção preservando configurações e dados;
- [x] preparar e criar a tag `v2.0.1`.

### V2-P6 — Portabilidade e hotfix v2.0.2

- [x] reproduzir a consulta de IP encaminhada incorretamente ao Ollama;
- [x] responder variações de IP pela rota local somente leitura;
- [x] remover `python -c` dos lançadores do pacote Debian;
- [x] impedir caminhos temporários nos entry points empacotados;
- [x] adicionar testes de roteamento e auditoria dos lançadores;
- [x] executar suíte, arquitetura, build e instalação limpa;
- [x] validar a candidata no segundo notebook;
- [x] atualizar metadados e criar a tag `v2.0.2`.

---

## v2.1 — Qualidade arquitetural e manutenção

### Objetivo

Reduzir dívida técnica e fortalecer a evolução segura da plataforma sem alterar
as capacidades, políticas de risco ou compatibilidade pública da v2.0.2.

### V2.1-P1 — Contratos e dependências acíclicas

- [x] criar contratos de contexto independentes do pacote `agent`;
- [x] remover a dependência `context -> agent`;
- [x] mover `PlanningProfile` para o domínio de decisão;
- [x] remover a dependência `decision -> planner`;
- [x] preservar os imports públicos anteriores por fachadas compatíveis;
- [x] adicionar teste que rejeita ciclos entre pacotes de alto nível;
- [x] executar suíte completa e auditoria arquitetural;
- [x] documentar evidências e criar o commit do incremento.

### V2.1-P2 — Decomposição da interface gráfica

- [x] mapear responsabilidades de `gui/app.py`;
- [x] extrair funções puras de apresentação;
- [x] centralizar tokens visuais em módulo de tema;
- [x] extrair a construção visual do painel de capacidades;
- [x] extrair a construção e apresentação do painel de automação;
- [x] extrair os controles visuais de destino local e SSH;
- [x] extrair cartões visuais de plano e resultado da execução;
- [x] extrair componentes sem alterar comportamento visual;
- [x] reduzir acoplamento entre GUI, backend e execução;
- [x] adicionar testes de regressão da composição da interface.
- [x] extrair estrutura principal, cabeçalho e barra de entrada;
- [x] extrair tela de boas-vindas e apresentação das mensagens;
- [x] extrair apresentação do estado ocupado da interface;

### V2.1-P3 — Pipeline e manutenção da release

- [x] atualizar actions com avisos de runtime depreciado;
- [x] proteger automaticamente a composição e o tamanho da GUI;
- [x] preservar CI, release, attestations e checksums;
- [x] executar build e instalação limpa;
- [x] preparar a release `v2.1.0`.

### V2.1-P4 — Homologação funcional e release v2.1.0

- [x] corrigir a entrega assíncrona dos resultados à thread principal da GUI;
- [x] validar ações anunciadas e suas variações naturais na interface;

- [x] alinhar consultas operacionais, tarefas, perfis e plugins ao estado real;
- [x] integrar exemplos naturais ao diagnóstico SSH e aos agentes especializados;

- [x] inventariar todas as perguntas exibidas em Recursos e ajuda;
- [x] criar matriz rastreável para os 39 exemplos e 8 casos negativos;
- [x] corrigir os cinco casos anunciados de abertura segura do desktop;
- [x] responder localmente consultas anunciadas de runtime e instalação;
- [x] corrigir diagnóstico de lentidão e conhecimento Linux anunciado;
- [x] testar localmente os 20 recursos e suas principais variações;
- [x] validar rotas locais, Ollama, automação e execução controlada;
- [ ] validar operação local e em computador remoto por SSH;
- [x] testar confirmações, cancelamentos e bloqueios por risco;
- [x] testar entradas inválidas e indisponibilidade de dependências;
- [x] executar homologação visual local completa da GUI;
- [x] registrar resultados em uma matriz de evidências;
- [x] corrigir falhas ou documentar limitações conhecidas;
- [x] validar pacote Debian em instalação e atualização reais;
- [x] executar suíte, arquitetura, CI e auditoria dos artefatos;
- [x] preparar changelog, documentação e tag `v2.1.0`.

### V2.2-P1 — Ações naturais seguras no desktop

- [x] criar resolução segura de aplicativos instalados por entradas `.desktop`;
- [x] abrir Calculadora, LibreOffice e Terminal por linguagem natural;
- [x] abrir sites HTTP/HTTPS e aliases confiáveis no navegador;
- [x] bloquear protocolos, URLs e argumentos inseguros;
- [x] ampliar pastas XDG, incluindo Downloads e nomes localizados;
- [x] separar abertura do Terminal da execução de comandos;
- [x] criar prévia e confirmação para alterações controladas;
- [x] preservar bloqueios para elevação e comandos críticos;
- [x] auditar aplicativo, pasta, domínio, comando e resultado;
- [x] testar frases oficiais e principais variações naturais;
- [x] criar matriz de segurança e homologação da v2.2.0;
- [x] documentar arquitetura, limitações e evidências.
