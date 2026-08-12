from ubuntu_ai.domain.risk import RiskLevel
from ubuntu_ai.planner.builtin import BuiltinPlanner


def test_builtin_planner_creates_pwd_plan() -> None:
    planner = BuiltinPlanner()

    plan = planner.try_create_plan("mostre meu diretório atual")

    assert plan is not None
    assert plan.goal == "Mostrar diretório atual"
    assert plan.risk is RiskLevel.LOW
    assert plan.estimated_seconds == 1
    assert len(plan.steps) == 1
    assert plan.steps[0].command == ["pwd"]


def test_builtin_planner_creates_disk_plan() -> None:
    planner = BuiltinPlanner()

    plan = planner.try_create_plan("mostre o uso de disco")

    assert plan is not None
    assert plan.goal == "Mostrar uso de disco"
    assert plan.steps[0].command == ["df", "-h"]


def test_builtin_planner_creates_memory_plan() -> None:
    planner = BuiltinPlanner()

    plan = planner.try_create_plan("mostre a memória RAM")

    assert plan is not None
    assert plan.goal == "Mostrar uso de memória"
    assert plan.steps[0].command == ["free", "-h"]


def test_builtin_planner_creates_ls_plan() -> None:
    planner = BuiltinPlanner()

    plan = planner.try_create_plan("liste os arquivos desta pasta")

    assert plan is not None
    assert plan.goal == "Listar arquivos"
    assert plan.steps[0].command == ["ls"]


def test_builtin_planner_accepts_common_variations() -> None:
    planner = BuiltinPlanner()

    assert planner.try_create_plan("onde estou") is not None
    assert planner.try_create_plan("quanto espaço livre tenho?") is not None
    assert planner.try_create_plan("mostre memoria") is not None
    assert planner.try_create_plan("listar arquivos") is not None


def test_builtin_planner_returns_none_for_unknown_request() -> None:
    planner = BuiltinPlanner()

    assert planner.try_create_plan("instale o PostgreSQL") is None


def test_builtin_planner_returns_none_for_empty_request() -> None:
    planner = BuiltinPlanner()

    assert planner.try_create_plan("   ") is None