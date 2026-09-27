"""Input-bound replay opt-in; ordinary source validation stays strict."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from focus_dataset_contract import ROOT, digest, FocusDataError
from focus_mixed_assembly import reference
import focus_runtime_replay as replay
import focus_appearance_experiment as appearance


class RuntimeReplayTests(unittest.TestCase):
    def setUp(self):
        parent = ROOT / ".build/debug-output"; parent.mkdir(parents=True, exist_ok=True)
        self.tmp = tempfile.TemporaryDirectory(dir=parent); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.old = {"sourceSHA256": "old", "helperSHA256": "old-helper"}
        self.current = {"sourceSHA256": "new", "helperSHA256": "new-helper"}
        self.patch = patch.object(replay, "identity", return_value=self.current); self.patch.start(); self.addCleanup(self.patch.stop)
        self.spec = {"version": "focus-appearance-input-v1", "evaluation": []}
        self.doc = {"version": "focus-appearance-experiment-v1", "inputs": self.spec,
                    "samples": [{"id": "one", "crop": {"pixelSHA256": "pixels"}, "runtime": self.old}]}
        self.doc["protocolSHA256"] = digest(self.doc)
        source = self.save("source.json", self.doc)
        self.proof = {"version": "candidate-runtime-replay-v1", "source": source,
                      "runtime": self.current, "oldRuntimes": [self.old], "matches": 1,
                      "selectionValidated": True,
                      "samples": [{"id": "one", "pixelSHA256": "pixels", "matchesRetainedCrop": True}]}

    def save(self, name, doc):
        path = self.root / name; path.write_text(json.dumps(doc)); return reference(path)

    def bound(self, proof=None):
        return {**self.spec, "runtimeReplay": self.save("proof.json", proof or self.proof)}

    def test_opt_in_only_and_context_restored(self):
        self.assertFalse(replay.matches(self.old)); self.assertTrue(replay.matches(self.current))
        with replay.replay_scope(self.bound()):
            self.assertTrue(replay.matches(self.old)); self.assertFalse(replay.matches({"sourceSHA256": "unrelated"}))
        self.assertFalse(replay.matches(self.old))

    def test_failed_body_restores_context(self):
        with self.assertRaisesRegex(ValueError, "body"):
            with replay.replay_scope(self.bound()): raise ValueError("body")
        self.assertFalse(replay.matches(self.old))

    def test_incomplete_changed_pixels_or_runtime_rejected(self):
        changes = [lambda p: p.update(matches=0), lambda p: p.update(samples=[]),
                   lambda p: p["samples"][0].update(pixelSHA256="changed"),
                   lambda p: p["samples"][0].update(matchesRetainedCrop=False),
                   lambda p: p.update(oldRuntimes=[{}]), lambda p: p.update(runtime={}),
                   lambda p: p.update(selectionValidated=False)]
        for change in changes:
            proof = copy.deepcopy(self.proof); change(proof)
            with self.assertRaises(FocusDataError):
                with replay.replay_scope(self.bound(proof)): pass

    def test_input_or_source_tamper_rejected(self):
        spec = self.bound(); spec["evaluation"] = ["new data"]
        with self.assertRaisesRegex(FocusDataError, "input_drift"):
            with replay.replay_scope(spec): pass
        spec = self.bound(); (self.root / "source.json").write_text("{}")
        with self.assertRaisesRegex(FocusDataError, "changed_assembly_input"):
            with replay.replay_scope(spec): pass

    def test_runtime_drift_during_scope_rejected(self):
        with self.assertRaisesRegex(FocusDataError, "changed_replay_runtime"):
            with replay.replay_scope(self.bound()): self.current["helperSHA256"] = "changed"
        self.assertFalse(replay.matches(self.old))

    def test_reconstruction_cannot_change_membership(self):
        with patch.object(appearance, "_assemble", return_value={"samples": []}):
            with self.assertRaisesRegex(FocusDataError, "reconstruction_drift"): appearance.assemble(self.bound())

    def test_legacy_assembly_unchanged_without_proof(self):
        expected = {"legacy": True}
        with patch.object(appearance, "_assemble", return_value=expected):
            self.assertEqual(appearance.assemble(self.spec), expected)
        self.assertFalse(replay.matches(self.old))


if __name__ == "__main__": unittest.main()
