# Ações naturais seguras — visão v2.2.0

## Objetivo

Permitir que o usuário solicite em linguagem natural tarefas que normalmente
exigiriam interação com o mouse ou comandos de terminal, mantendo validação,
confirmação, limites de execução e auditoria.

O assistente deverá ajudar o usuário a operar o Ubuntu, e não apenas responder
perguntas sobre o sistema.

## Exemplos iniciais obrigatórios

- `Abra a Calculadora.`
- `Abra o LibreOffice.`
- `Abra o Terminal.`
- `Abra o GitHub no Firefox.`
- `Abra https://ubuntu.com.`
- `Abra minha pasta Downloads.`

Também deverão ser reconhecidas variações naturais equivalentes.

## Aplicativos instalados

A descoberta de aplicativos deverá utilizar entradas `.desktop` confiáveis do
Ubuntu, e não executar arbitrariamente qualquer binário encontrado no PATH.

Regras:

- localizar aplicativos em diretórios confiáveis;
- interpretar apenas campos necessários das entradas `.desktop`;
- rejeitar entradas inválidas, incompletas ou suspeitas;
- executar argumentos como lista, nunca por uma linha de shell;
- bloquear elevação, substituição de comandos e operadores de shell;
- informar claramente quando o aplicativo não estiver instalado;
- permitir catálogo explícito de aliases, como Calculadora e LibreOffice;
- registrar aplicativo, origem, argumentos, resultado e duração.

## Sites e URLs

A abertura de sites deverá aceitar somente URLs HTTP e HTTPS válidas.

Regras:

- bloquear `file:`, `javascript:`, `data:` e outros protocolos;
- rejeitar URLs com caracteres de controle ou construção ambígua;
- abrir URLs com navegador confiável e argumentos separados;
- usar confirmação para domínios desconhecidos quando a política determinar;
- não baixar, executar ou instalar conteúdo automaticamente;
- registrar navegador, domínio e resultado;
- permitir aliases confiáveis, como GitHub e documentação do Ubuntu.

## Pastas do usuário

O assistente deverá reconhecer pastas XDG e suas variações localizadas:

- Documentos;
- Downloads;
- Imagens;
- Música;
- Vídeos;
- Área de Trabalho.

Regras:

- resolver o caminho real antes da abertura;
- restringir abertura automática à pasta pessoal;
- impedir fuga por `..`, links simbólicos ou caminhos malformados;
- exigir existência e permissão de acesso;
- não abrir automaticamente diretórios sensíveis do sistema.

## Terminal e comandos

Abrir o aplicativo Terminal é uma ação diferente de executar um comando.

Regras:

- abrir o Terminal pode ser uma ação local de baixo risco;
- comandos nunca devem ser digitados ou executados implicitamente;
- consultas somente leitura podem seguir o planejador seguro;
- alterações exigem avaliação de risco e, quando aplicável, confirmação;
- comandos críticos, elevação não autorizada e padrões proibidos permanecem
  bloqueados;
- nenhuma solicitação pode ser convertida diretamente em `shell=True`.

## Níveis de ação

### Consulta

Exemplos: listar processos, consultar disco e verificar serviços.

- somente leitura;
- comandos previamente permitidos;
- retorno apresentado e auditado.

### Abertura

Exemplos: abrir aplicativo, pasta ou site.

- alvo validado;
- protocolo e origem confiáveis;
- sem execução de conteúdo baixado.

### Alteração controlada

Exemplos: criar pasta, mover arquivo ou modificar configuração autorizada.

- prévia obrigatória;
- avaliação de risco;
- confirmação quando necessária;
- destino e efeitos exibidos antes da execução.

### Ação proibida

Exemplos:

- elevação não autorizada;
- remoção destrutiva ampla;
- execução de conteúdo remoto;
- comandos ofuscados;
- acesso a credenciais;
- desativação de controles de segurança.

Essas ações deverão ser bloqueadas mesmo que um planejador ou modelo as
classifique incorretamente.

## Arquitetura prevista

A implementação deverá separar:

1. normalização da solicitação;
2. resolução de aplicativo, pasta ou URL;
3. validação do alvo;
4. classificação de risco;
5. criação de prévia;
6. confirmação;
7. execução controlada;
8. apresentação do resultado;
9. auditoria.

A IA poderá interpretar a intenção, mas não decidir sozinha o que é seguro.

## Critérios de aceitação

- exemplos obrigatórios funcionando pela GUI;
- variações naturais testadas;
- aplicativos inexistentes tratados claramente;
- URLs inseguras bloqueadas;
- caminhos fora da pasta pessoal bloqueados;
- Terminal aberto sem comando implícito;
- alterações exigindo confirmação;
- comandos críticos bloqueados;
- nenhum uso de `shell=True`;
- testes unitários, funcionais, arquiteturais e visuais;
- matriz de homologação específica;
- funcionamento preservado localmente e por SSH quando aplicável.
