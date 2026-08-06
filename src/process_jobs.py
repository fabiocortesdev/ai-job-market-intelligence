import csv
import html
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from src.geography import classify_source_market
from src.skills import detect_skills


PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_FILE = PROJECT_ROOT / "data" / "raw" / "jobs_raw.json"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
PROCESSED_JSON_FILE = PROCESSED_DIR / "jobs_processed.json"
PROCESSED_CSV_FILE = PROCESSED_DIR / "jobs_processed.csv"


def normalize_text(value):
    if value is None:
        return None

    normalized = re.sub(r"\s+", " ", str(value)).strip()

    return normalized or None


def normalize_string_list(value):
    if value is None:
        return []

    if not isinstance(value, list):
        raise TypeError(
            f"Expected a list, received {type(value).__name__}."
        )

    normalized_items = []

    for item in value:
        normalized_item = normalize_text(item)

        if normalized_item is not None:
            normalized_items.append(normalized_item)

    return normalized_items


def normalize_boolean(value):
    if value is None or isinstance(value, bool):
        return value

    raise TypeError(
        f"Expected a boolean or None, received {type(value).__name__}."
    )


def remove_html(value):
    if not value:
        return None

    decoded_text = html.unescape(str(value))
    text_without_tags = re.sub(r"<[^>]+>", " ", decoded_text)

    return normalize_text(text_without_tags)


def convert_timestamp(value):
    if isinstance(value, bool) or not isinstance(value, int):
        return None

    return datetime.fromtimestamp(
        value,
        tz=timezone.utc,
    ).isoformat()


def normalize_job(job):
    return {
        "job_id": normalize_text(job.get("slug")),
        "company_name": normalize_text(job.get("company_name")),
        "title": normalize_text(job.get("title")),
        "description_clean": remove_html(job.get("description")),
        "remote": normalize_boolean(job.get("remote")),
        "url": normalize_text(job.get("url")),
        "tags": normalize_string_list(job.get("tags")),
        "job_types": normalize_string_list(job.get("job_types")),
        "location": normalize_text(job.get("location")),
        "created_at_utc": convert_timestamp(job.get("created_at")),
    }


def write_processed_json(jobs):
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    with PROCESSED_JSON_FILE.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            jobs,
            file,
            ensure_ascii=False,
            indent=2,
        )
        file.write("\n")


def write_processed_csv(jobs):
    if not jobs:
        raise ValueError("Cannot write an empty processed CSV.")

    fieldnames = list(jobs[0].keys())

    with PROCESSED_CSV_FILE.open(
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )
        writer.writeheader()

        for job in jobs:
            csv_job = job.copy()
            csv_job["tags"] = json.dumps(
                job["tags"],
                ensure_ascii=False,
            )
            csv_job["job_types"] = json.dumps(
                job["job_types"],
                ensure_ascii=False,
            )
            csv_job["detected_skills"] = json.dumps(
                job["detected_skills"],
                ensure_ascii=False,
            )

            writer.writerow(csv_job)

