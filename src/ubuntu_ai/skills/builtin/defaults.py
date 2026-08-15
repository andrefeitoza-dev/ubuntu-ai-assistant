from ubuntu_ai.skills.builtin.core import BuiltinSkill
from ubuntu_ai.tools.default_capabilities import default_capabilities


def default_skills() -> tuple[BuiltinSkill, ...]:
    capabilities = {item.name: item for item in default_capabilities()}
    return (
        BuiltinSkill("packages", (capabilities["apt"], capabilities["snap"]), "Pacotes Ubuntu."),
        BuiltinSkill("services", (capabilities["systemctl"],), "Serviços systemd."),
        BuiltinSkill("containers", (capabilities["docker"],), "Containers Docker."),
        BuiltinSkill("version-control", (capabilities["git"],), "Controle de versão Git."),
        BuiltinSkill("python", (capabilities["python"],), "Ambientes e comandos Python."),
        BuiltinSkill("remote", (capabilities["ssh"],), "Operações remotas SSH."),
        BuiltinSkill("shell", (capabilities["shell"],), "Fallback de terminal."),
    )
