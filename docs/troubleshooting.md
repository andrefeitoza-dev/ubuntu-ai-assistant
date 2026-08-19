# Solução de problemas

## O comando não foi encontrado

```bash
ubuntu-ai lifecycle status
command -v ubuntu-ai
command -v ubuntu-ai-gui
```

Confirme que `~/.local/bin` está no `PATH`.

## Ollama está lento ou indisponível

```bash
ubuntu-ai doctor
ubuntu-ai diagnose-ai
ollama ps
```

Consultas determinísticas e ações seguras usam rotas locais. Conversas gerais
podem demorar mais em computadores CPU-only.

## O plugin aparece como untrusted

Inspecione o manifesto, fontes e permissões. Depois, se confiar no conteúdo:

```bash
ubuntu-ai ecosystem trust-plugin /caminho/plugin.toml
```

Qualquer alteração posterior revoga a aprovação.

## Permissão negada

O assistente não tenta `sudo` automaticamente. Execute somente ações
autorizadas para o usuário atual ou ajuste a permissão fora do assistente.

## VS Code não encontra o assistente

Execute `command -v ubuntu-ai` e configure `ubuntuAI.executable` com o
caminho absoluto retornado. O caminho deve terminar em `ubuntu-ai`.
