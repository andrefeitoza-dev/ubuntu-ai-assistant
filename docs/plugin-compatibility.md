# Plugins — compatibilidade, confiança e depreciação

## Contrato público

A API pública de plugins é composta por `UbuntuAIPlugin`, `PluginContext`,
`PluginManifest`, `Skill` e `PLUGIN_API_VERSION`. Plugins não devem importar
objetos internos do container, executor ou políticas.

## Compatibilidade

- o manifesto declara nome, versão, `api_version` e entrypoint;
- a versão segue formato numérico compatível com releases;
- a API precisa coincidir com `PLUGIN_API_VERSION`;
- permissões fora da lista admitida são recusadas;
- a inspeção do catálogo nunca importa o código do plugin.

## Confiança

Plugins são não confiáveis por padrão. A aprovação grava um SHA-256 calculado
sobre manifesto e fontes Python/JSON/TOML. Qualquer alteração revoga a
confiança e impede o carregamento até nova aprovação explícita.

A aprovação não transforma o plugin em processo isolado. Ela complementa a
política de capacidades; não autoriza shell, elevação, confirmação automática
ou acesso aos objetos internos do runtime.

## Estabilidade e depreciação

Mudanças compatíveis preservam a versão da API. Uma remoção ou alteração
incompatível exige nova `PLUGIN_API_VERSION`, documentação de migração e ao
menos uma release minor com aviso de depreciação quando tecnicamente possível.
