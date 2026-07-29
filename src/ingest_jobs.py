import json
from pathlib import Path
from urllib.request import urlopen


API_URL = "https://www.arbeitnow.com/api/job-board-api?page=1"

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


with urlopen(API_URL) as response:
    payload = json.load(response)


jobs = payload.get("data", [])

if not isinstance(jobs, list):
    raise ValueError("Invalid API response: 'data' is not a list.")

if len(jobs) < 100:
    raise ValueError(
        f"Insufficient number of jobs: expected at least 100, received {len(jobs)}."
    )


invalid_jobs = []

quality_issues = []

for index, job in enumerate(jobs):
    missing_fields = [
        field
        for field in QUALITY_FIELDS
        if not job.get(field)
    ]

    if missing_fields:
        quality_issues.append(
            {
                "index": index,
                "missing_fields": missing_fields,
            }
        )
if invalid_jobs:
    raise ValueError(
        f"Validation failed: {len(invalid_jobs)} jobs have missing required fields. "
        f"First errors: {invalid_jobs[:3]}"
    )


OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

with OUTPUT_FILE.open("w", encoding="utf-8") as file:
    json.dump(payload, file, ensure_ascii=False, indent=2)


print(f"Jobs collected: {len(jobs)}")
print(f"Valid jobs: {len(jobs) - len(invalid_jobs)}")
print(f"Invalid jobs: {len(invalid_jobs)}")
print(f"Jobs with quality warnings: {len(quality_issues)}")
print("Validation passed.")
print(f"First job: {jobs[0]['title']}")
print(f"Company: {jobs[0]['company_name']}")
print(f"Raw data saved to: {OUTPUT_FILE}")