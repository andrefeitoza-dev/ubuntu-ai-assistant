# Changelog

Todas as mudanças relevantes deste projeto são registradas neste arquivo.

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
