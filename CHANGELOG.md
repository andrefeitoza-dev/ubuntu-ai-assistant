# Changelog

Todas as mudanças relevantes deste projeto são registradas neste arquivo.

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
