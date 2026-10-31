import io
import logging
from typing import List, Dict, Any, BinaryIO
from src.schemas.source import SearchResultItem
from src.config import settings

logger = logging.getLogger(__name__)

class DocumentLoader:
    """Extracts, chunks, and formats content from uploaded PDF, TXT, and Markdown documents."""

    def __init__(self, chunk_size: int = settings.CHUNK_SIZE, chunk_overlap: int = settings.CHUNK_OVERLAP):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def process_file(self, filename: str, file_bytes: bytes) -> List[SearchResultItem]:
        """Extract text from uploaded file buffer and split into chunked SearchResultItems."""
        filename_lower = filename.lower()
        full_text = ""

        try:
            if filename_lower.endswith(".pdf"):
                full_text = self._extract_pdf(file_bytes)
            elif filename_lower.endswith((".txt", ".md", ".csv", ".json")):
                full_text = file_bytes.decode("utf-8", errors="replace")
            else:
                full_text = file_bytes.decode("utf-8", errors="ignore")
        except Exception as e:
            logger.error(f"Error parsing document {filename}: {e}")
            return []

        if not full_text.strip():
            logger.warning(f"File {filename} produced no readable text.")
            return []

        chunks = self._chunk_text(full_text)
        results: List[SearchResultItem] = []

        for i, chunk in enumerate(chunks):
            results.append(
                SearchResultItem(
                    title=f"{filename} (Section {i+1})",
                    url=f"local://uploaded_docs/{filename}#chunk-{i+1}",
                    content=chunk,
                    score=1.0,
                    source_type="document",
                )
            )

        logger.info(f"Loaded '{filename}': generated {len(results)} chunks.")
        return results

    def _extract_pdf(self, file_bytes: bytes) -> str:
        """Extract plain text from PDF bytes using pypdf."""
        import pypdf
        reader = pypdf.PdfReader(io.BytesIO(file_bytes))
        pages_text = []
        for idx, page in enumerate(reader.pages):
            text = page.extract_text()
            if text:
                pages_text.append(f"--- Page {idx+1} ---\n{text}")
        return "\n\n".join(pages_text)

    def _chunk_text(self, text: str) -> List[str]:
        """Chunk text with character overlap."""
        text = text.replace("\r\n", "\n")
        chunks = []
        start = 0
        text_length = len(text)

        while start < text_length:
            end = min(start + self.chunk_size, text_length)
            
            # Try to break on newline or space rather than cutting words
            if end < text_length:
                break_point = text.rfind("\n", start, end)
                if break_point == -1 or break_point < start + (self.chunk_size // 2):
                    break_point = text.rfind(" ", start, end)
                if break_point != -1 and break_point > start:
                    end = break_point

            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)

            start = end - self.chunk_overlap
            if start < 0 or start >= text_length or end >= text_length:
                break

        return chunks
