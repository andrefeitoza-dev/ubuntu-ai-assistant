# V2-P5 — Distribuição Debian simplificada

## Objetivo

Permitir que outro usuário instale o Ubuntu AI Assistant por um único arquivo
`.deb`, sem clonar o repositório e sem conhecer Python, Git ou uv.

## Implementação

- runtime Python 3.12, aplicação e dependências Python incorporados ao pacote;
- comandos globais e entrada no menu do Ubuntu;
- assistente de primeira configuração do runtime local;
- construtor determinístico e auditor estrutural do `.deb`;
- CI e release preparados para publicar e verificar o novo artefato.

## Limites intencionais

- o modelo não integra o pacote porque ocupa alguns gigabytes;
- o Ollama não é instalado por script remoto silencioso;
- a primeira candidata cobre Ubuntu 22.04 ou superior em `amd64` sem depender
  da versão do Python instalada no sistema.

## Validação real em segundo notebook

- equipamento: MacBook Air com Ubuntu 22.04 e Python 3.10 do sistema;
- primeira candidata recusada corretamente por exigir Python 3.12 do sistema;
- pacote corrigido passou a incorporar Python 3.12.13 e Tkinter 9.0;
- checksum SHA-256 aprovado antes da instalação;
- instalação real pelo `apt` aprovada;
- pacote `ubuntu-ai-assistant 2.0.1 amd64` confirmado pelo `dpkg-query`;
- comando de versão confirmou Python 3.12.13 incorporado e Ollama 0.30.8;
- configuração detectou e instalou o modelo `qwen2.5:3b`;
- ícone apresentado corretamente no menu de aplicativos;
- interface gráfica e respostas funcionais aprovadas pelo usuário.

## Validação ainda necessária

- remoção do pacote preservando configurações e dados do usuário;
- reconstrução final pelo CI antes da tag `v2.0.1`.

## Validação de remoção e reinstalação

- pacote removido pelo `apt` no segundo notebook;
- comandos e entrada desktop removidos corretamente;
- configurações, dados e estado do usuário preservados;
- pacote portátil reinstalado pelo mesmo arquivo `.deb`;
- versão `2.0.1` confirmada após a reinstalação;
- Ollama e modelo local permaneceram disponíveis;
- validação aprovada pelo usuário.
