# V2-P1 R1 — Contexto local e descoberta de recursos

## Objetivo

Corrigir o encaminhamento de perguntas factuais do computador e tornar os
recursos do assistente descobríveis sem depender do Ollama.

## Implementação

- consultas sobre Ubuntu, kernel, arquitetura, hostname, CPU, memória, disco,
  processos e rede usam coletores locais somente de leitura;
- a versão do Ubuntu é obtida de `/etc/os-release`, com fallback de plataforma;
- perguntas conceituais continuam na conversa e não são confundidas com fatos;
- destinos SSH nunca recebem silenciosamente dados do computador local;
- comandos Linux possuem categorias, descrições, exemplos e alertas;
- comandos executáveis instalados podem ser pesquisados sem execução;
- programas instalados são consultados no inventário real do `dpkg`, com saída limitada;
- o catálogo apresenta as áreas atendidas e exemplos de solicitações;
- a GUI possui o painel `Recursos e ajuda`, com vinte tópicos;
- subitens, exemplos, risco e disponibilidade aparecem somente após seleção.
- somente a categoria escolhida é enviada à conversa por ação explícita;
- reabrir o painel existente não duplica conteúdo no histórico.

## Segurança

- nenhuma consulta usa shell ou elevação de privilégios;
- explicar um comando não autoriza sua execução;
- comandos destrutivos ou administrativos exibem alerta;
- contexto local não é apresentado como se pertencesse a um destino remoto.

## Validação

- roteamento factual local;
- separação entre fatos e explicações conceituais;
- catálogo de comandos e capacidades;
- alertas para `rm`, `chmod`, `chown` e `kill`;
- proteção contra vazamento de contexto local em destino remoto;
- integração estrutural do botão `Recursos` na GUI.

## Continuidade

O próximo incremento do V2-P1 deverá responder às mesmas perguntas usando o
contexto SSH real, além de ampliar bateria, endereços de rede e serviços.

## Validação visual da GUI

- catálogo completo acessível por `Recursos e ajuda`;
- menu nativo substituído por painel interno;
- descrição atualizada com transição curta e sem piscadas;
- painel limitado ao interior da janela principal;
- `Esc` fecha integralmente o painel;
- minimizar a aplicação não deixa janelas auxiliares visíveis;
- clique externo fecha o painel;
- botão `Computador` funciona no mesmo clique;
- controles do computador recolhem ao clicar fora;
- destino selecionado permanece visível;
- validação visual aprovada pelo usuário.
