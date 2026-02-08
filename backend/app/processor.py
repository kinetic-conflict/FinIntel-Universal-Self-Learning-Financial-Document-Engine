import time
from app.jobs import update_job_status, set_job_result

def process_document(job_id: str):
    update_job_status(job_id, "RUNNING")

    # simulate processing time
    time.sleep(3)

    # mock Challenge-2 knowledge object
    result = {
        "doc_type": "unknown",
        "entities": {},
        "tables": [],
        "validation_status": "NEEDS_REVIEW"
    }

    set_job_result(job_id, result)
    update_job_status(job_id, "DONE")
