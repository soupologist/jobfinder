import re

# Matches: "5+ years", "3-5 years", "2 to 4 years",
# "at least 3 years", "minimum 2 years of experience", "1 year"
_YOE_PATTERN = re.compile(
    r"(?:at\s+least\s+|minimum\s+|over\s+)?(\d+)\s*(?:\+|-\d+|\s+to\s+\d+)?\s+years?",
    re.IGNORECASE,
)


def min_years_experience(text: str) -> int:
    matches = [int(m.group(1)) for m in _YOE_PATTERN.finditer(text)]
    return min(matches) if matches else 0
