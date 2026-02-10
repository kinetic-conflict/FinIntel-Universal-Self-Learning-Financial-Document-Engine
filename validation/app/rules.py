from typing import Any, Dict, List, Tuple, Optional
from datetime import datetime


def _to_float(x) -> Optional[float]:
    if x is None:
        return None
    try:
        return float(x)
    except:
        return None


def _to_date(x) -> Optional[datetime]:
    """
    Backend already converts dates to ISO strings in processor (make_json_safe).
    Example: "2026-02-01T00:00:00"
    """
    if x is None:
        return None
    if isinstance(x, datetime):
        return x
    if isinstance(x, str):
        try:
            return datetime.fromisoformat(x)
        except:
            return None
    return None


def validate_bank_statement(rows: List[Dict[str, Any]], filename: str) -> Tuple[int, int, int, int, List[dict]]:
    total = 0
    passed = 0
    warnings = 0
    errors = 0
    findings = []

    # ---- Rule 1: must have minimum rows ----
    total += 1
    if len(rows) >= 3:
        passed += 1
        findings.append({
            "type": "success",
            "title": "Sufficient transactions found",
            "details": f"Found {len(rows)} rows in bank statement.",
            "documents": [filename]
        })
    else:
        errors += 1
        findings.append({
            "type": "error",
            "title": "Too few transactions",
            "details": f"Only {len(rows)} rows found. Expected at least 3 rows.",
            "documents": [filename]
        })

    # ---- Rule 2: date sequencing (non-decreasing) ----
    total += 1
    dates = [_to_date(r.get("DATE")) for r in rows]
    cleaned = [d for d in dates if d is not None]
    if not cleaned:
        warnings += 1
        findings.append({
            "type": "warning",
            "title": "Dates not detected",
            "details": "Could not parse DATE column. Skipping date sequencing check.",
            "documents": [filename]
        })
    else:
        ok = True
        for i in range(1, len(cleaned)):
            if cleaned[i] < cleaned[i - 1]:
                ok = False
                break
        if ok:
            passed += 1
            findings.append({
                "type": "success",
                "title": "Dates are in sequence",
                "details": "Transaction dates appear chronological.",
                "documents": [filename]
            })
        else:
            warnings += 1
            findings.append({
                "type": "warning",
                "title": "Date order issue",
                "details": "Some transaction dates appear out of order.",
                "documents": [filename]
            })

    # ---- Rule 3: check debit/credit numeric sanity ----
    total += 1
    bad_count = 0
    for r in rows:
        d = _to_float(r.get("DEBIT"))
        c = _to_float(r.get("CREDIT"))
        # allow one of them to be None, but if both present, that's suspicious
        if d is not None and c is not None:
            bad_count += 1
        # negatives are suspicious
        if (d is not None and d < 0) or (c is not None and c < 0):
            bad_count += 1

    if bad_count == 0:
        passed += 1
        findings.append({
            "type": "success",
            "title": "Debit/Credit columns look valid",
            "details": "No obvious issues in DEBIT/CREDIT values.",
            "documents": [filename]
        })
    else:
        warnings += 1
        findings.append({
            "type": "warning",
            "title": "Debit/Credit values may be inconsistent",
            "details": f"Found {bad_count} suspicious debit/credit cases (both present or negative values).",
            "documents": [filename]
        })

    return total, passed, warnings, errors, findings


def validate_generic(doc_type: str, filename: str) -> Tuple[int, int, int, int, List[dict]]:
    # fallback for payslip/invoice/unknown
    total = 1
    passed = 0
    warnings = 1
    errors = 0
    findings = [{
        "type": "warning",
        "title": "Basic validation only",
        "details": f"No specific rules implemented yet for doc_type='{doc_type}'.",
        "documents": [filename]
    }]
    return total, passed, warnings, errors, findings
