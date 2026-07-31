#!/usr/bin/env python3
"""Gera métricas arquiteturais simples sem dependências externas."""

from __future__ import annotations

import ast
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGE_ROOT = ROOT / "src" / "ubuntu_ai"
TEST_ROOT = ROOT / "tests"


def python_files(root: Path) -> list[Path]:
    return sorted(root.rglob("*.py")) if root.exists() else []


def package_name(module: str) -> str:
    parts = module.split(".")
    return ".".join(parts[:2]) if len(parts) >= 2 else module


def package_dependencies(files: list[Path]) -> dict[str, set[str]]:
    dependencies: dict[str, set[str]] = defaultdict(set)
    for path in files:
        relative = path.relative_to(PACKAGE_ROOT).with_suffix("")
        source_package = relative.parts[0]
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            modules: list[str] = []
            if isinstance(node, ast.ImportFrom) and node.module:
                modules.append(node.module)
            elif isinstance(node, ast.Import):
                modules.extend(alias.name for alias in node.names)
            for module in modules:
                if not module.startswith("ubuntu_ai."):
                    continue
                target_package = module.split(".")[1]
                if target_package != source_package:
                    dependencies[source_package].add(target_package)
    return dependencies


def strongly_connected_components(graph: dict[str, set[str]]) -> list[list[str]]:
    index = 0
    indices: dict[str, int] = {}
    lowlinks: dict[str, int] = {}
    stack: list[str] = []
    on_stack: set[str] = set()
    components: list[list[str]] = []
    nodes = set(graph)
    for targets in graph.values():
        nodes.update(targets)

    def visit(node: str) -> None:
        nonlocal index
        indices[node] = index
        lowlinks[node] = index
        index += 1
        stack.append(node)
        on_stack.add(node)

        for target in graph.get(node, set()):
            if target not in indices:
                visit(target)
                lowlinks[node] = min(lowlinks[node], lowlinks[target])
            elif target in on_stack:
                lowlinks[node] = min(lowlinks[node], indices[target])

        if lowlinks[node] != indices[node]:
            return

        component: list[str] = []
        while stack:
            current = stack.pop()
            on_stack.remove(current)
            component.append(current)
            if current == node:
                break
        if len(component) > 1:
            components.append(sorted(component))

    for node in sorted(nodes):
        if node not in indices:
            visit(node)
    return components


def main() -> int:
    source_files = python_files(PACKAGE_ROOT)
    test_files = python_files(TEST_ROOT)
    graph = package_dependencies(source_files)
    cycles = strongly_connected_components(graph)
    largest = sorted(
        ((len(path.read_text(encoding="utf-8").splitlines()), path) for path in source_files),
        reverse=True,
    )[:10]

    print("Ubuntu AI — Architectural Audit")
    print(f"Source Python files: {len(source_files)}")
    print(f"Test Python files:   {len(test_files)}")
    print(f"Top-level cycles:    {len(cycles)}")
    for cycle in cycles:
        print(f"  - {' -> '.join(cycle)}")
    print("Largest source files:")
    for lines, path in largest:
        print(f"  {lines:4d}  {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
