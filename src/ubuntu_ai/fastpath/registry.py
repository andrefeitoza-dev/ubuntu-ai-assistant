from ubuntu_ai.fastpath.models import FastCommand


FAST_COMMANDS = [

    FastCommand(
        goal="Mostrar uso de disco",
        keywords=("uso de disco", "disco", "disk"),
        command=["df", "-h"],
        description="Mostra utilização do disco.",
    ),

    FastCommand(
        goal="Mostrar memória",
        keywords=("memória", "ram", "memory"),
        command=["free", "-h"],
        description="Mostra memória disponível.",
    ),

    FastCommand(
        goal="Mostrar diretório atual",
        keywords=("diretório atual", "pwd"),
        command=["pwd"],
        description="Mostra o diretório atual.",
    ),

    FastCommand(
        goal="Listar arquivos",
        keywords=("listar arquivos", "liste arquivos"),
        command=["ls"],
        description="Lista os arquivos do diretório atual.",
    ),

    FastCommand(
        goal="Listar arquivos ocultos",
        keywords=("arquivos ocultos",),
        command=["ls", "-la"],
        description="Lista inclusive arquivos ocultos.",
    ),

    FastCommand(
        goal="Mostrar endereço IP",
        keywords=("endereço ip", "ip"),
        command=["ip", "addr"],
        description="Mostra as interfaces de rede.",
    ),

    FastCommand(
        goal="Mostrar kernel",
        keywords=("kernel",),
        command=["uname", "-r"],
        description="Mostra a versão do kernel.",
    ),
]