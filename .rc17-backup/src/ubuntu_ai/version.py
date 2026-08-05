from importlib.metadata import PackageNotFoundError, version

PACKAGE_NAME = "ubuntu-ai-assistant"
FALLBACK_VERSION = "0.6.0rc1"


def get_version() -> str:
    """Retorna a versão instalada do pacote."""

    try:
        return version(PACKAGE_NAME)
    except PackageNotFoundError:
        return FALLBACK_VERSION


__version__ = get_version()
