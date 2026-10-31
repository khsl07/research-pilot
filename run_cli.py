import argparse
import sys
import datetime
from src.agent.graph import ResearchPilotAgent
from src.export.markdown_export import generate_markdown_bundle
from src.export.pdf_export import generate_pdf_bytes
from src.config import settings

def main():
    parser = argparse.ArgumentParser(description="ResearchPilot - Agentic Research Assistant CLI")
    parser.add_argument("--topic", type=str, default="Impact of Solid-State Batteries on Commercial EV Adoption by 2030", help="Research topic")
    parser.add_argument("--guidance", type=str, default=None, help="Optional user focus guidance")
    parser.add_argument("--export-pdf", type=str, default="research_report.pdf", help="Output path for PDF report")
    parser.add_argument("--export-md", type=str, default="research_report.md", help="Output path for Markdown report")
    args = parser.parse_args()

    print("\n" + "="*70)
    print("🔬 ResearchPilot — Agentic Research Assistant (CLI Mode)")
    print("="*70)
    print(f"Topic: {args.topic}")
    if args.guidance:
        print(f"Guidance: {args.guidance}")
    print("="*70 + "\n")

    def progress_callback(step: str, msg: str):
        print(f"[{step.upper()}] {msg}")

    agent = ResearchPilotAgent(step_callback=progress_callback)
    state = agent.run(topic=args.topic, user_guidance=args.guidance)

    print("\n" + "-"*70)
    print("📋 CITATION VERIFICATION SCORECARD")
    print("-"*70)
    audit = state.get("citation_audit")
    if audit:
        print(f"Citation Fidelity Score: {audit.fidelity_score}%")
        print(f"Verdict: {audit.verdict}")
        print(f"Verified Citations: {audit.verified_count} / {audit.total_claims_checked}")
        print(f"Flagged Unsupported Claims: {audit.flagged_count}")
        if audit.flagged_count > 0:
            print("\nFlagged Claims:")
            for item in audit.items:
                if item.flag_warning:
                    print(f"  - [{item.citation_index}] '{item.claim_text[:60]}...' -> {item.flag_warning}")

    print("\n" + "-"*70)
    print("⚖️ CONFLICTING CLAIMS SUMMARY")
    print("-"*70)
    conflicts = state.get("conflict_report")
    if conflicts and conflicts.conflicts:
        for cf in conflicts.conflicts:
            print(f"  * {cf.topic_aspect} [{cf.severity} Severity - {cf.category}]")
            print(f"    Claim A ({cf.source_a}): {cf.claim_a}")
            print(f"    Claim B ({cf.source_b}): {cf.claim_b}")
            print(f"    Analysis: {cf.analysis}\n")
    else:
        print("  No major contradictory claims detected across sources.")

    # Human-in-the-Loop Approval Prompt
    print("\n" + "="*70)
    print("✍️ HUMAN-IN-THE-LOOP APPROVAL REQUIRED")
    print("="*70)
    user_input = input("Do you approve this research report for export? (yes/no): ").strip().lower()

    draft = state.get("draft_report")
    if user_input in ["y", "yes"]:
        draft.approved_by_user = True
        draft.approval_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print("\n✅ Report approved by human lead!")

        # Export Files
        md_text = generate_markdown_bundle(draft, conflicts, audit)
        with open(args.export_md, "w", encoding="utf-8") as f:
            f.write(md_text)
        print(f"📁 Exported Markdown report to: {args.export_md}")

        pdf_bytes = generate_pdf_bytes(draft, conflicts, audit)
        with open(args.export_pdf, "wb") as f:
            f.write(pdf_bytes)
        print(f"📁 Exported PDF report to: {args.export_pdf}")
    else:
        print("\n❌ Report rejected or marked for revision. Export halted.")

    print("\n" + "="*70)
    print("Session finished.")
    print("="*70)

if __name__ == "__main__":
    main()
