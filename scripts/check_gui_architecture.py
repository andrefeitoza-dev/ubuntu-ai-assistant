from __future__ import annotations

from pathlib import Path

APP_FILE = Path("src/ubuntu_ai/gui/app.py")
MAX_APP_LINES = 1400

REQUIRED_COMPONENTS = (
    Path("src/ubuntu_ai/gui/automation_panel.py"),
    Path("src/ubuntu_ai/gui/capabilities_panel.py"),
    Path("src/ubuntu_ai/gui/conversation_view.py"),
    Path("src/ubuntu_ai/gui/execution_cards.py"),
    Path("src/ubuntu_ai/gui/interface.py"),
    Path("src/ubuntu_ai/gui/presentation.py"),
    Path("src/ubuntu_ai/gui/remote_controls.py"),
    Path("src/ubuntu_ai/gui/theme.py"),
)

REQUIRED_DELEGATIONS = (
    "build_main_interface(",
    "build_welcome(",
    "add_user_message(",
    "add_system_message(",
    "build_plan_card(",
    "build_execution_result_card(",
    "build_remote_controls",
    "build_automation_panel",
    "build_capabilities_panel",
)


def validate_gui_architecture() -> None:
    if not APP_FILE.is_file():
        raise ValueError(f"Arquivo principal ausente: {APP_FILE}")

    app_source = APP_FILE.read_text(encoding="utf-8")
    app_lines = len(app_source.splitlines())

    if app_lines > MAX_APP_LINES:
        raise ValueError(
            f"gui/app.py ultrapassou o limite arquitetural: {app_lines} > {MAX_APP_LINES} linhas"
        )

    missing_components = [
        str(component) for component in REQUIRED_COMPONENTS if not component.is_file()
    ]
    if missing_components:
        raise ValueError("Componentes visuais ausentes: " + ", ".join(missing_components))

    missing_delegations = [
        delegation
        for delegation in REQUIRED_DELEGATIONS
        if delegation not in app_source
        and delegation
        not in (
            "build_remote_controls",
            "build_automation_panel",
            "build_capabilities_panel",
        )
    ]

    component_sources = "\n".join(
        component.read_text(encoding="utf-8") for component in REQUIRED_COMPONENTS
    )

    for delegation in (
        "build_remote_controls",
        "build_automation_panel",
        "build_capabilities_panel",
    ):
        if delegation not in app_source and delegation not in component_sources:
            missing_delegations.append(delegation)

    if missing_delegations:
        raise ValueError("Delegações visuais ausentes: " + ", ".join(missing_delegations))

    print(
        "GUI architecture checks passed: "
        f"{app_lines}/{MAX_APP_LINES} lines, "
        f"{len(REQUIRED_COMPONENTS)} components."
    )


def main() -> None:
    validate_gui_architecture()


if __name__ == "__main__":
    main()
