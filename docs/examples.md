# Exemplos reproduzíveis

## Diagnóstico local

```bash
ubuntu-ai doctor
ubuntu-ai health
ubuntu-ai plan "mostre o uso de memória"
ubuntu-ai run --dry-run "mostre os serviços com falha"
```

## Ciclo de vida sem alteração

```bash
ubuntu-ai lifecycle status
ubuntu-ai lifecycle update --version 1.6.0 --dry-run
ubuntu-ai lifecycle uninstall --dry-run
```

## Configuração e perfis

```bash
ubuntu-ai ecosystem export-config /tmp/ubuntu-ai-config.toml
ubuntu-ai ecosystem profiles
```

## Catálogo de plugins

```bash
ubuntu-ai ecosystem scan-plugins ~/.local/share/ubuntu-ai/plugins
```

O comando apenas inspeciona. Não importa nem inicializa código do plugin.
