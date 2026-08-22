# V2-P1-R2 — Contexto completo do computador selecionado

## Escopo

- ampliar fatos locais para disco, rede, bateria, processos e serviços;
- responder consultas factuais usando o computador explicitamente selecionado;
- consultar destinos SSH somente com comandos de leitura;
- impedir mistura entre informações locais e remotas;
- manter consultas SSH fora da thread da GUI;
- fixar o destino no início da operação para evitar troca acidental de host.

## Segurança

- nenhuma elevação automática é utilizada;
- nenhum interpretador intermediário de shell é utilizado;
- somente comandos classificados como `LOW` são usados para fatos remotos;
- o nome do computador remoto aparece em todas as respostas;
- falhas e informações indisponíveis são apresentadas sem usar dados locais;
- a política remota e a auditoria existentes continuam centralizadas.

## Consultas cobertas

- sistema operacional e kernel;
- hostname e CPU;
- memória e armazenamento;
- interfaces de rede;
- bateria, quando disponível;
- quantidade de processos;
- serviços em estado de falha;
- resumo completo do destino selecionado.

## Evidências automatizadas

- fatos locais reconhecidos deterministicamente;
- provedores opcionais de bateria e serviços validados;
- consulta remota limitada ao tópico solicitado;
- formatação segura de sistema, memória e disco remotos;
- seleção explícita do host validada no backend;
- execução remota fora da thread da GUI validada estruturalmente.

## Validação visual

- consulta `existem serviços com falha?` respondida com dados reais;
- rota local selecionada corretamente;
- nenhuma ação ou plano executável foi criado;
- resultado apresentado em aproximadamente 51,5 ms;
- identificação do computador permaneceu visível;
- interface permaneceu responsiva;
- validação visual aprovada pelo usuário.
