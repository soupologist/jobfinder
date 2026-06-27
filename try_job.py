"""
Walk through a company's Greenhouse openings one by one and see what the LLM thinks.

Usage:
    python try_job.py <board-token>

Example:
    python try_job.py stripe
"""

import sys
import requests
from fetch_jobs import matches_location, matches_title
from llm import _PROMPT, _strip_html, OLLAMA_URL, MODEL


def fetch_jobs(board_token: str) -> list[dict]:
    url = f"https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs"
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    return r.json()["jobs"]


def ask_llm_raw(title: str, description: str) -> str:
    clean = _strip_html(description)[:3000]
    prompt = _PROMPT.format(title=title, description=clean)
    r = requests.post(
        OLLAMA_URL,
        json={"model": MODEL, "prompt": prompt, "stream": False},
        timeout=60,
    )
    r.raise_for_status()
    return r.json()["response"].strip()


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
        location = job.get("location", {}).get("name", "")
        description = job.get("content", "")

        url = job.get("absolute_url", "")
        print(f"[{i}/{len(jobs)}] {title}  |  {location}")
        print(f"  {url}")

        answer = ask_llm_raw(title, description)
        fresher = answer.lower().startswith("yes")
        icon = "✅" if fresher else "❌"
        print(f"  {icon}  LLM: \"{answer}\"\n")


if __name__ == "__main__":
    main()
