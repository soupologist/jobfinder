"""Fetch job listings from a company's Lever-hosted careers page.

Lever's public postings API returns every open posting for a company —
including the full HTML description — in a single request, no pagination
and no separate per-job fetch needed (unlike Greenhouse or the Google
scraper).
"""

import requests

POSTINGS_URL = "https://api.lever.co/v0/postings/{token}"


def fetch_jobs(token: str) -> list[dict]:
    response = requests.get(
        POSTINGS_URL.format(token=token),
        params={"mode": "json"},
        timeout=30,
    )
    response.raise_for_status()

    jobs = []
    for posting in response.json():
        jobs.append({
            "id": posting["id"],
            "title": posting.get("text", ""),
            "location": posting.get("categories", {}).get("location", ""),
            "url": posting.get("hostedUrl", ""),
            "description": posting.get("description", ""),
        })

    return jobs
