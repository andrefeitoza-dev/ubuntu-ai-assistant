from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "ubuntu_ai"

FORBIDDEN_PREFIXES = {
    "domain": ("ubuntu_ai.cli", "ubuntu_ai.tui", "requests", "sqlite3"),
    "context": ("ubuntu_ai.agent",),
    "decision": ("ubuntu_ai.planner",),
}


def imported_modules(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module)
    return modules


def main() -> int:
    violations: list[str] = []
    for area, prefixes in FORBIDDEN_PREFIXES.items():
        directory = SOURCE / area
        if not directory.exists():
            continue
        for path in directory.rglob("*.py"):
            for module in imported_modules(path):
                if module.startswith(prefixes):
                    violations.append(f"{path.relative_to(ROOT)} imports forbidden module {module}")

    if violations:
        print("Architecture violations:")
        for violation in violations:
            print(f"- {violation}")
        return 1

    print("Architecture checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
