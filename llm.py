import requests
from html.parser import HTMLParser

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.2"

_PROMPT = """You are screening job postings for a fresher software engineer with 0–2 years of experience (new graduate).

Job Title: {title}

Job Description:
{description}

Is this role suitable for a fresher or new graduate? Consider it suitable if:
- It's explicitly for interns, new grads, or junior engineers
- It doesn't require more than 2 years of experience
- The title doesn't include Senior, Staff, Lead, Principal, or similar

Reply with ONLY "yes" or "no"."""


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


def is_fresher_friendly(title: str, description: str) -> bool:
    clean = _strip_html(description)[:3000]
    prompt = _PROMPT.format(title=title, description=clean)

    try:
        response = requests.post(
            OLLAMA_URL,
            json={"model": MODEL, "prompt": prompt, "stream": False},
            timeout=60,
        )
        response.raise_for_status()
        answer = response.json()["response"].strip().lower()
        return answer.startswith("yes")
    except requests.exceptions.ConnectionError:
        print(f"  ⚠️  Ollama not running at {OLLAMA_URL} — skipping LLM filter")
        return True
    except Exception as e:
        print(f"  ⚠️  LLM error: {e} — keeping job")
        return True


def filter_fresher_friendly(jobs: list[dict]) -> list[dict]:
    print(f"\n🤖 Screening {len(jobs)} jobs with {MODEL}...")
    results = []

    for job in jobs:
        friendly = is_fresher_friendly(job["title"], job.get("description", ""))
        icon = "✅" if friendly else "❌"
        print(f"  {icon} {job['company']} — {job['title']}")
        if friendly:
            results.append(job)

    return results
