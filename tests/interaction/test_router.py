import pytest

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
        ("qual a memória?", InteractionRoute.ACTION),
        ("mostre os processos", InteractionRoute.ACTION),
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
