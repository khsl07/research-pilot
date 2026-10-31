import datetime
import streamlit as st
from src.config import settings
from src.agent.graph import ResearchPilotAgent
from src.schemas.state import ResearchState
from src.export.markdown_export import generate_markdown_bundle, generate_html_report
from src.export.pdf_export import generate_pdf_bytes
from src.ui.styles import CUSTOM_CSS
from src.ui.components import (
    render_header,
    render_stepper,
    render_audit_scorecard,
    render_conflicts_view,
    render_citations_audit_view,
)

# Set Streamlit Page Configuration
st.set_page_config(
    page_title="ResearchPilot — Agentic Research Assistant",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inject custom styling
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Initialize Session State
if "state" not in st.session_state:
    st.session_state.state = None
if "current_step" not in st.session_state:
    st.session_state.current_step = "init"
if "logs" not in st.session_state:
    st.session_state.logs = []
if "uploaded_files_data" not in st.session_state:
    st.session_state.uploaded_files_data = []

# ================= SIDEBAR =================
with st.sidebar:
    st.markdown("### ⚙️ Engine Configuration")

    gemini_key = st.text_input(
        "Gemini API Key",
        value=settings.GEMINI_API_KEY or "",
        type="password",
        help="Google Gemini API key for planner, synthesis, and verification.",
    )

    tavily_key = st.text_input(
        "Tavily Search API Key",
        value=settings.TAVILY_API_KEY or "",
        type="password",
        help="Tavily API key for web search. If omitted, DuckDuckGo & curated fallback will be used.",
    )

    model_choice = st.selectbox(
        "Research Model",
        options=["gemini-2.5-flash", "gemini-1.5-flash", "gemini-1.5-pro"],
        index=0,
    )

    st.markdown("---")
    st.markdown("### 📁 Primary Documents (RAG)")
    st.caption("Upload supplementary research papers or internal briefings (PDF, TXT, MD).")

    uploaded_files = st.file_uploader(
        "Upload research files",
        type=["pdf", "txt", "md"],
        accept_multiple_files=True,
    )

    if uploaded_files:
        files_data = []
        for uf in uploaded_files:
            files_data.append({"name": uf.name, "bytes": uf.getvalue()})
        st.session_state.uploaded_files_data = files_data
        st.success(f"Attached {len(files_data)} documents.")
    else:
        st.session_state.uploaded_files_data = []

    st.markdown("---")
    st.markdown("### 💡 Preset Sample Topics")
    sample_topic = st.selectbox(
        "Quick Load Topic",
        options=[
            "Custom Topic (Enter below)",
            "Commercial Viability of Solid-State Batteries in EVs by 2030",
            "Quantum Error Correction: Surface Codes vs LDPC Codes",
            "Autonomous AI Diagnostic Agents: Clinical Safety and Liability",
        ],
    )

    st.markdown("---")
    if st.button("🗑️ Reset All Agent State"):
        st.session_state.state = None
        st.session_state.current_step = "init"
        st.session_state.logs = []
        st.rerun()

# ================= MAIN PAGE =================
render_header()

# Topic Input Section
default_topic = "" if sample_topic.startswith("Custom") else sample_topic

col_top, col_guid = st.columns([3, 2])
with col_top:
    topic_input = st.text_input(
        "Enter Research Topic or Scientific Hypothesis",
        value=default_topic,
        placeholder="e.g. Impact of Solid-State Batteries on Commercial EV Adoption by 2030",
    )
with col_guid:
    guidance_input = st.text_input(
        "Optional Analyst Focus Guidance",
        placeholder="e.g. Emphasize manufacturing bottlenecks and cost parity with NMC",
    )

c_btn1, c_btn2, _ = st.columns([2, 2, 4])
with c_btn1:
    start_research = st.button("🚀 Run Autonomous Research Agent", type="primary", use_container_width=True)
with c_btn2:
    load_demo = st.button("🧪 Load Instant Demo State", use_container_width=True)

# Handler: Run Agent Workflow
if start_research:
    if not topic_input.strip():
        st.error("Please provide a research topic before starting.")
    else:
        status_box = st.status("🔬 ResearchPilot Agent Workflow Running...", expanded=True)

        def step_update(step_name: str, message: str):
            st.session_state.current_step = step_name
            status_box.write(f"**[{step_name.upper()}]** {message}")

        agent = ResearchPilotAgent(
            gemini_api_key=gemini_key,
            tavily_api_key=tavily_key,
            model_name=model_choice,
            step_callback=step_update,
        )

        with st.spinner("Agent orchestrating research, querying sources, and verifying citations..."):
            final_state = agent.run(
                topic=topic_input.strip(),
                user_guidance=guidance_input.strip() if guidance_input else None,
                uploaded_files_data=st.session_state.uploaded_files_data,
            )
            st.session_state.state = final_state
            st.session_state.current_step = "verifier"
            status_box.update(label="✅ Agentic Research Complete! Ready for Human Review.", state="complete")
            st.rerun()

# Handler: Load Demo State
if load_demo:
    demo_topic = "Commercial Viability of Solid-State Batteries in EVs by 2030"
    agent = ResearchPilotAgent(
        gemini_api_key="",  # Uses high quality deterministic engine
        tavily_api_key="",
    )
    with st.spinner("Generating demo agentic state..."):
        demo_state = agent.run(topic=demo_topic)
        st.session_state.state = demo_state
        st.session_state.current_step = "verifier"
        st.rerun()

# ================= RENDER TABS IF STATE EXISTS =================
state: Optional[ResearchState] = st.session_state.state

if state:
    current_step = st.session_state.get("current_step", "verifier")
    render_stepper(current_step)

    plan = state.get("plan")
    search_results = state.get("search_results", [])
    evidence = state.get("retrieved_evidence", [])
    conflict_rep = state.get("conflict_report")
    draft_rep = state.get("draft_report")
    audit_rep = state.get("citation_audit")
    logs = state.get("logs", [])

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🔬 Executive Overview",
        "🗺️ Research Plan",
        "📚 ChromaDB Knowledge Base",
        "⚖️ Conflicting Claims Matrix",
        "🛡️ Citation Verification Audit",
        "✍️ Human Approval & Export",
    ])

    # Tab 1: Executive Overview
    with tab1:
        st.markdown(f"### 🎯 Research Investigation: {state.get('topic')}")
        if plan:
            st.markdown(f"**Core Objective:** {plan.core_objective}")
            st.markdown(f"**Dimensions Evaluated:** {', '.join(plan.key_dimensions)}")

        c_stat1, c_stat2, c_stat3, c_stat4 = st.columns(4)
        c_stat1.metric("Sources Retrieved", len(search_results))
        c_stat2.metric("ChromaDB Chunks", state.get("vector_indexed_count", len(evidence)))
        c_stat3.metric("Conflicting Claims", len(conflict_rep.conflicts) if conflict_rep else 0)
        c_stat4.metric("Citation Fidelity", f"{audit_rep.fidelity_score}%" if audit_rep else "N/A")

        st.markdown("---")
        st.markdown("#### 📜 Live Agent Execution Trace")
        st.code("\n".join(logs), language="plaintext")

    # Tab 2: Research Plan
    with tab2:
        st.markdown("### 🗺️ Multi-Step Research Plan")
        if plan:
            st.markdown(f"**Core Hypothesis / Objective:** {plan.core_objective}")
            st.markdown("#### Targeted Query Strategies:")
            for idx, q in enumerate(plan.sub_queries):
                with st.container():
                    st.markdown(f"**Query {idx+1}:** `{q.search_query}`")
                    st.caption(f"**Analytical Angle:** {q.angle} | **Rationale:** {q.rationale}")
                    st.divider()

            st.markdown("#### Target Report Structure:")
            for sec in plan.planned_report_sections:
                st.markdown(f"- 📄 {sec}")

    # Tab 3: ChromaDB Knowledge Base
    with tab3:
        st.markdown("### 📚 ChromaDB Vector Knowledge Store")
        st.caption(f"Indexed evidence chunks stored with vector embeddings and assigned citation IDs [1], [2], ...")

        # Interactive Vector Search Tester
        search_test = st.text_input("Test semantic vector search query on ChromaDB:", placeholder="e.g. volumetric density degradation")
        if search_test:
            agent_temp = ResearchPilotAgent(gemini_api_key=gemini_key)
            test_results = agent_temp.vector_store.query(search_test, n_results=3)
            st.markdown(f"**Top {len(test_results)} Vector Matches:**")
            for tr in test_results:
                st.markdown(f"- **Source [{tr.source_id}] {tr.title}** (Sim: `{tr.similarity_score:.2f}`): {tr.text[:180]}...")

        st.markdown("---")
        st.markdown(f"**All Indexed Evidence Chunks ({len(evidence)}):**")
        for chunk in evidence:
            with st.expander(f"Source [{chunk.source_id}] {chunk.title} ({chunk.source_type.title()})"):
                st.markdown(f"**URL / Path:** `{chunk.url}`")
                st.markdown(f"**Topic Tag:** `{chunk.topic_tag}`")
                st.markdown(f"**Similarity Score:** `{chunk.similarity_score:.3f}`")
                st.text_area("Chunk Content", chunk.text, height=100, key=f"chunk_{chunk.chunk_id}")

    # Tab 4: Conflicting Claims Matrix
    with tab4:
        st.markdown("### ⚖️ Conflicting Claims & Contradiction Analysis")
        st.caption("Agentic cross-examination comparing contradictory numbers, timelines, and conclusions across primary sources.")
        render_conflicts_view(conflict_rep)

    # Tab 5: Citation Verification Audit
    with tab5:
        st.markdown("### 🛡️ Citation Verification & Fact-Checking Audit")
        st.caption("Evaluates every cited assertion in the report against ChromaDB evidence chunks to flag unsupported claims.")
        if audit_rep:
            render_audit_scorecard(audit_rep)
            st.markdown("---")
            render_citations_audit_view(audit_rep)
        else:
            st.info("No audit report generated yet.")

    # Tab 6: Human-in-the-Loop Approval & Export
    with tab6:
        st.markdown("### ✍️ Human-in-the-Loop Report Review & Approval")
        st.caption("Review the generated report and verification scorecard. User approval is required before final export or distribution.")

        approval_status = draft_rep.approved_by_user if draft_rep else False

        # Approval Banner
        if approval_status:
            st.success(f"✅ Report Approved by Human Reviewer at {draft_rep.approval_timestamp}. Ready for Export.")
        else:
            st.warning("⚠️ Report is in DRAFT state. Review flagged claims and click 'Approve Report' to authorize export.")

        # Report Editor & Preview
        st.markdown("#### Research Report Preview & Direct Editor")
        current_md = draft_rep.full_markdown if draft_rep else ""

        edited_md = st.text_area(
            "Report Markdown (Edit directly to refine draft before sign-off)",
            value=current_md,
            height=350,
        )

        # Human Approval Action Bar
        col_app1, col_app2, _ = st.columns([2, 2, 4])
        with col_app1:
            if st.button("✅ Approve Report for Export", type="primary", use_container_width=True):
                draft_rep.full_markdown = edited_md
                draft_rep.approved_by_user = True
                draft_rep.approval_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                st.session_state.current_step = "approved"
                st.toast("Report approved successfully!")
                st.rerun()

        with col_app2:
            if st.button("🔄 Request Revision / Reset Approval", use_container_width=True):
                draft_rep.approved_by_user = False
                draft_rep.approval_timestamp = None
                st.session_state.current_step = "verifier"
                st.rerun()

        st.markdown("---")
        st.markdown("#### 📥 Export Final Research Package")

        if draft_rep:
            # Prepare export formats
            final_bundle_md = generate_markdown_bundle(draft_rep, conflict_rep, audit_rep)
            html_bundle = generate_html_report(final_bundle_md, draft_rep.title)
            pdf_bytes = generate_pdf_bytes(draft_rep, conflict_rep, audit_rep)

            c_exp1, c_exp2, c_exp3 = st.columns(3)
            with c_exp1:
                st.download_button(
                    label="📄 Download Styled PDF Report",
                    data=pdf_bytes,
                    file_name=f"ResearchPilot_{datetime.datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                    disabled=not approval_status,
                    help="Requires Human Approval before export." if not approval_status else None,
                )
            with c_exp2:
                st.download_button(
                    label="📝 Download Markdown (.md)",
                    data=final_bundle_md,
                    file_name=f"ResearchPilot_{datetime.datetime.now().strftime('%Y%m%d')}.md",
                    mime="text/markdown",
                    use_container_width=True,
                    disabled=not approval_status,
                )
            with c_exp3:
                st.download_button(
                    label="🌐 Download HTML Report (.html)",
                    data=html_bundle,
                    file_name=f"ResearchPilot_{datetime.datetime.now().strftime('%Y%m%d')}.html",
                    mime="text/html",
                    use_container_width=True,
                    disabled=not approval_status,
                )

            if not approval_status:
                st.caption("🔒 *Export buttons are locked until the report is explicitly approved.*")
else:
    st.info("👆 Enter a research topic and click **'Run Autonomous Research Agent'** or test instantly with **'Load Instant Demo State'**.")
