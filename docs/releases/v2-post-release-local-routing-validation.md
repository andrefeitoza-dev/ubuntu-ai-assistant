# Hotfix v2 — respostas temporais locais

## Problema

Consultas simples com variações de linguagem, como `mostre o dia e mês atuais`,
eram enviadas ao modelo local. O modelo poderia responder com datas inventadas
e apresentava latência desnecessária.

## Correção

- reconhecimento flexível de solicitações de data;
- reconhecimento de dia e mês combinados;
- reconhecimento de mês, ano e horário atuais;
- normalização de acentos, pontuação e variações de frase;
- resposta baseada exclusivamente no relógio do computador;
- roteamento local obrigatório para essas consultas.

## Frases validadas

- `que mês estamos?`;
- `qual é o mês atual?`;
- `mostre o dia e mês atuais`;
- `que dia e mês estamos?`;
- `qual é a data atual?`;
- `que ano estamos?`;
- `mostre as horas`.

## Resultado funcional

Na validação de 22 de agosto de 2026, o assistente respondeu com agosto de 2026
pela rota local, sem consultar o Ollama.
