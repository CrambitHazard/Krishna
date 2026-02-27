"""
KRISHNA — Document service.

Extracts text from uploaded PDFs (via pypdf) and chunks the text into
segments suitable for embedding (~500-800 tokens ≈ 2000-3200 chars).

Chunking strategy
-----------------
* Splits on paragraph boundaries (double newlines).
* Merges small paragraphs into chunks until the soft limit is reached.
* Uses a configurable overlap so retrieval never loses cross-boundary context.
"""

from __future__ import annotations

import io
import logging
import uuid
from dataclasses import dataclass, field
from typing import Any

from pypdf import PdfReader

from app.core.vector_store import VectorStore

logger = logging.getLogger(__name__)

# ── Chunking tunables ───────────────────────────────────────────────────
_CHUNK_TARGET_CHARS = 2500     # ~625 tokens (≈ 4 chars/token)
_CHUNK_MAX_CHARS    = 3200     # hard ceiling  (~800 tokens)
_CHUNK_OVERLAP_CHARS = 200     # carry-over between consecutive chunks


@dataclass
class ProcessingResult:
    """Returned by DocumentService.process()."""
    document_id: str
    filename: str
    total_pages: int
    total_chunks: int
    chunk_ids: list[int] = field(default_factory=list)


class DocumentService:
    """Extracts, chunks, and indexes uploaded documents."""

    # ── PDF text extraction ─────────────────────────────────────────────
    @staticmethod
    def extract_text_from_pdf(content: bytes) -> tuple[str, int]:
        """
        Extract all text from a PDF byte stream.

        Returns
        -------
        tuple[str, int]
            (full_text, page_count)
        """
        reader = PdfReader(io.BytesIO(content))
        pages: list[str] = []
        for page in reader.pages:
            text = page.extract_text() or ""
            pages.append(text)
        full_text = "\n\n".join(pages)
        return full_text, len(reader.pages)

    # ── Semantic-aware chunking ─────────────────────────────────────────
    @staticmethod
    def chunk_text(
        text: str,
        target: int = _CHUNK_TARGET_CHARS,
        maximum: int = _CHUNK_MAX_CHARS,
        overlap: int = _CHUNK_OVERLAP_CHARS,
    ) -> list[str]:
        """
        Split *text* into overlapping segments of roughly *target* characters,
        respecting paragraph boundaries where possible.

        Parameters
        ----------
        text    : source text
        target  : soft character target per chunk
        maximum : hard character ceiling per chunk
        overlap : characters carried over between chunks
        """
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        if not paragraphs:
            return []

        chunks: list[str] = []
        current = ""

        for para in paragraphs:
            # If adding this paragraph stays within the soft limit → merge
            if len(current) + len(para) + 2 <= target:
                current = f"{current}\n\n{para}".strip()
            else:
                # Flush current chunk
                if current:
                    chunks.append(current)
                # If paragraph itself exceeds max, hard-split it
                if len(para) > maximum:
                    for i in range(0, len(para), maximum - overlap):
                        chunks.append(para[i : i + maximum])
                    current = ""
                else:
                    # Start overlap from the tail of the previous chunk
                    if chunks:
                        tail = chunks[-1][-overlap:]
                        current = f"{tail}\n\n{para}".strip()
                    else:
                        current = para

        if current:
            chunks.append(current)

        return chunks

    # ── Full pipeline ───────────────────────────────────────────────────
    async def process(
        self,
        filename: str,
        content: bytes,
    ) -> ProcessingResult:
        """
        End-to-end: extract → chunk → embed → store in vector DB.

        Returns a ``ProcessingResult`` with the document metadata.
        """
        document_id = str(uuid.uuid4())

        # 1. Extract
        raw_text, page_count = self.extract_text_from_pdf(content)
        logger.info(
            "Extracted %d chars from '%s' (%d pages).",
            len(raw_text), filename, page_count,
        )

        # 2. Chunk
        chunks = self.chunk_text(raw_text)
        logger.info("Produced %d chunks from '%s'.", len(chunks), filename)

        if not chunks:
            return ProcessingResult(
                document_id=document_id,
                filename=filename,
                total_pages=page_count,
                total_chunks=0,
            )

        # 3. Build per-chunk metadata
        metadatas: list[dict[str, Any]] = [
            {
                "document_id": document_id,
                "filename": filename,
                "chunk_index": i,
            }
            for i in range(len(chunks))
        ]

        # 4. Embed + store
        store = VectorStore.get_instance()
        chunk_ids = store.add_documents(chunks, metadatas)

        return ProcessingResult(
            document_id=document_id,
            filename=filename,
            total_pages=page_count,
            total_chunks=len(chunks),
            chunk_ids=chunk_ids,
        )
