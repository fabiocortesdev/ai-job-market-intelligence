import re


SKILL_PATTERNS = {
    "python": [r"\bpython\b"],
    "sql": [r"\bsql\b"],
    "power_bi": [r"\bpower\s*bi\b"],
    "tableau": [r"\btableau\b"],
    "excel": [r"\bexcel\b"],
    "azure": [r"\bazure\b"],
    "aws": [r"\baws\b", r"\bamazon web services\b"],
    "gcp": [r"\bgcp\b", r"\bgoogle cloud(?: platform)?\b"],
    "spark": [r"\b(?:apache\s+)?spark\b", r"\bpyspark\b"],
    "pandas": [r"\bpandas\b"],
    "docker": [r"\bdocker\b"],
    "kubernetes": [r"\bkubernetes\b", r"\bk8s\b"],
    "git": [r"\bgit\b", r"\bgithub\b", r"\bgitlab\b"],
    "machine_learning": [
    r"\bmachine learning\b",
    r"\bmaschinell(?:e|er|es|en|em)?\s+lernen\b",
],
"artificial_intelligence": [
    r"\bartificial intelligence\b",
    r"\bkünstlich(?:e|er|es|en|em)?\s+intelligenz\b",
    r"\bki\b",
],
}


def detect_skills(*text_values):
    combined_text = " ".join(
        value for value in text_values if isinstance(value, str)
    )

    detected_skills = []

    for skill, patterns in SKILL_PATTERNS.items():
        if any(
            re.search(pattern, combined_text, flags=re.IGNORECASE)
            for pattern in patterns
        ):
            detected_skills.append(skill)

    return detected_skills