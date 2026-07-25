from ubuntu_ai.executor.controlled_executor import ControlledExecutor


def test_executor_returns_success() -> None:
    executor = ControlledExecutor()

    result = executor.execute()

    assert result.success is True
    assert result.message == "Execução concluída com sucesso."