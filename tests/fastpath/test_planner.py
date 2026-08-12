from ubuntu_ai.fastpath.planner import FastPathPlanner


def test_build_disk_plan():

    plan = FastPathPlanner.build("mostre o uso de disco")

    assert plan is not None

    assert plan["goal"] == "Mostrar uso de disco"

    assert plan["steps"][0]["command"] == ["df", "-h"]


def test_build_unknown():

    assert FastPathPlanner.build("instale docker") is None