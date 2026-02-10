from openpyxl import load_workbook
from datetime import datetime, date
from decimal import Decimal

from app.jobs import update_job_status, set_job_result, get_job


def guess_doc_type(filename: str) -> str:
    name = filename.lower()
    if "bank" in name or "statement" in name:
        return "bank_statement"
    if "payslip" in name or "salary" in name:
        return "payslip"
    if "invoice" in name or "bill" in name:
        return "invoice"
    return "unknown"


def is_excel(filename: str) -> bool:
    return filename.lower().endswith(".xlsx")


def make_json_safe(value):
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    return value


def excel_to_rows(excel_path: str):
    wb = load_workbook(excel_path, data_only=True)
    sheet = wb.active

    rows = list(sheet.iter_rows(values_only=True))
    if not rows or len(rows) < 2:
        return []

    headers = [str(h).strip() if h else "" for h in rows[0]]

    data_rows = []
    for r in rows[1:]:
        record = {}
        for i, header in enumerate(headers):
            key = header if header else f"col_{i}"
            val = r[i] if i < len(r) else None
            record[key] = make_json_safe(val)
        data_rows.append(record)

    return data_rows


def process_document(job_id: str):
    update_job_status(job_id, "RUNNING")

    try:
        job = get_job(job_id)
        if not job:
            set_job_result(job_id, {"error": "Job not found"})
            update_job_status(job_id, "FAILED")
            return

        filename = job["filename"]
        path = job["path"]

        doc_type = guess_doc_type(filename)

        if is_excel(filename):
            rows = excel_to_rows(path)
            result = {
                "doc_type": doc_type,
                "source": "excel",
                "entities": {"rows": rows},
                "tables": [],
                "metadata": {"filename": filename, "job_id": job_id},
            }
        else:
            # If non-excel file uploaded, just store info (no OCR yet)
            result = {
                "doc_type": doc_type,
                "source": "file",
                "entities": {},
                "tables": [],
                "metadata": {"filename": filename, "job_id": job_id},
                "note": "Non-Excel file uploaded. OCR not enabled in this minimal backend run.",
            }

        set_job_result(job_id, result)
        update_job_status(job_id, "DONE")

    except Exception as e:
        set_job_result(job_id, {"error": str(e)})
        update_job_status(job_id, "FAILED")
