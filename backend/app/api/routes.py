"""
Documents:
  POST   /api/documents/upload          - Upload PDF -> classify -> store on disk + DB
  GET    /api/documents/                - List all documents
  GET    /api/documents/{id}            - Get by DB id
  GET    /api/documents/{id}/file       - Download stored PDF
  GET    /api/documents/hash/{doc_hash} - Get by SHA-256 hash

Audit:
  POST   /api/audit/verify              - Upload PDF for audit verification
  GET    /api/audit/{doc_hash}          - Full audit: DB + chain
  GET    /api/audit/chain/{doc_hash}    - Blockchain-only lookup
  GET    /api/audit/stats/summary       - Registry statistics

Models:
  GET    /api/models                    - List available models

Health:
  GET    /health
"""

import hashlib
import io
import logging
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.core.config import settings
from app.models.document import DocumentRecord
from app.api.schemas import (
    ClassificationResponse,
    DocumentSummary,
    AuditResponse,
    AuditVerification,
    HealthResponse,
)
from app.services.ml_service import (
    MLService,
    get_ml_service,
    get_available_models,
)
from app.services.blockchain_service import BlockchainService, get_blockchain_service
from app.services.storage_service import StorageService, get_storage_service

logger = logging.getLogger(__name__)
router = APIRouter()

MAX_BYTES = settings.MAX_FILE_SIZE_MB * 1024 * 1024


# Health
@router.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check(
    db: AsyncSession = Depends(get_db),
    ml: MLService = Depends(get_ml_service),
    chain: BlockchainService = Depends(get_blockchain_service),
):
    total_db = await db.scalar(select(func.count()).select_from(DocumentRecord)) or 0
    return HealthResponse(
        status="ok",
        model_loaded=ml.is_loaded,
        blockchain_connected=chain.is_connected,
        contract_address=settings.CONTRACT_ADDRESS or None,
        total_documents_db=total_db,
        total_documents_chain=chain.get_total_documents(),
    )


# Models
@router.get(
    "/api/models", tags=["Models"], summary="List available models and versions"
)
async def list_models():
    return get_available_models()


# Documents
@router.post(
    "/api/documents/upload",
    response_model=ClassificationResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Documents"],
    summary="Upload a PDF, classify it, store on disk and in DB",
)
async def upload_document(
    file: Annotated[UploadFile, File(description="PDF document to classify")],
    model_name: str = Form(default="SVM"),
    model_version: str = Form(default="1.0"),
    db: AsyncSession = Depends(get_db),
    ml: MLService = Depends(get_ml_service),
    chain: BlockchainService = Depends(get_blockchain_service),
    storage: StorageService = Depends(get_storage_service),
):
    if file.content_type not in ("application/pdf", "application/octet-stream"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Only PDF files are accepted.",
        )

    pdf_bytes = await file.read()

    if len(pdf_bytes) > MAX_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_TOO_LARGE,
            detail=f"File too large. Max size: {settings.MAX_FILE_SIZE_MB} MB.",
        )

    # ML classification
    try:
        result = ml.classify(pdf_bytes, model_name=model_name, version=model_version)
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
        )

    doc_hash = result["doc_hash"]
    classification = result["label"]
    model_hash = result["model_hash"]
    decision_index = result["decision_index"]

    # Duplicate check
    existing = await db.scalar(
        select(DocumentRecord).where(DocumentRecord.doc_hash == doc_hash)
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Document already registered. Hash: {doc_hash}",
        )

    # Save PDF to S3-compatible storage (SeaweedFS)
    object_key = storage.get_object_key(doc_hash)
    storage.upload_file(object_key, pdf_bytes, "application/pdf")
    logger.info("PDF uploaded to S3 as '%s'", object_key)

    # Blockchain registration
    tx_hash = None
    on_chain = False
    uploader_address = None

    if chain.is_ready:
        try:
            tx_result = chain.register_classification(
                doc_hash, model_hash, decision_index
            )
            if tx_result["status"] == 1:
                tx_hash = tx_result["tx_hash"]
                on_chain = True
                uploader_address = tx_result["uploader"]
                logger.info(
                    "Registered on chain. tx=%s block=%s", tx_hash, tx_result["block"]
                )
            else:
                logger.warning("Blockchain tx reverted for doc_hash=%s", doc_hash)
        except Exception as e:
            logger.error("Blockchain registration failed: %s", e)
    else:
        logger.warning("Blockchain not ready - skipping for %s", doc_hash)

    # Persist to SQLite
    record = DocumentRecord(
        filename=file.filename or "unknown.pdf",
        doc_hash=doc_hash,
        classification=classification,
        model_hash=model_hash,
        file_path=object_key,
        blockchain_tx=tx_hash,
        on_chain=on_chain,
        uploader_address=uploader_address,
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)

    return record


