# backend/app/main.py
from contextlib import asynccontextmanager
import uuid

from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException

from app.storage import save_file
from app.jobs import create_job, get_job
from app.processor import process_document
from app.db import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/")
def home():
    return {"message": "FinIntel backend is running"}

@app.post("/documents")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    try:
        contents = await file.read()

        job_id = uuid.uuid4().hex
        saved_path = save_file(contents, file.filename)

        create_job(job_id, file.filename, saved_path)
        background_tasks.add_task(process_document, job_id)

        return {"job_id": job_id, "status": "QUEUED"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.get("/jobs/{job_id}")
def job_status(job_id: str):
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@app.get("/jobs/{job_id}/result")
def job_result(job_id: str):
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.get("status") != "DONE":
        return {"status": job.get("status"), "message": "Result not ready yet"}

    return job.get("result")
