import streamlit as st
from typing import List, Dict, Any, Optional
from src.schemas.conflict import ConflictReport, ConflictingClaim
from src.schemas.verification import CitationAuditReport, VerificationItem
from src.schemas.source import EvidenceChunk

def render_header():
    """Render the executive top banner."""
    st.markdown(
        """
        <div class="pilot-header">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h1>ResearchPilot</h1>
                    <p>Agentic Research Assistant &bull; LangGraph &bull; Gemini &bull; ChromaDB &bull; Tavily</p>
                </div>
                <div style="background: rgba(255,255,255,0.1); padding: 8px 16px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.2); text-align: right;">
                    <div style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1px; color: #93c5fd;">System State</div>
                    <div style="font-weight: 600; color: #ffffff;">Autonomous Agent Active</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def render_stepper(current_step: str):
    """Render horizontal visual stepper showing LangGraph state progression."""
    steps = [
        ("planner", "1. Planner"),
        ("searcher", "2. Search Tools"),
        ("indexer", "3. Vector ChromaDB"),
        ("conflict_checker", "4. Conflict Analysis"),
        ("draftsman", "5. Report Drafting"),
        ("verifier", "6. Citation Audit"),
        ("approved", "7. Human Approval"),
    ]

    html = "<div style='margin-bottom: 20px; display: flex; flex-wrap: wrap; gap: 8px;'>"
    for step_id, label in steps:
        active = (step_id == current_step)
        css_class = "step-pill step-pill-active" if active else "step-pill"
        icon = "🔵" if active else "⚪"
        html += f"<span class='{css_class}'>{icon} {label}</span>"
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)

def render_audit_scorecard(audit: CitationAuditReport):
    """Render high-level fidelity score and metric boxes."""
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(
            f"""
            <div class="scorecard-box">
                <div class="scorecard-val">{audit.fidelity_score}%</div>
                <div class="scorecard-label">Citation Fidelity</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c2:
        st.markdown(
            f"""
            <div class="scorecard-box">
                <div class="scorecard-val" style="color: #16a34a;">{audit.verified_count}</div>
                <div class="scorecard-label">Verified Citations</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c3:
        color = "#dc2626" if audit.flagged_count > 0 else "#64748b"
        st.markdown(
            f"""
            <div class="scorecard-box">
                <div class="scorecard-val" style="color: {color};">{audit.flagged_count}</div>
                <div class="scorecard-label">Flagged / Unsupported</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c4:
        st.markdown(
            f"""
            <div class="scorecard-box">
                <div class="scorecard-val" style="font-size: 1.25rem; padding-top: 10px; color: #1e3a8a;">{audit.verdict}</div>
                <div class="scorecard-label">Credibility Verdict</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

def render_conflicts_view(conflicts_report: Optional[ConflictReport]):
    """Render side-by-side comparison cards for conflicting claims."""
    if not conflicts_report or not conflicts_report.conflicts:
        st.success("No critical contradictory claims detected across retrieved sources.")
        return

    st.markdown(f"**Identified {len(conflicts_report.conflicts)} Divergent Claims across Sources:**")
    st.caption(conflicts_report.executive_takeaway)

    for cf in conflicts_report.conflicts:
        badge_class = "badge-high" if cf.severity == "High" else "badge-medium"
        st.markdown(
            f"""
            <div class="conflict-card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <strong style="color: #0f172a; font-size: 1.05rem;">{cf.topic_aspect}</strong>
                    <div>
                        <span class="badge {badge_class}">{cf.severity} Severity</span>
                        <span class="badge" style="background:#f1f5f9; color:#475569; margin-left:6px;">{cf.category}</span>
                    </div>
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin: 12px 0;">
                    <div style="background: #f8fafc; padding: 12px; border-radius: 6px; border: 1px solid #e2e8f0;">
                        <div style="font-size: 0.75rem; font-weight: 600; color: #2563eb; text-transform: uppercase;">Source A ({cf.source_a})</div>
                        <div style="font-size: 0.9rem; color: #1e293b; margin-top: 4px;">"{cf.claim_a}"</div>
                    </div>
                    <div style="background: #f8fafc; padding: 12px; border-radius: 6px; border: 1px solid #e2e8f0;">
                        <div style="font-size: 0.75rem; font-weight: 600; color: #dc2626; text-transform: uppercase;">Source B ({cf.source_b})</div>
                        <div style="font-size: 0.9rem; color: #1e293b; margin-top: 4px;">"{cf.claim_b}"</div>
                    </div>
                </div>
                <div style="font-size: 0.88rem; color: #475569; background: #fff7ed; padding: 10px; border-radius: 6px; border: 1px solid #ffedd5;">
                    <strong>Agent Resolution & Analysis:</strong> {cf.analysis}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

def render_citations_audit_view(audit: CitationAuditReport):
    """Render interactive claim-by-claim verification matrix."""
    for idx, item in enumerate(audit.items):
        if item.status == "Verified":
            badge_html = "<span class='badge badge-verified'>Verified</span>"
        elif item.status == "Partially Supported":
            badge_html = "<span class='badge badge-partial'>Partially Supported</span>"
        else:
            badge_html = "<span class='badge badge-unsupported'>Unsupported Flag</span>"

        with st.expander(f"[{item.citation_index}] {item.claim_text[:80]}...  ({item.status})", expanded=(item.status != "Verified")):
            st.markdown(f"**Full Claim:** {item.claim_text}")
            st.markdown(f"**Cited Source:** [{item.citation_index}] {item.cited_source}")
            st.markdown(f"**Confidence Score:** `{int(item.confidence_score * 100)}%` | {badge_html}", unsafe_allow_html=True)
            st.markdown(f"**Evidence Snippet in ChromaDB:**")
            st.info(item.evidence_excerpt)

            if item.flag_warning:
                st.warning(f"⚠️ **Audit Warning:** {item.flag_warning}")
