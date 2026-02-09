import requests

def call_ocr_service(file_path: str) -> dict:
    # CHANGE THIS URL to AIML teammate endpoint
    OCR_URL = "http://127.0.0.1:9001/ocr"

    with open(file_path, "rb") as f:
        files = {"file": f}
        r = requests.post(OCR_URL, files=files, timeout=60)
    r.raise_for_status()
    return r.json()

def call_validation_service(knowledge_object: dict) -> dict:
    # CHANGE THIS URL to validation teammate endpoint
    VAL_URL = "http://127.0.0.1:9002/validate"

    r = requests.post(VAL_URL, json=knowledge_object, timeout=60)
    r.raise_for_status()
    return r.json()
