# Changelog

## 0.6.0-rc.1 — Em preparação

### Added

- Auditoria arquitetural RC1.1.
- Documentação atualizada de arquitetura e roadmap.
- Script reproduzível de métricas arquiteturais.

### Fixed

- Confiabilidade do planejamento local com Ollama.
- Validação de executáveis na skill shell.
- Normalização de caminhos antes da persistência SQLite.

### Validation

- Fluxo TUI completo validado com planejamento, confirmação e execução.
- 266 testes automatizados aprovados na base auditada.

## Unreleased

### Added

- DevOps Foundation
- GitHub Actions
- Coverage
- Pre-commit
- CodeQL
- Dependabot
- Releases automáticas

## [0.6.0rc1] - 2026-07-31

### Added

- Comando `ubuntu-ai version` com versão do pacote, Python, Ollama e modelo.
- Opção global `--debug` para preservar exceções e tracebacks durante diagnóstico.
- Tratamento uniforme de falhas operacionais da CLI.

### Changed

- Versão do pacote atualizada para `0.6.0rc1`.
- Comandos `plan` e `tui` agora exibem mensagens amigáveis no modo normal.
