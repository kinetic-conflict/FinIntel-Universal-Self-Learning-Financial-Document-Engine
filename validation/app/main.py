from fastapi import FastAPI
from app.schemas import KnowledgeObject, ValidationResponse
from app.rules import validate_bank_statement, validate_generic

app = FastAPI(title="FinIntel Validation Service", version="0.1.0")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/validate", response_model=ValidationResponse)
def validate(payload: KnowledgeObject):
    filename = payload.metadata.get("filename", "unknown")

    # Excel rows are inside payload.entities["rows"]
    rows = payload.entities.get("rows", [])
    doc_type = payload.doc_type or "unknown"

    if doc_type == "bank_statement" and isinstance(rows, list):
        total, passed, warnings, errors, findings = validate_bank_statement(rows, filename)
    else:
        total, passed, warnings, errors, findings = validate_generic(doc_type, filename)

    return {
        "totalChecks": total,
        "passed": passed,
        "warnings": warnings,
        "errors": errors,
        "findings": findings
    }