def main():
    with RAW_FILE.open("r", encoding="utf-8") as file:
        payload = json.load(file)


    raw_jobs = payload["data"]

    market_classifications = [
        classify_source_market(job)
        for job in raw_jobs
    ]

    unresolved_markets = [
        {
            "job_id": job.get("slug"),
            "url": job.get("url"),
            "source_domain": classification["source_domain"],
        }
        for job, classification in zip(
            raw_jobs,
            market_classifications,
            strict=True,
        )
        if classification["market_status"] != "confirmed"
    ]

    if unresolved_markets:
        raise ValueError(
            "Market classification cannot continue while "
            f"{len(unresolved_markets)} jobs are unresolved. "
            f"Details: {unresolved_markets}"
        )

    normalized_jobs = []

    for raw_job, classification in zip(
        raw_jobs,
        market_classifications,
        strict=True,
    ):
        normalized_job = normalize_job(raw_job)

        detected_skills = detect_skills(
            normalized_job["title"],
            normalized_job["description_clean"],
            " ".join(normalized_job["tags"]),
            " ".join(normalized_job["job_types"]),
        )

        normalized_job.update(
            {
                "source_domain": classification["source_domain"],
                "source_market": classification["source_market"],
                "source_market_code": classification[
                    "source_market_code"
                ],
                "detected_skills": detected_skills,
            }
        )

        normalized_jobs.append(normalized_job)

    market_counts = Counter(
        job["source_market_code"]
        for job in normalized_jobs
    )

    print("Source market classification:")
    print(f"- Raw jobs: {len(raw_jobs)}")
    print(f"- Germany (DE): {market_counts['DE']}")
    print(f"- United Kingdom (GB): {market_counts['GB']}")
    print(f"- Unresolved: {len(unresolved_markets)}")
    print(f"- Jobs selected for processing: {len(normalized_jobs)}")

    if not normalized_jobs:
        raise ValueError(
            "No jobs were available after market classification."
        )

    first_normalized_job = normalized_jobs[0]

    print("\nNormalized first job:")

    for field, value in first_normalized_job.items():
        preview = repr(value)

        if len(preview) > 200:
            preview = preview[:197] + "..."

        print(f"- {field}: {preview}")

    required_fields = [
        "job_id",
        "company_name",
        "title",
        "description_clean",
        "url",
        "created_at_utc",
    ]

    invalid_jobs = []

    for job in normalized_jobs:
        missing_required = [
            field
            for field in required_fields
            if job.get(field) is None
        ]

        if missing_required:
            invalid_jobs.append(
                {
                    "job_id": job.get("job_id"),
                    "missing_fields": missing_required,
                }
            )

    unique_job_ids = {
        job["job_id"]
        for job in normalized_jobs
        if job["job_id"] is not None
    }


    print("\nProcessing validation:")
    print(f"- Raw jobs: {len(raw_jobs)}")
    print(f"- Normalized jobs: {len(normalized_jobs)}")
    print(f"- Jobs missing required fields: {len(invalid_jobs)}")
    print(f"- Unique job IDs: {len(unique_job_ids)}")

    if invalid_jobs:
        print(f"- Invalid job details: {invalid_jobs}")

    html_pattern = re.compile(r"<[^>]+>")

    descriptions_with_html = [
        job["job_id"]
        for job in normalized_jobs
        if job["description_clean"]
        and html_pattern.search(job["description_clean"])
    ]

    empty_descriptions = [
        job["job_id"]
        for job in normalized_jobs
        if job["description_clean"] is None
    ]

    print("\nDescription validation:")
    print(
        f"- Descriptions still containing HTML: "
        f"{len(descriptions_with_html)}"
    )
    print(f"- Empty cleaned descriptions: {len(empty_descriptions)}")

    if descriptions_with_html:
        print(
            f"- Job IDs with remaining HTML: "
            f"{descriptions_with_html}"
        )

    if empty_descriptions:
        print(
            f"- Job IDs with empty descriptions: "
            f"{empty_descriptions}"
        )

    print("\nRemaining HTML samples:")

    sample_count = 0

    for job in normalized_jobs:
        description = job["description_clean"]

        if not description:
            continue

        matches = list(html_pattern.finditer(description))

        if not matches:
            continue

        print(f"\n- Job ID: {job['job_id']}")

        for match in matches[:3]:
            start = max(0, match.start() - 80)
            end = min(len(description), match.end() + 80)

            context = description[start:end]

            print(f"  Match: {match.group()!r}")
            print(f"  Context: {context!r}")

        sample_count += 1

        if sample_count == 10:
            break

    validation_errors = []

    if invalid_jobs:
        validation_errors.append(
            f"{len(invalid_jobs)} jobs are missing required fields."
        )

    if len(unique_job_ids) != len(normalized_jobs):
        validation_errors.append(
            "Normalized jobs contain duplicate or missing job IDs."
        )

    if descriptions_with_html:
        validation_errors.append(
            f"{len(descriptions_with_html)} descriptions still contain HTML."
        )

    if empty_descriptions:
        validation_errors.append(
            f"{len(empty_descriptions)} descriptions are empty."
        )

    if validation_errors:
        error_details = "\n".join(
            f"- {error}"
            for error in validation_errors
        )

        raise ValueError(
            "Processed dataset validation failed:\n"
            f"{error_details}"
        )

    print("\nFinal validation: PASSED")
    print("- Dataset is ready to be written.")

    write_processed_json(normalized_jobs)

    print("\nProcessed JSON written:")
    print(f"- File: {PROCESSED_JSON_FILE}")
    print(f"- Records: {len(normalized_jobs)}")

    write_processed_csv(normalized_jobs)

    print("\nProcessed CSV written:")
    print(f"- File: {PROCESSED_CSV_FILE}")
    print(f"- Records: {len(normalized_jobs)}")


if __name__ == "__main__":
    main()