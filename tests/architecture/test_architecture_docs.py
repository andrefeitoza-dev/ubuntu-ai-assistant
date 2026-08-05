from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_epic_zero_adrs_exist() -> None:
    adr_dir = ROOT / "docs" / "adr"
    expected = {
        "ADR-002-framework-architecture.md",
        "ADR-003-dependency-rules.md",
        "ADR-004-agent-lifecycle.md",
        "ADR-005-public-apis.md",
        "ADR-006-plugin-sdk.md",
        "ADR-007-memory-architecture.md",
        "ADR-008-execution-architecture.md",
    }

    assert expected <= {path.name for path in adr_dir.glob("ADR-*.md")}


def test_framework_architecture_document_exists() -> None:
    path = ROOT / "docs" / "architecture" / "framework-v0.7.md"
    assert path.exists()
    assert "intent-first" in path.read_text(encoding="utf-8")
