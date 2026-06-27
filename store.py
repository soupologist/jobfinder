import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "jobs.db"


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS seen_jobs (
            id          INTEGER PRIMARY KEY,
            company     TEXT,
            title       TEXT,
            url         TEXT,
            first_seen  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    return conn


def get_seen_ids() -> set[int]:
    with _connect() as conn:
        rows = conn.execute("SELECT id FROM seen_jobs").fetchall()
    return {row[0] for row in rows}


def mark_seen(jobs: list[dict]) -> None:
    with _connect() as conn:
        conn.executemany(
            "INSERT OR IGNORE INTO seen_jobs (id, company, title, url) VALUES (?, ?, ?, ?)",
            [(j["id"], j["company"], j["title"], j["url"]) for j in jobs],
        )
        conn.commit()
