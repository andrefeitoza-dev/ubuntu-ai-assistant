from ubuntu_ai.execution.models import ExecutionResult, ExecutionStatus
from ubuntu_ai.learning.models import LearningPattern
from ubuntu_ai.runtime_integration.models import RuntimeRequest
from ubuntu_ai.runtime_integration.workflow import RuntimeWorkflow


class FakeContext:
    project_name = "ubuntu-ai-assistant"
    working_directory = "/tmp/ubuntu-ai-assistant"


class FakeContextBuilder:
    def build(self, request):
        return FakeContext()


class FakeMemory:
    def is_empty(self):
        return True


class FakeMemoryBridge:
    def select(self, **kwargs):
        return FakeMemory()


class FakePlannerBridge:
    def create_plan(self, **kwargs):
        return object()


class FakeExecutionBridge:
    def execute(self, action):
        return action()


class FakeReflectionReport:
    retry_allowed = False

    def summary(self):
        return "Execução concluída e analisada."


class FakeReflectionBridge:
    def reflect(self, execution):
        return FakeReflectionReport()


class FakeLearningService:
    def __init__(self):
        self.calls = []

    def learn_from_execution(
        self,
        *,
        user_request,
        project_name,
        result,
    ):
        self.calls.append((user_request, project_name, result))
        return LearningPattern.create(
            request_pattern=user_request,
            command=result.command,
            project_name=project_name,
        )


def test_runtime_learns_from_execution() -> None:
    learning = FakeLearningService()

    workflow = RuntimeWorkflow(
        context_builder=FakeContextBuilder(),
        memory_bridge=FakeMemoryBridge(),
        planner_bridge=FakePlannerBridge(),
        execution_bridge=FakeExecutionBridge(),
        reflection_bridge=FakeReflectionBridge(),
        learning_service=learning,
    )

    execution = ExecutionResult(
        status=ExecutionStatus.EXECUTED,
        message="Executado com sucesso.",
        command="df -h",
        return_code=0,
    )

    result = workflow.run(
        RuntimeRequest(
            request="verifique o disco",
            session_id="test-session",
            execute=True,
        ),
        execution_action=lambda plan: execution,
    )

    assert result.execution is execution
    assert len(learning.calls) == 1

    user_request, project_name, learned_result = learning.calls[0]

    assert user_request == "verifique o disco"
    assert project_name == "ubuntu-ai-assistant"
    assert learned_result is execution


def test_runtime_exposes_memory_created_from_reflection() -> None:
    workflow = RuntimeWorkflow(
        context_builder=FakeContextBuilder(),
        memory_bridge=FakeMemoryBridge(),
        planner_bridge=FakePlannerBridge(),
        execution_bridge=FakeExecutionBridge(),
        reflection_bridge=FakeReflectionBridge(),
    )

    execution = ExecutionResult(
        status=ExecutionStatus.EXECUTED,
        message="Executado com sucesso.",
        command="df -h",
        return_code=0,
    )

    result = workflow.run(
        RuntimeRequest(
            request="verifique o disco",
            session_id="test-session",
            execute=True,
        ),
        execution_action=lambda plan: execution,
    )

    assert result.learned_memory is not None
    assert result.learned_memory.content == "Execução concluída e analisada."
    assert result.learned_memory.project_name == "ubuntu-ai-assistant"
    assert result.learned_memory.source == "reflection"


class FakeMemoryService:
    def __init__(self):
        self.calls = []

    def record_execution(
        self,
        *,
        session_id,
        user_request,
        working_directory,
        project_name,
        result,
    ):
        self.calls.append(
            (
                session_id,
                user_request,
                str(working_directory),
                project_name,
                result,
            )
        )
        return object()


def test_runtime_persists_execution_in_memory() -> None:
    memory_service = FakeMemoryService()

    workflow = RuntimeWorkflow(
        context_builder=FakeContextBuilder(),
        memory_bridge=FakeMemoryBridge(),
        planner_bridge=FakePlannerBridge(),
        execution_bridge=FakeExecutionBridge(),
        reflection_bridge=FakeReflectionBridge(),
        memory_service=memory_service,
    )

    execution = ExecutionResult(
        status=ExecutionStatus.EXECUTED,
        message="Executado com sucesso.",
        command="df -h",
        return_code=0,
    )

    result = workflow.run(
        RuntimeRequest(
            request="verifique o disco",
            session_id="memory-test-session",
            execute=True,
        ),
        execution_action=lambda plan: execution,
    )

    assert result.execution is execution
    assert len(memory_service.calls) == 1

    (
        session_id,
        user_request,
        working_directory,
        project_name,
        persisted_result,
    ) = memory_service.calls[0]

    assert session_id == "memory-test-session"
    assert user_request == "verifique o disco"
    assert project_name == "ubuntu-ai-assistant"
    assert persisted_result is execution
    assert working_directory
