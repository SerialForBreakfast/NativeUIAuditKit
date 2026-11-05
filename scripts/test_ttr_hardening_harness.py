#!/usr/bin/env python3
"""Unit tests for the TVTestRig Hardening Test Suite harness.

Tests output parsing, burst evaluation logic, and navigation graph analysis.
Conforms to ASD-STE100 Simplified Technical English requirements.
"""

from __future__ import annotations

import unittest
from scripts.ttr_fixture_hardening_suite import (
    BurstAnalyzer,
    NavigationGraph,
    extract_json,
)


class TestTTRHardeningHarness(unittest.TestCase):
    """Unit test suite for hardening harness helper functions."""

    def test_extract_json_clean(self):
        """Verify extraction from a pure JSON string."""
        sample = '{"status": "ok", "value": 42}'
        res = extract_json(sample)
        self.assertEqual(res["status"], "ok")
        self.assertEqual(res["value"], 42)

    def test_extract_json_with_lifecycle_prefix(self):
        """Verify extraction from text with lifecycle lines before JSON."""
        sample = (
            "[TVTR-LIFECYCLE] schema=2 event_id=ABC role=cli\n"
            "[TVTR-DEBUG] debug info here\n"
            "{\n"
            '  "command" : "status",\n'
            '  "success" : true,\n'
            '  "durationMilliseconds" : 12\n'
            "}\n"
            "[TVTR-LIFECYCLE] exit sequence\n"
        )
        res = extract_json(sample)
        self.assertEqual(res["command"], "status")
        self.assertTrue(res["success"])
        self.assertEqual(res["durationMilliseconds"], 12)

    def test_extract_json_no_json_raises(self):
        """Verify exception when no JSON object exists."""
        sample = "[TVTR-LIFECYCLE] just log lines\nno json here"
        with self.assertRaises(ValueError):
            extract_json(sample)

    def test_burst_analyzer_passed(self):
        """Verify burst evaluation when landing matches expected."""
        res = BurstAnalyzer.evaluate_burst(
            button="right",
            count=3,
            interval_s=0.1,
            start_focus="node_a",
            end_focus="node_d",
            expected_focus="node_d",
            dropped_count=0,
        )
        self.assertTrue(res["passed"])
        self.assertEqual(res["dropped_count"], 0)
        self.assertEqual(res["delivered_count"], 3)
        self.assertEqual(res["interval_ms"], 100.0)

    def test_burst_analyzer_failed_dropping(self):
        """Verify burst evaluation failure when inputs are dropped."""
        res = BurstAnalyzer.evaluate_burst(
            button="right",
            count=5,
            interval_s=0.05,
            start_focus="node_a",
            end_focus="node_c",
            expected_focus="node_f",
            dropped_count=2,
        )
        self.assertFalse(res["passed"])
        self.assertEqual(res["dropped_count"], 2)
        self.assertEqual(res["delivered_count"], 3)

    def test_burst_analyzer_failed_mismatched_landing(self):
        """Verify burst evaluation failure when landing is unexpected."""
        res = BurstAnalyzer.evaluate_burst(
            button="down",
            count=2,
            interval_s=0.15,
            start_focus="node_a",
            end_focus="node_x",
            expected_focus="node_b",
            dropped_count=0,
        )
        self.assertFalse(res["passed"])
        self.assertEqual(res["end_focus"], "node_x")
        self.assertEqual(res["expected_focus"], "node_b")

    def test_navigation_graph_cycles_and_dead_ends(self):
        """Verify graph cycle detection and dead end identification."""
        graph = NavigationGraph()
        # Add reversible pair A <-> B
        graph.add_edge("btn_a", "right", "btn_b")
        graph.add_edge("btn_b", "left", "btn_a")

        # Add reversible pair B <-> C
        graph.add_edge("btn_b", "down", "btn_c")
        graph.add_edge("btn_c", "up", "btn_b")

        # Add a dead end node D (reached from C, no outgoing edges)
        graph.add_edge("btn_c", "right", "btn_d")

        data = graph.to_dict()
        self.assertEqual(data["total_nodes"], 4)
        self.assertEqual(data["total_edges"], 5)
        self.assertIn("btn_d", data["dead_ends"])
        self.assertNotIn("btn_a", data["dead_ends"])

        cycles = graph.detect_cycles()
        self.assertIn(["btn_a", "btn_b"], cycles)
        self.assertIn(["btn_b", "btn_c"], cycles)


if __name__ == "__main__":
    unittest.main()
