import requests
import json
import pandas as pd


# =========================
# CONFIG
# =========================

# COMPANIES = {c["name"]: c["token"] for c in json.load(open("companies.json"))}
companies = pd.read_csv("companies.csv").to_dict("records")
# COMPANIES = ["groww"]

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

    location = location.lower()

    return any(
        term in location
        for term in LOCATION_FILTERS
    )


def matches_title(title: str) -> bool:
    title = title.lower()

    if any(
        exclude in title
        for exclude in TITLE_EXCLUDES
    ):
        return False

    return any(
        term in title
        for term in TITLE_FILTERS
    )


def main():
    matching_jobs = []

    for company in companies:
        name = company["name"]
        token = company["token"]
        company_type = company["type"]

        try:
            jobs = fetch_jobs(token)
            print(f"Fetching {name}...")

            for job in jobs:
                title = job.get("title", "")
                location = job.get("location", {}).get("name", "")

                if not matches_location(location):
                    continue

                if not matches_title(title):
                    continue

                matching_jobs.append({
                    "company": name,
                    "title": title,
                    "location": location,
                    "url": job["absolute_url"],
                })

        except Exception as e:
            print(f"Failed: {token}")
            print(e)

    print()
    print("=" * 100)
    print(f"FOUND {len(matching_jobs)} MATCHING JOBS")
    print("=" * 100)

    for job in matching_jobs:
        print()
        print(f"🏢 {job['company']}")
        print(f"💼 {job['title']}")
        print(f"📍 {job['location']}")
        print(f"🔗 {job['url']}")


if __name__ == "__main__":
    main()