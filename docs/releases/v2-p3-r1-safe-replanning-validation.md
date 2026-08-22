# V2-P3-R1 — Análise e replanejamento seguro

## Escopo

- análise estruturada de falhas em resultados parciais da orquestração;
- preservação explícita das tarefas já concluídas;
- classificação determinística da falha e plano de recuperação existente;
- alternativa limitada somente para falhas transitórias autorizadas;
- justificativa registrada para tentativa ou bloqueio;
- objetivo de recuperação separado do objetivo original.

## Garantias de segurança

- a alternativa mantém o mesmo especialista e as mesmas ações;
- ambiente, destino, confirmação e contexto mínimo são preservados;
- dependências concluídas não são repetidas;
- permissão, recurso ausente e falha desconhecida exigem revisão;
- o limite de tentativas não pode ser ultrapassado;
- resultados e tarefas estranhos ao objetivo são rejeitados;
- nenhum aprendizado ou execução automática foi adicionado.

## Validação automatizada

- resultado parcial com recuperação de rede;
- filtragem de contexto sensível;
- bloqueio de permissão, recurso ausente e causa desconhecida;
- limite máximo de tentativas;
- rejeição de resultado ou tarefa de outro objetivo;
- justificativa explicável para cada decisão.
