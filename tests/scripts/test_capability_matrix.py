from __future__ import annotations

import importlib.util
from pathlib import Path


def load_script():
    path = Path("scripts/capability_matrix.py")
    spec = importlib.util.spec_from_file_location("capability_matrix", path)
    assert spec is not None
    assert spec.loader is not None

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_committed_results_preserve_local_homologation() -> None:
    module = load_script()
    results = module.load_results()

    assert len(results) == 47
    assert results["H01"]["status"] == "APROVADO"
    assert results["H16"]["status"] == "PENDENTE"
    assert results["N05"]["status"] == "APROVADO"
    assert results["N07"]["status"] == "PENDENTE"


def test_rendered_summary_reflects_recorded_results() -> None:
    module = load_script()
    rendered = module.render_matrix()

    assert "- aprovados: 44;" in rendered
    assert "- limitações: 0;" in rendered
    assert "- falhas: 0;" in rendered
    assert "- pendentes: 3." in rendered


def test_write_does_not_erase_recorded_evidence(tmp_path, monkeypatch) -> None:
    module = load_script()
    output = tmp_path / "matrix.md"
    monkeypatch.setattr(module, "OUTPUT", output)

    module.write_matrix()

    rendered = output.read_text(encoding="utf-8")
    assert "H16" in rendered
    assert "Segundo computador SSH indisponível" in rendered
    assert "- aprovados: 44;" in rendered
