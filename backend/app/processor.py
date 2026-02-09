# backend/app/processor.py

from openpyxl import load_workbook
from datetime import datetime, date
from decimal import Decimal

from app.jobs import update_job_status, set_job_result, get_job
from app.client import call_ocr_service, call_validation_service


# -------------------- DOC TYPE GUESS (optional) --------------------
def guess_doc_type(filename: str) -> str:
    name = filename.lower()

    if "bank" in name or "statement" in name:
        return "bank_statement"
    if "payslip" in name or "salary" in name:
        return "payslip"
    if "invoice" in name or "bill" in name:
        return "invoice"

    return "unknown"


# -------------------- FILE TYPE CHECK --------------------
# openpyxl supports .xlsx, NOT .xls
def is_excel(filename: str) -> bool:
    return filename.lower().endswith(".xlsx")


# -------------------- JSON SAFE CONVERTER --------------------
def make_json_safe(value):
    # Excel can return datetime/date, Decimal, etc.
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    return value


# -------------------- EXCEL -> JSON-LIKE DATA --------------------
def excel_to_knowledge(excel_path: str) -> dict:
    """
    Reads the first sheet in Excel (.xlsx) and converts it into:
    {
      "rows": [
        {"Header1": value1, "Header2": value2, ...},
        ...
      ]
    }
    Assumption: first row has column headers.
    """
    wb = load_workbook(excel_path, data_only=True)
    sheet = wb.active

    rows = list(sheet.iter_rows(values_only=True))

    if not rows or len(rows) < 2:
        return {"rows": [], "note": "Excel empty or missing rows"}

    # headers from first row
    headers = []
    for h in rows[0]:
        if h is None:
            headers.append("")
        else:
            headers.append(str(h).strip())

    data_rows = []
    for row in rows[1:]:
        record = {}
        for i in range(len(headers)):
            key = headers[i] if headers[i] else f"col_{i}"
            value = row[i] if i < len(row) else None
            record[key] = make_json_safe(value)  # ✅ JSON-safe
        data_rows.append(record)

    return {"rows": data_rows}


# -------------------- MAIN BACKGROUND PROCESS --------------------
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

        # ---------- Build knowledge object depending on file type ----------
        if is_excel(filename):
            extracted = excel_to_knowledge(path)

            knowledge_object = {
                "source": "excel",
                "doc_type": doc_type,
                "entities": extracted,   # stored inside entities for now
                "tables": [],
                "metadata": {
                    "filename": filename,
                    "job_id": job_id
                }
            }

        else:
            # OCR path
            ocr_result = call_ocr_service(path)

            knowledge_object = {
                "source": "ocr",
                "doc_type": doc_type,
                "entities": ocr_result.get("entities", {}),
                "tables": ocr_result.get("tables", []),
                "metadata": {
                    "filename": filename,
                    "job_id": job_id
                }
            }

        # ---------- Validation always runs (but don't crash if service is down) ----------
        try:
            validation_result = call_validation_service(knowledge_object)
        except Exception as e:
            validation_result = {
                "error": str(e),
                "totalChecks": 0,
                "passed": 0,
                "warnings": 0,
                "errors": 1,
                "findings": [
                    {
                        "type": "error",
                        "title": "Validation service not reachable",
                        "details": str(e),
                        "documents": [filename]
                    }
                ]
            }

        # ---------- Final result stored in job ----------
        result = {
            "doc_type": doc_type,
            "source": knowledge_object["source"],
            "entities": knowledge_object["entities"],
            "tables": knowledge_object["tables"],
            "validation": validation_result,
            "metadata": knowledge_object["metadata"]  # optional but useful
        }

        set_job_result(job_id, result)
        update_job_status(job_id, "DONE")

    except Exception as e:
        set_job_result(job_id, {"error": str(e)})
        update_job_status(job_id, "FAILED")
