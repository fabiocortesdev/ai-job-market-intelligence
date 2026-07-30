GERMAN_LOCATIONS = {
    "auerbach",
    "augsburg",
    "bad dürkheim",
    "berlin",
    "berlin office",
    "berlin, berlin, germany",
    "berlin, germany",
    "bremen",
    "brunnthal",
    "cologne",
    "darmstadt",
    "dessau-roßlau",
    "dortmund, nordrhein-westfalen, deutschland",
    "frankfurt am main",
    "georgensgmünd",
    "germany",
    "gilching",
    "gilching, bayern, germany",
    "hamburg",
    "heidelberg",
    "ingelheim am rhein",
    "kassel",
    "langenhagen",
    "leer",
    "leipzig",
    "mainz",
    "munich",
    "mörfelden-walldorf",
    "mülheim",
    "münchen",
    "münster",
    "nürnberg",
    "römerberg",
    "singen",
    "stuttgart",
    "taunusstein",
    "würzburg",
}


AMBIGUOUS_LOCATIONS = {
    "",
    "homeoffice",
    "n/a",
    "remote",
    "remote job",
    "remote; remote - europe",
}


INCLUDE_GERMANY_AFTER_REVIEW = {
    "sales-director-dach-429913",
    "account-executive-dach-mid-market-192279",
    "remote-senior-product-manager-vcs-ecosystem-173221",
    "remote-werkstudent-finance-beratung-unternehmerisch-leistungsbasiert-hamburg-24797",
    "remote-werkstudent-executive-search-active-sourcing-berlin-221596",
    "remote-senior-staff-product-engineer-frontend-koln-102759",
    "remote-senior-staff-product-engineer-full-stack-koln-89000",
    "remote-solution-sales-executive-public-sector-region-sud-260084",
    "remote-solution-sales-executive-public-sector-region-nord-181591",
    "staff-senior-ai-engineer-ai-for-code-amsterdam-netherlands-belgrade-serbia-berlin-germany-limassol-cyprus-london-spain-munich-germany-war-97112",
    "remote-senior-product-manager-vcs-ecosystem-214366",
}


EXCLUDE_OUTSIDE_GERMANY_AFTER_REVIEW = {
    "remote-senior-commercial-account-executive-cis-russian-speaker-63307",
    "principal-data-scientist-london-zurich-302530",
    "product-growth-analytics-lead-amsterdam-netherlands-london-252385",
    "large-enterprise-account-executive-nordics-amsterdam-nl-copenhagen-dk-375429",
}


EXCLUDE_INSUFFICIENT_EVIDENCE_AFTER_REVIEW = {
    "remote-system-engineer-token-factory-370942",
    "senior-manager-application-security-engineering-emea-n-a-317454",
    "senior-it-operations-engineer-411931",
    "senior-solutions-architect-large-retail-account-21103",
    "remote-senior-talent-acquisition-manager-tech-435621",
    "remote-senior-people-culture-business-partner-tech-333751",
    "director-of-operations-248873",
    "remote-presales-sr-solutions-architect-french-defense-and-intelligence-329348",
}


def classify_geographic_scope(location):
    if not isinstance(location, str):
        return "needs_review"

    normalized_location = location.strip().casefold()

    if normalized_location in AMBIGUOUS_LOCATIONS:
        return "needs_review"

    if normalized_location in GERMAN_LOCATIONS:
        return "germany_confirmed"

    if ";" in normalized_location:
        return "needs_review"

    return "outside_germany"


def make_final_geographic_decision(job):
    initial_scope = classify_geographic_scope(job.get("location"))
    slug = job.get("slug")

    if initial_scope == "germany_confirmed":
        return "include_germany"

    if initial_scope == "outside_germany":
        return "exclude_outside_germany"

    if slug in INCLUDE_GERMANY_AFTER_REVIEW:
        return "include_germany"

    if slug in EXCLUDE_OUTSIDE_GERMANY_AFTER_REVIEW:
        return "exclude_outside_germany"

    if slug in EXCLUDE_INSUFFICIENT_EVIDENCE_AFTER_REVIEW:
        return "exclude_insufficient_evidence"

    return "unresolved"
