# AI Job Market Intelligence

A data project for collecting, validating, and analyzing job postings from the German job market.

## Current development status

**v0.1 — In progress**

Completed so far:

- raw job data ingestion from the Arbeitnow API;
- API response validation;
- data quality checks for essential fields;
- raw JSON dataset preservation.

The official v0.1 release is planned after data transformation,
exploratory analysis, Power BI visualization, and final documentation.

**Raw data ingestion**

The current pipeline:

1. Collects job postings from the Arbeitnow Job Board API.
2. Validates the API response structure.
3. Requires at least 100 job postings.
4. Validates essential fields in every job posting.
5. Reports non-critical data quality warnings.
6. Saves the complete API response as a raw JSON dataset.

## Data source

- Source: Arbeitnow Job Board API
- Endpoint: `https://www.arbeitnow.com/api/job-board-api?page=1`
- Accessed on: July 29, 2026

## Results

The first execution collected:

- 175 job postings
- 175 valid records
- 0 records with critical validation errors
- 5 records without location information
- 97.1% completeness for the `location` field

## Validation rules

The pipeline treats the following fields as required:

- `slug`
- `company_name`
- `title`
- `url`

If one of these fields is missing, the pipeline stops without overwriting the existing raw dataset.

The `location` field is monitored as a data quality field. A missing location generates a warning but does not invalidate the job posting.

## Project structure

```text
ai-job-market-intelligence/
├── data/
│   └── raw/
│       └── jobs_raw.json
├── src/
│   └── ingest_jobs.py
├── .gitignore
└── README.md
```

## How to run

### Requirements

- Python 3.10 or later
- Internet connection

No external Python packages are required for v0.1.

### Execution

From the project root:

```powershell
python .\src\ingest_jobs.py
```

The raw API response will be saved to:

```text
data/raw/jobs_raw.json
```

## Planned evolution

Future iterations may explore:

- LLM-based job enrichment and classification;
- historical job market tracking;
- automated and incremental data ingestion;
- data quality and automated testing;
- broader European market coverage using additional data sources;
- AI-assisted market insights.

## Author

Fabio Cortes Lima