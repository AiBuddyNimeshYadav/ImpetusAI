"""Documents API — upload HR policies, list, delete."""

import os
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_db
from app.models.document import Document
from app.models.user import User
from app.api.deps import get_current_user
from app.schemas.document import DocumentResponse, DocumentUploadResponse
from ai.rag.retriever import get_rag_service

router = APIRouter(prefix="/documents", tags=["Documents"])
settings = get_settings()

# Role → allowed doc_types for upload
_ROLE_DOC_PERMISSIONS: dict[str, list[str]] = {
    "admin": ["hr_policy", "it_runbook", "sop", "general"],
    "hr_admin": ["hr_policy"],
    "it_agent": ["it_runbook", "sop", "general"],
}


@router.post("/upload", response_model=DocumentUploadResponse, status_code=201)
async def upload_document(
    file: UploadFile = File(...),
    doc_type: str = "hr_policy",
    category: str = "General",
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Upload and ingest a document into the RAG knowledge base."""
    allowed_types = _ROLE_DOC_PERMISSIONS.get(current_user.role)
    if allowed_types is None:
        raise HTTPException(status_code=403, detail="No permission to upload documents.")
    if doc_type not in allowed_types:
        raise HTTPException(
            status_code=403,
            detail=f"Role '{current_user.role}' cannot upload '{doc_type}'. "
            f"Allowed: {allowed_types}",
        )

    # Validate file type
    allowed = (".pdf", ".docx", ".md", ".txt")
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in allowed:
        raise HTTPException(status_code=400, detail=f"Unsupported file type. Allowed: {allowed}")

    # Validate file size
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    content = await file.read()
    if len(content) > max_bytes:
        raise HTTPException(status_code=400, detail=f"File too large. Max: {settings.MAX_UPLOAD_SIZE_MB}MB")

    # Save file
    upload_dir = os.path.join(settings.UPLOAD_DIR, doc_type)
    os.makedirs(upload_dir, exist_ok=True)

    unique_name = f"{uuid.uuid4().hex[:12]}_{file.filename}"
    file_path = os.path.join(upload_dir, unique_name)
    with open(file_path, "wb") as f:
        f.write(content)

    # Ingest into vector store
    rag = get_rag_service()
    try:
        chunk_count = rag.ingest_document(
            file_path,
            doc_type=doc_type if doc_type != "hr_policy" else "hr_policies",
            metadata_extra={"category": category},
        )
    except Exception as e:
        os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")

    # Save document record
    doc = Document(
        filename=unique_name,
        original_name=file.filename or "unknown",
        file_path=file_path,
        file_size=len(content),
        doc_type=doc_type,
        category=category,
        chunk_count=chunk_count,
        is_indexed=True,
        uploaded_by=current_user.id,
    )
    db.add(doc)
    await db.flush()
    await db.refresh(doc)

    return DocumentUploadResponse(
        document=DocumentResponse.model_validate(doc),
        chunks_created=chunk_count,
        message=f"Document '{file.filename}' uploaded and indexed ({chunk_count} chunks).",
    )


@router.get("", response_model=list[DocumentResponse])
async def list_documents(
    doc_type: str | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all uploaded documents."""
    query = select(Document).order_by(Document.created_at.desc())
    if doc_type:
        query = query.where(Document.doc_type == doc_type)
    result = await db.execute(query)
    return [DocumentResponse.model_validate(d) for d in result.scalars().all()]


@router.get("/policy/{filename}")
async def get_policy_file(filename: str):
    """Serve a demo policy document by filename (public, read-only)."""
    if "/" in filename or "\\" in filename or ".." in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")
    demo_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "demo_policies"))
    file_path = os.path.join(demo_dir, filename)
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="Policy file not found")
    return FileResponse(file_path, media_type="text/plain; charset=utf-8")


@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a document and its file."""
    result = await db.execute(select(Document).where(Document.id == document_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Only uploaders and privileged roles can delete
    privileged = current_user.role in ("admin", "hr_admin", "it_agent")
    if not privileged and doc.uploaded_by != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Remove file
    if os.path.exists(doc.file_path):
        os.remove(doc.file_path)

    await db.delete(doc)
    return {"status": "deleted", "document_id": document_id}
