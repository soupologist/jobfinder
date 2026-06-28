"""
Test the years-of-experience regex against real Greenhouse job postings.

Usage:
    python try_job.py <board-token>

Example:
    python try_job.py singlestore
"""

import sys
import requests
from fetch_jobs import matches_location, matches_title
from llm import _strip_html
from extract import min_years_experience


def fetch_jobs(board_token: str) -> list[dict]:
    url = f"https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs"
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    return r.json()["jobs"]


def fetch_job_detail(board_token: str, job_id: int) -> str:
    url = f"https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs/{job_id}"
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    return r.json().get("content", "")


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)

    board_token = sys.argv[1]
    print(f"Fetching jobs for '{board_token}'...")
    all_jobs = fetch_jobs(board_token)

    jobs = [
        j for j in all_jobs
        if matches_location(j.get("location", {}).get("name", ""))
        and matches_title(j.get("title", ""))
    ]
    print(f"Found {len(all_jobs)} openings, {len(jobs)} after location/title filter.\n")

    for i, job in enumerate(jobs, 1):
        title    = job.get("title", "")
        location = job.get("location", {}).get("name", "").strip()
        job_id   = job.get("id")

        print(f"[{i}/{len(jobs)}] {title}  |  {location}")
        print(f"  {job.get('absolute_url', '')}")

        description = fetch_job_detail(board_token, job_id)
        clean = _strip_html(description)
        min_exp = min_years_experience(clean)
        icon = "✅" if min_exp <= 2 else "❌"
        print(f"  {icon}  min_exp={min_exp}")
        print()


if __name__ == "__main__":
    main()
