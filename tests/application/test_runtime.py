from dataclasses import dataclass

from ubuntu_ai.application.runtime import ApplicationRuntime


@dataclass
class FakeSnapshot:
    requires_confirmation: bool


class FakeController:
    def __init__(self) -> None:
        self.confirmations = 0
        self.cancelled = False

    def start(self, goal: str):
        assert goal == "status"
        return FakeSnapshot(requires_confirmation=True)

    def confirm(self):
        self.confirmations += 1
        return FakeSnapshot(requires_confirmation=self.confirmations < 2)

    def cancel(self):
        self.cancelled = True
        return FakeSnapshot(requires_confirmation=False)

    def snapshot(self):
        return FakeSnapshot(requires_confirmation=False)


def build_runtime(controller: FakeController) -> ApplicationRuntime:
    return ApplicationRuntime(
        controller=controller,
        multi_agent=object(),
        autonomous=object(),
        remote=object(),
    )


def test_application_runtime_stops_for_confirmation_by_default() -> None:
    controller = FakeController()

    result = build_runtime(controller).run("status")

    assert result.requires_confirmation
    assert controller.confirmations == 0


def test_application_runtime_can_drive_loop_to_terminal_state() -> None:
    controller = FakeController()

    result = build_runtime(controller).run(
        "status",
        auto_confirm=True,
    )

    assert not result.requires_confirmation
    assert controller.confirmations == 2
