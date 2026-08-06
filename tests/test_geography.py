from src.geography import (
    classify_source_market,
    extract_source_domain,
)


def test_extract_source_domain_from_valid_url():
    result = extract_source_domain(
        "https://www.arbeitnow.com/jobs/example-job"
    )

    assert result == "www.arbeitnow.com"


def test_extract_source_domain_returns_none_for_missing_url():
    assert extract_source_domain(None) is None
    assert extract_source_domain("") is None


def test_classify_german_source_market():
    job = {
        "url": "https://www.arbeitnow.com/jobs/data-analyst",
    }

    result = classify_source_market(job)

    assert result == {
        "source_domain": "www.arbeitnow.com",
        "source_market": "Germany",
        "source_market_code": "DE",
        "market_status": "confirmed",
        "market_reason": "source_domain",
    }


def test_classify_united_kingdom_source_market():
    job = {
        "url": "https://www.arbeitnow.co.uk/jobs/data-analyst",
    }

    result = classify_source_market(job)

    assert result == {
        "source_domain": "www.arbeitnow.co.uk",
        "source_market": "United Kingdom",
        "source_market_code": "GB",
        "market_status": "confirmed",
        "market_reason": "source_domain",
    }


def test_classify_unknown_source_as_unresolved():
    job = {
        "url": "https://example.com/jobs/data-analyst",
    }

    result = classify_source_market(job)

    assert result == {
        "source_domain": "example.com",
        "source_market": None,
        "source_market_code": None,
        "market_status": "unresolved",
        "market_reason": "unknown_source_domain",
    }


def test_remote_location_does_not_change_source_market():
    job = {
        "url": "https://www.arbeitnow.co.uk/jobs/remote-engineer",
        "location": "remote",
    }

    result = classify_source_market(job)

    assert result["source_market_code"] == "GB"
    assert result["market_status"] == "confirmed"