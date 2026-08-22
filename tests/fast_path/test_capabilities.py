from ubuntu_ai.fast_path import CapabilityCatalog


def test_capability_catalog_exposes_all_main_areas() -> None:
    response = CapabilityCatalog().respond("o que voce pode fazer")

    assert response is not None
    assert "Informações do computador" in response
    assert "Comandos Linux" in response
    assert "Rede e SSH — Administração remota" in response
    assert "Automações" in response
    assert "Integração com VS Code" in response
    assert len(CapabilityCatalog().topics) == 20


def test_topic_help_returns_example() -> None:
    response = CapabilityCatalog().respond("ajuda sobre rede")

    assert response is not None
    assert response.startswith("Rede")
    assert "interfaces de rede" in response
    assert "Risco:" in response
    assert "Disponibilidade:" in response


def test_topic_can_be_selected_by_number() -> None:
    response = CapabilityCatalog().detail("04")

    assert response.startswith("Comandos Linux")
    assert "Explique o comando chmod" in response
