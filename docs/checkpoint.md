# Ubuntu AI Assistant — Development Checkpoint

> Última atualização: 2026-08-18

## Estado atual

- Versão-base: `1.2.0`
- Branch: `develop/v1.3`
- Release `v1.2.0`: concluída
- Fase atual: v1.3 — inteligência, conversa e desempenho

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
- respostas locais instantâneas;
- cancelamento protegido contra resultados antigos;
- roteamento entre resposta local, ação auditável e conversa;
- conversa geral pelo Ollama sem criar planos executáveis;
- histórico recente incorporado às respostas conversacionais.

## Segurança

Somente planos `LOW` podem executar automaticamente. Planos sensíveis aguardam
confirmação e podem ser cancelados sem chamar o executor.

## Evidências

- `docs/releases/v1.2.0-risk-validation.md`
- `docs/releases/v1.2.0-installation-validation.md`
- `docs/releases/v1.2.0.md`

## Próxima tarefa

Validar o roteador conversacional na GUI real e avançar para sinônimos,
similaridade de intenções, aprendizado aprovado e métricas de latência.
