from fastapi import FastAPI, UploadFile, File
import uuid

from app.storage import save_file

app = FastAPI()

@app.get("/")
def home():
    return {"message": "FinIntel backend is running"}

@app.post("/documents")
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a financial document (PDF / image).
    """
    contents = await file.read()

    job_id = uuid.uuid4().hex
    saved_path = save_file(contents, file.filename)

    return {
        "job_id": job_id,
        "filename": file.filename,
        "saved_path": saved_path
    }
