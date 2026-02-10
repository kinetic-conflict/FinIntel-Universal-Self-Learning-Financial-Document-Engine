# backend/app/jobs.py
import json
from typing import Optional, Dict, Any

from app.db import get_conn

# In-memory cache (fast)
JOBS: Dict[str, Dict[str, Any]] = {}

def create_job(job_id: str, filename: str, path: str):
    job = {
        "job_id": job_id,
        "filename": filename,
        "path": path,
        "status": "QUEUED",
        "result": None
    }
    JOBS[job_id] = job

    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT OR REPLACE INTO jobs (job_id, filename, path, status, result_json) VALUES (?, ?, ?, ?, ?)",
        (job_id, filename, path, "QUEUED", None),
    )
    conn.commit()
    conn.close()

def get_job(job_id: str) -> Optional[dict]:
    # 1) Try memory
    if job_id in JOBS:
        return JOBS[job_id]

    # 2) Fallback DB
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM jobs WHERE job_id = ?", (job_id,))
    row = cur.fetchone()
    conn.close()

    if not row:
        return None

    result = json.loads(row["result_json"]) if row["result_json"] else None
    job = {
        "job_id": row["job_id"],
        "filename": row["filename"],
        "path": row["path"],
        "status": row["status"],
        "result": result
    }
    JOBS[job_id] = job
    return job

def update_job_status(job_id: str, status: str):
    job = get_job(job_id)
    if not job:
        return

    job["status"] = status
    JOBS[job_id] = job

    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE jobs SET status = ? WHERE job_id = ?", (status, job_id))
    conn.commit()
    conn.close()

def set_job_result(job_id: str, result: dict):
    job = get_job(job_id)
    if not job:
        return

    job["result"] = result
    JOBS[job_id] = job

    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE jobs SET result_json = ? WHERE job_id = ?", (json.dumps(result), job_id))
    conn.commit()
    conn.close()
