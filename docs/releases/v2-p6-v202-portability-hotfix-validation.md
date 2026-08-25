# V2-P6 — Portabilidade e roteamento local da v2.0.2

## Origem

A instalação pública da v2.0.1 foi validada em um segundo notebook com Ubuntu
22.04. O runtime Python incorporado, o Ollama, o modelo e a interface gráfica
funcionaram, mas perguntas sobre o IP local seguiram para a conversa com IA.

Também foi constatado que os lançadores Debian executavam módulos por
`python -c`, exibindo `Usage: -c`, enquanto os entry points internos mantinham
o caminho temporário usado durante a construção do pacote.

## Correções

- reconhecer `meu IP`, `IP local`, `endereço IP` e variações equivalentes;
- consultar o IPv4 da rota padrão sem usar Ollama, shell ou privilégios;
- preservar a resposta na rota local compartilhada pela GUI;
- executar os entry points empacotados sem `python -c`;
- reescrever shebangs temporários para o runtime final em `/opt`;
- auditar lançadores públicos e internos dentro do `.deb` extraído.

## Evidência já obtida

As quatro variações de consulta de IP foram aprovadas no segundo notebook por
meio de hotfix reversível. A implementação permanente reproduz esse
comportamento no código-fonte e adiciona cobertura automatizada.

## Pendências para publicação

- executar a suíte completa e a auditoria de arquitetura;
- construir e auditar o novo pacote Debian;
- instalar a candidata em ambiente limpo;
- repetir a validação funcional no segundo notebook;
- atualizar metadados e publicar a tag `v2.0.2`.
