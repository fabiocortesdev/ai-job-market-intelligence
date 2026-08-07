import pytest

from src.run_pipeline import run_pipeline


def test_run_pipeline_executes_steps_in_order():
    executed_steps = []

    def ingest_step():
        executed_steps.append("ingest")

    def process_step():
        executed_steps.append("process")

    def analyze_step():
        executed_steps.append("analyze")

    run_pipeline(
        ingest_step=ingest_step,
        process_step=process_step,
        analyze_step=analyze_step,
    )

    assert executed_steps == [
        "ingest",
        "process",
        "analyze",
    ]


def test_run_pipeline_stops_when_a_step_fails():
    executed_steps = []

    def ingest_step():
        executed_steps.append("ingest")

    def process_step():
        executed_steps.append("process")
        raise RuntimeError("Processing failed.")

    def analyze_step():
        executed_steps.append("analyze")

    with pytest.raises(
        RuntimeError,
        match="Processing failed.",
    ):
        run_pipeline(
            ingest_step=ingest_step,
            process_step=process_step,
            analyze_step=analyze_step,
        )

    assert executed_steps == [
        "ingest",
        "process",
    ]


def test_run_pipeline_reports_success(capsys):
    run_pipeline(
        ingest_step=lambda: None,
        process_step=lambda: None,
        analyze_step=lambda: None,
    )

    captured = capsys.readouterr()

    assert "Pipeline started" in captured.out
    assert "Pipeline status: SUCCESS" in captured.out
    assert "Pipeline duration:" in captured.out


def test_run_pipeline_reports_failure(capsys):
    def failing_step():
        raise ValueError("Invalid API response.")

    with pytest.raises(
        ValueError,
        match="Invalid API response.",
    ):
        run_pipeline(
            ingest_step=failing_step,
            process_step=lambda: None,
            analyze_step=lambda: None,
        )

    captured = capsys.readouterr()

    assert "Pipeline status: FAILED" in captured.out
    assert "Invalid API response." in captured.out