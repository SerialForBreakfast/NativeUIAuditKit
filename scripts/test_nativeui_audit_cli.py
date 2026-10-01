#!/usr/bin/env python3
"""Offline real-process CLI/MCP contract tests. No model inference."""
import json
import os
from pathlib import Path
import subprocess
import unittest
import uuid

ROOT = Path(__file__).resolve().parents[1]
BINARY = ROOT / ".build/debug/nativeui-audit"


class CLIProcessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.work = ROOT / ".build/debug-output" / ("cli-process-" + str(uuid.uuid4()))
        cls.work.mkdir(parents=True)
        (cls.work / "corrupt.png").write_bytes(b"not an image")

    def run_cli(self, *args, stdin=None):
        return subprocess.run([str(BINARY), *args], input=stdin, text=True,
                              capture_output=True, timeout=30, cwd=ROOT,
                              env=dict(os.environ, TMPDIR=str(ROOT / ".build/debug-output")))

    def test_help_and_usage(self):
        self.assertEqual(self.run_cli("--help").returncode, 0)
        for args in [("mcp",), ("scan",), ("scan", "a", "--min-confidence", "nan"),
                     ("doctor", "--strict"), ("scan", "a", "--unexpected")]:
            p = self.run_cli(*args)
            self.assertEqual(p.returncode, 2, p)
            self.assertEqual(json.loads(p.stderr)["status"], "failed")

    def test_scan_errors_and_batch_accounting(self):
        for name in ("corrupt.png", "missing.png", "../escape.png"):
            p = self.run_cli("scan", name, "--root", str(self.work))
            self.assertEqual(p.returncode, 1, p)
            self.assertEqual(json.loads(p.stdout)["status"], "failed")
        p = self.run_cli("scan-batch", ".", "--root", str(self.work))
        value = json.loads(p.stdout)
        self.assertEqual(p.returncode, 1)
        self.assertEqual(value["count"], 1)
        self.assertEqual(value["failed"], 1)
        p = self.run_cli("scan", "missing.png", "--root", str(self.work), "--format", "table")
        self.assertEqual(p.returncode, 1)
        self.assertIn("Status: failed", p.stdout)

    def test_mcp_real_stdio(self):
        messages = [
            {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {
                "protocolVersion": "2025-11-25", "capabilities": {},
                "clientInfo": {"name": "process-tests", "version": "1"}}},
            {"jsonrpc": "2.0", "method": "notifications/initialized"},
            {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
            {"jsonrpc": "2.0", "id": "scan", "method": "tools/call", "params": {
                "name": "audit_screenshot", "arguments": {"imagePath": "corrupt.png"}}},
            {"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {
                "name": "audit_screenshot", "arguments": {"imagePath": "../escape.png"}}},
            {"jsonrpc": "2.0", "id": 5, "method": "ping"},
        ]
        p = self.run_cli("mcp", "--root", str(self.work),
                         stdin="\n".join(map(json.dumps, messages)) + "\n{\n")
        self.assertEqual(p.returncode, 0, p.stderr)
        replies = [json.loads(line) for line in p.stdout.splitlines()]
        self.assertEqual(len(replies), 6)
        self.assertEqual(len(replies[1]["result"]["tools"]), 2)
        self.assertTrue(replies[2]["result"]["isError"])
        self.assertEqual(replies[3]["result"]["structuredContent"]["error"]["code"], "outside_root")
        self.assertEqual(replies[4]["result"], {})
        self.assertEqual(replies[5]["error"]["code"], -32700)

    def test_oversize_line_stops(self):
        p = self.run_cli("mcp", "--root", str(self.work), stdin=" " * (1048576 + 100) + "\n")
        self.assertEqual(p.returncode, 2)
        self.assertEqual(p.stdout, "")
        self.assertEqual(json.loads(p.stderr)["error"]["code"], "message_too_large")


if __name__ == "__main__":
    unittest.main()
