from urllib.parse import urlparse


SOURCE_MARKETS = {
    "arbeitnow.com": {
        "source_market": "Germany",
        "source_market_code": "DE",
    },
    "www.arbeitnow.com": {
        "source_market": "Germany",
        "source_market_code": "DE",
    },
    "arbeitnow.co.uk": {
        "source_market": "United Kingdom",
        "source_market_code": "GB",
    },
    "www.arbeitnow.co.uk": {
        "source_market": "United Kingdom",
        "source_market_code": "GB",
    },
}


def extract_source_domain(url):
    if not isinstance(url, str) or not url.strip():
        return None

    parsed_url = urlparse(url.strip())

    return parsed_url.netloc.casefold() or None


def classify_source_market(job):
    domain = extract_source_domain(job.get("url"))

    market = SOURCE_MARKETS.get(domain)

    if market is None:
        return {
            "source_domain": domain,
            "source_market": None,
            "source_market_code": None,
            "market_status": "unresolved",
            "market_reason": "unknown_source_domain",
        }

    return {
        "source_domain": domain,
        "source_market": market["source_market"],
        "source_market_code": market["source_market_code"],
        "market_status": "confirmed",
        "market_reason": "source_domain",
    }