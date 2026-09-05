# Instalação e ciclo de vida

## Requisitos

- Ubuntu ou Linux compatível;
- Python 3.12 ou superior;
- `uv`;
- Ollama apenas para recursos de IA local.

## Instalação isolada

### Pacote Ubuntu pela GitHub Release

Para usuários finais, o caminho recomendado é baixar na página de Releases do
GitHub o arquivo `.deb` correspondente à arquitetura e o `SHA256SUMS`. Antes da
instalação, valide a integridade no diretório do download:

```bash
sha256sum --check SHA256SUMS --ignore-missing
sudo apt install ./ubuntu-ai-assistant_VERSION_ARQUITETURA.deb
```

O pacote inclui o runtime necessário, os comandos e a entrada no menu. O Ollama
e o modelo local permanecem separados por causa do tamanho e são preparados
depois pelo atalho **Configurar Ubuntu AI Assistant**. O assistente gráfico abre
as instruções oficiais do Ollama, verifica o serviço e somente baixa o modelo
local depois da autorização do usuário. A alternativa pelo terminal é
`ubuntu-ai-setup --pull-model`.

O mesmo configurador oferece separadamente o modelo oficial leve de voz em
português. O download tem cerca de 31 MB, é validado por SHA-256 e permanece
nos dados privados do usuário. Nenhum áudio é enviado pela internet ou mantido
depois do reconhecimento.

Não é recomendado executar instaladores remotos com `curl | sh`.

### Instalação Python isolada

```bash
uv tool install ubuntu-ai-assistant
ubuntu-ai-install-launcher
ubuntu-ai version
ubuntu-ai doctor
```

Também é possível instalar um wheel local validado:

```bash
ubuntu-ai lifecycle install --wheel /caminho/absoluto/pacote.whl
```

## Atualização

```bash
ubuntu-ai lifecycle update
```

Para uma versão ou wheel específico:

```bash
ubuntu-ai lifecycle update --version 1.6.0
ubuntu-ai lifecycle update --wheel /caminho/absoluto/pacote.whl
```

As operações mostram o plano e pedem confirmação. Use `--dry-run` para não
alterar o computador.

## Desinstalação

```bash
ubuntu-ai lifecycle uninstall
```

Launcher, entrada desktop, ícone e pacote são removidos. Configuração, dados,
estado, logs e histórico permanecem preservados.

## Distribuição futura por um comando

O caminho previsto para `apt install ubuntu-ai-assistant` é publicar um
repositório APT HTTPS com metadados `InRelease` assinados, rotação documentada
de chaves e os mesmos artefatos auditados da GitHub Release. Essa etapa não deve
ser simulada com um script de instalação: depende de hospedagem estável,
assinatura, política de atualização e testes em versões Ubuntu suportadas.
