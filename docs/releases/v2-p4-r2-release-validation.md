# V2-P4-R2 — Validação e fechamento da release

## Escopo

- metadados e documentação atualizados para `2.0.0`;
- workflow de publicação vinculado às notas da v2.0;
- validador funcional para diagnóstico multiagente SSH;
- verificação de destino explícito e dos quatro comandos somente leitura;
- comprovação dos registros de auditoria concluídos;
- preparação para auditoria de artefatos e ciclo de vida limpo.

## Critérios de segurança

- o destino `local` é recusado pelo validador SSH;
- o plano deve manter ambiente remoto e nome do host selecionado;
- somente `uptime`, `ip route`, `df -h` e `systemctl --failed` são aceitos;
- a execução usa a engine comum, com política e auditoria centralizadas;
- a validação não recebe senhas, tokens ou chaves pela linha de comando.

## Evidência pendente antes da tag

- saída da validação SSH real;
- suíte completa e auditoria arquitetural;
- documentação estrita;
- wheel e source archive auditados;
- checksums verificados;
- instalação, atualização e desinstalação limpas.

## Validação SSH real e isolada

- servidor efêmero limitado a `127.0.0.1`;
- autenticação exclusivamente por chave aprovada;
- verificação obrigatória de `known_hosts`;
- chave não autorizada recusada;
- timeout com encerramento aprovado;
- agentes de sistema, rede, armazenamento e serviços executados;
- `uptime`, `ip route`, `df -h` e `systemctl --failed` concluídos;
- quatro resultados com código de saída `0`;
- oito eventos de auditoria registrados;
- inventário e dados normais do usuário não foram alterados.

## Auditoria final

- suíte completa aprovada;
- arquitetura e integridade aprovadas;
- documentação construída em modo estrito;
- metadados `2.0.0` consistentes;
- wheel e source archive auditados;
- checksums SHA-256 gerados e verificados;
- instalação, atualização e remoção aprovadas em ambiente limpo.
