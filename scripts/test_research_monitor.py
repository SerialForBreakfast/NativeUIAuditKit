#!/usr/bin/env python3
"""Unit tests for research monitor utility (ASD-STE100)."""
import json
from pathlib import Path
import shutil
import tempfile
import unittest

import research_monitor

class ResearchMonitorTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="test-monitor-"))
        self.queue = self.tmp / "queue"
        self.jobs = self.queue / "jobs"
        self.jobs.mkdir(parents=True, exist_ok=True)

        # Create one mock completed job
        j1 = self.jobs / "job-01"
        j1.mkdir(parents=True, exist_ok=True)
        spec = {"limits": {"maxAttempts": 2}}
        (j1 / "spec.json").write_text(json.dumps(spec))
        att1 = j1 / "attempts/1"
        att1.mkdir(parents=True, exist_ok=True)
        res = {"status": "complete", "outputs": []}
        (att1 / "result.json").write_text(json.dumps(res))
        out = att1 / "out"
        out.mkdir(parents=True, exist_ok=True)
        summary = {"metrics": {"accuracy": 0.95}}
        (out / "benchmark_summary.json").write_text(json.dumps(summary))

        # Create one mock pending job
        j2 = self.jobs / "job-02"
        j2.mkdir(parents=True, exist_ok=True)
        (j2 / "spec.json").write_text(json.dumps(spec))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_get_queue_stats(self):
        stats = research_monitor.get_queue_stats(self.queue)
        self.assertEqual(stats["total"], 2)
        self.assertEqual(stats["complete"], 1)
        self.assertEqual(stats["pending"], 1)
        self.assertEqual(len(stats["jobs"]), 2)

if __name__ == "__main__":
    unittest.main()
