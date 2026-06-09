import re
from typing import Optional

YEARS_PATTERNS = [
    # "5+ years"
    re.compile(r"(\d+)\s*\+\s*years?", re.I),

    # "5 years"
    re.compile(r"(\d+)\s+years?\s+(?:of\s+)?experience", re.I),

    # "5-7 years"
    re.compile(r"(\d+)\s*[-–]\s*(\d+)\s+years?", re.I),

    # "at least 3 years"
    re.compile(r"at\s+least\s+(\d+)\s+years?", re.I),

    # "minimum of 2 years"
    re.compile(r"minimum\s+of\s+(\d+)\s+years?", re.I),

    # "2 or more years"
    re.compile(r"(\d+)\s+or\s+more\s+years?", re.I),
]


def extract_years(text: str) -> tuple[Optional[int], Optional[int]]:
    text = text.lower()

    for pattern in YEARS_PATTERNS:
        match = pattern.search(text)

        if not match:
            continue

        groups = match.groups()

        if len(groups) == 2 and groups[1]:
            return int(groups[0]), int(groups[1])

        return int(groups[0]), None

    return None, None

SENIORITY_PATTERNS = {
    "intern": [
        r"\bintern\b",
        r"\binternship\b",
    ],
    "new_grad": [
        r"new grad",
        r"new graduate",
        r"graduate software engineer",
        r"university graduate",
    ],
    "junior": [
        r"\bjunior\b",
        r"\bjr\.?\b",
    ],
    "mid": [
        r"\bsoftware engineer\b",
        r"\bengineer ii\b",
    ],
    "senior": [
        r"\bsenior\b",
        r"\bsr\.?\b",
        r"\bengineer iii\b",
    ],
    "staff": [
        r"\bstaff engineer\b",
    ],
    "principal": [
        r"\bprincipal engineer\b",
    ],
    "manager": [
        r"\bengineering manager\b",
        r"\bmanager\b",
    ],
}

def extract_seniority(title: str, description: str) -> str:
    text = f"{title} {description}".lower()

    for level, patterns in SENIORITY_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, text):
                return level

    return "unknown"