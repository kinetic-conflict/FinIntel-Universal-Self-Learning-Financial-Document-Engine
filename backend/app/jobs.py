import json
from typing import Optional, Dict, Any

from app.db import get_conn


def create_job(job_id: str, filename: str, path: str):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        "INSERT OR REPLACE INTO jobs (job_id, filename, path, status, result_json) VALUES (?, ?, ?, ?, ?)",
        (job_id, filename, path, "QUEUED", None),
    )

    conn.commit()
    conn.close()


def get_job(job_id: str) -> Optional[Dict[str, Any]]:
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT job_id, filename, path, status, result_json, created_at FROM jobs WHERE job_id = ?", (job_id,))
    row = cur.fetchone()
    conn.close()

    if not row:
        return None

    result = None
    if row["result_json"]:
        try:
            result = json.loads(row["result_json"])
        except:
            result = row["result_json"]

    return {
        "job_id": row["job_id"],
        "filename": row["filename"],
        "path": row["path"],
        "status": row["status"],
        "result": result,
        "created_at": row["created_at"],
    }


def update_job_status(job_id: str, status: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE jobs SET status = ? WHERE job_id = ?", (status, job_id))
    conn.commit()
    conn.close()


def set_job_result(job_id: str, result: Dict[str, Any]):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "UPDATE jobs SET result_json = ?, status = ? WHERE job_id = ?",
        (json.dumps(result), "DONE", job_id),
    )
    conn.commit()
    conn.close()
