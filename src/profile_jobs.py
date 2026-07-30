import json
from collections import Counter
from pathlib import Path

from src.geography import (
    classify_geographic_scope,
    make_final_geographic_decision,
)


PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_FILE = PROJECT_ROOT / "data" / "raw" / "jobs_raw.json"

RELEVANT_FIELDS = [
    "slug",
    "company_name",
    "title",
    "description",
    "remote",
    "url",
    "tags",
    "job_types",
    "location",
    "created_at",
]

USABILITY_FIELDS = [
    "slug",
    "company_name",
    "title",
    "description",
    "url",
    "created_at",
]

def is_missing(value):
    if value is None:
        return True

    if isinstance(value, str):
        return not value.strip()

    if isinstance(value, (list, dict)):
        return len(value) == 0

    return False

def get_usability_issues(job):
    issues = []

    for field in USABILITY_FIELDS:
        if is_missing(job.get(field)):
            issues.append(f"missing_{field}")

    if not isinstance(job.get("created_at"), int):
        issues.append("invalid_created_at_type")

    return issues

with RAW_FILE.open("r", encoding="utf-8") as file:
    payload = json.load(file)


jobs = payload["data"]

missing_counts = Counter()
field_types = {
    field: Counter()
    for field in RELEVANT_FIELDS
}

slugs = []
urls = []
complete_records = []

usable_jobs = 0
unusable_reasons = Counter()

for job in jobs:
    usability_issues = get_usability_issues(job)

    if usability_issues:
        unusable_reasons.update(usability_issues)
    else:
        usable_jobs += 1

    for field in RELEVANT_FIELDS:
        value = job.get(field)

        field_types[field][type(value).__name__] += 1

        if is_missing(value):
            missing_counts[field] += 1

    if not is_missing(job.get("slug")):
        slugs.append(job["slug"])

    if not is_missing(job.get("url")):
        urls.append(job["url"])

    complete_records.append(
        json.dumps(job, sort_keys=True, ensure_ascii=False)
    )
duplicate_slugs = {
    value: count
    for value, count in Counter(slugs).items()
    if count > 1
}

duplicate_urls = {
    value: count
    for value, count in Counter(urls).items()
    if count > 1
}

exact_duplicates = sum(
    count - 1
    for count in Counter(complete_records).values()
    if count > 1
)


print(f"Total jobs: {len(jobs)}")

print("\nMissing values:")

for field in RELEVANT_FIELDS:
    missing = missing_counts[field]
    completeness = ((len(jobs) - missing) / len(jobs)) * 100

    print(
        f"- {field}: missing={missing}, "
        f"completeness={completeness:.1f}%"
    )


print("\nObserved field types:")

for field in RELEVANT_FIELDS:
    print(f"- {field}: {dict(field_types[field])}")


print("\nDuplicate checks:")
print(f"- Duplicate slug values: {len(duplicate_slugs)}")
print(f"- Duplicate URL values: {len(duplicate_urls)}")
print(f"- Exact duplicate records beyond first occurrence: {exact_duplicates}")

if duplicate_slugs:
    print(f"- Duplicate slug details: {duplicate_slugs}")

if duplicate_urls:
    print(f"- Duplicate URL details: {duplicate_urls}")

print("\nAnalytical usability:")
print(f"- Usable jobs: {usable_jobs}")
print(f"- Unusable jobs: {len(jobs) - usable_jobs}")
print(f"- Usability rate: {(usable_jobs / len(jobs)) * 100:.1f}%")

if unusable_reasons:
    print(f"- Unusable reasons: {dict(unusable_reasons)}")

location_counts = Counter(
    job["location"].strip()
    for job in jobs
    if isinstance(job.get("location"), str)
    and job["location"].strip()
)

print("\nLocation distribution:")
print(f"- Unique non-empty locations: {len(location_counts)}")
print("- Top 20 locations:")

for location, count in location_counts.most_common(20):
    print(f"  - {location!r}: {count}")

print("\nAll non-empty locations:")

for location, count in sorted(
    location_counts.items(),
    key=lambda item: item[0].casefold(),
):
    print(f"- {location!r}: {count}")

geographic_scope_counts = Counter()
jobs_needing_location_review = []

for job in jobs:
    scope = classify_geographic_scope(job.get("location"))
    geographic_scope_counts[scope] += 1

    if scope == "needs_review":
        jobs_needing_location_review.append(
            {
                "slug": job.get("slug"),
                "location": job.get("location"),
                "remote": job.get("remote"),
            }
        )


print("\nGeographic scope:")
print(
    f"- Germany confirmed: "
    f"{geographic_scope_counts['germany_confirmed']}"
)
print(
    f"- Outside Germany: "
    f"{geographic_scope_counts['outside_germany']}"
)
print(
    f"- Needs review: "
    f"{geographic_scope_counts['needs_review']}"
)
print(
    f"- Total classified: "
    f"{sum(geographic_scope_counts.values())}"
)

print("\nJobs needing location review:")

for job in jobs_needing_location_review:
    print(
        f"- slug={job['slug']!r}, "
        f"location={job['location']!r}, "
        f"remote={job['remote']!r}"
    )

GERMANY_EVIDENCE_TERMS = (
    "germany",
    "deutschland",
    "german",
    "deutsch",
    "berlin",
    "hamburg",
    "munich",
    "münchen",
    "cologne",
    "köln",
    "dach",
)


def find_germany_evidence(job):
    searchable_fields = {
        "title": job.get("title"),
        "description": job.get("description"),
        "url": job.get("url"),
        "location": job.get("location"),
    }

    evidence = []

    for field_name, value in searchable_fields.items():
        if not isinstance(value, str):
            continue

        normalized_value = value.casefold()

        for term in GERMANY_EVIDENCE_TERMS:
            position = normalized_value.find(term.casefold())

            if position == -1:
                continue

            start = max(0, position - 80)
            end = min(len(value), position + len(term) + 80)

            evidence.append(
                {
                    "field": field_name,
                    "term": term,
                    "context": value[start:end],
                }
            )

    return evidence

print("\nLocation review evidence:")

for job in jobs:
    scope = classify_geographic_scope(job.get("location"))

    if scope != "needs_review":
        continue

    evidence = find_germany_evidence(job)

    print(f"\n- Slug: {job.get('slug')!r}")
    print(f"  Company: {job.get('company_name')!r}")
    print(f"  Title: {job.get('title')!r}")
    print(f"  Location: {job.get('location')!r}")
    print(f"  Remote: {job.get('remote')!r}")
    print(f"  URL: {job.get('url')!r}")

    if evidence:
        print("  Germany evidence:")

        for item in evidence[:5]:
            print(
                f"    - field={item['field']!r}, "
                f"term={item['term']!r}, "
                f"context={item['context']!r}"
            )
    else:
        print("  Germany evidence: none")

final_geographic_counts = Counter(
    make_final_geographic_decision(job)
    for job in jobs
)

print("\nFinal geographic decision:")
print(
    f"- Include Germany: "
    f"{final_geographic_counts['include_germany']}"
)
print(
    f"- Exclude outside Germany: "
    f"{final_geographic_counts['exclude_outside_germany']}"
)
print(
    f"- Exclude insufficient evidence: "
    f"{final_geographic_counts['exclude_insufficient_evidence']}"
)
print(
    f"- Unresolved: "
    f"{final_geographic_counts['unresolved']}"
)
print(
    f"- Total decided: "
    f"{sum(final_geographic_counts.values())}"
)