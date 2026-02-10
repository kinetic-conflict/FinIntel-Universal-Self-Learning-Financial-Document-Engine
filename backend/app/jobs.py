from contextlib import asynccontextmanager

from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException
import uuid

from app.storage import save_file
from app.jobs import create_job, get_job
from app.processor import process_document
from app.db import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Runs once when the server starts, and once when it shuts down.
    Replaces deprecated @app.on_event("startup").
    """
    init_db()
    yield
    # If you ever add cleanup (closing DB, etc), do it after yield.


app = FastAPI(lifespan=lifespan)


@app.get("/")
def home():
    return {"message": "FinIntel backend is running"}


@app.post("/upload")
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
):
    """
    1) Save uploaded file
    2) Create a job
    3) Start background processing
    """
    try:
        job_id = str(uuid.uuid4())

        # save_file should return (filename, path) OR a dict with these
        saved = await save_file(file) if callable(getattr(save_file, "__await__", None)) else save_file(file)

        # Support both return styles: tuple or dict
        if isinstance(saved, (tuple, list)) and len(saved) >= 2:
            filename, path = saved[0], saved[1]
        elif isinstance(saved, dict) and "filename" in saved and "path" in saved:
            filename, path = saved["filename"], saved["path"]
        else:
            raise ValueError("save_file() must return (filename, path) or {'filename':..., 'path':...}")

        create_job(job_id=job_id, filename=filename, path=path)

        # Run processing in background
        background_tasks.add_task(process_document, job_id)

        return {"job_id": job_id, "status": "queued"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {e}")


@app.get("/jobs/{job_id}")
def job_status(job_id: str):
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job
