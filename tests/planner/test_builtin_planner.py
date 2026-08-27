from ubuntu_ai.planner.builtin.builtin_planner import BuiltinPlanner

planner = BuiltinPlanner()


#
# DIRETÓRIO
#
def test_builtin_pwd():
    assert planner.try_create_plan("pwd") is not None
    assert planner.try_create_plan("onde estou") is not None
    assert planner.try_create_plan("qual pasta") is not None
    assert planner.try_create_plan("diretório") is not None


#
# DISCO
#
def test_builtin_disk():
    assert planner.try_create_plan("disco") is not None
    assert planner.try_create_plan("df") is not None
    assert planner.try_create_plan("ssd") is not None
    assert planner.try_create_plan("hd") is not None
    assert planner.try_create_plan("armazenamento") is not None
    assert planner.try_create_plan("quanto espaço tenho") is not None
    assert planner.try_create_plan("espaço livre") is not None


#
# MEMÓRIA
#
def test_builtin_memory():
    assert planner.try_create_plan("memória") is not None
    assert planner.try_create_plan("ram") is not None
    assert planner.try_create_plan("free") is not None
    assert planner.try_create_plan("quanta memória") is not None
    assert planner.try_create_plan("quanto de ram") is not None


#
# ARQUIVOS
#
def test_builtin_ls():
    assert planner.try_create_plan("ls") is not None
    assert planner.try_create_plan("arquivos") is not None
    assert planner.try_create_plan("listar pasta") is not None
    assert planner.try_create_plan("mostrar arquivos") is not None


#
# REDE
#
def test_builtin_network():
    assert planner.try_create_plan("rede") is not None
    assert planner.try_create_plan("ip") is not None
    assert planner.try_create_plan("wifi") is not None
    assert planner.try_create_plan("interfaces") is not None
    assert planner.try_create_plan("meu ip") is not None


#
# CPU
#
def test_builtin_cpu():
    assert planner.try_create_plan("cpu") is not None
    assert planner.try_create_plan("processador") is not None
    assert planner.try_create_plan("lscpu") is not None


#
# HOSTNAME
#
def test_builtin_hostname():
    assert planner.try_create_plan("hostname") is not None
    assert planner.try_create_plan("nome do computador") is not None


#
# KERNEL
#
def test_builtin_kernel():
    assert planner.try_create_plan("kernel") is not None
    assert planner.try_create_plan("uname") is not None


#
# UPTIME
#
def test_builtin_uptime():
    assert planner.try_create_plan("uptime") is not None
    assert planner.try_create_plan("tempo ligado") is not None


#
# USUÁRIO
#
def test_builtin_user():
    assert planner.try_create_plan("whoami") is not None
    assert planner.try_create_plan("quem sou eu") is not None
    assert planner.try_create_plan("usuário atual") is not None


#
# DESCONHECIDO
#
def test_builtin_unknown():
    assert planner.try_create_plan("instale kubernetes") is None
    assert planner.try_create_plan("crie um cluster") is None
    assert planner.try_create_plan("") is None


def test_builtin_prioritizes_specific_phrase() -> None:
    plan = planner.try_create_plan("mostre a arquitetura das pastas")

    assert plan is not None
    assert plan.steps[0].command == ["find", ".", "-maxdepth", "2", "-print"]


def test_builtin_recognizes_safe_typo_by_similarity() -> None:
    plan = planner.try_create_plan("mostre os prosessos")

    assert plan is not None
    assert plan.steps[0].command[0] == "ps"


def test_builtin_does_not_match_keyword_inside_another_word() -> None:
    assert planner.try_create_plan("explique pipeline") is None


def test_builtin_exposes_match_confidence() -> None:
    match = planner.find_match("quanta memoria esta disponivel")

    assert match is not None
    assert match.command.goal == "Mostrar uso de memória"
    assert match.confidence >= 0.78


def test_builtin_computer_configuration_uses_real_local_data() -> None:
    plan = planner.try_create_plan("mostre a configuração desse computador")

    assert plan is not None
    assert plan.steps[0].command == ["hostnamectl"]


def test_builtin_lists_block_devices_without_elevation() -> None:
    plan = planner.try_create_plan("mostre os discos e partições")

    assert plan is not None
    assert plan.steps[0].command[0] == "lsblk"
    assert plan.steps[0].command[-1].endswith("MOUNTPOINTS")


def test_builtin_lists_running_services_as_read_only_query() -> None:
    plan = planner.try_create_plan("quais serviços estão ativos?")

    assert plan is not None
    assert plan.steps[0].command[:2] == ["systemctl", "list-units"]
    assert "--state=running" in plan.steps[0].command


def test_builtin_lists_failed_services_as_read_only_query() -> None:
    plan = planner.try_create_plan("existem serviços com falha?")

    assert plan is not None
    assert plan.steps[0].command == ["systemctl", "--failed", "--no-pager", "--plain"]


def test_builtin_shows_network_gateway() -> None:
    plan = planner.try_create_plan("mostre o gateway padrão")

    assert plan is not None
    assert plan.steps[0].command == ["ip", "route"]


def test_builtin_lists_hidden_files() -> None:
    plan = planner.try_create_plan("mostre os arquivos ocultos")

    assert plan is not None
    assert plan.steps[0].command == ["ls", "-la"]


def test_builtin_routes_dynamic_file_search_without_ai() -> None:
    plan = planner.try_create_plan("encontre o arquivo pyproject.toml")

    assert plan is not None
    assert plan.risk.value == "low"
    assert plan.steps[0].command[0] == "find"
    assert plan.steps[0].command[-2] == "*pyproject.toml*"


def test_builtin_does_not_fall_back_after_rejected_file_search() -> None:
    request = "encontre o arquivo ../../etc/passwd"

    assert planner.try_create_plan(request) is None
    assert planner.rejection_reason(request) is not None


def test_catalog_disks_example_ignores_sentence_punctuation() -> None:
    plan = BuiltinPlanner().try_create_plan("Mostre meus discos.")

    assert plan is not None
    assert plan.steps[0].command[0] == "lsblk"
