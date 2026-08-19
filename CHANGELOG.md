# Changelog

Todas as mudanças relevantes deste projeto são registradas neste arquivo.

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
