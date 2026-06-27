import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "jobs.db"

VALID_STATUSES = ("new", "applied", "skipped", "interviewing", "rejected", "offer")


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS seen_jobs (
            id          INTEGER PRIMARY KEY,
            company     TEXT,
            title       TEXT,
            url         TEXT,
            first_seen  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status      TEXT NOT NULL DEFAULT 'new'
        )
    """)
    try:
        conn.execute("ALTER TABLE seen_jobs ADD COLUMN status TEXT NOT NULL DEFAULT 'new'")
    except sqlite3.OperationalError:
        pass  # column already exists
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


def get_jobs(status: str | None = None) -> list[dict]:
    with _connect() as conn:
        if status:
            rows = conn.execute(
                "SELECT id, company, title, url, first_seen, status FROM seen_jobs "
                "WHERE status = ? ORDER BY first_seen DESC",
                (status,),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT id, company, title, url, first_seen, status FROM seen_jobs "
                "ORDER BY first_seen DESC"
            ).fetchall()
    return [
        {"id": r[0], "company": r[1], "title": r[2], "url": r[3], "first_seen": r[4], "status": r[5]}
        for r in rows
    ]


def update_status(job_id: int, status: str) -> bool:
    if status not in VALID_STATUSES:
        raise ValueError(f"Invalid status '{status}'. Choose from: {VALID_STATUSES}")
    with _connect() as conn:
        cursor = conn.execute(
            "UPDATE seen_jobs SET status = ? WHERE id = ?", (status, job_id)
        )
        conn.commit()
        return cursor.rowcount > 0


def delete_job(job_id: int) -> bool:
    with _connect() as conn:
        cursor = conn.execute("DELETE FROM seen_jobs WHERE id = ?", (job_id,))
        conn.commit()
        return cursor.rowcount > 0


def clean_jobs(status: str, older_than_days: int | None = None) -> int:
    if status not in VALID_STATUSES:
        raise ValueError(f"Invalid status '{status}'. Choose from: {VALID_STATUSES}")
    with _connect() as conn:
        if older_than_days:
            cursor = conn.execute(
                "DELETE FROM seen_jobs WHERE status = ? AND first_seen < datetime('now', ?)",
                (status, f"-{older_than_days} days"),
            )
        else:
            cursor = conn.execute("DELETE FROM seen_jobs WHERE status = ?", (status,))
        conn.commit()
        return cursor.rowcount
