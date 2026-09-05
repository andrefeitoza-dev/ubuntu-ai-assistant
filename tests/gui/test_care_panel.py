from ubuntu_ai.gui.care_panel import CARE_ACTIONS


def test_care_panel_exposes_four_safe_entry_points() -> None:
    assert tuple(action.title for action in CARE_ACTIONS) == (
        "Diagnosticar lentidão",
        "Liberar espaço",
        "Verificar atualizações",
        "Verificar segurança",
    )
    assert len({action.request for action in CARE_ACTIONS}) == 4


def test_read_only_care_actions_do_not_claim_to_change_the_system() -> None:
    assert CARE_ACTIONS[0].request.endswith("lento?")
    assert CARE_ACTIONS[2].request.endswith("disponíveis?")
