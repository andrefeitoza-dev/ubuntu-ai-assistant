# Ubuntu AI Assistant

Framework local e extensível para construir agentes inteligentes voltados à administração segura de sistemas Linux, com foco inicial no Ubuntu.

O Ubuntu AI transforma solicitações em linguagem natural em planos auditáveis, apresenta um preview, aplica políticas de risco, solicita confirmação quando necessário e executa comandos de forma controlada.

## Recursos da v1.3.0

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

## Requisitos

- Ubuntu ou distribuição Linux compatível;
- Python 3.12 ou superior;
- Ollama para funcionalidades de IA local.

Para máquinas com aproximadamente 8 GB de RAM:

```bash
ollama pull qwen2.5:3b
```

## Instalação com pipx

Depois de baixar ou clonar o projeto:

```bash
pipx install .
ubuntu-ai-install-launcher
ubuntu-ai version
ubuntu-ai doctor
```

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
- `docs/project-context.md` — contexto técnico do projeto;
- `docs/roadmap.md` — roadmap;
- `docs/releases/` — notas das RCs e releases;
- `docs/adr/` — decisões arquiteturais;
- `CONTRIBUTING.md` — guia para contribuições.

## Estado do projeto

A versão `1.3.0` consolida o Ubuntu AI Assistant como aplicação desktop
inteligente, rápida, contextual e segura. Consultas conhecidas são resolvidas
localmente em microssegundos ou milissegundos, enquanto o Ollama permanece
reservado para conversação e raciocínio.

Esta é a versão preparada para apresentação do TCC. As próximas versões
avançarão para administração remota, automação, agentes especializados,
distribuição e colaboração multiagente.

## Licença

MIT.
