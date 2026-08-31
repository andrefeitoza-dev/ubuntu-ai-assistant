import importlib.util
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / "scripts/report_junit_failures.py"
SPEC = importlib.util.spec_from_file_location("report_junit_failures", SCRIPT)
assert SPEC and SPEC.loader
reporter = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(reporter)


def test_reports_junit_failure_as_github_annotation(tmp_path: Path, capsys) -> None:
    junit = tmp_path / "results.xml"
    junit.write_text(
        '<testsuite><testcase classname="tests.example" name="test_case">'
        '<failure message="expected true">trace\nline</failure>'
        "</testcase></testsuite>",
        encoding="utf-8",
    )

    assert reporter.report(junit) == 1
    output = capsys.readouterr().out
    assert "::error title=Teste automatizado reprovado::" in output
    assert "tests.example.test_case: expected true" in output


def test_reports_unassociated_pytest_failure(tmp_path: Path, capsys) -> None:
    junit = tmp_path / "results.xml"
    junit.write_text('<testsuite tests="1" failures="0"/>', encoding="utf-8")

    assert reporter.report(junit) == 1
    assert "pytest falhou sem caso JUnit associado" in capsys.readouterr().out
