import logging
from typing import List, Dict, Any, Optional
from src.schemas.plan import ResearchPlan
from src.schemas.source import SearchResultItem
from src.tools.web_search import WebSearchTool
from src.tools.doc_loader import DocumentLoader

logger = logging.getLogger(__name__)

def execute_search_and_retrieval(
    plan: ResearchPlan,
    uploaded_files_data: Optional[List[Dict[str, Any]]] = None,
    tavily_api_key: Optional[str] = None,
    max_results_per_query: int = 4,
) -> List[SearchResultItem]:
    """Execute all planned search queries and ingest uploaded documents."""
    search_tool = WebSearchTool(tavily_api_key=tavily_api_key)
    doc_loader = DocumentLoader()

    all_results: List[SearchResultItem] = []
    seen_urls = set()

    # 1. Ingest uploaded files first if present
    if uploaded_files_data:
        for file_info in uploaded_files_data:
            name = file_info.get("name", "uploaded_doc")
            data = file_info.get("bytes", b"")
            if data:
                doc_chunks = doc_loader.process_file(name, data)
                all_results.extend(doc_chunks)

    # 2. Execute Web Searches for each planned sub-query
    for sq in plan.sub_queries:
        query = sq.search_query
        logger.info(f"Executing search query: {query}")
        results = search_tool.search(query, max_results=max_results_per_query)

        for res in results:
            if res.url not in seen_urls:
                seen_urls.add(res.url)
                all_results.append(res)

    logger.info(f"Total search and document items retrieved: {len(all_results)}")
    return all_results
