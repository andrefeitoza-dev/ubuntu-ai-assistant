from ubuntu_ai.fast_path import LinuxCommandCatalog


def test_main_linux_commands_are_grouped() -> None:
    response = LinuxCommandCatalog().respond("mostre os principais comandos linux")

    assert response is not None
    assert "Navegação" in response
    assert "Rede" in response
    assert "systemctl" in response


def test_command_explanation_does_not_execute() -> None:
    response = LinuxCommandCatalog().respond("explique o comando chmod")

    assert response is not None
    assert "chmod u+x script.sh" in response
    assert "Atenção" in response
    assert "Nenhum comando foi executado" in response


def test_destructive_command_contains_warning() -> None:
    response = LinuxCommandCatalog().respond("explique o comando rm")

    assert response is not None
    assert "irreversível" in response


def test_network_category_is_available() -> None:
    response = LinuxCommandCatalog().respond("mostre os comandos de rede")

    assert response is not None
    assert "ip -brief address" in response
    assert "ss -ltn" in response
