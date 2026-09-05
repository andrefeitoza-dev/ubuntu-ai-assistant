# Changelog

## [2.3.5] - 2026-09-05

### Alterado

- `voice input` agora é um botão circular azul com ícone de microfone;
- `voice output` agora é um botão circular com ícone de alto-falante;
- saída desligada usa tom neutro e saída ligada usa verde;
- nomes dos controles aparecem como dicas ao passar o mouse;
- ativação por teclado com Enter e espaço foi preservada.

### Validação

- 1.224 testes aprovados com 80,01% de cobertura;
- arquitetura, estilo e GUI aprovados.

## [2.3.4] - 2026-09-05

### Corrigido

- após criar arquivo ou pasta, o gerenciador abre/focaliza automaticamente a pasta pai;
- o novo item aparece sem depender da atualização manual da janela Arquivos;
- a atualização visual faz parte da prévia segura apresentada ao usuário.

### Validação

- 1.220 testes aprovados com 80,13% de cobertura;
- arquitetura, estilo e GUI aprovados.

## [2.3.3] - 2026-09-05

### Alterado

- botão de reconhecimento renomeado para `>> voice input`;
- botão de leitura das respostas renomeado para `voice output`;
- estado da voz de saída indicado pela cor do botão, sem alterar seu nome.

### Corrigido

- resultado de criação mostra o caminho real do arquivo ou pasta somente após sucesso;
- orientação de atualização com `F5` exibida quando a janela Arquivos já estava aberta;
- criação dentro de subpastas mantém retorno verificável e não usa confirmação da IA.

### Validação

- 1.220 testes aprovados com 80,12% de cobertura;
- arquitetura, estilo e GUI aprovados.

## [2.3.2] - 2026-09-05

### Adicionado

- leitura opcional das respostas em voz alta pelo sintetizador local do Ubuntu;
- abertura do navegador padrão com “abra o navegador”;
- reconhecimento de navegadores instalados por nomes naturais, incluindo Opera.

### Corrigido

- criação de arquivos dentro de subpastas existentes da Home usa execução real;
- respostas conversacionais não confirmam mais falsamente essa criação sem comando;
- caminhos ausentes ou inseguros continuam recusados antes do planejamento por IA.

### Validação

- 1.218 testes automatizados aprovados;
- arquitetura, matriz funcional e estilo aprovados;
- GUI preservada em 1.399 de 1.400 linhas permitidas.

## [2.3.1] - 2026-09-05

### Corrigido

- painel **Computador local** exibido abaixo da barra superior, sem esconder opções;
- criação de arquivos e remoção de arquivos ou pastas reconhecidas localmente, sem
  aguardar o planejamento pelo modelo;
- remoção rápida e recuperável pela Lixeira, ainda protegida por prévia e confirmação.

### Validação

- 1.205 testes automatizados aprovados;
- arquitetura e estilo aprovados;
- GUI preservada em 1.396 de 1.400 linhas permitidas.

## [2.3.0] - 2026-09-05

### Adicionado

- configuração gráfica da IA local, com instalação orientada do Ollama e do modelo;
- entrada por voz local em português, sem exibir nem armazenar a transcrição;
- diagnóstico seguro de CPU, memória, disco, processos, rede e proteção do sistema;
- apresentação do assistente e catálogo ampliado de perguntas e capacidades;
- ações determinísticas para limpeza, atualização de pacotes e ativação do firewall,
  sempre com plano e confirmação.

### Alterado

- tipografia e tamanho dos textos da interface para melhorar a leitura;
- empacotamento Debian para incluir os novos atalhos, dependências e telas.

### Validação

- 1.197 testes automatizados aprovados;
- arquitetura sem ciclos e GUI preservada dentro do limite estrutural;
- catálogo com 20 áreas e exemplos naturais sincronizado com a matriz funcional.

Todas as mudanças relevantes deste projeto são registradas neste arquivo.

## [2.2.0] - 2026-08-31

### Added

- Abertura por linguagem natural de aplicativos instalados, sites HTTP/HTTPS e pastas XDG.
- Descoberta segura e dinâmica de aplicativos por entradas `.desktop` confiáveis.
- Operações controladas de criação, cópia, movimentação, renomeação e envio à Lixeira.
- Auditoria local protegida e exportação sanitizada de diagnósticos.
- Modo global de simulação e permissões adicionais por capacidade.
- Consultas locais sobre aprendizado persistente e consumo de memória do assistente.

### Changed

- Três controles superiores permanecem discretos até receberem hover ou foco do teclado.
- Busca local reconhece nomes naturais, plurais e documentos PDF.
- Contexto curto permite repetir consultas locais de leitura sem autorizar ações ambíguas.
- Falhas conhecidas apresentam causa provável e uma próxima ação segura.

### Security

- Aplicativos, URLs e caminhos são validados independentemente antes da execução.
- Protocolos inseguros, operadores de shell, elevação e comandos críticos permanecem bloqueados.
- Alterações apresentam prévia e exigem confirmação; destinos existentes não são sobrescritos.
- Remoção permanente não é oferecida e ações locais geram registros redigidos.

