import sys
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from time import perf_counter


if __package__ in {None, ""}:
    project_root = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(project_root))


from src.analyze_jobs import main as analyze_jobs
from src.ingest_jobs import main as ingest_jobs
from src.process_jobs import main as process_jobs


PipelineStep = Callable[[], None]


def run_pipeline(
    ingest_step: PipelineStep = ingest_jobs,
    process_step: PipelineStep = process_jobs,
    analyze_step: PipelineStep = analyze_jobs,
) -> None:
    """Execute the complete job-market pipeline in sequence."""
    started_at = datetime.now(UTC)
    started_timer = perf_counter()

    print(f"Pipeline started: {started_at.isoformat()}")

    try:
        print("Running step: ingest")
        ingest_step()

        print("Running step: process")
        process_step()

        print("Running step: analyze")
        analyze_step()

    except Exception as error:
        duration = perf_counter() - started_timer

        print("Pipeline status: FAILED")
        print(f"Pipeline error: {error}")
        print(f"Pipeline duration: {duration:.2f} seconds")

        raise

    duration = perf_counter() - started_timer

    print("Pipeline status: SUCCESS")
    print(f"Pipeline duration: {duration:.2f} seconds")


def main() -> None:
    """Run the pipeline using the production steps."""
    run_pipeline()


if __name__ == "__main__":
    main()