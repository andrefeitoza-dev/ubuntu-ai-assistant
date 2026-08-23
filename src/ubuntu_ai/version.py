from importlib.metadata import PackageNotFoundError, version

PACKAGE_NAME = "ubuntu-ai-assistant"
FALLBACK_VERSION = "2.0.1"


def get_version() -> str:
    """Retorna a versão instalada do pacote."""

    try:
        return version(PACKAGE_NAME)
    except PackageNotFoundError:
        return FALLBACK_VERSION


__version__ = get_version()
