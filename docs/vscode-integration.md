# Integração com VS Code

A extensão em `integrations/vscode` é opcional e não faz parte do runtime
principal. Ela chama apenas os entry points públicos `ubuntu-ai` e
`ubuntu-ai-gui`.

## Capacidades

- abrir a GUI;
- executar `doctor` e `health`;
- gerar planos sem executar;
- gerar prévias com `run --dry-run`;
- listar perfis restritivos.

## Segurança

- nenhum shell é aberto;
- entradas são argumentos estruturados;
- executáveis configurados precisam usar o nome esperado;
- não existe comando de execução confirmada na extensão;
- confirmação, risco e execução permanecem no aplicativo principal.

## Desenvolvimento local

Abra `integrations/vscode` no VS Code e pressione `F5`. Para verificar a
sintaxe:

```bash
cd integrations/vscode
npm test
```