@router.get(
    "/api/documents/",
    response_model=list[DocumentSummary],
    tags=["Documents"],
    summary="List all registered documents",
)
async def list_documents(
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(DocumentRecord)
        .order_by(DocumentRecord.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


@router.get(
    "/api/documents/hash/{doc_hash}",
    response_model=ClassificationResponse,
    tags=["Documents"],
    summary="Look up a document by its SHA-256 hash",
)
async def get_document_by_hash(doc_hash: str, db: AsyncSession = Depends(get_db)):
    if not doc_hash.startswith("0x"):
        doc_hash = "0x" + doc_hash
    record = await db.scalar(
        select(DocumentRecord).where(DocumentRecord.doc_hash == doc_hash)
    )
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Document not found."
        )
    return record


@router.get(
    "/api/documents/{doc_id}/file",
    tags=["Documents"],
    summary="Download the stored PDF for a document",
)
async def get_document_file(
    doc_id: int,
    db: AsyncSession = Depends(get_db),
    storage: StorageService = Depends(get_storage_service),
):
    record = await db.get(DocumentRecord, doc_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Document not found."
        )
    if not record.file_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No file key stored for this document.",
        )
    try:
        pdf_bytes = storage.download_file(record.file_path)
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found in object storage.",
        )
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{record.filename}"'
        },
    )


@router.get(
    "/api/documents/{doc_id}",
    response_model=ClassificationResponse,
    tags=["Documents"],
    summary="Get a document record by database ID",
)
async def get_document(doc_id: int, db: AsyncSession = Depends(get_db)):
    record = await db.get(DocumentRecord, doc_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Document not found."
        )
    return record


# Audit
@router.post(
    "/api/audit/verify",
    response_model=AuditResponse,
    tags=["Audit"],
    summary="Upload a PDF to verify: re-classify and compare hash + model + decision",
)
async def audit_verify(
    file: Annotated[UploadFile, File(description="PDF to verify")],
    db: AsyncSession = Depends(get_db),
    ml: MLService = Depends(get_ml_service),
    chain: BlockchainService = Depends(get_blockchain_service),
):
    pdf_bytes = await file.read()

    # compute hash of uploaded file
    uploaded_hash = "0x" + hashlib.sha256(pdf_bytes).hexdigest()

    # look up original record by hash
    db_record = await db.scalar(
        select(DocumentRecord).where(DocumentRecord.doc_hash == uploaded_hash)
    )
    chain_record = chain.get_classification(uploaded_hash) if chain.is_ready else None

    if not db_record and not chain_record:
        return AuditResponse(
            db_record=None,
            chain_record=None,
            hashes_match=None,
            verification=None,
            message="Document not found - this file was never registered.",
        )

    # doc hash check
    doc_hash_matches = (
        db_record is not None
    )  # if we found it by hash, hash matches by definition

    # re-run classification using the same model that was used originally
    stored_model_hash = (
        db_record.model_hash if db_record else chain_record["model_hash"]
    )
    stored_classification = (
        db_record.classification if db_record else chain_record["decision"].lower()
    )

    # find which model/version has this hash
    registry = get_available_models()
    matched_model_name = None
    matched_model_version = None
    for m_name, versions in registry.items():
        for v, meta in versions.items():
            candidate = meta["hash"]
            if not candidate.startswith("0x"):
                candidate = "0x" + candidate
            if candidate == stored_model_hash:
                matched_model_name = m_name
                matched_model_version = v
                break
        if matched_model_name:
            break

    rerun_classification = None
    current_model_hash = stored_model_hash  # fallback

    if matched_model_name:
        try:
            rerun_result = ml.classify(
                pdf_bytes, model_name=matched_model_name, version=matched_model_version
            )
            rerun_classification = rerun_result["label"]
            current_model_hash = rerun_result["model_hash"]
        except Exception as e:
            logger.error("Re-classification failed: %s", e)
            rerun_classification = "error"
    else:
        # Model not found in registry - use default model
        logger.warning("Original model hash not found in registry, using default model")
        try:
            rerun_result = ml.classify(pdf_bytes)
            rerun_classification = rerun_result["label"]
            current_model_hash = rerun_result["model_hash"]
        except Exception:
            rerun_classification = "error"

    model_hash_matches = current_model_hash == stored_model_hash
    classification_matches = rerun_classification == stored_classification

    # Build verdict
    checks = []
    if doc_hash_matches:
        checks.append("Document hash matches")
    else:
        checks.append("Document hash mismatch")

    if model_hash_matches:
        checks.append("Model hash matches")
    else:
        checks.append("Model hash mismatch")

    if classification_matches:
        checks.append(f"Classification consistent ({rerun_classification})")
    else:
        checks.append(
            f"Classification changed: was '{stored_classification}', now '{rerun_classification}'"
        )

    all_ok = doc_hash_matches and model_hash_matches and classification_matches
    verdict = (
        "All checks passed, so document is authentic"
        if all_ok
        else "Verification failed"
    )

    verification = AuditVerification(
        doc_hash_matches=doc_hash_matches,
        model_hash_matches=model_hash_matches,
        classification_matches=classification_matches,
        rerun_classification=rerun_classification,
        stored_classification=stored_classification,
        stored_model_hash=stored_model_hash,
        current_model_hash=current_model_hash,
        verdict=verdict,
    )

    # DB vs chain match
    hashes_match = None
    message_parts = checks

    if db_record and chain_record:
        db_class = db_record.classification.upper()
        chain_class = chain_record["decision"]
        hashes_match = db_class == chain_class

    return AuditResponse(
        db_record=db_record,
        chain_record=chain_record,
        hashes_match=hashes_match,
        verification=verification,
        message=" & ".join(message_parts),
    )


