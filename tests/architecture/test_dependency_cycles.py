from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

from ubuntu_ai.agent.context import (
    AgentContext as LegacyAgentContext,
)
from ubuntu_ai.agent.context import (
    ContextProvider as LegacyContextProvider,
)
from ubuntu_ai.context.provider import AgentContext, ContextProvider
from ubuntu_ai.decision.models import PlanningProfile
from ubuntu_ai.planner.models import (
    PlanningProfile as LegacyPlanningProfile,
)

ROOT = Path(__file__).resolve().parents[2]


def load_architecture_audit() -> ModuleType:
    path = ROOT / "scripts" / "architecture_audit.py"
    spec = importlib.util.spec_from_file_location(
        "architecture_audit_under_test",
        path,
    )
    assert spec is not None
    assert spec.loader is not None

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_top_level_package_dependencies_are_acyclic() -> None:
    audit = load_architecture_audit()
    source_files = audit.python_files(audit.PACKAGE_ROOT)
    graph = audit.package_dependencies(source_files)

    assert audit.strongly_connected_components(graph) == []


def test_legacy_context_imports_preserve_identity() -> None:
    assert LegacyAgentContext is AgentContext
    assert LegacyContextProvider is ContextProvider


def test_legacy_planning_profile_import_preserves_identity() -> None:
    assert LegacyPlanningProfile is PlanningProfile
