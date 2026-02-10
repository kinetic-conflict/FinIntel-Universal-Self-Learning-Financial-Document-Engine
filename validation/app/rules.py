from typing import Dict, Any, List, Union
from app.schemas import KnowledgeObject


def validate_bank_statement(entities: Dict[str, Any], filename: str) -> List[dict]:
    findings = []
    rows = entities.get("rows", [])

    # Rule 1: Minimum transactions
    if len(rows) >= 3:
        findings.append({
            "type": "success",
            "title": "Sufficient transactions found",
            "details": f"{len(rows)} transactions detected",
            "documents": [filename]
        })
    else:
        findings.append({
            "type": "error",
            "title": "Too few transactions",
            "details": "Less than 3 transactions found",
            "documents": [filename]
        })

    # Rule 2: Salary credit check
    salary_found = any(
        "salary" in str(r.get("DESCRIPTION", "")).lower()
        for r in rows
        if isinstance(r, dict)
    )

    if salary_found:
        findings.append({
            "type": "success",
            "title": "Salary credit detected",
            "details": "Salary entry found in statement",
            "documents": [filename]
        })
    else:
        findings.append({
            "type": "warning",
            "title": "Salary credit not found",
            "details": "No salary transaction detected",
            "documents": [filename]
        })

    return findings


def run_validation(knowledge: Union[KnowledgeObject, Dict[str, Any]]) -> Dict[str, Any]:
    # Allow both dict and Pydantic model
    if isinstance(knowledge, KnowledgeObject):
        knowledge_object = knowledge.model_dump()
    else:
        knowledge_object = knowledge

    findings = []

    doc_type = knowledge_object.get("doc_type", "unknown")
    entities = knowledge_object.get("entities", {})
    filename = knowledge_object.get("metadata", {}).get("filename", "unknown")

    if doc_type == "bank_statement":
        findings.extend(validate_bank_statement(entities, filename))
    else:
        findings.append({
            "type": "warning",
            "title": "Unsupported document type",
            "details": f"No rules for {doc_type}",
            "documents": [filename]
        })

    passed = sum(1 for f in findings if f["type"] == "success")
    warnings = sum(1 for f in findings if f["type"] == "warning")
    errors = sum(1 for f in findings if f["type"] == "error")

    return {
        "totalChecks": len(findings),
        "passed": passed,
        "warnings": warnings,
        "errors": errors,
        "findings": findings
    }
