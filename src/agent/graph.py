import datetime
import logging
from typing import Dict, Any, Optional, Callable
from langgraph.graph import StateGraph, START, END

from src.schemas.state import ResearchState
from src.agent.planner import plan_research
from src.agent.searcher import execute_search_and_retrieval
from src.agent.indexer import index_and_retrieve_evidence
from src.agent.conflict_checker import detect_conflicting_claims
from src.agent.draftsman import draft_research_report
from src.agent.verifier import verify_citations_and_claims
from src.tools.vector_store import ChromaResearchStore
from src.config import settings

logger = logging.getLogger(__name__)

class ResearchPilotAgent:
    """Orchestrates the multi-agent research workflow using LangGraph."""

    def __init__(
        self,
        gemini_api_key: Optional[str] = None,
        tavily_api_key: Optional[str] = None,
        model_name: Optional[str] = None,
        step_callback: Optional[Callable[[str, str], None]] = None,
    ):
        self.gemini_api_key = gemini_api_key or settings.GEMINI_API_KEY
        self.tavily_api_key = tavily_api_key or settings.TAVILY_API_KEY
        self.model_name = model_name or settings.DEFAULT_MODEL
        self.step_callback = step_callback
        self.vector_store = ChromaResearchStore(gemini_api_key=self.gemini_api_key)
        self.graph = self._build_graph()

    def _notify(self, step_name: str, message: str):
        if self.step_callback:
            try:
                self.step_callback(step_name, message)
            except Exception as e:
                logger.debug(f"Callback error: {e}")

    # ================= NODES =================

    def planner_node(self, state: ResearchState) -> Dict[str, Any]:
        """Node 1: Plan research dimensions and search queries."""
        topic = state.get("topic", "")
        guidance = state.get("user_guidance")
        self._notify("planner", f"Formulating multi-angle research strategy for '{topic}'...")

        plan = plan_research(
            topic=topic,
            user_guidance=guidance,
            api_key=self.gemini_api_key,
            model_name=self.model_name,
        )

        logs = state.get("logs", [])
        logs.append(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Planner created {len(plan.sub_queries)} targeted search queries.")

        return {
            "plan": plan,
            "logs": logs,
            "current_step": "planner",
        }

    def searcher_node(self, state: ResearchState) -> Dict[str, Any]:
        """Node 2: Execute web search and document retrieval tools."""
        plan = state.get("plan")
        uploaded_files = state.get("uploaded_files_data", [])
        self._notify("searcher", f"Executing web search and document extraction across {len(plan.sub_queries)} queries...")

        search_results = execute_search_and_retrieval(
            plan=plan,
            uploaded_files_data=uploaded_files,
            tavily_api_key=self.tavily_api_key,
            max_results_per_query=4,
        )

        logs = state.get("logs", [])
        logs.append(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Retrieved {len(search_results)} primary sources and document passages.")

        return {
            "search_results": search_results,
            "logs": logs,
            "current_step": "searcher",
        }

    def indexer_node(self, state: ResearchState) -> Dict[str, Any]:
        """Node 3: Index sources into ChromaDB and extract semantic evidence."""
        plan = state.get("plan")
        raw_results = state.get("search_results", [])
        self._notify("indexer", f"Indexing {len(raw_results)} sources into ChromaDB vector database...")

        # Reset store for clean session
        self.vector_store.clear()
        indexed_count, evidence_chunks = index_and_retrieve_evidence(
            plan=plan,
            raw_results=raw_results,
            vector_store=self.vector_store,
            top_k_per_query=4,
        )

        logs = state.get("logs", [])
        logs.append(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Indexed {indexed_count} items into ChromaDB. Extracted {len(evidence_chunks)} evidence chunks.")

        return {
            "vector_indexed_count": indexed_count,
            "retrieved_evidence": evidence_chunks,
            "logs": logs,
            "current_step": "indexer",
        }

    def conflict_node(self, state: ResearchState) -> Dict[str, Any]:
        """Node 4: Detect conflicting claims and divergent data."""
        topic = state.get("topic", "")
        evidence = state.get("retrieved_evidence", [])
        self._notify("conflict_checker", f"Cross-analyzing {len(evidence)} evidence chunks for conflicting claims...")

        conflict_report = detect_conflicting_claims(
            topic=topic,
            evidence_chunks=evidence,
            api_key=self.gemini_api_key,
            model_name=self.model_name,
        )

        logs = state.get("logs", [])
        logs.append(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Conflict checker evaluated evidence: {len(conflict_report.conflicts)} conflicting claims documented.")

        return {
            "conflict_report": conflict_report,
            "logs": logs,
            "current_step": "conflict_checker",
        }

    def draftsman_node(self, state: ResearchState) -> Dict[str, Any]:
        """Node 5: Synthesize findings into fully cited research report."""
        topic = state.get("topic", "")
        plan = state.get("plan")
        evidence = state.get("retrieved_evidence", [])
        conflict_rep = state.get("conflict_report")
        self._notify("draftsman", f"Synthesizing findings into cited research report...")

        draft_report = draft_research_report(
            topic=topic,
            plan=plan,
            evidence_chunks=evidence,
            conflict_report=conflict_rep,
            api_key=self.gemini_api_key,
            model_name=self.model_name,
        )

        logs = state.get("logs", [])
        logs.append(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Drafted comprehensive report with {len(draft_report.citations)} cited sources.")

        return {
            "draft_report": draft_report,
            "logs": logs,
            "current_step": "draftsman",
        }

    def verifier_node(self, state: ResearchState) -> Dict[str, Any]:
        """Node 6: Verify citations and audit factual fidelity."""
        draft_report = state.get("draft_report")
        evidence = state.get("retrieved_evidence", [])
        self._notify("verifier", f"Auditing citations against ChromaDB vector store...")

        audit_report = verify_citations_and_claims(
            report=draft_report,
            evidence_chunks=evidence,
            api_key=self.gemini_api_key,
            model_name=self.model_name,
        )

        logs = state.get("logs", [])
        logs.append(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Citation Audit Complete: {audit_report.fidelity_score}% fidelity score. {audit_report.flagged_count} warnings flagged.")

        return {
            "citation_audit": audit_report,
            "logs": logs,
            "current_step": "verifier",
        }

    # ================= GRAPH BUILDER =================

    def _build_graph(self):
        """Construct the LangGraph StateGraph."""
        builder = StateGraph(ResearchState)

        builder.add_node("planner", self.planner_node)
        builder.add_node("searcher", self.searcher_node)
        builder.add_node("indexer", self.indexer_node)
        builder.add_node("conflict_checker", self.conflict_node)
        builder.add_node("draftsman", self.draftsman_node)
        builder.add_node("verifier", self.verifier_node)

        builder.add_edge(START, "planner")
        builder.add_edge("planner", "searcher")
        builder.add_edge("searcher", "indexer")
        builder.add_edge("indexer", "conflict_checker")
        builder.add_edge("conflict_checker", "draftsman")
        builder.add_edge("draftsman", "verifier")
        builder.add_edge("verifier", END)

        return builder.compile()

    def run(
        self,
        topic: str,
        user_guidance: Optional[str] = None,
        uploaded_files_data: Optional[list] = None,
    ) -> ResearchState:
        """Run the full agent research pipeline synchronously."""
        initial_state: ResearchState = {
            "topic": topic,
            "user_guidance": user_guidance,
            "uploaded_files_data": uploaded_files_data or [],
            "logs": [f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Initialized ResearchPilot agent session."],
            "human_approved": False,
            "current_step": "init",
        }

        final_state = self.graph.invoke(initial_state)
        return final_state
