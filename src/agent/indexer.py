import logging
from typing import List, Tuple, Optional
from src.schemas.plan import ResearchPlan
from src.schemas.source import SearchResultItem, EvidenceChunk
from src.tools.vector_store import ChromaResearchStore

logger = logging.getLogger(__name__)

def index_and_retrieve_evidence(
    plan: ResearchPlan,
    raw_results: List[SearchResultItem],
    vector_store: ChromaResearchStore,
    top_k_per_query: int = 4,
) -> Tuple[int, List[EvidenceChunk]]:
    """Index gathered search results into ChromaDB and retrieve evidence chunks for research angles."""
    # 1. Upsert into ChromaDB
    indexed_count = vector_store.add_search_results(raw_results)
    logger.info(f"Indexed {indexed_count} items into ChromaDB.")

    # 2. Query vector store across all planned angles to extract structured evidence chunks
    retrieved_evidence: List[EvidenceChunk] = []
    seen_chunk_ids = set()

    # Query for the overall objective first
    main_chunks = vector_store.query(plan.core_objective, n_results=top_k_per_query)
    for c in main_chunks:
        if c.chunk_id not in seen_chunk_ids:
            seen_chunk_ids.add(c.chunk_id)
            c.topic_tag = "core_objective"
            retrieved_evidence.append(c)

    # Query for each subtopic query
    for sq in plan.sub_queries:
        sub_chunks = vector_store.query(sq.search_query, n_results=top_k_per_query)
        for c in sub_chunks:
            if c.chunk_id not in seen_chunk_ids:
                seen_chunk_ids.add(c.chunk_id)
                c.topic_tag = sq.angle
                retrieved_evidence.append(c)

    logger.info(f"Extracted {len(retrieved_evidence)} distinct evidence chunks from vector database.")
    return indexed_count, retrieved_evidence
