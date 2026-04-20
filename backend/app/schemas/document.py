"""Document-related Pydantic schemas."""

from pydantic import BaseModel
from datetime import datetime


class DocumentResponse(BaseModel):
    id: str
    filename: str
    original_name: str
    file_size: int
    doc_type: str
    category: str
    description: str | None = None
    chunk_count: int
    is_indexed: bool
    is_demo: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class DocumentUploadResponse(BaseModel):
    document: DocumentResponse
    chunks_created: int
    message: str
