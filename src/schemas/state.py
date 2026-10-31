from typing import TypedDict, List, Dict, Optional, Any
from .source import SearchResultItem, EvidenceChunk
from .plan import ResearchPlan
from .conflict import ConflictReport
from .verification import CitationAuditReport, FinalResearchReport

class ResearchState(TypedDict, total=False):
    """LangGraph State passed across all nodes in the ResearchPilot agent workflow."""
    topic: str
    user_guidance: Optional[str]
    plan: Optional[ResearchPlan]
    search_results: List[SearchResultItem]
    uploaded_files_data: List[Dict[str, Any]]
    vector_indexed_count: int
    retrieved_evidence: List[EvidenceChunk]
    conflict_report: Optional[ConflictReport]
    draft_report: Optional[FinalResearchReport]
    citation_audit: Optional[CitationAuditReport]
    human_approved: bool
    human_feedback: Optional[str]
    logs: List[str]
    current_step: str
    error: Optional[str]
