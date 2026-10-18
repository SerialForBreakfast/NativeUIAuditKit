"""Unit tests for Tranche 2 novel templates T77 through T86 (EXP418-11 through EXP418-20)."""
from __future__ import annotations

import unittest
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

import nullspace_focus_train418 as t77
import copula_proposal_stn418 as t78
import group_dro_pareto418 as t79
import conformal_energy_abstention418 as t80
import strip_iou_detector418 as t81
import prefix_ocr_route_matcher418 as t82
import context_counterfactual_crops418 as t83
import submodular_coreset_subset418 as t84
import focus_graph_relation418 as t85
import fisher_model_soup418 as t86


class Tranche2TemplateTests(unittest.TestCase):
    def test_t77_nullspace_projector_preserves_anchor_activations_exactly(self) -> None:
        torch.manual_seed(371)
        # Anchor features span only the first 3 dimensions of an 8D space
        anchor_x = torch.zeros((16, 8), dtype=torch.float32)
        anchor_x[:, :3] = torch.randn(16, 3)

        layer = nn.Linear(8, 4, bias=False)
        initial_anchor_out = layer(anchor_x).detach().clone()

        projector = t77.OrthogonalSubspaceProjector(energy_threshold=1.0)
        stats = projector.fit_anchor_matrix("layer", anchor_x)
        self.assertEqual(stats["retainedRank"], 3.0)
        self.assertEqual(stats["nullRank"], 5.0)

        # Optimize on a native feature vector that has components in all 8 dimensions
        native_x = torch.randn(10, 8)
        target_y = torch.ones(10, 4)
        opt = torch.optim.SGD(layer.parameters(), lr=0.5)
        for _ in range(5):
            opt.zero_grad()
            loss = F.mse_loss(layer(native_x), target_y)
            loss.backward()
            projector.project_linear_grad("layer", layer)
            opt.step()

        # Verify zero drift on anchor activations!
        final_anchor_out = layer(anchor_x).detach()
        max_drift = float((final_anchor_out - initial_anchor_out).abs().max().item())
        self.assertLess(max_drift, 1e-5)

    def test_t78_copula_error_sampler_and_stn_identity_init(self) -> None:
        matches = [
            {"role": "training", "trainingEligible": True, "error4d": [-12.0, 2.0, -0.08, 0.01]},
            {"role": "training", "trainingEligible": True, "error4d": [-10.0, 1.5, -0.06, 0.02]},
            {"role": "training", "trainingEligible": True, "error4d": [-14.0, 2.5, -0.10, 0.00]},
            {"role": "training", "trainingEligible": True, "error4d": [-8.0, 1.0, -0.04, 0.01]},
            {"role": "training", "trainingEligible": True, "error4d": [-11.0, 1.8, -0.07, 0.01]},
        ]
        sampler = t78.EmpiricalCopulaErrorSampler(matches, seed=371)
        samples = sampler.sample(32)
        self.assertEqual(samples.shape, (32, 4))
        self.assertTrue(np.all(samples[:, 0] <= -8.0))

        # Reject development or ambiguous matches in training error sampler
        with self.assertRaisesRegex(ValueError, "copula_training_role_required"):
            t78.EmpiricalCopulaErrorSampler([{"role": "development", "error4d": [0, 0, 0, 0]}] * 4)

        stn = t78.ProposalSTNRefiner(in_channels=3)
        x = torch.rand(2, 3, 32, 32)
        warped, delta = stn(x)
        self.assertEqual(float(delta.abs().max().item()), 0.0)
        self.assertLess(float((warped - x).abs().max().item()), 1e-5)

    def test_t79_group_dro_upweights_high_loss_group_and_pareto_selector(self) -> None:
        dro = t79.GroupDROLoss([100, 10], eta_q=0.10, size_penalty=1.0)
        # Group 0 has low loss, Group 1 has high loss
        logits = torch.tensor([-4.0, -4.0, -3.0, -3.0], requires_grad=True)
        targets = torch.tensor([0.0, 0.0, 1.0, 1.0])
        groups = torch.tensor([0, 0, 1, 1])
        loss = dro(logits, targets, groups)
        loss.backward()
        self.assertGreater(float(dro.group_probs[1].item()), float(dro.group_probs[0].item()))

        ckpts = [
            {"epoch": 10, "noFocusFalsePositives": 0, "decorativeFalsePositives": 0, "lostAnchorSuccesses": 1, "familyAccuracies": {"row": 0.90, "tab": 0.90}},
            {"epoch": 20, "noFocusFalsePositives": 0, "decorativeFalsePositives": 0, "lostAnchorSuccesses": 0, "familyAccuracies": {"row": 0.75, "tab": 0.88}},
            {"epoch": 30, "noFocusFalsePositives": 0, "decorativeFalsePositives": 0, "lostAnchorSuccesses": 0, "familyAccuracies": {"row": 0.62, "tab": 0.99}},
        ]
        chosen = t79.select_pareto_checkpoint(ckpts, {"g_sel"}, {"g_eval"})
        # Epoch 10 rejected due to lostAnchorSuccesses=1; Epoch 20 beats Epoch 30 on worst-family (0.75 vs 0.62)
        self.assertEqual(chosen["epoch"], 20)

        with self.assertRaisesRegex(ValueError, "group_dro_group_leakage"):
            t79.select_pareto_checkpoint(ckpts, {"shared"}, {"shared"})

    def test_t80_conformal_energy_four_state_classification(self) -> None:
        q_hat = t80.fit_conformal_quantile([0.02, 0.05, 0.08, 0.12, 0.15, 0.20], alpha=0.05)
        # 1. Clear single focus peak
        cert = t80.classify_screen_conformal_energy([0.96, 0.02, 0.01, 0.03], q_hat=q_hat)
        self.assertEqual(cert["state"], "certified_focus")
        self.assertEqual(cert["selectedIndex"], 0)

        # 2. Verified no-focus screen
        nofoc = t80.classify_screen_conformal_energy([0.01, 0.02, 0.03], q_hat=q_hat)
        self.assertEqual(nofoc["state"], "verified_no_focus")
        self.assertIsNone(nofoc["selectedIndex"])

        # 3. Competing twin peaks (ambiguous competition)
        comp = t80.classify_screen_conformal_energy([0.95, 0.94, 0.01, 0.01], q_hat=0.80)
        self.assertEqual(comp["state"], "ambiguous_competition")
        self.assertIsNone(comp["selectedIndex"])

        # 4. OOD screen where all background crops score > 0.85
        ood = t80.classify_screen_conformal_energy([0.91, 0.90, 0.89, 0.90], q_hat=0.20, ood_energy_threshold=0.5)
        self.assertEqual(ood["state"], "suspected_missing_proposal_or_ood")
        self.assertIsNone(ood["selectedIndex"])

    def test_t81_strip_iou_non_zero_horizontal_gradient_on_disjoint_rows(self) -> None:
        # Two wide rows slightly separated vertically (zero 2D IoU) and truncated horizontally
        pred = torch.tensor([[600.0, 200.0, 900.0, 40.0]], requires_grad=True)
        target = torch.tensor([[750.0, 260.0, 1400.0, 40.0]])
        res = t81.marginal_projection_iou_loss_xywh(pred, target, proj_iou_weight=0.5)
        self.assertEqual(float(res["iou2d"].item()), 0.0)
        self.assertGreater(float(res["giouX"].item()), 0.5)
        res["loss"].backward()
        self.assertGreater(float(pred.grad[0, 2].abs().item()), 1e-4)

        spm = t81.AnisotropicStripPooling(channels=8)
        x = torch.randn(2, 8, 12, 24)
        self.assertEqual(spm(x).shape, (2, 8, 12, 24))

    def test_t82_prefix_anchored_ocr_matcher_b405_220_and_adversarial_safety(self) -> None:
        before = {
            "page": "Accessibility > Display",
            "focusKey": "focus_style_row",
            "settingValue": "Standard",
            "fullOcrLine": "Focus Style Standard Controls how focus indicators appear on screen",
        }
        # Clipped right-edge tail on Display (B405-220 reproduction)
        after_clipped = {
            "page": "Accessibility > Display",
            "focusKey": "focus_style_row",
            "settingValue": "Standard",
            "fullOcrLine": "Focus Style Standard Controls how focus indicators appear on scr...",
        }
        res = t82.match_prefix_anchored_observation(before, after_clipped)
        self.assertTrue(res["matched"])
        self.assertEqual(res["reason"], "prefix_anchored_tail_clip_match")

        # Adversarial mutation 1: Standard -> High Contrast MUST be rejected
        adv_val = dict(after_clipped, settingValue="High Contrast")
        self.assertFalse(t82.match_prefix_anchored_observation(before, adv_val)["matched"])

        # Adversarial mutation 2: Focus moved to another row MUST be rejected
        adv_foc = dict(after_clipped, focusKey="bold_text_row")
        self.assertFalse(t82.match_prefix_anchored_observation(before, adv_foc)["matched"])

        # Adversarial mutation 3: Prefix mutated before Focus Style MUST be rejected
        adv_pre = dict(after_clipped, fullOcrLine="Display Mode Focus Style Standard Controls how focus")
        self.assertFalse(t82.match_prefix_anchored_observation(before, adv_pre)["matched"])

    def test_t83_context_counterfactual_crops_preserves_halo_bit_identically(self) -> None:
        rng = np.random.default_rng(371)
        crop = rng.integers(0, 255, size=(128, 128, 3), dtype=np.uint8)
        donor = rng.integers(0, 255, size=(128, 128, 3), dtype=np.uint8)
        h0, b0 = 12, 24
        h1, b1 = 128 - h0, 128 - b0

        for mode in ("ctx-harmonic-neutral", "ctx-transplant", "interior-neutral"):
            out = t83.apply_concentric_intervention(crop, mode=mode, halo_outer_px=h0, body_inner_inset_px=b0, donor_rgb=donor)
            # Verify all 4 sides of Z_halo are 100% bit-identical to crop
            self.assertTrue(np.array_equal(out[h0:b0, h0:h1], crop[h0:b0, h0:h1]))
            self.assertTrue(np.array_equal(out[b1:h1, h0:h1], crop[b1:h1, h0:h1]))
            self.assertTrue(np.array_equal(out[h0:h1, h0:b0], crop[h0:h1, h0:b0]))
            self.assertTrue(np.array_equal(out[h0:h1, b1:h1], crop[h0:h1, b1:h1]))

    def test_t84_submodular_badge_coreset_preserves_groups_and_rejects_impossible_quota(self) -> None:
        rows = [
            {"id": "r1", "group": "g1", "family": "row", "role": "training", "trainingEligible": True, "features": [1.0, 0.0, 0.0], "prob": 0.2, "focused": 1},
            {"id": "r2", "group": "g1", "family": "row", "role": "training", "trainingEligible": True, "features": [0.9, 0.1, 0.0], "prob": 0.1, "focused": 0},
            {"id": "r3", "group": "g2", "family": "tab", "role": "training", "trainingEligible": True, "features": [0.0, 1.0, 0.0], "prob": 0.8, "focused": 0},
            {"id": "r4", "group": "g3", "family": "button", "role": "training", "trainingEligible": True, "features": [0.0, 0.0, 1.0], "prob": 0.3, "focused": 1},
        ]
        params = t84.parameters({"selectionStrategy": "submod-badge-coreset", "targetCount": 2, "uncertaintyWeight": 0.25, "seed": 371})
        res = t84.select_group_preserving_subset({"rows": rows}, params)
        self.assertEqual(len(res["selectedGroups"]), 2)
        # If g1 is selected, both r1 and r2 must be present (no split group)
        if "g1" in res["selectedGroups"]:
            ids = {r["id"] for r in res["rows"]}
            self.assertTrue({"r1", "r2"} <= ids)

        with self.assertRaisesRegex(ValueError, "coreset_impossible_quota"):
            t84.select_group_preserving_subset({"rows": rows}, dict(params, targetCount=10))

    def test_t85_focus_graph_relation_suppresses_nested_child_box(self) -> None:
        # Box 0: parent listRow [500, 200, 800, 60] scoring 0.91
        # Box 1: child label strictly inside Box 0 [300, 200, 200, 36] also scoring 0.89
        # Box 2: unfocused peer row [500, 300, 800, 60] scoring 0.04
        boxes = torch.tensor([
            [500.0, 200.0, 800.0, 60.0],
            [300.0, 200.0, 200.0, 36.0],
            [500.0, 300.0, 800.0, 60.0],
        ])
        scores = torch.tensor([0.91, 0.89, 0.04])
        rel = t85.compute_pairwise_box_relations(boxes)
        # Box 1 is 100% contained inside Box 0 -> IoA_contain[1, 0] == 1.0
        self.assertAlmostEqual(float(rel[1, 0, 5].item()), 1.0, places=5)

        kept, adj = t85.suppress_nested_child_candidates(boxes, scores, ioa_threshold=0.80)
        self.assertEqual(kept, [0, 2])
        above = [i for i, v in enumerate(adj.tolist()) if v >= 0.85]
        self.assertEqual(above, [0])

    def test_t86_fisher_model_soup_preserves_high_precision_coordinates(self) -> None:
        # Model 0 is highly certain on param 0 (Fisher=1000) and uncertain on param 1 (Fisher=0.001)
        # Model 1 is uncertain on param 0 (Fisher=0.001) and highly certain on param 1 (Fisher=1000)
        sd0 = {"w": torch.tensor([2.0, -5.0])}
        sd1 = {"w": torch.tensor([-9.0, 4.0])}
        f0 = {"w": torch.tensor([1000.0, 0.001])}
        f1 = {"w": torch.tensor([0.001, 1000.0])}

        merged = t86.merge_checkpoints_fisher([sd0, sd1], [f0, f1], [1.0, 1.0], mode="fisher-soup-bn")
        self.assertAlmostEqual(float(merged["w"][0].item()), 2.0, places=2)
        self.assertAlmostEqual(float(merged["w"][1].item()), 4.0, places=2)


if __name__ == "__main__":
    unittest.main()
