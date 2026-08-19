# Instalação e ciclo de vida

## Requisitos

- Ubuntu ou Linux compatível;
- Python 3.12 ou superior;
- `uv`;
- Ollama apenas para recursos de IA local.

## Instalação isolada

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
