import pytest

from src.process_jobs import normalize_string_list, normalize_text


def test_normalize_text_removes_extra_whitespace():
    value = "  Data   Analyst  "

    result = normalize_text(value)

    assert result == "Data Analyst"


def test_normalize_text_preserves_none():
    result = normalize_text(None)

    assert result is None


def test_normalize_text_converts_non_string_value_to_text():
    result = normalize_text(123)

    assert result == "123"


def test_normalize_text_returns_none_for_whitespace_only():
    result = normalize_text("   \n\t   ")

    assert result is None


def test_normalize_string_list_removes_empty_items_and_whitespace():
    value = [" Python ", "", "  SQL  ", "   ", None]

    result = normalize_string_list(value)

    assert result == ["Python", "SQL"]


def test_normalize_string_list_returns_empty_list_for_none():
    result = normalize_string_list(None)

    assert result == []


def test_normalize_string_list_rejects_non_list_value():
    with pytest.raises(TypeError):
        normalize_string_list("Python")