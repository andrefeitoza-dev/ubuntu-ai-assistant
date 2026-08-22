# V2-P2-R1 — Fundação de orquestração multiagente

## Escopo

- modelos imutáveis para objetivos, tarefas, dependências e resultados;
- validação do grafo antes de qualquer despacho;
- coordenação determinística dos especialistas de sistema, rede, armazenamento e serviços;
- compartilhamento explícito e mínimo de contexto por tarefa;
- política de risco e confirmação aplicada pelo coordenador central;
- progresso e resultado individual observáveis.

## Limites de segurança

- o orquestrador não executa comandos;
- somente agentes especializados podem receber tarefas desta camada;
- ciclos, tarefas duplicadas e dependências ausentes são rejeitados;
- contexto não declarado não é compartilhado;
- ações `CRITICAL` continuam bloqueadas;
- ações sensíveis continuam dependentes de confirmação explícita.

## Validação automatizada

- ordenação de dependências;
- rejeição de grafos inválidos;
- isolamento de contexto;
- bloqueio central de ação sensível sem confirmação;
- acompanhamento de progresso e resultados.
