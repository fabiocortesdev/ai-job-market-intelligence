import pytest

from src.process_jobs import (
    normalize_boolean,
    normalize_job,
    normalize_string_list,
    normalize_text,
    remove_html,
    convert_timestamp
)


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


def test_normalize_string_list_extracts_values_from_numeric_key_mapping():
    value = {
        "1": "professional / experienced",
    }

    result = normalize_string_list(value)

    assert result == [
        "professional / experienced",
    ]


def test_normalize_string_list_rejects_non_list_value():
    with pytest.raises(TypeError):
        normalize_string_list("Python")


@pytest.mark.parametrize("value", [True, False])
def test_normalize_boolean_preserves_boolean_values(value):
    result = normalize_boolean(value)

    assert result is value


def test_normalize_boolean_preserves_none():
    result = normalize_boolean(None)

    assert result is None


def test_normalize_boolean_rejects_non_boolean_value():
    with pytest.raises(
        TypeError,
        match="Expected a boolean or None, received str",
    ):
        normalize_boolean("true")


def test_remove_html_removes_tags_and_normalizes_whitespace():
    value = "<p>Data <strong>Analyst</strong></p><p>Python</p>"

    result = remove_html(value)

    assert result == "Data Analyst Python"


def test_remove_html_decodes_html_entities():
    value = "<p>Data &amp; Analytics</p>"

    result = remove_html(value)

    assert result == "Data & Analytics"


@pytest.mark.parametrize("value", [None, "", "   "])
def test_remove_html_returns_none_for_empty_value(value):
    result = remove_html(value)

    assert result is None


def test_convert_timestamp_converts_unix_timestamp_to_utc_isoformat():
    result = convert_timestamp(0)

    assert result == "1970-01-01T00:00:00+00:00"


@pytest.mark.parametrize(
    "value",
    [None, "1704067200", 1704067200.0, True, False],
)
def test_convert_timestamp_returns_none_for_invalid_value(value):
    result = convert_timestamp(value)

    assert result is None


def test_normalize_job_transforms_complete_job():
    job = {
        "slug": "  data-analyst-123  ",
        "company_name": "  Example   Company  ",
        "title": "  Data   Analyst  ",
        "description": "<p>Analyze <strong>data</strong> &amp; reports.</p>",
        "remote": True,
        "url": "  https://example.com/jobs/123  ",
        "tags": [" Python ", "SQL", "", None],
        "job_types": [" Full-time ", "   "],
        "location": "  Berlin,   Germany  ",
        "created_at": 0,
    }

    result = normalize_job(job)

    assert result == {
        "job_id": "data-analyst-123",
        "company_name": "Example Company",
        "title": "Data Analyst",
        "description_clean": "Analyze data & reports.",
        "remote": True,
        "url": "https://example.com/jobs/123",
        "tags": ["Python", "SQL"],
        "job_types": ["Full-time"],
        "location": "Berlin, Germany",
        "created_at_utc": "1970-01-01T00:00:00+00:00",
    }


def test_normalize_job_handles_missing_fields():
    result = normalize_job({})

    assert result == {
        "job_id": None,
        "company_name": None,
        "title": None,
        "description_clean": None,
        "remote": None,
        "url": None,
        "tags": [],
        "job_types": [],
        "location": None,
        "created_at_utc": None,
    }