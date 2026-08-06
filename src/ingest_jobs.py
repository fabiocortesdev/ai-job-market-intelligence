import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen


API_BASE_URL = "https://www.arbeitnow.com/api/job-board-api"
PAGES_TO_FETCH = (1, 2, 3)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_FILE = PROJECT_ROOT / "data" / "raw" / "jobs_raw.json"

REQUIRED_FIELDS = [
    "slug",
    "company_name",
    "title",
    "url",
]

QUALITY_FIELDS = [
    "location",
]


def fetch_page(page_number, opener=urlopen):
    url = f"{API_BASE_URL}?page={page_number}"

    with opener(url) as response:
        payload = json.load(response)

    jobs = payload.get("data")

    if not isinstance(jobs, list):
        raise ValueError(
            f"Invalid API response on page {page_number}: "
            "'data' is not a list."
        )

    return jobs


def fetch_jobs(page_numbers=PAGES_TO_FETCH, opener=urlopen):
    all_jobs = []
    page_counts = {}

    for page_number in page_numbers:
        page_jobs = fetch_page(page_number, opener=opener)
        page_counts[page_number] = len(page_jobs)
        all_jobs.extend(page_jobs)

    return all_jobs, page_counts


def validate_jobs(jobs):
    invalid_jobs = []
    quality_issues = []

    for index, job in enumerate(jobs):
        if not isinstance(job, dict):
            invalid_jobs.append(
                {
                    "index": index,
                    "missing_fields": REQUIRED_FIELDS.copy(),
                    "reason": "job is not an object",
                }
            )
            continue

        missing_required_fields = [
            field
            for field in REQUIRED_FIELDS
            if not job.get(field)
        ]

        if missing_required_fields:
            invalid_jobs.append(
                {
                    "index": index,
                    "missing_fields": missing_required_fields,
                }
            )

        missing_quality_fields = [
            field
            for field in QUALITY_FIELDS
            if not job.get(field)
        ]

        if missing_quality_fields:
            quality_issues.append(
                {
                    "index": index,
                    "missing_fields": missing_quality_fields,
                }
            )

    if invalid_jobs:
        raise ValueError(
            f"Validation failed: {len(invalid_jobs)} jobs have missing "
            f"required fields. First errors: {invalid_jobs[:3]}"
        )

    return quality_issues


def deduplicate_jobs(jobs):
    unique_jobs = []
    seen_slugs = set()

    for job in jobs:
        slug = job["slug"]

        if slug in seen_slugs:
            continue

        seen_slugs.add(slug)
        unique_jobs.append(job)

    return unique_jobs


def build_snapshot(jobs, page_counts):
    jobs_fetched = sum(page_counts.values())

    return {
        "data": jobs,
        "links": {
            "source": API_BASE_URL,
        },
        "meta": {
            "count": len(jobs),
            "pages_requested": list(page_counts),
            "jobs_per_page": {
                str(page): count
                for page, count in page_counts.items()
            },
            "jobs_fetched": jobs_fetched,
            "duplicates_removed": jobs_fetched - len(jobs),
            "collected_at_utc": datetime.now(timezone.utc).isoformat(),
        },
    }


def save_snapshot(payload, output_file=OUTPUT_FILE):
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with output_file.open("w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)


def main():
    jobs, page_counts = fetch_jobs()

    quality_issues = validate_jobs(jobs)
    unique_jobs = deduplicate_jobs(jobs)
    snapshot = build_snapshot(unique_jobs, page_counts)

    save_snapshot(snapshot)

    print(f"Pages collected: {list(page_counts)}")

    for page_number, count in page_counts.items():
        print(f"Page {page_number}: {count} jobs")

    print(f"Jobs fetched: {sum(page_counts.values())}")
    print(f"Unique jobs: {len(unique_jobs)}")
    print(
        "Duplicates removed: "
        f"{sum(page_counts.values()) - len(unique_jobs)}"
    )
    print("Invalid jobs: 0")
    print(f"Jobs with quality warnings: {len(quality_issues)}")
    print("Validation passed.")

    if unique_jobs:
        print(f"First job: {unique_jobs[0]['title']}")
        print(f"Company: {unique_jobs[0]['company_name']}")

    print(f"Raw data saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()