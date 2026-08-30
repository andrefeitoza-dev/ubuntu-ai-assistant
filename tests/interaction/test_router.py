import pytest

from ubuntu_ai.benchmark import BenchmarkService
from ubuntu_ai.interaction import InteractionRoute, InteractionRouter


class FakeLearningService:
    def __init__(self, approved: bool) -> None:
        self.approved = approved

    def approved_recommendations(self, request: str, *, limit: int):
        assert request
        assert limit == 1
        return (object(),) if self.approved else ()


@pytest.fixture
def router() -> InteractionRouter:
    return InteractionRouter()


@pytest.mark.parametrize(
    ("phrase", "expected"),
    [
        ("que dia é hoje?", InteractionRoute.LOCAL),
        ("que mês estamos?", InteractionRoute.LOCAL),
        ("mostre o dia e mês atuais", InteractionRoute.LOCAL),
        ("qual é o ano atual?", InteractionRoute.LOCAL),
        ("mostre as horas", InteractionRoute.LOCAL),
        ("como está este computador?", InteractionRoute.LOCAL),
        ("qual a versão do Ubuntu?", InteractionRoute.LOCAL),
        ("qual é o kernel deste computador?", InteractionRoute.LOCAL),
        ("qual é o IP local deste computador?", InteractionRoute.LOCAL),
        ("qual é meu IP?", InteractionRoute.LOCAL),
        ("mostre meu endereço IP", InteractionRoute.LOCAL),
        ("informe o IP deste computador", InteractionRoute.LOCAL),
        ("quanto tenho de memória?", InteractionRoute.LOCAL),
        ("mostre os principais comandos Linux", InteractionRoute.LOCAL),
        ("explique o comando chmod", InteractionRoute.LOCAL),
        ("o que você pode fazer?", InteractionRoute.LOCAL),
        ("quais programas tenho instalados?", InteractionRoute.LOCAL),
        ("qual a memória?", InteractionRoute.LOCAL),
        ("mostre os processos", InteractionRoute.ACTION),
        ("mostre a configuração desse computador", InteractionRoute.ACTION),
        ("mostre os discos e partições", InteractionRoute.ACTION),
        ("quais serviços estão ativos?", InteractionRoute.ACTION),
        ("existem serviços com falha?", InteractionRoute.LOCAL),
        ("mostre o gateway padrão", InteractionRoute.ACTION),
        ("mostre os arquivos ocultos", InteractionRoute.ACTION),
        ("encontre o arquivo pyproject.toml", InteractionRoute.ACTION),
        ("procure a pasta Downloads", InteractionRoute.ACTION),
        ("acesse o site ubuntu.com", InteractionRoute.ACTION),
        ("abra o Firefox", InteractionRoute.ACTION),
        ("instale o Docker", InteractionRoute.ACTION),
        ("sudo apt update", InteractionRoute.ACTION),
        ("o que é memória RAM?", InteractionRoute.CHAT),
        ("como instalar Docker?", InteractionRoute.CHAT),
        ("qual é a capital de Portugal?", InteractionRoute.CHAT),
        ("escreva um resumo sobre Linux", InteractionRoute.CHAT),
    ],
)
def test_routes_requests(
    router: InteractionRouter,
    phrase: str,
    expected: InteractionRoute,
) -> None:
    assert router.route(phrase).route is expected


def test_local_route_contains_response(router: InteractionRouter) -> None:
    decision = router.route("help")

    assert decision.route is InteractionRoute.LOCAL
    assert decision.response is not None


def test_empty_request_is_rejected(router: InteractionRouter) -> None:
    with pytest.raises(ValueError, match="Digite uma solicitação"):
        router.route("   ")


def test_approved_learning_can_route_unknown_phrase_to_safe_pipeline() -> None:
    router = InteractionRouter(
        learning_service=FakeLearningService(True),  # type: ignore[arg-type]
    )

    assert router.route("exibir os itens deste local").route is InteractionRoute.ACTION


def test_unapproved_learning_does_not_promote_unknown_phrase() -> None:
    router = InteractionRouter(
        learning_service=FakeLearningService(False),  # type: ignore[arg-type]
    )

    assert router.route("exibir os itens deste local").route is InteractionRoute.CHAT


def test_router_records_selected_route_latency() -> None:
    benchmark = BenchmarkService()
    router = InteractionRouter(benchmark_service=benchmark)

    decision = router.route("que dia é hoje?")

    assert decision.duration >= 0
    record = benchmark.report().records[0]
    assert record.operation == "interaction.route.local"
    assert record.success is True


def test_router_refuses_unsafe_file_search_without_action() -> None:
    decision = InteractionRouter().route("encontre o arquivo ../../etc/passwd")

    assert decision.route is InteractionRoute.LOCAL
    assert decision.response is not None
    assert "não executada" in decision.response
    assert "sem caminhos" in decision.response


def test_router_explains_ambiguous_email_without_execution() -> None:
    decision = InteractionRouter().route("abra meu email")

    assert decision.route is InteractionRoute.LOCAL
    assert decision.response is not None
    assert "ambíguo" in decision.response


def test_router_refuses_unsafe_url_without_execution() -> None:
    decision = InteractionRouter().route("abra javascript:alert(1)")

    assert decision.route is InteractionRoute.LOCAL
    assert decision.response is not None
    assert "Site não aberto" in decision.response
    assert "HTTP ou HTTPS" in decision.response


@pytest.mark.parametrize(
    "phrase",
    (
        "Abra o Firefox.",
        "Abra as configurações de rede.",
        "Abra o VS Code.",
    ),
)
def test_catalog_desktop_app_examples_route_to_safe_action(
    phrase: str,
) -> None:
    decision = InteractionRouter().route(phrase)

    assert decision.route is InteractionRoute.ACTION
    assert decision.response is None


@pytest.mark.parametrize(
    "phrase",
    (
        "Qual a versão do assistente?",
        "Qual é a versão do assistente?",
        "Qual a versão do Ubuntu AI?",
        "Que versão do Ubuntu AI está instalada?",
    ),
)
def test_assistant_version_variations_stay_on_local_route(
    phrase: str,
) -> None:
    decision = InteractionRouter().route(phrase)

    assert decision.route is InteractionRoute.LOCAL
    assert decision.response is not None
    assert "Ubuntu AI Assistant: versão 2.1.0" in decision.response


@pytest.mark.parametrize(
    "phrase",
    (
        "Abra a Calculadora.",
        "Abra o LibreOffice.",
        "Abra o Terminal.",
        "Abra o GitHub no Firefox.",
        "Abra https://ubuntu.com.",
        "Abra minha pasta Downloads.",
    ),
)
def test_v22_natural_open_actions_use_safe_route(
    phrase: str,
    tmp_path,
    monkeypatch,
) -> None:
    (tmp_path / "Downloads").mkdir()
    monkeypatch.setattr("pathlib.Path.home", lambda: tmp_path)

    decision = InteractionRouter().route(phrase)

    assert decision.route is InteractionRoute.ACTION
    assert decision.response is None
