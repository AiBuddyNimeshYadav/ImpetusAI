"""
RAG Service — Document ingestion + retrieval with ChromaDB.

Handles: PDF/DOCX/MD parsing → text chunking → embedding → vector storage → retrieval.
"""

import logging
import os
import uuid
from pathlib import Path

import chromadb
from chromadb.config import Settings as ChromaSettings

from backend.app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class RAGService:
    """Retrieval-Augmented Generation pipeline."""

    def __init__(self):
        self._client: chromadb.ClientAPI | None = None
        self._embedding_fn = None

    @property
    def client(self) -> chromadb.ClientAPI:
        if self._client is None:
            persist_dir = settings.CHROMA_PERSIST_DIR
            os.makedirs(persist_dir, exist_ok=True)
            self._client = chromadb.PersistentClient(
                path=persist_dir,
                settings=ChromaSettings(anonymized_telemetry=False),
            )
        return self._client

    @property
    def embedding_fn(self):
        if self._embedding_fn is None:
            from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
            self._embedding_fn = SentenceTransformerEmbeddingFunction(
                model_name=settings.EMBEDDING_MODEL
            )
        return self._embedding_fn

    def get_collection(self, name: str = "hr_policies"):
        """Get or create a ChromaDB collection."""
        return self.client.get_or_create_collection(
            name=name,
            embedding_function=self.embedding_fn,
            metadata={"hnsw:space": "cosine"},
        )

    # ── Document Parsing ────────────────────────────────────────────

    def _parse_pdf(self, file_path: str) -> str:
        """Extract text from a PDF file."""
        from pypdf import PdfReader
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n\n"
        return text.strip()

    def _parse_docx(self, file_path: str) -> str:
        """Extract text from a DOCX file."""
        from docx import Document as DocxDocument
        doc = DocxDocument(file_path)
        return "\n\n".join(p.text for p in doc.paragraphs if p.text.strip())

    def _parse_markdown(self, file_path: str) -> str:
        """Read a markdown/text file."""
        return Path(file_path).read_text(encoding="utf-8")

    def parse_document(self, file_path: str) -> str:
        """Parse a document based on its extension."""
        ext = Path(file_path).suffix.lower()
        if ext == ".pdf":
            return self._parse_pdf(file_path)
        elif ext == ".docx":
            return self._parse_docx(file_path)
        elif ext in (".md", ".txt", ".text"):
            return self._parse_markdown(file_path)
        else:
            raise ValueError(f"Unsupported file type: {ext}")

    # ── Chunking ────────────────────────────────────────────────────

    def chunk_text(self, text: str) -> list[str]:
        """Split text into overlapping chunks."""
        chunk_size = settings.RAG_CHUNK_SIZE * 4  # rough char-to-token ratio
        overlap = settings.RAG_CHUNK_OVERLAP * 4
        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            if chunk.strip():
                chunks.append(chunk.strip())
            start += chunk_size - overlap
        return chunks

    # ── Ingestion ───────────────────────────────────────────────────

    def ingest_document(
        self,
        file_path: str,
        doc_type: str = "hr_policy",
        metadata_extra: dict | None = None,
    ) -> int:
        """
        Parse, chunk, embed, and store a document in ChromaDB.

        Returns the number of chunks created.
        """
        text = self.parse_document(file_path)
        if not text.strip():
            logger.warning(f"Empty document: {file_path}")
            return 0

        chunks = self.chunk_text(text)
        if not chunks:
            return 0

        collection = self.get_collection(name=doc_type)
        filename = Path(file_path).name

        ids = []
        documents = []
        metadatas = []

        for i, chunk in enumerate(chunks):
            chunk_id = f"{filename}__chunk_{i}_{uuid.uuid4().hex[:8]}"
            meta = {
                "source": filename,
                "chunk_index": i,
                "doc_type": doc_type,
            }
            if metadata_extra:
                meta.update(metadata_extra)

            ids.append(chunk_id)
            documents.append(chunk)
            metadatas.append(meta)

        collection.add(ids=ids, documents=documents, metadatas=metadatas)
        logger.info(f"Ingested {len(chunks)} chunks from {filename} → collection '{doc_type}'")
        return len(chunks)

    # ── Retrieval ───────────────────────────────────────────────────

    def search(
        self,
        query: str,
        collection_name: str = "hr_policies",
        top_k: int | None = None,
    ) -> list[dict]:
        """
        Search the vector store for relevant chunks.

        Returns list of {"content": ..., "metadata": ..., "score": ...}
        """
        k = top_k or settings.RAG_TOP_K
        collection = self.get_collection(name=collection_name)

        if collection.count() == 0:
            logger.warning(f"Collection '{collection_name}' is empty")
            return []

        results = collection.query(
            query_texts=[query],
            n_results=min(k, collection.count()),
            include=["documents", "metadatas", "distances"],
        )

        hits = []
        if results and results["documents"]:
            for doc, meta, dist in zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0],
            ):
                # ChromaDB cosine distance: 0 = identical, 2 = opposite
                # Convert to similarity score: 1 - (distance / 2)
                score = 1.0 - (dist / 2.0)
                if score >= settings.RAG_SCORE_THRESHOLD:
                    hits.append({
                        "content": doc,
                        "metadata": meta,
                        "score": round(score, 4),
                    })

        return hits

    def ingest_demo_policies(self, demo_dir: str) -> int:
        """Ingest all demo policy files from a directory."""
        total = 0
        demo_path = Path(demo_dir)
        if not demo_path.exists():
            logger.warning(f"Demo directory does not exist: {demo_dir}")
            return 0

        for f in demo_path.iterdir():
            if f.suffix.lower() in (".md", ".txt", ".pdf", ".docx"):
                try:
                    count = self.ingest_document(
                        str(f),
                        doc_type="hr_policies",
                        metadata_extra={"is_demo": True},
                    )
                    total += count
                except Exception as e:
                    logger.error(f"Failed to ingest {f.name}: {e}")
        return total


# ── Module-level singleton ──────────────────────────────────────────
_rag: RAGService | None = None


def get_rag_service() -> RAGService:
    global _rag
    if _rag is None:
        _rag = RAGService()
    return _rag
