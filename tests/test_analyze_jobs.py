import csv

from src.analyze_jobs import (
    build_jobs_skills,
    build_market_summary,
    build_skills_by_market,
    write_csv,
)


SAMPLE_JOBS = [
    {
        "job_id": "de-python-sql",
        "source_market_code": "DE",
        "source_market": "Germany",
        "remote": True,
        "detected_skills": ["python", "sql"],
    },
    {
        "job_id": "de-no-skills",
        "source_market_code": "DE",
        "source_market": "Germany",
        "remote": False,
        "detected_skills": [],
    },
    {
        "job_id": "gb-python",
        "source_market_code": "GB",
        "source_market": "United Kingdom",
        "remote": False,
        "detected_skills": ["python"],
    },
]


def test_build_market_summary_calculates_germany_metrics():
    result = build_market_summary(SAMPLE_JOBS)

    germany = next(
        row for row in result
        if row["source_market_code"] == "DE"
    )

    assert germany == {
        "source_market_code": "DE",
        "source_market": "Germany",
        "total_jobs": 2,
        "remote_jobs": 1,
        "remote_job_rate": 0.5,
        "jobs_with_skills": 1,
        "skill_coverage_rate": 0.5,
        "unique_skills": 2,
        "skill_mentions": 2,
    }


def test_build_market_summary_calculates_united_kingdom_metrics():
    result = build_market_summary(SAMPLE_JOBS)

    united_kingdom = next(
        row for row in result
        if row["source_market_code"] == "GB"
    )

    assert united_kingdom["total_jobs"] == 1
    assert united_kingdom["remote_jobs"] == 0
    assert united_kingdom["remote_job_rate"] == 0.0
    assert united_kingdom["jobs_with_skills"] == 1
    assert united_kingdom["skill_coverage_rate"] == 1.0
    assert united_kingdom["unique_skills"] == 1
    assert united_kingdom["skill_mentions"] == 1


def test_build_jobs_skills_creates_one_row_per_job_and_skill():
    result = build_jobs_skills(SAMPLE_JOBS)

    assert result == [
        {
            "job_id": "de-python-sql",
            "source_market_code": "DE",
            "source_market": "Germany",
            "skill": "python",
        },
        {
            "job_id": "de-python-sql",
            "source_market_code": "DE",
            "source_market": "Germany",
            "skill": "sql",
        },
        {
            "job_id": "gb-python",
            "source_market_code": "GB",
            "source_market": "United Kingdom",
            "skill": "python",
        },
    ]


def test_build_jobs_skills_excludes_jobs_without_detected_skills():
    result = build_jobs_skills(SAMPLE_JOBS)

    job_ids = {row["job_id"] for row in result}

    assert "de-no-skills" not in job_ids
    assert len(result) == 3


def test_build_skills_by_market_calculates_counts_and_rates():
    result = build_skills_by_market(SAMPLE_JOBS)

    assert result == [
        {
            "source_market_code": "DE",
            "source_market": "Germany",
            "skill": "python",
            "jobs_mentioning_skill": 1,
            "total_jobs_in_market": 2,
            "skill_mention_rate": 0.5,
            "rank_in_market": 1,
        },
        {
            "source_market_code": "DE",
            "source_market": "Germany",
            "skill": "sql",
            "jobs_mentioning_skill": 1,
            "total_jobs_in_market": 2,
            "skill_mention_rate": 0.5,
            "rank_in_market": 2,
        },
        {
            "source_market_code": "GB",
            "source_market": "United Kingdom",
            "skill": "python",
            "jobs_mentioning_skill": 1,
            "total_jobs_in_market": 1,
            "skill_mention_rate": 1.0,
            "rank_in_market": 1,
        },
    ]


def test_build_skills_by_market_ranks_by_count_then_skill_name():
    jobs = [
        {
            "job_id": "de-1",
            "source_market_code": "DE",
            "source_market": "Germany",
            "remote": False,
            "detected_skills": ["sql", "python"],
        },
        {
            "job_id": "de-2",
            "source_market_code": "DE",
            "source_market": "Germany",
            "remote": False,
            "detected_skills": ["python", "aws"],
        },
        {
            "job_id": "de-3",
            "source_market_code": "DE",
            "source_market": "Germany",
            "remote": False,
            "detected_skills": [],
        },
    ]

    result = build_skills_by_market(jobs)

    assert [
        (row["skill"], row["jobs_mentioning_skill"], row["rank_in_market"])
        for row in result
    ] == [
        ("python", 2, 1),
        ("aws", 1, 2),
        ("sql", 1, 3),
    ]


def test_write_csv_creates_file_with_expected_content(tmp_path):
    rows = [
        {
            "source_market_code": "DE",
            "total_jobs": 300,
        },
        {
            "source_market_code": "GB",
            "total_jobs": 75,
        },
    ]
    output_file = tmp_path / "market_summary.csv"

    write_csv(
        rows,
        output_file,
        fieldnames=[
            "source_market_code",
            "total_jobs",
        ],
    )

    with output_file.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        saved_rows = list(csv.DictReader(file))

    assert saved_rows == [
        {
            "source_market_code": "DE",
            "total_jobs": "300",
        },
        {
            "source_market_code": "GB",
            "total_jobs": "75",
        },
    ]


def test_write_csv_rejects_empty_rows(tmp_path):
    output_file = tmp_path / "empty.csv"

    try:
        write_csv(
            [],
            output_file,
            fieldnames=["source_market_code"],
        )
    except ValueError as error:
        assert str(error) == "Cannot write an empty CSV."
    else:
        raise AssertionError("ValueError was not raised.")