### Validation

- Seis exemplos obrigatórios de ações naturais homologados visualmente na GUI local.
- Vinte tópicos e 39 paráfrases do painel Recursos e ajuda cobertos automaticamente.
- Regressão anterior à promoção da candidata aprovada com 1.136 testes.

## [2.1.0] - 2026-08-30

### Added

- Proteção contra ciclos arquiteturais.
- Matriz persistente de homologação funcional.
- Respostas locais de runtime, instalação e conhecimento Linux.
- Planos determinísticos para consultas anunciadas.

### Changed

- GUI dividida em oito componentes especializados.
- `gui/app.py` reduzido de 2.213 para 1.374 linhas.
- GitHub Actions e CodeQL modernizados.

### Fixed

- Entrega assíncrona de resultados na thread do Tkinter.
- Ações que permaneciam indefinidamente em execução.
- Variações naturais de consultas e ações anunciadas.

### Security

- Ações críticas bloqueadas e ações sensíveis confirmadas.
- Execução com argumentos separados e sem `shell=True`.

### Validation

- 44 de 47 casos aprovados e nenhuma falha.
- Três testes SSH adiados até o segundo computador.

## [2.0.2] - 2026-08-25

### Fixed

- Roteamento local das consultas de endereço IP.
- Lançadores Debian sem uso de `python -c`.
- Entry points sem caminhos temporários do build.
- Limpeza de runtimes obsoletos durante atualizações do pacote.

### Security

- Consulta de IP sem shell e com timeout limitado.
- Auditoria do pacote rejeita lançadores inconsistentes.

### Validation

- 884 testes aprovados na candidata final.
- Quatro variações de consulta de IP validadas pela rota da GUI.


## [2.0.1] - 2026-08-22

### Added

- Pacote Debian único com aplicação, dependências Python, comandos e integração desktop.
- Assistente de primeira configuração para verificar o Ollama e baixar o modelo padrão.
- Auditoria estrutural do `.deb` e publicação automática no GitHub Release.

### Fixed

- Identidade da janela e controle de instância única no desktop.
- Roteamento local de perguntas sobre data, hora, mês e ano sem alucinação do modelo.

### Security

- Nenhum instalador remoto é executado automaticamente pela aplicação.
- Download do modelo usa argumentos fixos e execução sem shell.

## [2.0.0] - 2026-08-22

### Added

- Respostas factuais usando o computador local ou SSH selecionado.
- Catálogo completo de capacidades e comandos Linux na GUI.
- Orquestração coordenada de agentes de sistema, rede, armazenamento e serviços.
- Prévia multiagente com confirmação humana antes da execução.
- Progresso, pausa, retomada, cancelamento, métricas e auditoria na GUI.
- Replanejamento limitado, checkpoints persistentes e recuperação segura.
- Memória aprovada sem aprendizado automático implícito.

### Security

- Destino local ou remoto permanece explícito em todo o fluxo.
- Especialistas não podem elevar privilégios nem delegar ações críticas.
- Replanejamento não amplia silenciosamente o escopo original.
- Contexto compartilhado é limitado às chaves declaradas por tarefa.
- Execução multiagente reutiliza a política e a auditoria remotas centrais.

### Validation

- Operação multiagente local validada visual e funcionalmente.
- Seleção, orquestração, recuperação e controles cobertos por testes.
- Validação SSH real, auditoria final e instalação limpa executadas antes da tag.

## [1.6.0] - 2026-08-21

### Added

- Ciclo de vida controlado para instalação, atualização e desinstalação.
- Configurações portáteis e perfis restritivos de agentes.
- Catálogo de plugins com confiança explícita.
- Integração opcional com VS Code.
- Documentação pública e exemplos reproduzíveis.
- Pipeline auditável com checksums e proveniência.
- Menu expansível para seleção de computadores.

### Security

- Segredos e caminhos privados excluídos das exportações.
- Plugins alterados perdem automaticamente a aprovação.
- Integração VS Code sem shell ou confirmação automática.
- Artefatos inseguros ou divergentes são recusados.
- Proveniência sem chaves privadas armazenadas.

### Validation

- 742 testes automatizados aprovados.
- Arquitetura e documentação aprovadas.
- Ciclo de vida validado em ambiente isolado.
- Wheel, source archive e checksums verificados.

## [1.5.0] - 2026-08-19

### Added

- Tarefas longas com progresso observável.
- Checkpoints, retomada e agendamento seguro.
- Histórico persistente de automações.
- Agentes especializados de sistema, rede, armazenamento e serviços.
- Eventos, métricas e indicador de automações na GUI.

### Security

- Recuperação sempre retorna ao estado pendente.
- Agendamentos sensíveis exigem confirmação.
- Ações críticas não podem ser agendadas ou delegadas.
- Limites de ações, tentativas e duração por agente.
- Elevação automática permanece bloqueada.

