from ubuntu_ai.intent import EntityExtractor


def test_extracts_known_entities_without_duplicates() -> None:
    extractor = EntityExtractor()

    entities = extractor.extract("Configure Docker com PostgreSQL no Ubuntu")

    assert tuple(entity.name for entity in entities) == (
        "docker",
        "postgresql",
        "ubuntu",
    )


def test_avoids_partial_word_matches() -> None:
    extractor = EntityExtractor(("git",))

    assert extractor.extract("digital") == ()
