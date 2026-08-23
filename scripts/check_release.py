from __future__ import annotations

import re
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_VERSION = "2.0.1"


def main() -> None:
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    package_version = pyproject["project"]["version"]
    version_source = (ROOT / "src/ubuntu_ai/version.py").read_text(encoding="utf-8")
    match = re.search(r'FALLBACK_VERSION = "([^"]+)"', version_source)

    if match is None:
        raise SystemExit("FALLBACK_VERSION não encontrado.")
    if package_version != EXPECTED_VERSION:
        raise SystemExit(f"pyproject.toml usa {package_version}, esperado {EXPECTED_VERSION}.")
    if match.group(1) != EXPECTED_VERSION:
        raise SystemExit(f"version.py usa {match.group(1)}, esperado {EXPECTED_VERSION}.")

    required = [
        ROOT / "README.md",
        ROOT / "CHANGELOG.md",
        ROOT / "LICENSE",
        ROOT / "docs/releases/v2.0.1.md",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.exists()]
    if missing:
        raise SystemExit("Arquivos de release ausentes: " + ", ".join(missing))

    print(f"Release {EXPECTED_VERSION} consistente.")


if __name__ == "__main__":
    main()
