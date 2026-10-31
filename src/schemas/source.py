from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class SearchResultItem(BaseModel):
    """Raw search or document item retrieved from external sources."""
    title: str = Field(description="Title of source document or web page")
    url: str = Field(description="URL or file path of the source")
    content: str = Field(description="Raw snippet or extracted text content")
    score: float = Field(default=1.0, description="Search relevance score")
    source_type: str = Field(default="web", description="'web' or 'document'")

class EvidenceChunk(BaseModel):
    """Atomic evidence chunk stored in ChromaDB with metadata for verification."""
    chunk_id: str = Field(description="Unique identifier for chunk")
    source_id: int = Field(description="Numeric citation ID (e.g., 1, 2, 3)")
    title: str = Field(description="Title of source")
    url: str = Field(description="Source URL or file path")
    source_type: str = Field(default="web", description="'web' or 'document'")
    text: str = Field(description="Actual content snippet")
    topic_tag: str = Field(default="general", description="Subtopic category")
    similarity_score: float = Field(default=0.0, description="Vector similarity score")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
