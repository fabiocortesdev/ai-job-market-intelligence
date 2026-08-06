from src.skills import detect_skills


def test_detect_skills_finds_multiple_technologies():
    result = detect_skills(
        "Data Analyst",
        "Experience with Python, SQL, Power BI and Azure.",
    )

    assert result == ["python", "sql", "power_bi", "azure"]


def test_detect_skills_is_case_insensitive():
    result = detect_skills("PYTHON and sql")

    assert result == ["python", "sql"]


def test_detect_skills_supports_german_ai_terms():
    result = detect_skills(
        "Entwicklung mit Künstlicher Intelligenz und maschinellem Lernen"
    )

    assert result == [
        "machine_learning",
        "artificial_intelligence",
    ]


def test_detect_skills_avoids_partial_word_matches():
    result = detect_skills(
        "The candidate will maintain reporting systems."
    )

    assert result == []


def test_detect_skills_ignores_none_and_empty_values():
    result = detect_skills(None, "", "   ")

    assert result == []