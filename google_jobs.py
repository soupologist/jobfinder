"""Fetch and parse job listings from Google's careers site.

Google doesn't offer a public jobs API like Greenhouse's boards-api, so this
scrapes the server-rendered HTML of careers.google.com/jobs/results. That
page happens to render full job cards (title, location, qualifications, job
id) in the initial HTML response, no JS execution needed, and supports
deep-linkable pagination via a `page` query param.

The markup is Google-internal and undocumented, so it can change without
notice. If the expected elements disappear, fetch_jobs() raises instead of
silently returning nothing, so a broken scraper is noticed rather than
mistaken for "no matching jobs".

Scraping ~30 pages of listings plus a description page per matched job adds
up fast if run frequently (e.g. from a cron job), so both are cached in
jobs.db and only re-fetched once the cache is more than a day old.
"""

import json
import sqlite3
from datetime import datetime, timedelta, timezone
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from store import DB_PATH

BASE_URL = "https://www.google.com/about/careers/applications/"
RESULTS_URL = BASE_URL + "jobs/results/"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}

CACHE_MAX_AGE = timedelta(days=1)


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS google_jobs_cache (
            location    TEXT PRIMARY KEY,
            payload     TEXT NOT NULL,
            fetched_at  TIMESTAMP NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS google_job_description_cache (
            id          INTEGER PRIMARY KEY,
            description TEXT NOT NULL,
            fetched_at  TIMESTAMP NOT NULL
        )
    """)
    return conn


def _is_fresh(fetched_at: str) -> bool:
    return datetime.now(timezone.utc) - datetime.fromisoformat(fetched_at) < CACHE_MAX_AGE


def _read_jobs_cache(location: str) -> list[dict] | None:
    with _connect() as conn:
        row = conn.execute(
            "SELECT payload, fetched_at FROM google_jobs_cache WHERE location = ?",
            (location,),
        ).fetchone()
    if not row or not _is_fresh(row[1]):
        return None
    return json.loads(row[0])


def _write_jobs_cache(location: str, jobs: list[dict]) -> None:
    with _connect() as conn:
        conn.execute(
            "INSERT INTO google_jobs_cache (location, payload, fetched_at) VALUES (?, ?, ?) "
            "ON CONFLICT(location) DO UPDATE SET payload = excluded.payload, fetched_at = excluded.fetched_at",
            (location, json.dumps(jobs), datetime.now(timezone.utc).isoformat()),
        )
        conn.commit()


def _read_description_cache(job_id: int) -> str | None:
    with _connect() as conn:
        row = conn.execute(
            "SELECT description, fetched_at FROM google_job_description_cache WHERE id = ?",
            (job_id,),
        ).fetchone()
    if not row or not _is_fresh(row[1]):
        return None
    return row[0]


def _write_description_cache(job_id: int, description: str) -> None:
    with _connect() as conn:
        conn.execute(
            "INSERT INTO google_job_description_cache (id, description, fetched_at) VALUES (?, ?, ?) "
            "ON CONFLICT(id) DO UPDATE SET description = excluded.description, fetched_at = excluded.fetched_at",
            (job_id, description, datetime.now(timezone.utc).isoformat()),
        )
        conn.commit()


def _fetch_page(location: str, page: int) -> str:
    response = requests.get(
        RESULTS_URL,
        params={"location": location, "page": page},
        headers=HEADERS,
        timeout=30,
    )
    response.raise_for_status()
    return response.text


def _parse_listing_page(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    jobs = []

    for card in soup.select("li.lLd3Je"):
        ssk = card.get("ssk", "")
        if ":" not in ssk:
            continue
        job_id = int(ssk.rsplit(":", 1)[-1])

        title_el = card.select_one("h3.QJPWVe")
        title = title_el.get_text(strip=True) if title_el else ""

        company, location = "Google", ""
        meta_el = card.select_one("p.l103df")
        if meta_el:
            meta_text = meta_el.get_text(" ", strip=True)
            if "|" in meta_text:
                company_part, location_part = meta_text.split("|", 1)
                company = company_part.strip() or "Google"
                location = location_part.strip()

        link_el = card.select_one("a.WpHeLc[href]")
        url = urljoin(BASE_URL, link_el["href"]) if link_el else ""

        if not title or not url:
            continue

        jobs.append({
            "id": job_id,
            "company": company,
            "title": title,
            "location": location,
            "url": url,
        })

    return jobs


def fetch_jobs(location: str = "India", max_pages: int = 30) -> list[dict]:
    """Fetch all Google job listings for a location, across pages.

    Cached in jobs.db for a day, since a full scrape is ~30 requests.
    """
    cached = _read_jobs_cache(location)
    if cached is not None:
        return cached

    all_jobs = []
    seen_ids = set()

    for page in range(1, max_pages + 1):
        jobs = _parse_listing_page(_fetch_page(location, page))
        new_jobs = [j for j in jobs if j["id"] not in seen_ids]
        if not new_jobs:
            break
        seen_ids.update(j["id"] for j in new_jobs)
        all_jobs.extend(new_jobs)

    if not all_jobs:
        raise RuntimeError(
            "Parsed 0 Google jobs — careers.google.com's page structure "
            "may have changed and google_jobs.py needs updating."
        )

    _write_jobs_cache(location, all_jobs)
    return all_jobs


def fetch_job_description(job_id: int, url: str) -> str:
    """Fetch the full description HTML for a single Google job posting.

    Cached in jobs.db for a day, keyed by job id.
    """
    cached = _read_description_cache(job_id)
    if cached is not None:
        return cached

    response = requests.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    container = soup.select_one("div.aG5W3")
    description = str(container) if container else ""

    _write_description_cache(job_id, description)
    return description
