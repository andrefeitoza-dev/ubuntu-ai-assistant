# Administração remota por SSH

O Ubuntu AI Assistant administra computadores Ubuntu autorizados sem misturar o
destino local com o remoto. A conexão usa chave SSH, verificação de
`known_hosts`, timeout e a mesma política de risco das operações locais.

## Controles da GUI

O botão `Computador: local ▾` mantém o destino atual visível sem ocupar o
cabeçalho com controles pouco usados. Ao clicar, são exibidos:

- `Destino`: seleciona `local` ou um host cadastrado;
- `+`: cadastra hostname, usuário, porta, chave e `known_hosts`;
- `−`: remove o host selecionado do inventário;
- `Diagnosticar`: valida conexão e consulta o contexto do host.

Quando um host remoto está selecionado, seu nome permanece no botão e também no
estado da aplicação. Isso reduz o risco de executar uma solicitação no
computador errado.

## Preparação do servidor

No servidor Ubuntu autorizado:

```bash
sudo apt update
sudo apt install openssh-server
sudo systemctl enable --now ssh
```

No computador do usuário, gere uma chave e autorize somente a chave pública:

```bash
ssh-keygen -t ed25519
ssh-copy-id usuario@servidor
ssh-keyscan -H servidor >> ~/.ssh/known_hosts
```

Confira manualmente a impressão digital antes de confiar no registro produzido
por `ssh-keyscan`.

## Limites de segurança

- senhas não são armazenadas nem solicitadas pela GUI;
- a identidade do servidor não é aceita automaticamente;
- `sudo`, `su`, shells intermediários e elevação automática são bloqueados;
- ações de alteração exigem confirmação proporcional ao risco;
- falhas de permissão são explicadas sem tentativa de contorno.
