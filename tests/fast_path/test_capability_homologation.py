from __future__ import annotations

import subprocess
import sys

from ubuntu_ai.fast_path.capabilities import CapabilityCatalog


def test_catalog_has_twenty_sequential_topics() -> None:
    topics = CapabilityCatalog().topics

    assert len(topics) == 20
    assert tuple(topic.code for topic in topics) == tuple(f"{number:02}" for number in range(1, 21))


def test_catalog_has_thirty_nine_announced_questions() -> None:
    topics = CapabilityCatalog().topics
    examples = [example for topic in topics for example in topic.examples]

    assert len(examples) == 39
    assert all(example.strip() for example in examples)


def test_every_topic_has_complete_safety_metadata() -> None:
    for topic in CapabilityCatalog().topics:
        assert topic.title.strip()
        assert topic.capabilities
        assert topic.kind.strip()
        assert topic.risk.strip()
        assert topic.confirmation.strip()
        assert topic.availability.strip()


def test_rendered_help_lists_every_topic() -> None:
    catalog = CapabilityCatalog()
    response = catalog.render()

    for topic in catalog.topics:
        assert f"{topic.code}. {topic.title}" in response


def test_every_topic_detail_contains_examples_and_policy() -> None:
    catalog = CapabilityCatalog()

    for topic in catalog.topics:
        detail = catalog.detail(topic.code)

        assert topic.title in detail
        assert f"Risco: {topic.risk}" in detail
        assert f"Confirmação: {topic.confirmation}" in detail
        assert f"Disponibilidade: {topic.availability}" in detail

        for example in topic.examples:
            assert example in detail


def test_generated_homologation_matrix_is_current() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/capability_matrix.py",
            "--check",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert "39 casos anunciados" in result.stdout