@router.get(
    "/api/audit/stats/summary",
    tags=["Audit"],
    summary="Registry statistics",
)
async def get_stats(
    db: AsyncSession = Depends(get_db),
    chain: BlockchainService = Depends(get_blockchain_service),
):
    total_db = await db.scalar(select(func.count()).select_from(DocumentRecord))
    on_chain_count = await db.scalar(
        select(func.count()).select_from(DocumentRecord).where(DocumentRecord.on_chain)
    )
    class_counts_result = await db.execute(
        select(DocumentRecord.classification, func.count()).group_by(
            DocumentRecord.classification
        )
    )
    class_breakdown = {row[0]: row[1] for row in class_counts_result.all()}

    return {
        "total_documents_db": total_db,
        "on_chain_count": on_chain_count,
        "pending_chain": (total_db or 0) - (on_chain_count or 0),
        "total_documents_chain": chain.get_total_documents()
        if chain.is_ready
        else None,
        "classification_breakdown": class_breakdown,
        "blockchain_connected": chain.is_connected,
    }


@router.get(
    "/api/audit/chain/{doc_hash}",
    tags=["Audit"],
    summary="Direct blockchain lookup (no DB)",
)
async def get_chain_record(
    doc_hash: str,
    chain: BlockchainService = Depends(get_blockchain_service),
):
    if not chain.is_ready:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Blockchain service not available.",
        )
    if not doc_hash.startswith("0x"):
        doc_hash = "0x" + doc_hash
    record = chain.get_classification(doc_hash)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {doc_hash} not found on blockchain.",
        )
    return record


@router.get(
    "/api/audit/{doc_hash}",
    response_model=AuditResponse,
    tags=["Audit"],
    summary="Full audit: verify DB record matches blockchain",
)
async def audit_document(
    doc_hash: str,
    db: AsyncSession = Depends(get_db),
    chain: BlockchainService = Depends(get_blockchain_service),
):
    if not doc_hash.startswith("0x"):
        doc_hash = "0x" + doc_hash

    db_record = await db.scalar(
        select(DocumentRecord).where(DocumentRecord.doc_hash == doc_hash)
    )
    chain_record = chain.get_classification(doc_hash) if chain.is_ready else None

    if not db_record and not chain_record:
        return AuditResponse(
            db_record=None,
            chain_record=None,
            hashes_match=None,
            verification=None,
            message="Document not found in database or on blockchain.",
        )

    hashes_match = None
    message_parts = []

    if db_record and chain_record:
        db_class = db_record.classification.upper()
        chain_class = chain_record["decision"]
        hashes_match = db_class == chain_class
        if hashes_match:
            message_parts.append(f"Classifications match: {db_class}")
        else:
            message_parts.append(
                f"Mismatch! DB says '{db_class}', chain says '{chain_class}'"
            )
    elif db_record and not chain_record:
        message_parts.append("Found in database but NOT on blockchain.")
    elif chain_record and not db_record:
        message_parts.append("Found on blockchain but NOT in database.")

    return AuditResponse(
        db_record=db_record,
        chain_record=chain_record,
        hashes_match=hashes_match,
        verification=None,
        message=" & ".join(message_parts),
    )
