"""Fetch job listings from a company's Zoho Recruit careers site.

Zoho's official Recruit API needs OAuth credentials from the company's own
account, but the public careers page server-renders every open job —
including the full HTML description — as JSON in a hidden <input>. One GET
and a parse gets everything: no JS, no pagination, no per-job fetch.

The token is the careers site hostname (e.g. "career.qure.ai"). The embedded
blob is undocumented, so if it disappears this raises rather than quietly
returning zero jobs.
"""

import json

import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0"}


def fetch_jobs(token: str) -> list[dict]:
    response = requests.get(f"https://{token}/jobs/Careers", headers=HEADERS, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    blob = next(
        (el["value"] for el in soup.select('input[type="hidden"][value]')
         if "Posting_Title" in el["value"]),
        None,
    )
    if blob is None:
        raise RuntimeError(
            f"No embedded job data found on {token} — the Zoho Recruit page "
            "structure may have changed, or the company has no openings."
        )

    jobs = []
    for posting in json.loads(blob):
        location = ", ".join(
            part for part in (posting.get("City"), posting.get("State"), posting.get("Country")) if part
        )
        jobs.append({
            "id": posting["id"],
            "title": posting.get("Posting_Title", ""),
            "location": location,
            "url": f"https://{token}/jobs/Careers/{posting['id']}",
            "description": posting.get("Job_Description") or "",
        })

    return jobs
