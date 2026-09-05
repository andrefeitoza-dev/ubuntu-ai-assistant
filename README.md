# Ubuntu AI Assistant

Framework local e extensível para construir agentes inteligentes voltados à administração segura de sistemas Linux, com foco inicial no Ubuntu.

O Ubuntu AI transforma solicitações em linguagem natural em planos auditáveis, apresenta um preview, aplica políticas de risco, solicita confirmação quando necessário e executa comandos de forma controlada.

## Recursos atuais

- GUI desktop moderna em Tkinter;
- launcher, ícone e integração com o Dock do Ubuntu;
- planejamento determinístico e por IA local com Ollama;
- roteamento entre resposta local, ação segura e conversa;
- Fast Path adaptativo com sinônimos e similaridade;
- aprendizado somente após sucesso e aprovação;
- contexto automático do computador;
- consultas locais de sistema, CPU, memória, disco, rede e serviços;
- busca segura de arquivos e pastas;
- perfil automático de saúde do computador;
- abertura validada de pastas, arquivos, sites e aplicativos;
- autoexecução exclusiva para planos `LOW`;
- confirmação para riscos `MEDIUM`, `HIGH` e `CRITICAL`;
- mensagens de permissão sem elevação automática;
- cancelamento confiável de operações;
- benchmark reproduzível por rota;
- mais de 600 testes automatizados.

- administração remota segura por SSH;
- inventário de computadores Ubuntu autorizados;
- diagnóstico remoto de sistema, CPU, memória, disco, rede e serviços;
- seleção explícita e visível do computador de destino;
- timeout, cancelamento e auditoria separados por host;

- tarefas longas com progresso, pausa e cancelamento;
- persistência de checkpoints e retomada segura;
- agendamento protegido por classificação de risco;
- agentes especializados em sistema, rede, armazenamento e serviços;
- observabilidade estruturada e progresso na GUI;
- instalação, atualização e desinstalação controladas;
- configurações portáteis sem segredos;
- perfis restritivos de agentes;
- catálogo local com confiança explícita de plugins;
- integração opcional e segura com VS Code;
- catálogo visível de recursos e comandos Linux;
- contexto factual do computador local ou SSH selecionado;
- orquestração multiagente de sistema, rede, armazenamento e serviços;
- prévia e confirmação antes da execução multiagente;
- progresso, pausa, retomada, cancelamento e auditoria na GUI;
- replanejamento limitado e recuperação por checkpoints;

## Requisitos

- Ubuntu ou distribuição Linux compatível;
- Python 3.12 ou superior;
- Ollama para funcionalidades de IA local.

Para máquinas com aproximadamente 8 GB de RAM:

```bash
ollama pull qwen2.5:3b
```

## Instalação isolada

### Ubuntu — pacote único recomendado

Baixe `ubuntu-ai-assistant_2.3.0_amd64.deb` na release e abra o arquivo pela
Central de Aplicativos ou execute:

```bash
sudo apt install ./ubuntu-ai-assistant_2.3.0_amd64.deb
```

O pacote instala o runtime Python 3.12, a aplicação, suas dependências, os
comandos, o ícone e a entrada no menu. Portanto, também funciona no Ubuntu
22.04, cujo Python padrão é o 3.10. O modelo local não é incorporado ao `.deb` porque ocupa
alguns gigabytes. Depois de instalar o Ollama, sua preparação é guiada por:

- abra **Configurar Ubuntu AI Assistant** no menu de aplicativos; ou
- use o terminal:

```bash
ubuntu-ai-setup --pull-model
```

### Instalação de desenvolvimento com uv

```bash
uv tool install ubuntu-ai-assistant
ubuntu-ai-install-launcher
ubuntu-ai version
ubuntu-ai doctor
```

Consulte [instalação e ciclo de vida](docs/installation.md) para atualização,
wheel local e desinstalação.

Para desenvolvimento:

```bash
uv sync --all-extras --dev
uv run ruff check src tests
uv run ruff format --check src tests
uv run pytest
```

## Uso rápido

```bash
ubuntu-ai doctor
ubuntu-ai diagnose-ai
ubuntu-ai benchmark
ubuntu-ai plan "mostrar o diretório atual"
ubuntu-ai run --dry-run "mostrar os serviços com falha"
ubuntu-ai lifecycle status
ubuntu-ai ecosystem profiles
ubuntu-ai tui
ubuntu-ai-gui
```

Na TUI:

```text
Objetivo> mostrar o diretório atual
Confirmar este plano? y
```

## Fluxo seguro

```text
Objetivo → Contexto → Planejamento → Preview → Reflexão → Confirmação
        → Preflight → Política → Execução → Memória → Aprendizado
```

Nenhum plano ou replanejamento deve executar sem passar pelas regras de confirmação aplicáveis.

## SDK

```python
from ubuntu_ai import UbuntuAI

assistant = UbuntuAI()
result = assistant.plan("mostrar o diretório atual")
print(result.rendered_preview)
```

## Documentação

- `docs/architecture.md` — arquitetura atual;
- `docs/installation.md` — instalação e ciclo de vida;
- `docs/configuration-profiles-plugins.md` — ecossistema extensível;
- `docs/vscode-integration.md` — integração opcional com VS Code;
- `docs/troubleshooting.md` — solução de problemas;
- `docs/examples.md` — exemplos reproduzíveis;
- `docs/project-context.md` — contexto técnico do projeto;
- `docs/roadmap.md` — roadmap;
- `docs/releases/` — notas das RCs e releases;
- `docs/adr/` — decisões arquiteturais;
- `CONTRIBUTING.md` — guia para contribuições.

## Estado do projeto

A versão `2.0` consolida o Ubuntu AI Assistant como plataforma multiagente para
operações locais e SSH. Contexto, destino, confirmação, política de risco,
progresso e auditoria permanecem explícitos; não existe autonomia irrestrita.

## Licença

MIT.
