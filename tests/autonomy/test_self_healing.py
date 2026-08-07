from ubuntu_ai.autonomy.self_healing import SelfHealingAdvisor
from ubuntu_ai.reflection.v2 import ReflectionEngineV2


def test_network_retry_is_safe_to_automate() -> None:
    reflection = ReflectionEngineV2().reflect(
        success=False,
        stderr="Connection refused",
    )

    advice = SelfHealingAdvisor().advise(reflection)

    assert advice.action == "retry"
    assert advice.safe_to_automate
