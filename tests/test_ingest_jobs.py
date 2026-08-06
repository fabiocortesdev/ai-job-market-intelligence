import json
from io import StringIO

import pytest

from src.ingest_jobs import (
    build_snapshot,
    deduplicate_jobs,
    fetch_jobs,
    fetch_page,
    validate_jobs,
)


def make_job(slug="job-1", location="Berlin"):
    return {
        "slug": slug,
        "company_name": "Example Company",
        "title": "Data Analyst",
        "url": f"https://example.com/{slug}",
        "location": location,
    }


def make_response(payload):
    return StringIO(json.dumps(payload))


def test_fetch_page_returns_jobs_from_valid_response():
    expected_jobs = [
        make_job("job-1"),
        make_job("job-2"),
    ]

    def fake_opener(url):
        return make_response({"data": expected_jobs})

    result = fetch_page(1, opener=fake_opener)

    assert result == expected_jobs


def test_fetch_page_rejects_non_list_data():
    def fake_opener(url):
        return make_response({"data": {"slug": "job-1"}})

    with pytest.raises(
        ValueError,
        match="Invalid API response on page 1",
    ):
        fetch_page(1, opener=fake_opener)


def test_fetch_jobs_combines_multiple_pages():
    jobs_by_page = {
        1: [make_job("job-1"), make_job("job-2")],
        2: [make_job("job-3")],
        3: [make_job("job-4"), make_job("job-5")],
    }

    def fake_opener(url):
        page_number = int(url.rsplit("=", 1)[1])
        return make_response({"data": jobs_by_page[page_number]})

    jobs, page_counts = fetch_jobs(
        page_numbers=(1, 2, 3),
        opener=fake_opener,
    )

    assert len(jobs) == 5
    assert page_counts == {
        1: 2,
        2: 1,
        3: 2,
    }


def test_validate_jobs_rejects_missing_required_field():
    invalid_job = make_job()
    invalid_job["title"] = None

    with pytest.raises(
        ValueError,
        match="missing required fields",
    ):
        validate_jobs([invalid_job])


def test_validate_jobs_reports_quality_warning():
    job_without_location = make_job(location=None)

    quality_issues = validate_jobs([job_without_location])

    assert quality_issues == [
        {
            "index": 0,
            "missing_fields": ["location"],
        }
    ]


def test_deduplicate_jobs_preserves_first_job_for_each_slug():
    first_job = make_job("job-1")
    duplicate_job = make_job("job-1")
    duplicate_job["title"] = "Duplicate title"
    second_job = make_job("job-2")

    result = deduplicate_jobs(
        [first_job, duplicate_job, second_job]
    )

    assert result == [first_job, second_job]


def test_build_snapshot_records_collection_metadata():
    jobs = [
        make_job("job-1"),
        make_job("job-2"),
    ]
    page_counts = {
        1: 2,
        2: 1,
        3: 1,
    }

    snapshot = build_snapshot(jobs, page_counts)

    assert snapshot["data"] == jobs
    assert snapshot["meta"]["count"] == 2
    assert snapshot["meta"]["pages_requested"] == [1, 2, 3]
    assert snapshot["meta"]["jobs_per_page"] == {
        "1": 2,
        "2": 1,
        "3": 1,
    }
    assert snapshot["meta"]["jobs_fetched"] == 4
    assert snapshot["meta"]["duplicates_removed"] == 2
    assert snapshot["meta"]["collected_at_utc"]