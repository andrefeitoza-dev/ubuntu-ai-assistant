# Ubuntu AI Assistant para VS Code

Integração opcional que utiliza exclusivamente os entry points públicos do
Ubuntu AI Assistant.

## Comandos

- abrir a GUI;
- verificar ambiente e saúde;
- gerar um plano sem execução;
- gerar uma prévia obrigatoriamente com `--dry-run`;
- listar perfis de agentes.

A extensão não executa comandos confirmados, não abre shell e não replica a
política de risco. Processos recebem argumentos estruturados com `shell: false`.

## Desenvolvimento

```bash
cd integrations/vscode
npm test
```

Use `F5` no VS Code para iniciar um Extension Development Host.
