# V2-P4-R1 — Experiência integrada

## Escopo

- painel interno de agentes, tarefas, progresso e auditoria;
- destino selecionado permanentemente visível no cabeçalho e no painel;
- controles cooperativos de pausa, retomada e cancelamento;
- métricas e contagem de eventos sem exibir payloads ou segredos;
- prévia multiagente explícita pelo prefixo `agentes:` ou `multiagente:`;
- confirmação humana entre a prévia e a execução;
- execução observável das quatro consultas somente leitura pela engine comum;
- resultado consolidado com saída resumida de cada especialista;
- seleção de especialistas de sistema, rede, armazenamento e serviços;
- planos somente leitura, sem execução implícita ou elevação de privilégios.

## Segurança

A integração gráfica não cria um executor paralelo. A confirmação proporcional
ao risco, o escopo, o destino e as políticas permanecem centralizados nos
componentes existentes. A prévia multiagente apenas apresenta o plano e os
comandos de leitura que seriam atribuídos aos especialistas.

## Validação automatizada

- contratos do backend para tarefas, métricas, eventos e controles;
- planejamento local e SSH com destino explícito;
- prefixos multiagente sem interferir nas rotas existentes;
- presença estrutural do painel interno e dos controles na GUI;
- qualidade, suíte completa, arquitetura e integridade antes da consolidação.

## Pendente para V2-P4-R2

- validação visual e funcional local, remota e multiagente;
- documentação final da versão;
- auditoria dos artefatos, build e instalação limpa;
- tag `v2.0.0`.

## Validação visual e funcional

- prévia multiagente apresentada corretamente na conversa;
- confirmação humana exigida antes da execução;
- diagnóstico completo executado no computador local;
- agentes de sistema, rede, armazenamento e serviços concluídos;
- progresso registrado como `completed` e `100%`;
- resultados consolidados sem sobreposição do painel;
- painel fechado automaticamente ao concluir;
- nenhuma ação de alteração ou elevação de privilégios executada.
