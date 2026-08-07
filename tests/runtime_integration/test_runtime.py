from ubuntu_ai.runtime_integration.models import RuntimeRequest
from ubuntu_ai.runtime_integration.runtime import MultiAgentRuntime


class FakeWorkflow:
    def run(self, request, execution_action=None):
        return ("ok", request.session_id, execution_action)


def test_runtime_delegates_to_workflow() -> None:
    runtime = MultiAgentRuntime(FakeWorkflow())

    result = runtime.run(
        RuntimeRequest(
            request="status",
            session_id="abc",
        )
    )

    assert result[0] == "ok"
    assert result[1] == "abc"
