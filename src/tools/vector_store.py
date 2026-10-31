import os
import math
import hashlib
import logging
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.api.types import EmbeddingFunction, Documents, Embeddings
from src.schemas.source import SearchResultItem, EvidenceChunk
from src.config import settings

logger = logging.getLogger(__name__)

class DeterministicDenseEmbeddingFunction(EmbeddingFunction[Documents]):
    """Pure-Python normalized dense embedding function.
    Provides 100% reliable fallback vector embeddings without C++ DLL dependencies.
    """
    def __init__(self, dim: int = 128):
        self.dim = dim

    def name(self) -> str:
        return "deterministic_dense"

    def get_config(self) -> Dict[str, Any]:
        return {"dim": self.dim}

    def __call__(self, input: Documents) -> Embeddings:
        embeddings: Embeddings = []
        for text in input:
            vec = [0.0] * self.dim
            words = text.lower().split()
            if not words:
                embeddings.append(vec)
                continue
            for i, w in enumerate(words):
                h = hash(w)
                idx = abs(h) % self.dim
                sign = 1.0 if (h > 0) else -1.0
                vec[idx] += sign * (1.0 / (1.0 + 0.05 * i))
            # L2 normalize
            norm = math.sqrt(sum(x * x for x in vec))
            if norm > 1e-9:
                vec = [x / norm for x in vec]
            embeddings.append(vec)
        return embeddings

class ChromaResearchStore:
    """Manages ChromaDB vector indexing and semantic retrieval for ResearchPilot."""

    def __init__(
        self,
        persist_dir: Optional[str] = None,
        gemini_api_key: Optional[str] = None,
        collection_name: str = settings.CHROMA_COLLECTION,
    ):
        self.persist_dir = persist_dir or str(settings.CHROMA_DIR)
        self.gemini_api_key = gemini_api_key or settings.GEMINI_API_KEY
        self.collection_name = collection_name
        self._source_registry: Dict[str, int] = {}  # URL/Title -> citation_id
        self._next_source_id = 1

        # Initialize Chroma Client
        try:
            self.client = chromadb.PersistentClient(path=self.persist_dir)
            logger.info(f"Initialized Chroma PersistentClient at {self.persist_dir}")
        except Exception as e:
            logger.warning(f"Using ephemeral ChromaDB client: {e}")
            self.client = chromadb.Client()

        # Configure Embedding Function
        self.embedding_function = self._get_embedding_function()

        # Get or create collection (reset if conflicting schema exists)
        try:
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                embedding_function=self.embedding_function,
                metadata={"hnsw:space": "cosine"},
            )
        except Exception as e:
            logger.warning(f"Resetting existing collection due to embedding schema update: {e}")
            try:
                self.client.delete_collection(name=self.collection_name)
            except Exception:
                pass
            self.collection = self.client.create_collection(
                name=self.collection_name,
                embedding_function=self.embedding_function,
                metadata={"hnsw:space": "cosine"},
            )

    def _get_embedding_function(self):
        """Select Gemini Embeddings if available, then ONNX, then pure-Python dense fallback."""
        if self.gemini_api_key and self.gemini_api_key.strip():
            try:
                from chromadb.utils import embedding_functions
                ef = embedding_functions.GoogleGenerativeAiEmbeddingFunction(
                    api_key=self.gemini_api_key.strip(),
                    model_name="models/text-embedding-004",
                )
                logger.info("Using Google text-embedding-004 for ChromaDB.")
                return ef
            except Exception as e:
                logger.warning(f"Google embedding function error: {e}. Checking alternatives.")

        # Try default ONNX embedding if onnxruntime is loaded
        try:
            import onnxruntime
            from chromadb.utils import embedding_functions
            return embedding_functions.DefaultEmbeddingFunction()
        except Exception:
            pass

        # Robust pure-Python dense fallback
        logger.info("Using DeterministicDenseEmbeddingFunction for ChromaDB.")
        return DeterministicDenseEmbeddingFunction(dim=128)

    def add_search_results(self, items: List[SearchResultItem]) -> int:
        """Index external web and document results into ChromaDB with citation IDs."""
        if not items:
            return 0

        documents = []
        metadatas = []
        ids = []

        for item in items:
            # Deterministic source ID for [1], [2], [3] citations
            source_key = item.url or item.title
            if source_key not in self._source_registry:
                self._source_registry[source_key] = self._next_source_id
                self._next_source_id += 1

            source_id = self._source_registry[source_key]

            # Unique deterministic chunk hash
            content_clean = item.content.strip()
            if not content_clean:
                continue

            chunk_id = hashlib.sha256(f"{source_key}:{content_clean[:100]}".encode()).hexdigest()[:16]

            documents.append(content_clean)
            ids.append(chunk_id)
            metadatas.append({
                "source_id": int(source_id),
                "title": item.title,
                "url": item.url,
                "source_type": item.source_type,
                "search_score": float(item.score),
            })

        if not documents:
            return 0

        try:
            self.collection.upsert(
                documents=documents,
                metadatas=metadatas,
                ids=ids,
            )
            logger.info(f"Successfully upserted {len(documents)} chunks to ChromaDB.")
            return len(documents)
        except Exception as e:
            logger.error(f"Failed to upsert to ChromaDB: {e}")
            return 0

    def query(self, query_text: str, n_results: int = settings.TOP_K_RETRIEVAL) -> List[EvidenceChunk]:
        """Perform semantic similarity search and map to structured EvidenceChunks."""
        evidence: List[EvidenceChunk] = []

        total_count = self.collection.count()
        if total_count == 0:
            return evidence

        actual_n = min(n_results, total_count)

        try:
            res = self.collection.query(
                query_texts=[query_text],
                n_results=actual_n,
                include=["documents", "metadatas", "distances"],
            )

            docs = res.get("documents", [[]])[0]
            metas = res.get("metadatas", [[]])[0]
            distances = res.get("distances", [[]])[0] if "distances" in res else [0.0] * len(docs)
            ids = res.get("ids", [[]])[0]

            for doc, meta, dist, cid in zip(docs, metas, distances, ids):
                sim_score = max(0.0, 1.0 - float(dist)) if dist is not None else 0.85
                evidence.append(
                    EvidenceChunk(
                        chunk_id=cid,
                        source_id=meta.get("source_id", 1),
                        title=meta.get("title", "Unknown Source"),
                        url=meta.get("url", ""),
                        source_type=meta.get("source_type", "web"),
                        text=doc,
                        similarity_score=sim_score,
                        topic_tag=meta.get("topic_tag", "general"),
                        metadata=meta,
                    )
                )
        except Exception as e:
            logger.error(f"Error querying ChromaDB: {e}")

        return evidence

    def get_registered_sources(self) -> List[Dict[str, Any]]:
        """Return the authoritative list of cited sources with assigned citation indexes."""
        sources = []
        for url_or_title, sid in sorted(self._source_registry.items(), key=lambda x: x[1]):
            sources.append({
                "source_id": sid,
                "citation_tag": f"[{sid}]",
                "identifier": url_or_title,
            })
        return sources

    def clear(self):
        """Reset the collection and registry."""
        try:
            self.client.delete_collection(name=self.collection_name)
        except Exception:
            pass
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=self.embedding_function,
            metadata={"hnsw:space": "cosine"},
        )
        self._source_registry.clear()
        self._next_source_id = 1
        logger.info("Chroma collection cleared and reset.")
