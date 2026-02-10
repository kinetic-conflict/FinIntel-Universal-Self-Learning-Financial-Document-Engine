from fastapi import FastAPI, UploadFile, File, BackgroundTasks
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
import os
import uuid

from app.storage import save_file
from app.jobs import create_job, get_job, init_db
from app.processor import process_document

app = FastAPI()


# ---------- INIT ----------
@app.on_event("startup")
def startup():
    init_db()


# ---------- FRONTEND PATH SETUP ----------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

STATIC_DIR = os.path.join(FRONTEND_DIR, "static")
if os.path.isdir(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


# ---------- FRONTEND ROUTES ----------
@app.get("/")
def root():
    return RedirectResponse(url="/upload")


@app.get("/upload")
def upload_page():
    return FileResponse(os.path.join(FRONTEND_DIR, "upload.html"))


@app.get("/review")
def review_page():
    return FileResponse(os.path.join(FRONTEND_DIR, "review.html"))


@app.get("/final")
def final_page():
    return FileResponse(os.path.join(FRONTEND_DIR, "final.html"))


# ---------- BACKEND API ----------
@app.post("/documents")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    contents = await file.read()

    job_id = uuid.uuid4().hex
    path = save_file(contents, file.filename)

    create_job(job_id, file.filename, path)

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
def job_result(job_id: str):
    job = get_job(job_id)
    if not job:
        return {"error": "Job not found"}

    if job["status"] != "DONE":
        return {"status": job["status"]}

    return job["result"]
