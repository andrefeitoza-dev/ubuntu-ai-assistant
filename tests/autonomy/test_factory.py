from ubuntu_ai.autonomy.factory import build_autonomous_runtime


class FakeRuntime:
    def run(self, request, execution_action=None):
        raise RuntimeError("not used")


def test_factory_builds_autonomous_runtime() -> None:
    runtime = build_autonomous_runtime(FakeRuntime())

    assert runtime is not None
