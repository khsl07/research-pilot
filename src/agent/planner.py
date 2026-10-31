import logging
from typing import Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from src.schemas.plan import ResearchPlan, SubTopicQuery
from src.config import settings

logger = logging.getLogger(__name__)

PLANNER_SYSTEM_PROMPT = """You are the Principal Lead Research Planner for ResearchPilot, an enterprise-grade agentic research system.
Your job is to formulate a rigorous, multi-angle research plan for any complex technical, scientific, or market topic.

Given the topic and any optional user focus instructions:
1. Formulate a precise, scientific core objective.
2. Identify 3 to 5 distinct analytical dimensions (e.g. Technological Architecture, Real-world Benchmarks, Cost & Commercial Parity, Regulatory/Safety Constraints, Competing Paradigms).
3. Generate 3 to 5 specific, high-yield web search queries tailored to retrieve hard empirical data, dates, metrics, and industry reports.
4. Define proposed section headings for the comprehensive final report.

Be direct, objective, and deeply analytical."""

def plan_research(topic: str, user_guidance: Optional[str] = None, api_key: Optional[str] = None, model_name: Optional[str] = None) -> ResearchPlan:
    """Generate structured research plan using Gemini LLM."""
    api_key = api_key or settings.GEMINI_API_KEY
    model = model_name or settings.DEFAULT_MODEL

    if api_key and api_key.strip():
        try:
            llm = ChatGoogleGenerativeAI(
                model=model,
                google_api_key=api_key.strip(),
                temperature=0.2,
            )
            structured_llm = llm.with_structured_output(ResearchPlan)

            user_prompt = f"Research Topic: {topic}\n"
            if user_guidance:
                user_prompt += f"User Focus Guidance: {user_guidance}\n"

            messages = [
                SystemMessage(content=PLANNER_SYSTEM_PROMPT),
                HumanMessage(content=user_prompt),
            ]

            plan: ResearchPlan = structured_llm.invoke(messages)
            logger.info(f"Generated research plan with {len(plan.sub_queries)} queries.")
            return plan
        except Exception as e:
            logger.warning(f"Gemini structured plan generation failed: {e}. Using deterministic plan builder.")

    # High-quality deterministic fallback plan
    return _build_fallback_plan(topic, user_guidance)

def _build_fallback_plan(topic: str, user_guidance: Optional[str] = None) -> ResearchPlan:
    """Fallback planner for testing and demonstration without active API keys."""
    queries = [
        SubTopicQuery(
            angle="Technological Architecture & Mechanism",
            search_query=f"{topic} core technology breakthroughs architecture specifications",
            rationale="Establish technical baseline and recent advancements.",
        ),
        SubTopicQuery(
            angle="Commercialization Timelines & Industry Parity",
            search_query=f"{topic} commercialization timeline cost parity roadmap 2026 2030",
            rationale="Uncover concrete production schedules, cost barriers, and market viability.",
        ),
        SubTopicQuery(
            angle="Critical Trade-offs & Failure Modes",
            search_query=f"{topic} bottlenecks degradation challenges risks limitations",
            rationale="Identify unresolved engineering, economic, and safety hurdles.",
        ),
        SubTopicQuery(
            angle="Competitive Landscape & Alternatives",
            search_query=f"{topic} competing alternatives industry leaders market share",
            rationale="Compare against dominant incumbents and alternative approaches.",
        ),
    ]

    return ResearchPlan(
        topic=topic,
        core_objective=f"Conduct an empirical investigation into {topic}, evaluating technological feasibility, industry timelines, and conflicting claims.",
        key_dimensions=[
            "Technical Performance & Specifications",
            "Manufacturing & Cost Economics",
            "Safety, Degradation & Reliability",
            "Commercial Deployment Trajectory (2026-2030)",
        ],
        sub_queries=queries,
        planned_report_sections=[
            "Executive Summary",
            "Technological Foundations & Current State-of-the-Art",
            "Commercial Readiness & Cost Parity Projections",
            "Conflicting Industry Claims & Risk Matrix",
            "Strategic Recommendations & Future Outlook",
        ],
    )