### Validation

- Concorrência, persistência, retomada e agendamento validados.
- Isolamento, limites e políticas dos agentes validados.

## [1.4.0] - 2026-08-19

### Added

- Administração remota segura por SSH.
- Inventário persistente de hosts autorizados.
- Diagnóstico e contexto remoto.
- Seleção explícita do destino na GUI.
- Timeout, cancelamento e auditoria separados por host.
- Ambiente SSH real e isolado para testes de integração.

### Security

- Autenticação não interativa exclusivamente por chave.
- Verificação obrigatória por `known_hosts`.
- Elevação automática e shells intermediários bloqueados.
- Matriz remota `LOW`, `MEDIUM`, `HIGH` e `CRITICAL`.
- Proteção contra execução no computador errado.

### Validation

- Integração SSH real e isolada aprovada.
- Identidade, autenticação, timeout e chave não autorizada validados.

## [1.3.0] - 2026-08-19

### Added

- Roteamento entre resposta local, ação segura e conversa.
- Conversação pelo Ollama com memória recente.
- Fast Path adaptativo, sinônimos e aprendizado aprovado.
- Métricas de latência e benchmark por rota.
- Contexto local e perfil automático de saúde.
- Busca segura de arquivos e pastas.
- Ações desktop validadas para pastas, arquivos, sites e aplicativos.
- Evidências reproduzíveis para apresentação do TCC.

### Changed

- Consultas conhecidas deixam de utilizar o Ollama.
- Processos gráficos são iniciados de forma desacoplada.
- Falhas de permissão recebem mensagens específicas.

### Security

- Autoexecução continua exclusiva para risco `LOW`.
- Caminhos, URLs e aplicativos recebem validação antes da execução.
- Nenhuma elevação automática é tentada após falha de permissão.

### Validation

- 609 testes automatizados aprovados antes da auditoria final.
- Validado em notebook CPU-only com aproximadamente 8 GB de RAM.

## [1.2.0] - 2026-08-16

### Added

- GUI Tkinter, launcher, ícone e integração com o Dock.
- Instalador `ubuntu-ai-install-launcher`.
- Assets e instalador incluídos no wheel.
- Autoexecução exclusiva para `LOW`.
- Interrupção cooperativa e atalhos de teclado.
- Matrizes de risco e instalação limpa isolada.

### Changed

- Mensagens de falha da GUI aprimoradas.
- Documentação e arquitetura atualizadas.

### Validation

- Riscos `LOW`, `MEDIUM`, `HIGH` e `CRITICAL` validados.
- Mais de 500 testes automatizados aprovados.

## [0.6.0] - 2026-08-05

### Added

- Framework de planejamento seguro para administração Linux.
- Planejamento determinístico e por IA local com Ollama.
- Runtime com contexto, confirmação, execução controlada e ciclo de vida.
- Memória, conversa, conhecimento local, RAG, aprendizado e reflexão.
- Tool Selection, Execution Intelligence, Skills e Plugin SDK.
- Agent Loop com replanejamento controlado.
- TUI interativa com Rich e experiência visual aprimorada.
- Diagnóstico do runtime local de IA.
- Configuração persistente e logging rotativo.
- Benchmark de Planner e Pipeline com comando `ubuntu-ai benchmark`.
- Comando `ubuntu-ai version` e opção global `--debug`.
- SDK Python por meio de `UbuntuAI`.
- Automação de CI, CodeQL, Dependabot e release por tag.

### Changed

- Versão promovida de `0.6.0rc1` para `0.6.0`.
- README atualizado para apresentar o projeto como framework open source.
- Metadados de empacotamento preparados para instalação com `pipx`.
- Documentação de instalação, contribuição e release consolidada.

### Fixed

- Confiabilidade do planejamento local com Ollama.
- Validação de executáveis na skill shell.
- Normalização de caminhos antes da persistência SQLite.
- Colisões de nomes durante coleta de testes.
- Compatibilidade de logging e benchmark com doubles de teste.

### Validation

- Ruff aprovado.
- Mais de 300 testes automatizados aprovados.
- TUI, benchmark, diagnóstico e fluxo de planejamento validados.

## [0.6.0rc1] - 2026-07-31

### Added

- Primeira candidata à release com auditoria arquitetural e hardening.

Ubuntu AI Assistant v1.1
Objetivo

Melhorar significativamente a experiência do usuário, reduzindo o tempo de resposta para comandos simples e apresentando respostas mais úteis.

Escopo
Fast Path Engine
Response Formatter
stdout automático
ubuntu-ai inicia a TUI por padrão
ubuntu-ai examples
Instalação profissional
Empacotamento (uv tool, .deb)

## Sprint 9 - Builtin Intelligence

### Added
- Semantic normalization
- Builtin metrics
- Network commands
- CPU commands
- Kernel commands
- Hostname commands
- User commands

### Improved
- Expanded builtin vocabulary
- Natural language matching
- Alias coverage

### Tests
- 32 tests passing
