from ubuntu_ai.container.lifetimes import Lifetime


def test_lifetime_values() -> None:
    assert Lifetime.SINGLETON == "singleton"
    assert Lifetime.TRANSIENT == "transient"
