# Intent Domain — Epic 1A

## Objetivo

Introduzir um domínio independente para transformar solicitações textuais em uma
representação estruturada antes da futura integração com o Planner.

## Contratos públicos

- `Intent`: solicitação interpretada.
- `IntentCategory`: categoria funcional.
- `IntentGoal`: objetivo operacional.
- `IntentEntity`: tecnologia ou recurso detectado.
- `IntentEngine`: fachada pública.
- `IntentRepository`: contrato de persistência.

## Estratégia inicial

O Pacote A usa classificação determinística por regras. Isso fornece comportamento
reprodutível, rápido e testável. Provedores baseados em IA poderão implementar o
mesmo contrato em um pacote posterior.

## Compatibilidade

Este pacote é aditivo: o Planner continua recebendo `str`. A migração para o fluxo
Intent First ocorrerá no Epic 1B, preservando compatibilidade durante a transição.
