import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "jobs_processed.json"
)

ANALYTICS_DIR = (
    PROJECT_ROOT
    / "data"
    / "analytics"
)

MARKET_SUMMARY_FIELDS = [
    "source_market_code",
    "source_market",
    "total_jobs",
    "remote_jobs",
    "remote_job_rate",
    "jobs_with_skills",
    "skill_coverage_rate",
    "unique_skills",
    "skill_mentions",
]

JOBS_SKILLS_FIELDS = [
    "job_id",
    "source_market_code",
    "source_market",
    "skill",
]

SKILLS_BY_MARKET_FIELDS = [
    "source_market_code",
    "source_market",
    "skill",
    "jobs_mentioning_skill",
    "total_jobs_in_market",
    "skill_mention_rate",
    "rank_in_market",
]


def build_market_summary(jobs):
    markets = defaultdict(
        lambda: {
            "source_market": None,
            "total_jobs": 0,
            "remote_jobs": 0,
            "jobs_with_skills": 0,
            "skills": set(),
            "skill_mentions": 0,
        }
    )

    for job in jobs:
        market_code = job["source_market_code"]
        market = markets[market_code]
        detected_skills = job["detected_skills"]

        market["source_market"] = job["source_market"]
        market["total_jobs"] += 1
        market["remote_jobs"] += int(job["remote"] is True)

        if detected_skills:
            market["jobs_with_skills"] += 1

        market["skills"].update(detected_skills)
        market["skill_mentions"] += len(detected_skills)

    summary = []

    for market_code in sorted(markets):
        market = markets[market_code]
        total_jobs = market["total_jobs"]

        summary.append(
            {
                "source_market_code": market_code,
                "source_market": market["source_market"],
                "total_jobs": total_jobs,
                "remote_jobs": market["remote_jobs"],
                "remote_job_rate": market["remote_jobs"] / total_jobs,
                "jobs_with_skills": market["jobs_with_skills"],
                "skill_coverage_rate": (
                    market["jobs_with_skills"] / total_jobs
                ),
                "unique_skills": len(market["skills"]),
                "skill_mentions": market["skill_mentions"],
            }
        )

    return summary


def build_jobs_skills(jobs):
    rows = []

    for job in jobs:
        for skill in job["detected_skills"]:
            rows.append(
                {
                    "job_id": job["job_id"],
                    "source_market_code": job["source_market_code"],
                    "source_market": job["source_market"],
                    "skill": skill,
                }
            )

    return rows


def build_skills_by_market(jobs):
    markets = defaultdict(
        lambda: {
            "source_market": None,
            "total_jobs": 0,
            "skill_counts": Counter(),
        }
    )

    for job in jobs:
        market_code = job["source_market_code"]
        market = markets[market_code]

        market["source_market"] = job["source_market"]
        market["total_jobs"] += 1
        market["skill_counts"].update(job["detected_skills"])

    rows = []

    for market_code in sorted(markets):
        market = markets[market_code]
        total_jobs = market["total_jobs"]

        ranked_skills = sorted(
            market["skill_counts"].items(),
            key=lambda item: (-item[1], item[0]),
        )

        for rank, (skill, count) in enumerate(
            ranked_skills,
            start=1,
        ):
            rows.append(
                {
                    "source_market_code": market_code,
                    "source_market": market["source_market"],
                    "skill": skill,
                    "jobs_mentioning_skill": count,
                    "total_jobs_in_market": total_jobs,
                    "skill_mention_rate": count / total_jobs,
                    "rank_in_market": rank,
                }
            )

    return rows


def write_csv(rows, output_file, fieldnames):
    if not rows:
        raise ValueError("Cannot write an empty CSV.")

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with output_file.open(
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )
        writer.writeheader()
        writer.writerows(rows)


def main():
    with INPUT_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:
        jobs = json.load(file)

    market_summary = build_market_summary(jobs)
    jobs_skills = build_jobs_skills(jobs)
    skills_by_market = build_skills_by_market(jobs)

    write_csv(
        market_summary,
        ANALYTICS_DIR / "market_summary.csv",
        MARKET_SUMMARY_FIELDS,
    )
    write_csv(
        jobs_skills,
        ANALYTICS_DIR / "jobs_skills.csv",
        JOBS_SKILLS_FIELDS,
    )
    write_csv(
        skills_by_market,
        ANALYTICS_DIR / "skills_by_market.csv",
        SKILLS_BY_MARKET_FIELDS,
    )

    print(f"Input jobs: {len(jobs)}")
    print(f"Market summary rows: {len(market_summary)}")
    print(f"Job-skill rows: {len(jobs_skills)}")
    print(f"Skill-market rows: {len(skills_by_market)}")
    print(f"Analytics files saved to: {ANALYTICS_DIR}")


if __name__ == "__main__":
    main()