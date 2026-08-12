from ubuntu_ai.fastpath.matcher import FastMatcher


def test_match_disk():

    command = FastMatcher.match("mostre o uso de disco")

    assert command is not None
    assert command.command == ["df", "-h"]


def test_match_memory():

    command = FastMatcher.match("mostre a memória")

    assert command is not None
    assert command.command == ["free", "-h"]


def test_match_pwd():

    command = FastMatcher.match("mostre o diretório atual")

    assert command.command == ["pwd"]


def test_unknown_command():

    assert FastMatcher.match("instale docker") is None