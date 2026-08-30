# Processo de release

## Pipeline contínuo

Cada push e pull request executa Ruff, testes com cobertura, auditoria de
arquitetura, build estrito da documentação e construção dos artefatos.

O wheel e o source archive são inspecionados antes do upload. O auditor rejeita
arquivos de backup, bytecode, caminhos inseguros, versão divergente e ausência
de recursos essenciais.

## Integridade

O arquivo `SHA256SUMS` é gerado de forma determinística:

```bash
uv build
uv run python scripts/release_artifacts.py validate dist
uv run python scripts/release_artifacts.py checksums dist
uv run python scripts/release_artifacts.py verify dist
```

## Proveniência e assinatura

O GitHub Actions emite um atestado de proveniência usando OIDC. A assinatura é
vinculada ao workflow e ao commit da tag, sem armazenar chave privada ou segredo
de assinatura no repositório.

## Publicação

A tag deve corresponder exatamente à versão do `pyproject.toml`. O workflow da
tag repete toda a auditoria, valida o ciclo de vida em ambiente isolado e publica
wheel, source archive e `SHA256SUMS` na GitHub Release.

O pacote Debian e o arquivo de checksums também fazem parte do atestado de
proveniência. A futura distribuição por APT deverá reutilizar exatamente esses
artefatos, sem reconstrução fora do workflow da tag.
