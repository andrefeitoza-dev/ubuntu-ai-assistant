from __future__ import annotations

from dataclasses import dataclass

from ubuntu_ai.domain.risk import RiskLevel


@dataclass(frozen=True, slots=True)
class BuiltinCommand:
    """Representa um plano determinístico simples do sistema."""

    goal: str
    title: str
    description: str
    command: tuple[str, ...]
    keywords: tuple[str, ...]
    risk: RiskLevel = RiskLevel.LOW
    estimated_seconds: int = 1


BUILTIN_COMMANDS: tuple[BuiltinCommand, ...] = (
    #
    # DIRETÓRIO
    #
    BuiltinCommand(
        goal="Mostrar diretório atual",
        title="Mostrar diretório atual",
        description="Exibe o diretório de trabalho atual.",
        command=("pwd",),
        keywords=(
            "pwd",
            "diretório",
            "diretorio",
            "diretório atual",
            "diretorio atual",
            "diretório de trabalho",
            "diretorio de trabalho",
            "working directory",
            "onde estou",
            "qual pasta",
            "pasta atual",
            "mostrar diretório",
            "mostrar diretorio",
            "mostre o diretório",
            "mostre o diretorio",
            "current directory",
        ),
    ),
    #
    # DISCO
    #
    BuiltinCommand(
        goal="Mostrar uso de disco",
        title="Verificar uso de disco",
        description="Exibe o uso dos sistemas de arquivos.",
        command=("df", "-h"),
        keywords=(
            "df",
            "df -h",
            "disco",
            "ssd",
            "hd",
            "armazenamento",
            "armazenamento local",
            "espaço",
            "espaco",
            "espaço em disco",
            "espaco em disco",
            "espaço livre",
            "espaco livre",
            "mostrar disco",
            "mostre o disco",
            "veja o disco",
            "ver disco",
            "quanto espaço tenho",
            "quanto espaco tenho",
            "quanto espaço livre tenho",
            "quanto espaco livre tenho",
            "disk",
            "disk usage",
            "storage",
            "uso de disco",
        ),
    ),
    #
    # MEMÓRIA
    #
    BuiltinCommand(
        goal="Mostrar uso de memória",
        title="Verificar memória",
        description="Exibe memória RAM.",
        command=("free", "-h"),
        keywords=(
            "free",
            "free -h",
            "ram",
            "memória",
            "memoria",
            "memory",
            "memória ram",
            "memoria ram",
            "uso de memória",
            "uso de memoria",
            "consumo de memória",
            "consumo de memoria",
            "memória usada",
            "memoria usada",
            "memória livre",
            "memoria livre",
            "quanta memória",
            "quanta memoria",
            "quanto de memória",
            "quanto de memoria",
            "quanto de ram",
            "memória disponível",
            "memoria disponivel",
            "quanto resta de memória",
            "quanto resta de memoria",
            "veja a ram",
        ),
    ),
    #
    # ARQUIVOS
    #
    BuiltinCommand(
        goal="Listar arquivos",
        title="Listar arquivos",
        description="Lista arquivos do diretório atual.",
        command=("ls",),
        keywords=(
            "ls",
            "arquivos",
            "listar arquivos",
            "liste os arquivos",
            "mostrar arquivos",
            "mostre os arquivos",
            "listar pasta",
            "conteúdo da pasta",
            "conteudo da pasta",
            "listar diretório",
            "listar diretorio",
            "itens da pasta",
            "mostre o conteúdo",
            "mostre o conteudo",
        ),
    ),
    #
    # ÁRVORE DE DIRETÓRIOS
    #
    BuiltinCommand(
        goal="Mostrar estrutura de diretórios",
        title="Estrutura de diretórios",
        description="Exibe a estrutura do diretório atual em até dois níveis.",
        command=("find", ".", "-maxdepth", "2", "-print"),
        keywords=(
            "estrutura de pastas",
            "estrutura dos diretórios",
            "estrutura dos diretorios",
            "árvore de diretórios",
            "arvore de diretorios",
            "arquitetura das pastas",
            "hierarquia de pastas",
        ),
    ),
    #
    # ARQUIVOS OCULTOS
    #
    BuiltinCommand(
        goal="Listar arquivos ocultos",
        title="Arquivos ocultos",
        description="Lista os itens do diretório atual, incluindo arquivos ocultos.",
        command=("ls", "-la"),
        keywords=(
            "arquivos ocultos",
            "mostrar arquivos ocultos",
            "mostre os arquivos ocultos",
            "listar arquivos ocultos",
            "itens ocultos da pasta",
            "ls -la",
        ),
    ),
    #
    # PROCESSOS
    #
    BuiltinCommand(
        goal="Mostrar processos ativos",
        title="Processos ativos",
        description="Lista processos com uso de CPU e memória.",
        command=("ps", "-eo", "pid,comm,%cpu,%mem", "--sort=-%cpu"),
        keywords=(
            "processos",
            "listar processos",
            "mostre os processos",
            "processos ativos",
            "processos rodando",
            "tarefas em execução",
            "tarefas em execucao",
            "uso de cpu por processo",
        ),
    ),
    #
    # REDE
    #
    BuiltinCommand(
        goal="Mostrar interfaces",
        title="Interfaces de rede",
        description="Mostra as interfaces de rede.",
        command=("ip", "-br", "addr"),
        keywords=(
            "rede",
            "network",
            "ip",
            "ip addr",
            "meu ip",
            "mostrar ip",
            "interface",
            "interfaces",
            "interfaces de rede",
            "ethernet",
            "wifi",
            "wi-fi",
        ),
    ),
    #
    # ROTAS DE REDE
    #
    BuiltinCommand(
        goal="Mostrar rotas de rede",
        title="Rotas de rede",
        description="Exibe rotas locais e o gateway padrão.",
        command=("ip", "route"),
        keywords=(
            "rotas de rede",
            "rota de rede",
            "mostrar gateway",
            "mostre o gateway",
            "gateway padrão",
            "gateway padrao",
            "ip route",
        ),
    ),
    #
    # CPU
    #
    BuiltinCommand(
        goal="Mostrar CPU",
        title="Informações da CPU",
        description="Mostra informações resumidas da CPU.",
        command=("lscpu",),
        keywords=(
            "cpu",
            "processador",
            "informações da cpu",
            "informacoes da cpu",
            "mostrar cpu",
            "lscpu",
        ),
    ),
    #
    # CONFIGURAÇÃO DO COMPUTADOR
    #
    BuiltinCommand(
        goal="Mostrar configuração do computador",
        title="Configuração do computador",
        description="Exibe sistema operacional, kernel, arquitetura e identificação da máquina.",
        command=("hostnamectl",),
        keywords=(
            "configuração do computador",
            "configuracao do computador",
            "configuração desse computador",
            "configuracao desse computador",
            "configuração da máquina",
            "configuracao da maquina",
            "informações do computador",
            "informacoes do computador",
            "detalhes da máquina",
            "detalhes da maquina",
            "resumo do sistema",
            "mostre meu computador",
        ),
    ),
    #
    # DISPOSITIVOS DE BLOCO
    #
    BuiltinCommand(
        goal="Mostrar discos e partições",
        title="Discos e partições",
        description="Lista discos, partições, sistemas de arquivos e pontos de montagem.",
        command=("lsblk", "-o", "NAME,SIZE,TYPE,FSTYPE,MOUNTPOINTS"),
        keywords=(
            "discos e partições",
            "discos e particoes",
            "mostrar partições",
            "mostrar particoes",
            "mostre as partições",
            "mostre as particoes",
            "dispositivos de bloco",
            "discos conectados",
            "mostre meus discos",
            "lsblk",
        ),
    ),
    #
    # SERVIÇOS EM EXECUÇÃO
    #
    BuiltinCommand(
        goal="Mostrar serviços em execução",
        title="Serviços em execução",
        description="Lista serviços systemd atualmente em execução.",
        command=(
            "systemctl",
            "list-units",
            "--type=service",
            "--state=running",
            "--no-pager",
            "--plain",
        ),
        keywords=(
            "serviços em execução",
            "servicos em execucao",
            "serviços rodando",
            "servicos rodando",
            "listar serviços ativos",
            "listar servicos ativos",
            "quais serviços estão ativos",
            "quais servicos estao ativos",
        ),
    ),
    #
    # SERVIÇOS COM FALHA
    #
    BuiltinCommand(
        goal="Mostrar serviços com falha",
        title="Serviços com falha",
        description="Lista serviços systemd que estão em estado de falha.",
        command=("systemctl", "--failed", "--no-pager", "--plain"),
        keywords=(
            "serviços com falha",
            "servicos com falha",
            "existem serviços com falha",
            "existem servicos com falha",
            "serviços falhando",
            "servicos falhando",
            "falhas nos serviços",
            "falhas nos servicos",
            "problemas nos serviços",
            "problemas nos servicos",
            "systemctl --failed",
        ),
    ),
    #
    # HOSTNAME
    #
    BuiltinCommand(
        goal="Mostrar hostname",
        title="Hostname",
        description="Mostra o hostname do computador.",
        command=("hostname",),
        keywords=(
            "hostname",
            "nome do computador",
            "nome da máquina",
            "nome da maquina",
            "identificação",
            "identificacao",
        ),
    ),
    #
    # KERNEL
    #
    BuiltinCommand(
        goal="Mostrar kernel",
        title="Kernel Linux",
        description="Mostra a versão do kernel.",
        command=("uname", "-r"),
        keywords=(
            "kernel",
            "versão do kernel",
            "versao do kernel",
            "uname",
            "linux kernel",
        ),
    ),
    #
    # UPTIME
    #
    BuiltinCommand(
        goal="Mostrar uptime",
        title="Tempo ligado",
        description="Mostra há quanto tempo o sistema está ligado.",
        command=("uptime",),
        keywords=(
            "uptime",
            "tempo ligado",
            "há quanto tempo ligado",
            "ha quanto tempo ligado",
            "tempo de atividade",
        ),
    ),
    #
    # USUÁRIO
    #
    BuiltinCommand(
        goal="Mostrar usuário",
        title="Usuário atual",
        description="Mostra o usuário logado.",
        command=("whoami",),
        keywords=(
            "whoami",
            "usuário",
            "usuario",
            "usuário atual",
            "usuario atual",
            "quem sou eu",
            "quem está logado",
            "quem esta logado",
        ),
    ),
)
