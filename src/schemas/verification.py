from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field

class VerificationItem(BaseModel):
    """Validation status for an individual claim made in the drafted report."""
    claim_text: str = Field(description="Sentence or claim asserting a factual statement")
    citation_index: int = Field(description="Citation index referenced, e.g. 1 for [1]")
    cited_source: str = Field(description="Name/URL of the cited source")
    evidence_snippet: str = Field(default="", description="Relevant evidence snippet found in vector store")
    evidence_excerpt: Optional[str] = Field(default=None, description="Alias for evidence snippet")
    status: str = Field(
        default="Verified",
        description="Status: 'Verified', 'Partially Supported', 'Unsupported', 'Contradicted'"
    )
    confidence_score: float = Field(
        default=0.9,
        ge=0.0,
        le=1.0,
        description="Confidence score (0.0 to 1.0) on claim factual support"
    )
    flag_warning: Optional[str] = Field(
        default=None,
        description="Warning explanation if claim is unsupported or extrapolated beyond evidence"
    )

    def model_post_init(self, __context: Any) -> None:
        if not self.evidence_snippet and self.evidence_excerpt:
            self.evidence_snippet = self.evidence_excerpt
        elif not self.evidence_excerpt and self.evidence_snippet:
            self.evidence_excerpt = self.evidence_snippet

class CitationAuditReport(BaseModel):
    """Full citation audit and factual fidelity evaluation."""
    total_claims_checked: int = Field(default=0)
    verified_count: int = Field(default=0)
    flagged_count: int = Field(default=0)
    fidelity_score: float = Field(default=100.0, description="Percentage of supported citations (0-100%)")
    items: List[VerificationItem] = Field(default_factory=list)
    verdict: str = Field(
        default="High Support",
        description="'High Support (Ready)', 'Moderate Support (Caution)', 'Low Support (Needs Review)'"
    )
    audit_summary: str = Field(default="", description="Summary of citation verification audit")

class FinalResearchReport(BaseModel):
    """The final synthesized research report ready for human review and export."""
    title: str = Field(description="Descriptive title of research report")
    topic: str = Field(description="Original research topic")
    executive_summary: str = Field(description="High-level executive summary")
    sections: Dict[str, str] = Field(default_factory=dict, description="Section Title -> Section Markdown Content")
    conflicts_analysis: str = Field(default="", description="Summary of conflicting viewpoints or data discrepancies")
    key_findings: List[str] = Field(default_factory=list, description="Bullet points of verified key takeaways")
    citations: List[Dict[str, Any]] = Field(default_factory=list, description="Ordered list of cited sources with metadata")
    full_markdown: str = Field(default="", description="Complete assembled markdown report")
    approved_by_user: bool = Field(default=False, description="Whether user explicitly approved report for export")
    approval_timestamp: Optional[str] = Field(default=None, description="ISO timestamp when human approved")
