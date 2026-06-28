from html.parser import HTMLParser

from extract import min_years_experience

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.2"


class _Stripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self._parts = []

    def handle_data(self, data):
        self._parts.append(data)

    def get_text(self) -> str:
        return " ".join(self._parts)


def _strip_html(html: str) -> str:
    s = _Stripper()
    s.feed(html)
    return s.get_text()


def filter_fresher_friendly(jobs: list[dict], max_years: int = 2) -> list[dict]:
    print(f"\nScreening {len(jobs)} jobs (max {max_years} yrs exp)...")
    results = []

    for job in jobs:
        description = _strip_html(job.get("description", ""))
        min_exp = min_years_experience(description)
        friendly = min_exp <= max_years
        icon = "✅" if friendly else "❌"
        print(f"  {icon} {job['company']} — {job['title']} (requires {min_exp}+ yrs)")
        if friendly:
            results.append(job)

    return results
