from ubuntu_ai.formatter import (
    CommandOutput,
    ResponseFormatter,
)


def test_pwd_formatter():
    formatter = ResponseFormatter()

    text = formatter.format(
        CommandOutput(
            command="pwd",
            stdout="/home/andre",
        )
    )

    assert "Diretório Atual" in text
    assert "/home/andre" in text


def test_df_formatter():
    formatter = ResponseFormatter()

    text = formatter.format(
        CommandOutput(
            command="df -h",
            stdout="Filesystem Size Used",
        )
    )

    assert "Uso de Disco" in text


def test_free_formatter():
    formatter = ResponseFormatter()

    text = formatter.format(
        CommandOutput(
            command="free -h",
            stdout="Mem:",
        )
    )

    assert "Memória RAM" in text


def test_ls_formatter():
    formatter = ResponseFormatter()

    text = formatter.format(
        CommandOutput(
            command="ls",
            stdout="README.md",
        )
    )

    assert "Arquivos" in text


def test_unknown_command_returns_stdout():
    formatter = ResponseFormatter()

    text = formatter.format(
        CommandOutput(
            command="echo",
            stdout="hello",
        )
    )

    assert text == "hello"