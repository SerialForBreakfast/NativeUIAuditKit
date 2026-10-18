"""End-to-end template compilation, plan validation, and isolated queue execution tests for T67 through T86."""
from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

import backlog_pipeline as bp
import hcf_templates395 as t
import research_approval as approval
import research_queue as q
from experiment_templates import pin


class NovelTemplatesQueueTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(dir=q.ROOT / ".build", prefix="novel418-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.queue = self.root / "queue"

    def doc(self, name: str, value: object) -> dict:
        path = self.root / name
        q.save(path, value)
        return pin(path)

    def bytes_doc(self, name: str, data: bytes = b"weights-stub") -> dict:
        path = self.root / name
        path.write_bytes(data)
        return pin(path)

    def build_all_20_template_descriptions(self) -> list[dict]:
        init_ref = self.bytes_doc("init.pt")
        cfg_ref = self.doc("config.json", {"initialization": init_ref})
        train_mem = self.doc(
            "train_membership.json",
            {"rows": [{"id": "r1", "group": "g1", "role": "training", "trainingEligible": True, "focused": 1},
                      {"id": "r2", "group": "g2", "role": "training", "trainingEligible": True, "focused": 0}]},
        )
        dev_eval = self.doc("dev_eval.json", {"role": "development", "trainingEligible": False, "frames": [{"id": "f1", "fullPreds": [], "tilePreds": []}], "labels": []})

        specs = [
            ("T67", {"configuration": cfg_ref, "initialization": init_ref, "membership": train_mem, "evalLabels": dev_eval},
             {"nwdWeight": 0.5, "nwdConstant": 12.8, "smallAreaMax": 0.01, "seed": 371}, True),
            ("T68", {"configuration": cfg_ref, "initialization": init_ref, "membership": train_mem, "styleRefs": self.doc("style.json", {"rows": [{"id": "s1", "role": "calibration"}]})},
             {"beta": 0.03, "blendProb": 0.5, "seed": 371}, True),
            ("T69", {"configuration": cfg_ref, "initialization": init_ref, "membership": train_mem, "screenGroups": self.doc("screens.json", {"screens": [{"candidates": [{"sceneId": "sc1", "focused": 1}, {"sceneId": "sc1", "focused": 0}]}]})},
             {"supconWeight": 0.25, "listmleWeight": 0.5, "temperature": 0.1, "seed": 371}, True),
            ("T70", {"configuration": cfg_ref, "initialization": init_ref, "membership": train_mem},
             {"encodingMode": "coord-5ch", "stripHeight": 32, "perimeterWidth": 256, "seed": 371}, True),
            ("T71", {"manifest": self.doc("dipole.json", {"rows": [{"id": "d1", "theme": "light", "profile": "hcf", "noFocus": False, "bgLuma": [244, 245, 243, 246], "ringLuma": [255, 255, 255, 255], "moatLuma": [17, 18, 17, 17]}]})},
             {"kernelVariant": "dipole-ring-moat-v1", "dipoleZMin": 2.0, "moatContrastMin": 35.0}, False),
            ("T72", {"failureReport": self.doc("fail.json", {"role": "development"})},
             {"twinFamily": "selected-tab-unfocused", "pairCount": 3, "seed": 371}, False),
            ("T73", {"model": self.doc("model.json", {"identity": "v3.0"}), "labels": dev_eval},
             {"tileLayout": "top-band-plus-2x2", "scaleGatePolicy": "scale-gated-wbf", "wbfIouThreshold": 0.55, "confidence": 0.25}, False),
            ("T74", {"checkpoint": self.doc("ckpt.json", {"weights": [[0.2, -0.3, 0.5, 0.1]]}), "calibrationManifest": self.doc("cal.json", {"role": "training", "trainingEligible": True, "features": [[1.0, 0.0, 1.0, 0.5], [0.0, 1.0, -0.5, 0.2]], "teacherLogits": [2.1, -1.2]})},
             {"compressionMode": "margin-distilled-palette6", "marginTemperature": 0.35, "flipPenalty": 10.0, "maxBytes": 5_000_000}, False),
            ("T75", {"pairsManifest": self.doc("pairs.json", {"pairs": [{"id": "p1", "action": "down", "beforeFocusXY": [400, 300], "afterFocusXY": [400, 300], "scrollDxDy": [0, -80]}]})},
             {"scrollPhaseThreshold": 8.0, "coneHalfAngleDeg": 45.0}, False),
            ("T76", {"primaryPreds": self.doc("p1.json", {"predictions": [{"frameId": "f1", "class": "navigationBar", "box": [0, 0, 390, 44], "score": 0.85}]}), "secondaryPreds": self.doc("p2.json", {"predictions": [{"frameId": "f1", "class": "navigationBar", "box": [0, 0, 390, 44], "score": 0.80}]}), "groundTruth": dev_eval, "renderedBodies": self.doc("bodies.json", {"bodies": [{"frameId": "f1", "box": [0, 0, 390, 44]}]})},
             {"minConfidence": 0.25, "iouMatchThreshold": 0.5}, False),
            ("T77", {"configuration": cfg_ref, "initialization": init_ref, "membership": train_mem, "anchorManifest": train_mem},
             {"subspaceEnergy": 0.99, "lpWarmupEpochs": 5, "seed": 371}, True),
            ("T78", {"configuration": cfg_ref, "initialization": init_ref, "membership": train_mem, "trainingMatches": self.doc("matches.json", {"matches": [{"role": "training", "trainingEligible": True, "error4d": [-8.0, 1.0, -0.05, 0.01]}] * 6})},
             {"samplerMode": "copula-plus-stn", "enableStnRefiner": True, "stnLossWeight": 0.5, "seed": 371}, True),
            ("T79", {"configuration": cfg_ref, "initialization": init_ref, "membership": train_mem, "selectionGroups": self.doc("sel.json", {"selectionGroupIds": ["s1"], "evaluationGroupIds": ["e1"], "checkpoints": [{"epoch": 20, "noFocusFalsePositives": 0, "decorativeFalsePositives": 0, "lostAnchorSuccesses": 0, "familyAccuracies": {"row": 0.8, "tab": 0.9}}]})},
             {"mode": "group-dro-pareto", "droEta": 0.02, "droSizePenalty": 1.0, "seed": 371}, True),
            ("T80", {"calibrationReports": self.doc("cal_rep.json", {"rows": [{"id": f"c{i}", "group": "cal_g", "scores": [0.95, 0.02], "focusedIndex": 0} for i in range(4)]}), "evaluationReports": self.doc("eval_rep.json", {"rows": [{"id": "e1", "group": "eval_g", "scores": [0.96, 0.01]}]})},
             {"alpha": 0.05, "temperature": 1.0, "oodEnergyThreshold": 0.5}, False),
            ("T81", {"configuration": cfg_ref, "initialization": init_ref, "membership": train_mem, "evalLabels": dev_eval},
             {"projIouWeight": 0.4, "enableStripPooling": True, "seed": 371}, True),
            ("T82", {"observationsPath": self.doc("obs.json", {"pairs": [{"id": "o1", "before": {"page": "Display", "focusKey": "fs", "settingValue": "Standard", "fullOcrLine": "Focus Style Standard Controls how focus appears"}, "after": {"page": "Display", "focusKey": "fs", "settingValue": "Standard", "fullOcrLine": "Focus Style Standard Controls how focus app..."}}]}), "adversarialPath": self.doc("adv.json", {"pairs": [{"id": "a1", "before": {"page": "Display", "focusKey": "fs", "settingValue": "Standard", "fullOcrLine": "Focus Style Standard"}, "after": {"page": "Display", "focusKey": "fs", "settingValue": "High Contrast", "fullOcrLine": "Focus Style High Contrast"}}]})},
             {"anchorPhrase": "Focus Style", "maxTailCost": 0.15}, False),
            ("T83", {"cropsManifest": self.doc("crops.json", {"rows": [{"id": "c1", "role": "development", "trainingEligible": False, "size": 64}]})},
             {"interventionMode": "ctx-harmonic-neutral", "haloOuterPx": 10, "bodyInnerInsetPx": 18}, False),
            ("T84", {"poolManifest": train_mem},
             {"selectionStrategy": "submod-badge-coreset", "targetCount": 2, "uncertaintyWeight": 0.25, "seed": 371}, False),
            ("T85", {"screenFeaturesManifest": self.doc("graph.json", {"screens": [{"id": "s1", "role": "development", "trainingEligible": False, "boxes": [[500, 200, 800, 60], [300, 200, 200, 36]], "scores": [0.92, 0.89]}]})},
             {"mode": "containment-nms-rule", "containmentIoaThreshold": 0.80}, False),
            ("T86", {"checkpoints": self.doc("soup.json", {"models": [{"initialization": "seed371", "weights": [2.0, -4.0], "fisher": [100.0, 0.01], "lambda": 1.0}, {"initialization": "seed371", "weights": [-5.0, 3.0], "fisher": [0.01, 100.0], "lambda": 1.0}]}), "trainingManifests": self.doc("soup_train.json", {"role": "training", "trainingEligible": True, "features": [[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]]})},
             {"mergeMode": "fisher-soup-bn", "recalibrateBn": True}, False),
        ]

        docs = []
        for tid, inputs, params, is_training in specs:
            doc = {
                "version": "hcf-template-description-v1",
                "id": f"job-{tid.lower()}",
                "owner": "Maximum-mini-NUIAK",
                "template": tid,
                "task": "B405-229",
                "question": f"Does template {tid} compile and execute its bounded verification contract?",
                "hypothesis": f"Template {tid} enforces its input, role, and parameter invariants.",
                "controlledComparison": "Control arm versus candidate arm on identical pinned inputs.",
                "decision": "Require exact output receipts and zero role violations.",
                "outcomes": {
                    "supported": "Admit the template to queue batch expansion.",
                    "contradicted": "Fix the failing invariant before registering batches.",
                    "inconclusive": "Complete all unit and queue checks first.",
                },
                "inputs": inputs,
                "parameters": params,
                "dependencies": [],
            }
            if is_training:
                doc["training"] = {
                    "experimentLogRunId": "FOCUS366",
                    "initialization": init_ref,
                    "membership": [train_mem],
                    "epochs": 30,
                    "storageBudgetBytes": 2 << 30,
                    "acceptanceEvidence": "Require zero regressions and positive gain on benchmark_summary.json.",
                    "resume": "restart",
                }
            docs.append(doc)
        return docs

    def test_all_20_templates_compile_register_and_execute_in_isolated_queue(self) -> None:
        docs = self.build_all_20_template_descriptions()
        self.assertEqual(len(docs), 20)
        for doc in docs:
            with self.subTest(template=doc["template"]):
                t.register(doc, self.queue)
                approval.approve(self.queue, doc["id"], "test", "Isolated software qualification for novel template.")
                result = q.run(self.queue, max_jobs=1, lock=self.root / "lock", job_ids=[doc["id"]])
                self.assertEqual(result, [(doc["id"], "complete")])
                out_dir = self.queue / "jobs" / doc["id"] / "attempts/1/out"
                summary = q.load(out_dir / "benchmark_summary.json")
                self.assertFalse(summary["modelAccepted"])

    def test_backlog_pipeline_validates_novel_template_plans_and_rejects_bad_params(self) -> None:
        docs = self.build_all_20_template_descriptions()
        t82_doc = next(d for d in docs if d["template"] == "T82")
        rec = {
            "id": "B405-244",
            "title": "Prefix-anchored OCR matcher",
            "priority": 0,
            "hypothesis": "Prefix-anchored matching resolves clipped Display OCR lines safely.",
            "comparison": "Exact string match versus prefix-anchored tail-clip matcher",
            "requirements": [{"owner": "Maximum-mini-NUIAK"}],
            "reconciliation": {"disposition": "unresolved", "reason": "open"},
            "plan": {
                "template": "T82",
                "owner": "Maximum-mini-NUIAK",
                "jobPrefix": "ocr-route-t82",
                "question": "Does prefix-anchored OCR matching accept clipped Display lines and reject value mutations?",
                "decision": "Require 100% valid matches and 0% adversarial state-mutation accepts.",
                "outcomes": t82_doc["outcomes"],
                "rule": "gain-without-loss",
                "control": "exact",
                "shared": {"inputs": t82_doc["inputs"], "parameters": {"anchorPhrase": "Focus Style"}},
                "arms": [
                    {"id": "exact", "parameters": {"maxTailCost": 0.0}},
                    {"id": "clipped", "parameters": {"maxTailCost": 0.15}},
                ],
            },
        }
        expanded = bp.descriptions(rec)
        self.assertEqual(len(expanded), 2)

        # Bad parameter value (maxTailCost > 0.30) must be rejected by backlog_pipeline.validate_plan
        rec["plan"]["arms"][1]["parameters"]["maxTailCost"] = 0.85
        with self.assertRaisesRegex(ValueError, "ocr_matcher_tail_cost_range"):
            bp.validate_plan(rec)

    def test_additions_418_novel_catalog_admission_and_template_coverage(self) -> None:
        import copy
        import experiment_backlog as eb

        catalog = copy.deepcopy(q.load(q.ROOT / "Research/Experiments/backlog405.json"))
        additions = q.load(q.ROOT / "Research/Experiments/additions-418-novel.json")
        self.assertEqual(len(additions), 20)
        added = []
        for item in additions:
            self.assertIn(item["template"], t.CONTRACTS)
            added.append(bp.add(catalog, item)["id"])
        self.assertEqual(len(added), 20)
        self.assertEqual(added[0], "B405-230")
        self.assertEqual(added[-1], "B405-249")
        validated = eb.validate(catalog, q.ROOT)
        self.assertEqual(validated["records"], 248)


if __name__ == "__main__":
    unittest.main()
