# Ubuntu AI Assistant — Product Architecture

## 1. Visão

O Ubuntu AI Assistant é uma plataforma de administração e automação do Ubuntu
orientada por inteligência artificial.

O sistema interpreta solicitações em linguagem natural, gera planos estruturados,
avalia riscos e executa ações somente após a aprovação do usuário.

## 2. Objetivos

- Administrar o Ubuntu por linguagem natural
- Diagnosticar problemas do sistema
- Criar planos antes de executar alterações
- Explicar comandos e impactos
- Executar tarefas com segurança
- Integrar modelos locais por meio do Ollama
- Suportar servidores remotos via SSH
- Permitir ferramentas e plugins adicionais

## 3. Modos de operação

### Doctor Mode

Verifica a saúde do ambiente:

- Python
- sistema operacional
- CPU
- memória
- Git
- Ollama
- modelos instalados

### Chat Mode

Permite conversar com o modelo local sem executar alterações no sistema.

### Plan Mode

Transforma uma solicitação em um plano estruturado.

Exemplo:

> Instale Docker e configure PostgreSQL.

Resultado esperado:

1. Verificar requisitos
2. Atualizar os repositórios
3. Instalar Docker
4. Habilitar o serviço
5. Criar volume
6. Criar PostgreSQL
7. Testar a conexão

### Explain Mode

Explica:

- comandos que serão utilizados
- impacto esperado
- riscos
- possibilidade de reversão

### Execute Mode

Executa um plano aprovado, etapa por etapa.

### Remote Mode

Executa diagnósticos e planos em servidores Ubuntu via SSH.

## 4. Fluxo principal

```text
Usuário
   |
   v
CLI
   |
   v
Core Engine
   |
   +--> Intent Analyzer
   |
   +--> Planner
   |
   +--> Risk Evaluator
   |
   +--> Permission Manager
   |
   +--> Executor
   |
   v
Tool Registry
   |
   +--> System Tools
   +--> Filesystem Tools
   +--> APT Tools
   +--> Docker Tools
   +--> Git Tools
   +--> Network Tools
   +--> SSH Tools
   |
   v
Ubuntu