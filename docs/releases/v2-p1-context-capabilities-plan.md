# V2-P1 — Contexto, comandos e descoberta de recursos

## Problema observado

A pergunta `qual a versão do Ubuntu?` foi encaminhada para a rota de conversa
por IA. A resposta explicou como consultar a versão, mas não apresentou a
informação real do computador selecionado.

O usuário também não possui uma forma central de descobrir tudo o que o
assistente pode fazer.

## Resultado esperado

O assistente deve reconhecer consultas factuais sobre o sistema e responder
com dados reais do destino selecionado, sem depender do Ollama.

Também deve oferecer ajuda determinística sobre comandos Linux e um catálogo
navegável das capacidades disponíveis.

## Áreas do catálogo

- informações do computador;
- diagnóstico do sistema;
- comandos Linux;
- arquivos e diretórios;
- processos e desempenho;
- armazenamento;
- rede;
- serviços;
- pacotes e aplicativos;
- ações no desktop;
- administração remota por SSH;
- automações e tarefas longas;
- agentes especializados;
- conhecimento e conversação;
- configurações, perfis e plugins;
- ciclo de vida do aplicativo;
- integração com VS Code.

## Regras

- consultas factuais usam coletores seguros e somente leitura;
- o computador de destino deve estar explícito;
- explicações de comandos não autorizam execução;
- comandos perigosos devem apresentar alerta;
- nenhuma elevação automática deve ser tentada;
- respostas locais devem ter prioridade sobre o modelo conversacional;
- falhas de permissão devem ser diferentes de recursos inexistentes.

## Exemplos de aceitação

- `qual a versão do Ubuntu?`;
- `qual é o kernel deste computador?`;
- `quanto tenho de memória?`;
- `mostre os principais comandos Linux`;
- `explique o comando chmod`;
- `qual comando localiza arquivos?`;
- `mostre os comandos instalados`;
- `o que você pode fazer?`;
- `ajuda sobre rede`;
- `mostre exemplos de solicitações`.
