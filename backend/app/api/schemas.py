"""
Pydantic schemas for API request/response validation
"""

from pydantic import BaseModel, field_serializer
from datetime import datetime
from typing import Optional


class ClassificationResponse(BaseModel):
    """Returned after a successful document upload & classification"""

    id: int
    filename: str
    doc_hash: str
    classification: str
    model_hash: str
    file_path: Optional[str]
    blockchain_tx: Optional[str]
    on_chain: bool
    uploader_address: Optional[str]
    created_at: datetime

    @field_serializer("created_at")
    def serialize_dt(self, dt: datetime) -> str:
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    model_config = {"from_attributes": True}


class DocumentSummary(BaseModel):
    """Compact document info for list endpoints"""

    id: int
    filename: str
    doc_hash: str
    classification: str
    on_chain: bool
    file_path: Optional[str]
    created_at: datetime

    @field_serializer("created_at")
    def serialize_dt(self, dt: datetime) -> str:
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    model_config = {"from_attributes": True}


class AuditVerification(BaseModel):
    """Result of re-running classification during audit"""

    doc_hash_matches: bool  # uploaded file hash == stored hash
    model_hash_matches: bool  # current model hash == stored model hash
    classification_matches: bool  # re-classified result == stored classification
    rerun_classification: str  # model's decision
    stored_classification: str  # what was stored originally
    stored_model_hash: str
    current_model_hash: str
    verdict: str


class AuditResponse(BaseModel):
    """Returned when an auditor looks up a document hash"""

    db_record: Optional[ClassificationResponse]
    chain_record: Optional[dict]
    hashes_match: Optional[bool]
    verification: Optional[AuditVerification]
    message: str


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    blockchain_connected: bool
    contract_address: Optional[str]
    total_documents_db: int
    total_documents_chain: Optional[int]
