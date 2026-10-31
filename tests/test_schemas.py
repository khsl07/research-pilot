import unittest
from src.schemas.plan import ResearchPlan, SubTopicQuery
from src.schemas.conflict import ConflictingClaim, ConflictReport
from src.schemas.verification import VerificationItem, CitationAuditReport, FinalResearchReport
from src.schemas.source import SearchResultItem, EvidenceChunk

class TestSchemas(unittest.TestCase):
    def test_research_plan(self):
        plan = ResearchPlan(
            topic="Solid-State Batteries",
            core_objective="Evaluate commercial adoption timeline by 2030",
            key_dimensions=["Maturity", "Cost"],
            sub_queries=[
                SubTopicQuery(
                    angle="Cost",
                    search_query="solid-state battery cost per kwh",
                    rationale="Check price parity with NMC",
                )
            ],
            planned_report_sections=["Executive Summary", "Economics"],
        )
        self.assertEqual(len(plan.sub_queries), 1)
        self.assertEqual(plan.sub_queries[0].angle, "Cost")

    def test_conflicting_claim(self):
        claim = ConflictingClaim(
            topic_aspect="Launch Year",
            claim_a="Launch in 2026",
            source_a="OEM Press Release",
            claim_b="Mass adoption delayed to 2031",
            source_b="Analyst Report",
            category="Timeline Divergence",
            severity="High",
            analysis="OEM refers to halo low-volume line; analyst refers to mass market.",
        )
        report = ConflictReport(
            conflicts_detected=True,
            conflicts=[claim],
            consensus_points=["Electrolyte stability is improving"],
            executive_takeaway="Timeline is bifurcated between premium and mass market.",
        )
        self.assertTrue(report.conflicts_detected)
        self.assertEqual(len(report.conflicts), 1)

    def test_verification_item(self):
        v = VerificationItem(
            claim_text="Cells achieved 1000 Wh/L volumetric energy density.",
            citation_index=1,
            cited_source="QuantumScape Specs",
            evidence_snippet="achieved 1,000 Wh/L volumetric energy density",
            status="Verified",
            confidence_score=0.95,
        )
        audit = CitationAuditReport(
            total_claims_checked=1,
            verified_count=1,
            flagged_count=0,
            fidelity_score=100.0,
            items=[v],
            verdict="High Support",
        )
        self.assertEqual(audit.fidelity_score, 100.0)
        self.assertEqual(audit.verified_count, 1)

if __name__ == "__main__":
    unittest.main()
