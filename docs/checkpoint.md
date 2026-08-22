# Ubuntu AI Assistant — Development Checkpoint

> Última atualização: 2026-08-22

## Estado atual

- Versão candidata: `2.0.0`;
- Branch: `develop/v2.0`;
- V2-P1, V2-P2 e V2-P3: concluídos;
- V2-P4-R1: experiência multiagente integrada e publicada;
- V2-P4-R2: validação SSH, artefatos e fechamento da release.

## Capacidades da v2.0

- contexto factual real do computador selecionado;
- catálogo completo de recursos e comandos Linux;
- seleção de especialistas por domínio explícito;
- orquestração limitada de sistema, rede, armazenamento e serviços;
- prévia e confirmação antes da execução multiagente;
- progresso, pausa, retomada e cancelamento cooperativos;
- métricas, histórico e auditoria sem payloads secretos;
- replanejamento seguro sem ampliação silenciosa de escopo;
- retomada por checkpoints e memória somente após aprovação;
- operação local ou SSH com destino sempre visível.

## Segurança

- nenhuma elevação automática de privilégios;
- ações críticas não são delegadas a especialistas;
- confirmação e política de risco permanecem centralizadas;
- contexto compartilhado é mínimo e declarado;
- execução SSH exige inventário, chave e `known_hosts` explícitos;
- aprendizado automático não aprovado permanece bloqueado.

## Evidências principais

- `docs/releases/v2-p1-r1-local-assistance-validation.md`;
- `docs/releases/v2-p1-r2-selected-context-validation.md`;
- `docs/releases/v2-p2-r1-orchestration-foundation-validation.md`;
- `docs/releases/v2-p2-r2-specialist-selection-validation.md`;
- `docs/releases/v2-p3-r1-safe-replanning-validation.md`;
- `docs/releases/v2-p3-r2-persistent-recovery-validation.md`;
- `docs/releases/v2-p4-r1-integrated-experience-validation.md`;
- `docs/releases/v2-p4-r2-release-validation.md`;
- `docs/releases/v2.0.0.md`.

## Fechamento pendente

- validar diagnóstico multiagente em destino SSH real e isolado;
- executar suíte, arquitetura, documentação e auditoria dos artefatos;
- validar instalação, atualização e desinstalação limpas;
- criar e publicar a tag `v2.0.0`.
