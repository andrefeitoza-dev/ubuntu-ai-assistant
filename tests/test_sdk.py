import pytest

from ubuntu_ai import UbuntuAI
from ubuntu_ai.pipeline.models import PipelineResult


def test_sdk_plans_request() -> None:
    assistant = UbuntuAI()

    result = assistant.plan("Instale Docker")

    assert isinstance(result, PipelineResult)
    assert result.plan.goal == "Instalar e configurar o Docker"
    assert result.preview.dry_run is True
    assert "Execution Preview (DRY RUN)" in result.rendered_preview


def test_sdk_rejects_empty_request() -> None:
    assistant = UbuntuAI()

    with pytest.raises(ValueError, match="solicitação não pode estar vazia"):
        assistant.plan("   ")