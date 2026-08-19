# Configurações, perfis e plugins

## Configuração portátil

```bash
ubuntu-ai ecosystem export-config /caminho/absoluto/config.toml
ubuntu-ai ecosystem import-config /caminho/absoluto/config.toml
```

A exportação exclui segredos e caminhos locais. A importação valida o TOML,
recusa campos potencialmente secretos e preserva os diretórios XDG atuais.

## Perfis de agentes

```bash
ubuntu-ai ecosystem profiles
```

Os perfis padrão são restritivos para sistema, rede, armazenamento e serviços.
Um perfil pode reduzir executáveis, ações, tentativas e duração, mas nunca
ampliar os limites internos nem autorizar elevação.

## Catálogo de plugins

```bash
ubuntu-ai ecosystem scan-plugins /caminho/dos/plugins
ubuntu-ai ecosystem trust-plugin /caminho/plugin.toml
```

O catálogo inspeciona manifestos sem importar código. Plugins são bloqueados
até aprovação explícita. A confiança é associada ao SHA-256 do manifesto e dos
fontes; qualquer alteração exige nova aprovação.

Consulte também [compatibilidade de plugins](plugin-compatibility.md).
