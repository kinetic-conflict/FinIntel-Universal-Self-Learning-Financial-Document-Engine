import sqlite3
import json
from pathlib import Path

DB_PATH = Path("data/jobs.db")


def init_db():
    DB_PATH.parent.mkdir(exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            job_id TEXT PRIMARY KEY,
            filename TEXT,
            path TEXT,
            status TEXT,
            result TEXT
        )
    """)

    conn.commit()
    conn.close()


def create_job(job_id: str, filename: str, path: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO jobs (job_id, filename, path, status, result)
        VALUES (?, ?, ?, ?, ?)
    """, (job_id, filename, path, "QUEUED", None))

    conn.commit()
    conn.close()


def get_job(job_id: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT job_id, filename, path, status, result
        FROM jobs WHERE job_id = ?
    """, (job_id,))

    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return {
        "job_id": row[0],
        "filename": row[1],
        "path": row[2],
        "status": row[3],
        "result": json.loads(row[4]) if row[4] else None
    }


def update_job_status(job_id: str, status: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE jobs SET status = ? WHERE job_id = ?
    """, (status, job_id))

    conn.commit()
    conn.close()


def set_job_result(job_id: str, result: dict):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE jobs SET result = ?, status = 'DONE'
        WHERE job_id = ?
    """, (json.dumps(result), job_id))

    conn.commit()
    conn.close()
