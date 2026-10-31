import unittest
from src.agent.graph import ResearchPilotAgent

class TestGraphFlow(unittest.TestCase):
    def test_full_pipeline_execution(self):
        steps_executed = []

        def callback(step, msg):
            steps_executed.append(step)

        agent = ResearchPilotAgent(
            gemini_api_key="",  # Runs high quality deterministic pipeline
            tavily_api_key="",
            step_callback=callback,
        )

        topic = "Commercial Viability of Solid-State Batteries in EVs by 2030"
        state = agent.run(topic=topic)

        # Check all nodes executed in LangGraph sequence
        self.assertIn("planner", steps_executed)
        self.assertIn("searcher", steps_executed)
        self.assertIn("indexer", steps_executed)
        self.assertIn("conflict_checker", steps_executed)
        self.assertIn("draftsman", steps_executed)
        self.assertIn("verifier", steps_executed)

        # Check state outputs
        self.assertIsNotNone(state.get("plan"))
        self.assertGreater(len(state.get("retrieved_evidence", [])), 0)
        self.assertIsNotNone(state.get("conflict_report"))
        self.assertIsNotNone(state.get("draft_report"))
        self.assertIsNotNone(state.get("citation_audit"))
        self.assertGreater(state.get("citation_audit").fidelity_score, 0.0)

if __name__ == "__main__":
    unittest.main()
