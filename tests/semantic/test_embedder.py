import pytest

from ubuntu_ai.semantic import LocalHashEmbedder


def test_embedder_is_deterministic_and_normalized() -> None:
    embedder = LocalHashEmbedder(dimensions=64)

    first = embedder.embed("instalar docker no ubuntu")
    second = embedder.embed("instalar docker no ubuntu")

    assert first == second
    assert sum(value * value for value in first) == pytest.approx(1.0)


def test_related_texts_have_greater_similarity() -> None:
    embedder = LocalHashEmbedder(dimensions=128)
    query = embedder.embed("configurar firewall ubuntu")
    related = embedder.embed("configuração do firewall no ubuntu")
    unrelated = embedder.embed("criar ambiente python virtual")

    assert embedder.cosine_similarity(query, related) > embedder.cosine_similarity(
        query, unrelated
    )
