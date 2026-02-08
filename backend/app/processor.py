import time
from app.jobs import update_job_status

def process_document(job_id: str):
    """
    Simulates document processing.
    Later this will do OCR, extraction, validation.
    """
    update_job_status(job_id, "RUNNING")

    # simulate heavy processing
    time.sleep(5)

    update_job_status(job_id, "DONE")
