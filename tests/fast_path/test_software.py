from ubuntu_ai.fast_path import InstalledSoftwareResponder


def packages() -> tuple[tuple[str, str], ...]:
    return (
        ("curl", "8.5.0"),
        ("firefox", "141.0"),
        ("python3", "3.12.3"),
    )


def test_installed_programs_are_answered_from_real_inventory() -> None:
    response = InstalledSoftwareResponder(packages).respond("quais programas tenho instalados")

    assert response is not None
    assert "3 pacotes" in response
    assert "firefox — 141.0" in response
    assert "nenhum pacote foi alterado" in response


def test_inventory_is_limited_and_explains_refinement() -> None:
    response = InstalledSoftwareResponder(packages, preview_limit=2).respond(
        "liste os pacotes instalados"
    )

    assert response is not None
    assert "Exibindo 2 de 3" in response
    assert "python3" not in response


def test_conceptual_package_question_continues_to_chat() -> None:
    responder = InstalledSoftwareResponder(packages)

    assert responder.respond("como listar programas instalados") is None
