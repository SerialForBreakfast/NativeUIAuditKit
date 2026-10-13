"""Unit tests for backlog_groomer (ASD-STE100)."""
import unittest
from pathlib import Path

import backlog_groomer as bg
import research_queue as q


class BacklogGroomerTests(unittest.TestCase):
    def test_directories_exist(self):
        bg.ensure_directories()
        self.assertTrue(bg.PROPOSALS_DIR.exists())
        self.assertTrue(bg.QUARANTINE_DIR.exists())

    def test_is_proposal_detection(self):
        self.assertTrue(bg.is_proposal({"planningOnly": True}))
        self.assertTrue(bg.is_proposal({"requirements": ["Remote-TTR: test requirement"]}))
        self.assertTrue(bg.is_proposal({"requirements": ["External dependency missing"]}))
        self.assertFalse(bg.is_proposal({"requirements": []}))
        self.assertFalse(bg.is_proposal({}))

    def test_queue_status_contract(self):
        counts, ready = bg.get_queue_status()
        self.assertIn("ready", counts)
        self.assertIn("complete", counts)
        self.assertIn("blocked", counts)
        self.assertIsInstance(ready, list)
        self.assertGreaterEqual(counts["ready"], 0)


if __name__ == "__main__":
    unittest.main()
