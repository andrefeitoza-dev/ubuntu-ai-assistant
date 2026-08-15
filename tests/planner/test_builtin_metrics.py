from ubuntu_ai.planner.builtin.metrics import collect_metrics


def test_builtin_metrics():

    metrics = collect_metrics()

    assert metrics.commands >= 10

    assert metrics.aliases >= 100
