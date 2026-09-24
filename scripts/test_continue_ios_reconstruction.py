"""Offline safeguards; these tests never invoke Xcode or simctl."""
import json
from pathlib import Path
import tempfile
import unittest
from contextlib import ExitStack, redirect_stdout
import io
import sys
from unittest.mock import patch

import continue_ios_reconstruction as r


class ContinuationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=r.ROOT / ".build/debug-output")
        self.root = Path(self.temp.name)
        prefix = self.root / "prefix"
        prefix.mkdir()
        (prefix / "manifest.json").write_text(json.dumps({"entries": [{}] * 14340}))
        (prefix / "capture-ledger.json").write_text('{"version":1}')
        self.prefix_patch = patch.object(r, "PREFIX", prefix)
        self.destination_patch = patch.object(r, "DESTINATION", self.root / "corpus")
        self.prefix_patch.start()
        self.destination_patch.start()

    def tearDown(self):
        self.prefix_patch.stop()
        self.destination_patch.stop()
        self.temp.cleanup()

    def test_plan_has_no_native_calls_and_preserves_counts(self):
        with patch.object(r, "command", side_effect=AssertionError("native mutation")):
            doc = r.plan("test-plan")
        self.assertEqual(sum(doc["remaining"].values()), 2600)
        self.assertEqual(sum(doc["expectedCounts"].values()), 16940)
        self.assertFalse(doc["trainingAuthorized"])

    def test_wrong_target_and_unsafe_names(self):
        for name, target in (("test", "booted"), ("../dataset", r.TARGET), ("", r.TARGET)):
            with self.assertRaises(ValueError):
                r.plan(name, target)

    def test_changed_source_and_prefix(self):
        doc = r.plan("pins")
        with patch.object(r, "sources", return_value={}):
            with self.assertRaisesRegex(ValueError, "source_changed"):
                r.check_pins(doc)
        doc["prefixManifestSHA256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "prefix_changed"):
            r.check_pins(doc)

    def test_staging_collision_and_copy_hashes(self):
        source = self.root / "source"
        source.mkdir()
        (source / "file").write_bytes(b"original")
        destination = self.root / "destination"
        r.copy_new(source, destination)
        self.assertEqual((source / "file").read_bytes(), (destination / "file").read_bytes())
        with self.assertRaisesRegex(ValueError, "collision"):
            r.copy_new(source, destination)
        (source / "link").symlink_to(source / "file")
        with self.assertRaisesRegex(ValueError, "symlink"):
            r.copy_new(source, self.root / "not-created")
        self.assertFalse((self.root / "not-created").exists())

    def test_missing_destination_parent_is_created_without_recapture(self):
        source = self.root / "source"
        source.mkdir()
        (source / "file").write_bytes(b"completed-capture")
        destination = self.root / "new-parent/new-child/corpus"
        r.copy_new(source, destination)
        self.assertEqual((destination / "file").read_bytes(), b"completed-capture")

    def test_runtime_unavailable_before_mutation(self):
        with patch.object(r, "command", side_effect=["Xcode 26.6\nBuild version 17F113", '{"devices":{}}']):
            with self.assertRaisesRegex(ValueError, "missing_or_ambiguous"):
                r.runtime()

    def test_partial_skipped_and_failed_tests_cannot_pass(self):
        log = self.root / "test.log"
        for text in ("TEST SUCCEEDED", "Test Case 'method' skipped", "Test Case 'method' failed"):
            log.write_text(text)
            with self.assertRaisesRegex(ValueError, "not_executed"):
                r.require_test_pass(log, "method")
        log.write_text("Test Case 'method' passed (2 seconds)")
        r.require_test_pass(log, "method")

    def test_container_is_resolved_each_time_not_cached(self):
        base = Path.home() / "Library/Developer/CoreSimulator/Devices" / r.TARGET / "data/Containers/Data/Application"
        with patch.object(r, "command", side_effect=[str(base / "old"), str(base / "new")]), \
             patch.object(Path, "is_dir", return_value=True):
            self.assertNotEqual(r.container(), r.container())

    def test_timeout_is_preserved_and_owned_process_only(self):
        import subprocess
        from unittest.mock import MagicMock
        process = MagicMock(pid=123)
        process.wait.side_effect = [subprocess.TimeoutExpired("owned", 1), 0]
        with patch.object(r.subprocess, "Popen", return_value=process):
            with self.assertRaisesRegex(RuntimeError, "no_retry"):
                r.run_logged(["owned"], self.root, "timeout", 1)
        process.terminate.assert_called_once()
        report = json.loads((self.root / "timeout-result.json").read_text())
        self.assertEqual(report["cleanup"], "native_test_state_unresolved")
        self.assertTrue(report["timeout"])

    def test_space_and_host_boundary(self):
        with patch.object(r.shutil, "disk_usage") as usage:
            usage.return_value.free = 1
            with self.assertRaisesRegex(ValueError, "space"):
                r.enough_space(self.root, 2)
        with self.assertRaisesRegex(ValueError, "boundary"):
            r.local("/tmp/not-allowed")

    def test_native_dispatch_requires_xctestrun_extension_and_injected_environment(self):
        import plistlib
        products = self.root / "DerivedData/Build/Products"
        products.mkdir(parents=True)
        base = {"GeneratorRunnerTests": {"TestBundlePath": "__TESTROOT__/tests"}}
        (products / "GeneratorRunnerTests.xctestrun").write_bytes(plistlib.dumps(base))
        log = self.root / "passed.log"
        log.write_text("Test Case 'method' passed")
        with patch.object(r, "run_logged", return_value=log) as run:
            r.test(self.root, "stride", "Class", "method", {"NUA_RECONSTRUCTION_RUN_NAME": "safe"}, 600)
        args = run.call_args.args[0]
        dispatch = Path(args[args.index("-xctestrun") + 1])
        self.assertEqual(dispatch.suffix, ".xctestrun")
        self.assertEqual(plistlib.loads(dispatch.read_bytes())["GeneratorRunnerTests"]["EnvironmentVariables"],
                         {"NUA_RECONSTRUCTION_RUN_NAME": "safe"})

    def test_real_cli_planning_and_execution_authority_boundary(self):
        work = self.root / "cli"
        with patch.object(sys, "argv", ["driver", "plan", "--work", str(work)]), \
             patch.object(r, "command", side_effect=AssertionError("native call")), redirect_stdout(io.StringIO()):
            r.main()
        self.assertTrue((work / "plan.json").is_file())
        with patch.object(sys, "argv", ["driver", "build", "--work", str(work)]), \
             patch.object(r, "execute_phase", side_effect=AssertionError("mutation")):
            with self.assertRaisesRegex(ValueError, "explicit_execution_required"):
                r.main()
        self.assertFalse((work / "tmp").exists())

    def simulated_generation(self, failure=False):
        work = self.root / "work"
        work.mkdir()
        for name, value in (("build-identity.json", {"files": {}}), ("stride-accepted.json", {}),
                            ("prefix-inventory.json", {"totalBytes": 1})):
            (work / name).write_text(json.dumps(value))
        before, after = self.root / "container-before", self.root / "container-after"
        (before / "Documents").mkdir(parents=True)
        current = after / "Documents/reconstruction/run"
        current.mkdir(parents=True)
        (current / "manifest.json").write_text(json.dumps({"entries": [{}] * 16940}))
        log = work / "generate.log"
        log.write_text("Test Case 'testRemainingReconstructionQualification' passed")
        (work / "generate-result.json").write_text(json.dumps({"exitCode": 0, "logSHA256": r.v.sha256(log)}))
        with ExitStack() as stack:
            for name, value in (("check_pins", None), ("runtime", {}), ("command", str(self.root / "app")),
                                ("enough_space", None)):
                stack.enter_context(patch.object(r, name, return_value=value))
            stack.enter_context(patch.object(r.retention, "verify", return_value={}))
            stack.enter_context(patch.object(r, "container", side_effect=[before, after]))
            stack.enter_context(patch.object(r, "test", side_effect=RuntimeError("failed_cleanup") if failure else None))
            copy = stack.enter_context(patch.object(r, "copy_new"))
            if failure:
                with self.assertRaisesRegex(RuntimeError, "failed_cleanup"):
                    r.execute_phase("generate", work, {"stagingName": "run"})
                self.assertEqual(copy.call_args.args, (current, work / "failed-generation"))
                self.assertFalse((work / "retrieval.json").exists())
            else:
                r.execute_phase("generate", work, {"stagingName": "run"})
                self.assertEqual(copy.call_args.args, (current, r.DESTINATION))
                receipt = json.loads((work / "retrieval.json").read_text())
                self.assertEqual(receipt["retrievedFrom"], str(current))
                self.assertEqual(receipt["initialContainer"], str(before))

    def test_actual_generate_flow_retrieves_migrated_container(self):
        self.simulated_generation()

    def test_failed_cleanup_preserves_evidence_without_publishing_corpus(self):
        self.simulated_generation(failure=True)


if __name__ == "__main__":
    unittest.main()
