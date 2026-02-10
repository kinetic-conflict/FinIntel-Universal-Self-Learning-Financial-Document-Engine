from pydantic import BaseModel, Field
from typing import List, Dict, Any


class KnowledgeObject(BaseModel):
    source: str = "excel"
    doc_type: str = "unknown"
    entities: Dict[str, Any] = Field(default_factory=dict)
    tables: List[Any] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Finding(BaseModel):
    type: str
    title: str
    details: str
    documents: List[str] = Field(default_factory=list)


class ValidationResult(BaseModel):
    totalChecks: int
    passed: int
    warnings: int
    errors: int
    findings: List[Finding] = Field(default_factory=list)
