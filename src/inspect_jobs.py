import json
from collections import Counter
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_FILE = PROJECT_ROOT / "data" / "raw" / "jobs_raw.json"


with RAW_FILE.open("r", encoding="utf-8") as file:
    payload = json.load(file)


print(f"Raw file: {RAW_FILE}")
print(f"Root type: {type(payload).__name__}")

if not isinstance(payload, dict):
    raise TypeError("Expected the JSON root to be an object.")

print(f"Root keys: {list(payload.keys())}")


for key, value in payload.items():
    if key != "data":
        print(
            f"Metadata | key={key!r} | "
            f"type={type(value).__name__} | value={value!r}"
        )


jobs = payload.get("data")

if not isinstance(jobs, list):
    raise TypeError("Expected payload['data'] to be a list.")

print(f"Number of jobs: {len(jobs)}")

if not jobs:
    raise ValueError("The jobs list is empty.")


all_keys = sorted(
    {
        key
        for job in jobs
        if isinstance(job, dict)
        for key in job
    }
)

print(f"All job fields: {all_keys}")


field_presence = Counter()

for job in jobs:
    if not isinstance(job, dict):
        continue

    for key in job:
        field_presence[key] += 1


print("\nField presence:")

for field in all_keys:
    print(f"- {field}: {field_presence[field]}/{len(jobs)}")


first_job = jobs[0]

print("\nFirst job field types:")

for field, value in first_job.items():
    preview = repr(value)

    if len(preview) > 120:
        preview = preview[:117] + "..."

    print(
        f"- {field}: type={type(value).__name__}, "
        f"preview={preview}"
    )