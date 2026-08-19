# Ubuntu AI Assistant — Development Checkpoint

> Última atualização: 2026-08-19

## Estado atual

- Versão: `1.4.0`
- Branch: `develop/v1.4`
- Release `v1.3.0`: concluída e publicada
- R1, R2 e R3 da v1.4: concluídos
- R4: auditoria e release final

## Funcionalidades validadas

- respostas locais rápidas e conversa pelo Ollama;
- contexto inteligente do computador local;
- ações desktop e pesquisas locais seguras;
- administração remota por SSH;
- inventário persistente de hosts autorizados;
- autenticação por chave e validação de `known_hosts`;
- diagnóstico remoto;
- seleção explícita do destino na GUI;
- timeout e cancelamento remoto;
- matriz de risco remoto completa;
- auditoria e histórico separados por host.

## Segurança remota

O assistente não utiliza senha SSH interativa, não tenta elevar privilégios
automaticamente e não executa comandos por shells intermediários. O destino
permanece visível, e alterações exigem confirmação proporcional ao risco.

## Evidências da v1.4

- `docs/releases/v1.4-r1-foundation-validation.md`
- `docs/releases/v1.4-r2-context-execution-validation.md`
- `docs/releases/v1.4-r3-gui-audit-validation.md`
- `docs/releases/v1.4-ssh-integration-validation.md`
- `docs/releases/v1.4.0.md`

## Próxima evolução

A v1.5 será dedicada a automação, tarefas longas e agentes especializados.
