from fastapi import FastAPI, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import uuid

from app.storage import save_file
from app.jobs import create_job, get_job
from app.processor import process_document

app = FastAPI()

# ✅ Allow frontend to call backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # for demo — allow all
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {"message": "FinIntel backend is running"}


@app.post("/documents")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    contents = await file.read()

    job_id = uuid.uuid4().hex
    saved_path = save_file(contents, file.filename)

    create_job(job_id, file.filename, saved_path)

    background_tasks.add_task(process_document, job_id)

    return {
        "job_id": job_id,
        "status": "QUEUED"
    }


@app.get("/jobs/{job_id}")
def job_status(job_id: str):
    job = get_job(job_id)
    if not job:
        return {"error": "Job not found"}
    return job


@app.get("/jobs/{job_id}/result")
def get_job_result(job_id: str):
    job = get_job(job_id)
    if not job:
        return {"error": "Job not found"}

    if job["status"] != "DONE":
        return {"status": job["status"], "message": "Result not ready yet"}

    return job["result"]
