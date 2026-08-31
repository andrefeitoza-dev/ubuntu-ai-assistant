import subprocess
from unittest.mock import Mock, patch

from ubuntu_ai.services.shell import ShellService


def test_shell_echo() -> None:
    shell = ShellService()

    result = shell.run(["echo", "Ubuntu AI"])

    assert result.success
    assert result.stdout == "Ubuntu AI"


@patch("ubuntu_ai.services.shell.subprocess.Popen")
def test_launch_detaches_graphical_process(popen, monkeypatch) -> None:
    monkeypatch.setenv("DISPLAY", ":99")
    process = Mock()
    process.wait.side_effect = subprocess.TimeoutExpired("gtk-launch", 0.5)
    popen.return_value = process

    result = ShellService().launch(["gtk-launch", "firefox"])

    assert result.success
    popen.assert_called_once()
    _, kwargs = popen.call_args
    assert kwargs["start_new_session"] is True
    assert kwargs["env"]["DISPLAY"] == ":99"
    process.wait.assert_called_once_with(timeout=0.5)


@patch("ubuntu_ai.services.shell.subprocess.Popen")
def test_launch_reports_immediate_graphical_failure(popen) -> None:
    process = Mock()
    process.wait.return_value = 1
    popen.return_value = process

    result = ShellService().launch(["gnome-calculator"])

    assert result.success is False
    assert result.return_code == 1


@patch("ubuntu_ai.services.shell.subprocess.Popen")
def test_launch_removes_toolkit_environment_injection(popen, monkeypatch) -> None:
    monkeypatch.setenv("GIO_EXTRA_MODULES", "/snap/code/modules")
    monkeypatch.setenv("GIO_LAUNCHED_DESKTOP_FILE", "/snap/code/code.desktop")
    monkeypatch.setenv("LD_LIBRARY_PATH", "/snap/code/lib")
    monkeypatch.setenv("LOCPATH", "/snap/code/usr/lib/locale")
    monkeypatch.setenv("PATH", "/tmp/untrusted:/usr/bin")
    monkeypatch.setenv("XDG_DATA_DIRS", "/snap/code/usr/share:/usr/share")
    process = Mock()
    process.wait.side_effect = subprocess.TimeoutExpired("gtk-launch", 0.5)
    popen.return_value = process

    ShellService().launch(["gtk-launch", "org.gnome.Calculator"])

    environment = popen.call_args.kwargs["env"]
    assert "GIO_EXTRA_MODULES" not in environment
    assert "GIO_LAUNCHED_DESKTOP_FILE" not in environment
    assert "LD_LIBRARY_PATH" not in environment
    assert "LOCPATH" not in environment
    assert environment["PATH"] == (
        "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/snap/bin"
    )
    assert environment["XDG_DATA_DIRS"] == ("/usr/local/share:/usr/share:/var/lib/snapd/desktop")
