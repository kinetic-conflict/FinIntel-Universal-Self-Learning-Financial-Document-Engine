from fastapi import FastAPI
from app.schemas import KnowledgeObject, ValidationResult
from app.rules import run_validation

app = FastAPI(title="FinIntel Validation Service")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/validate", response_model=ValidationResult)
def validate_document(knowledge: KnowledgeObject):
    return run_validation(knowledge)
