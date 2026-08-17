# Ubuntu AI Assistant — Development Checkpoint

> Última atualização: 2026-08-16

## Estado atual

- Versão: `1.2.0`
- Branch: `develop/v1.2`
- Fase: G4 — preparação final da release
- G1, G2 e G3: concluídas
- G4: auditoria final pendente

## Funcionalidades validadas

- GUI Tkinter moderna;
- launcher no menu e no Dock;
- ícone e assets no wheel;
- comando `ubuntu-ai-install-launcher`;
- instalação e desinstalação isoladas;
- autoexecução para `LOW`;
- confirmação para `MEDIUM`, `HIGH` e `CRITICAL`;
- mensagens amigáveis e interrupção cooperativa;
- atalhos `Esc` e `Ctrl+L`;
- CLI, TUI, GUI e SDK preservados.

## Segurança

Somente planos `LOW` podem executar automaticamente. Planos sensíveis aguardam
confirmação e podem ser cancelados sem chamar o executor.

## Evidências

- `docs/releases/v1.2.0-risk-validation.md`
- `docs/releases/v1.2.0-installation-validation.md`
- `docs/releases/v1.2.0.md`

## Próxima tarefa

Executar auditoria final, validar build e working tree e criar a tag `v1.2.0`.

## Próxima evolução

Tornar o assistente mais inteligente e rápido com sinônimos, similaridade de
intenções, aprendizado aprovado, Fast Path adaptativo e menor uso do Ollama.
