import json
import stat
from pathlib import Path
from types import SimpleNamespace

import pytest

from ubuntu_ai.diagnostics import SanitizedDiagnosticExporter


def test_export_contains_only_aggregated_private_diagnostics(tmp_path: Path) -> None:
    exporter = SanitizedDiagnosticExporter(tmp_path / "Downloads")
    records = (
        SimpleNamespace(status="executed", command=("secret",), request="token=secret"),
        SimpleNamespace(status="blocked", stderr="private"),
    )

    path = exporter.export(
        audit_records=records,
        simulation=True,
        denied_capabilities=("packages",),
    )

    payload = json.loads(path.read_text(encoding="utf-8"))
    serialized = json.dumps(payload)
    assert payload["audit_summary"]["statuses"] == {"blocked": 1, "executed": 1}
    assert payload["runtime"]["simulation"] is True
    assert "secret" not in serialized
    assert "private" not in serialized
    assert stat.S_IMODE(path.stat().st_mode) == 0o600


def test_export_refuses_symbolic_link_directory(tmp_path: Path) -> None:
    real = tmp_path / "real"
    real.mkdir()
    link = tmp_path / "Downloads"
    link.symlink_to(real, target_is_directory=True)

    with pytest.raises(OSError, match="seguro|simbólicos"):
        SanitizedDiagnosticExporter(link).export(
            simulation=False,
            denied_capabilities=(),
        )
