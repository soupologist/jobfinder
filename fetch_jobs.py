import requests
import json
import pandas as pd

from yoe_extractor import extract_seniority, extract_years
from llm import filter_fresher_friendly


# =========================
# CONFIG
# =========================

companies = pd.read_csv("companies.csv").to_dict("records")

LOCATION_FILTERS = [
    "bengaluru",
    "bangalore",
    "india",
    "gurgaon",
    "gurugram",
    "hyderabad",
    "mumbai"
]

TITLE_FILTERS = [
    "software engineer",
    "backend",
    "infrastructure",
    "platform",
    "full stack",
    "full-stack",
    "new grad",
    "university",
    "engineering",
    "engineer"
]

TITLE_EXCLUDES = [
    "senior",
    "staff",
    "sr",
    "principal",
    "director",
    "manager",
    "support",
    "reliability"
]

# =========================


def fetch_jobs(board_token: str):
    url = f"https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs"
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.json()["jobs"]


def matches_location(location: str) -> bool:
    if not location:
        return False
    return any(term in location.lower() for term in LOCATION_FILTERS)


def matches_title(title: str) -> bool:
    title = title.lower()
    if any(exclude in title for exclude in TITLE_EXCLUDES):
        return False
    return any(term in title for term in TITLE_FILTERS)


def get_matching_jobs() -> list[dict]:
    matching_jobs = []

    for company in companies:
        name = company["name"]
        token = company["token"]

        try:
            jobs = fetch_jobs(token)
            print(f"Fetching {name}...")

            for job in jobs:
                title = job.get("title", "")
                location = job.get("location", {}).get("name", "")
                description = job.get("content", "")

                if not matches_location(location):
                    continue
                if not matches_title(title):
                    continue

                min_years, max_years = extract_years(description)
                seniority = extract_seniority(title, description)

                matching_jobs.append({
                    "id": job["id"],
                    "company": name,
                    "title": title,
                    "location": location,
                    "url": job["absolute_url"],
                    "description": description,
                    "min_years": min_years,
                    "max_years": max_years,
                    "seniority": seniority,
                })

        except Exception as e:
            print(f"Failed: {token}")
            print(e)

    return matching_jobs


def print_jobs(jobs: list[dict], label: str = "MATCHING") -> None:
    print()
    print("=" * 100)
    print(f"FOUND {len(jobs)} {label} JOBS")
    print("=" * 100)

    for job in jobs:
        print()
        print(f"🏢 {job['company']}")
        print(f"💼 {job['title']}")
        print(f"📍 {job['location']}")

        if job["min_years"] is not None:
            if job["max_years"] is not None:
                print(f"📈 Experience: {job['min_years']}-{job['max_years']} years")
            else:
                print(f"📈 Experience: {job['min_years']}+ years")

        print(f"🎯 Seniority: {job['seniority']}")
        print(f"🔗 {job['url']}")


def main():
    jobs = get_matching_jobs()
    jobs = filter_fresher_friendly(jobs)
    print_jobs(jobs)


if __name__ == "__main__":
    main()
