from typing import List, Optional
from pydantic import BaseModel, Field

class ConflictingClaim(BaseModel):
    """Represents contradictory or divergent evidence across gathered sources."""
    topic_aspect: str = Field(description="Subtopic aspect where conflict exists (e.g., 'Commercialization Year', 'Cost Per kWh')")
    claim_a: str = Field(description="First claim or metric reported")
    source_a: str = Field(description="Citation / Title / URL of first source")
    claim_b: str = Field(description="Conflicting claim or metric reported")
    source_b: str = Field(description="Citation / Title / URL of second source")
    category: str = Field(
        default="Divergent Estimates",
        description="Category: 'Direct Contradiction', 'Timeline Divergence', 'Cost/Metric Discrepancy', 'Methodological Difference'"
    )
    severity: str = Field(
        default="Medium",
        description="Severity: 'High', 'Medium', or 'Nuance'"
    )
    analysis: str = Field(description="Explanation of why this disagreement exists and how to reconcile it objectively")

class ConflictReport(BaseModel):
    """Aggregate conflict analysis across all retrieved evidence."""
    conflicts_detected: bool = Field(default=False, description="Whether any conflicting claims were identified")
    conflicts: List[ConflictingClaim] = Field(default_factory=list, description="List of detected conflicting claims")
    consensus_points: List[str] = Field(default_factory=list, description="Major areas where all sources strongly agree")
    executive_takeaway: str = Field(default="", description="High-level takeaway on evidence alignment")
