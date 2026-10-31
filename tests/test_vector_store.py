import unittest
from src.tools.vector_store import ChromaResearchStore
from src.schemas.source import SearchResultItem

class TestVectorStore(unittest.TestCase):
    def setUp(self):
        # Use ephemeral in-memory collection for test
        self.store = ChromaResearchStore(collection_name="test_collection")
        self.store.clear()

    def test_add_and_query_results(self):
        items = [
            SearchResultItem(
                title="QuantumScape 2026 Test",
                url="https://quantumscape.com/test",
                content="QuantumScape cells achieved 1000 Wh/L volumetric density in lab trials.",
                score=0.95,
                source_type="web",
            ),
            SearchResultItem(
                title="Toyota Solid State 2027",
                url="https://toyota.com/tech",
                content="Toyota plans initial solid-state batteries in luxury vehicles for 2027.",
                score=0.90,
                source_type="web",
            ),
        ]

        indexed_count = self.store.add_search_results(items)
        self.assertEqual(indexed_count, 2)

        results = self.store.query("volumetric density", n_results=2)
        self.assertGreaterEqual(len(results), 1)
        self.assertTrue(results[0].source_id in [1, 2])
        self.assertIn("Wh/L", results[0].text)

if __name__ == "__main__":
    unittest.main()
