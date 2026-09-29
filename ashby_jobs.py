"""Fetch job listings from a company's Ashby-hosted careers page.

Ashby's public job board API returns every open posting for a company —
including the full HTML description — in a single request, no pagination
and no separate per-job fetch needed (unlike Greenhouse or the Google
scraper).
"""

import requests

JOB_BOARD_URL = "https://api.ashbyhq.com/posting-api/job-board/{token}"


def fetch_jobs(token: str) -> list[dict]:
    response = requests.get(JOB_BOARD_URL.format(token=token), timeout=30)
    response.raise_for_status()

    jobs = []
    for posting in response.json().get("jobs", []):
        jobs.append({
            "id": posting["id"],
            "title": posting.get("title", ""),
            "location": posting.get("location", ""),
            "url": posting.get("jobUrl", ""),
            "description": posting.get("descriptionHtml", ""),
        })

    return jobs
