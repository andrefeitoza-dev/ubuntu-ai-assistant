from unittest.mock import patch

from ubuntu_ai.services.shell import ShellService


def test_shell_echo() -> None:
    shell = ShellService()

    result = shell.run(["echo", "Ubuntu AI"])

    assert result.success
    assert result.stdout == "Ubuntu AI"


@patch("ubuntu_ai.services.shell.subprocess.Popen")
def test_launch_detaches_graphical_process(popen) -> None:
    result = ShellService().launch(["gtk-launch", "firefox"])

    assert result.success
    popen.assert_called_once()
    _, kwargs = popen.call_args
    assert kwargs["start_new_session"] is True
