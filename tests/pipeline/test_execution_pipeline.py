import pytest

from ubuntu_ai.pipeline.execution_pipeline import ExecutionPipeline
from ubuntu_ai.pipeline.models import PipelineResult


def test_pipeline_returns_complete_result() -> None:
    pipeline = ExecutionPipeline()

    result = pipeline.run("Instale Docker")

    assert isinstance(result, PipelineResult)
    assert result.plan.goal
    assert result.preview.goal == result.plan.goal
    assert result.preview.dry_run is True
    assert result.rendered_preview


def test_pipeline_renders_dry_run_preview() -> None:
    pipeline = ExecutionPipeline()

    result = pipeline.run("Instale Docker")

    assert "Execution Preview (DRY RUN)" in result.rendered_preview
    assert "Nenhuma alteração será realizada." in result.rendered_preview
    assert "Docker" in result.rendered_preview


def test_pipeline_rejects_empty_request() -> None:
    pipeline = ExecutionPipeline()

    with pytest.raises(ValueError, match="solicitação não pode estar vazia"):
        pipeline.run("   ")