from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class Finding(BaseModel):
    type: str  # "success" | "warning" | "error"
    title: str
    details: str
    documents: List[str]


class ValidationResponse(BaseModel):
    totalChecks: int
    passed: int
    warnings: int
    errors: int
    findings: List[Finding]


class KnowledgeObject(BaseModel):
    source: str                      # "excel" or "ocr"
    doc_type: str                    # "bank_statement" / "payslip" / "invoice" / "unknown"
    entities: Dict[str, Any]         # your extracted entities, excel rows etc
    tables: List[Any] = []           # optional
    metadata: Dict[str, Any] = {}    # filename, job_id, etc
