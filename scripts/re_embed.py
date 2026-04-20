"""
Script to re-embed documents when the embedding model is updated.

Usage:
    cd backend
    python ../scripts/re_embed.py
"""

import os
import sys
import logging
from sqlalchemy import select
import asyncio

# Add project root to python path to import everything
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.database import async_session_maker, init_db
from backend.app.models.document import Document
from ai.rag.retriever import get_rag_service
from backend.app.config import get_settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("re_embed")

async def re_embed_all_documents():
    """Fetches all documents currently in the DB and re-ingests them using the updated model."""
    settings = get_settings()
    logger.info(f"Starting re-embedding process using model: {settings.EMBEDDING_MODEL}")
    
    rag = get_rag_service()
    
    # 1. Clear existing collection
    for col in ["hr_policies", "hr_policy"]:
        try:
            rag.client.delete_collection(col)
            logger.info(f"Cleared existing collection: {col}")
        except Exception:
            pass
            
    # 2. Reingest from source files
    async with async_session_maker() as db:
        result = await db.execute(select(Document))
        docs = result.scalars().all()
        
        logger.info(f"Found {len(docs)} documents to re-embed.")
        
        for doc in docs:
            if not os.path.exists(doc.file_path):
                logger.warning(f"File not found on disk, skipping: {doc.file_path}")
                continue
                
            try:
                logger.info(f"Re-embedding {doc.original_name}...")
                chunk_count = rag.ingest_document(
                    doc.file_path,
                    doc_type=doc.doc_type if doc.doc_type != "hr_policy" else "hr_policies",
                    metadata_extra={"category": doc.category},
                )
                
                # Update DB chunk count
                doc.chunk_count = chunk_count
                await db.flush()
                logger.info(f"Success! {chunk_count} chunks generated.")
                
            except Exception as e:
                logger.error(f"Failed to ingest {doc.file_path}: {e}")

        await db.commit()

    logger.info("Re-embedding complete. Note: Demo policies must be seeded again on app restart.")

if __name__ == "__main__":
    asyncio.run(re_embed_all_documents())
