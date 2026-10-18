"""Unit tests for Tranche 1 novel templates T67 through T76 (EXP418-01 through EXP418-10)."""
from __future__ import annotations

import unittest
import numpy as np
import torch

import nwd_detector_train418 as t67
import fda_transfer418 as t68
import set_contrastive_focus418 as t69
import coord_ring_crop418 as t70
import dipole_ring_proposals418 as t71
import counterfactual_synthesis418 as t72
import sahi_wbf_inference418 as t73
import distilled_coreml_compress418 as t74
import kinematic_transition418 as t75
import confident_label_auditor418 as t76


class Tranche1TemplateTests(unittest.TestCase):
    def test_t67_nwd_smooth_gradients_on_tiny_boxes_and_param_bounds(self) -> None:
        # Tiny 8x8 px pageControl shifted by 9 px has 0.0 IoU but smooth >0.45 NWD similarity
        pred = torch.tensor([[100.0, 100.0, 8.0, 8.0]], requires_grad=True)
        target = torch.tensor([[109.0, 100.0, 8.0, 8.0]])
        res = t67.blended_nwd_ciou_loss(pred, target, image_size=640.0, nwd_weight=0.5, nwd_constant=12.8, small_area_max=0.01)
        self.assertEqual(float(res["iou"].item()), 0.0)
        self.assertGreater(float(res["nwd"].item()), 0.45)
        self.assertTrue(bool(res["smallMask"].item()))
        res["loss"].backward()
        self.assertIsNotNone(pred.grad)
        self.assertGreater(float(pred.grad.abs().sum().item()), 0.01)

        with self.assertRaisesRegex(ValueError, "nwd_weight_range"):
            t67.parameters({"nwdWeight": 1.5, "nwdConstant": 12.8, "smallAreaMax": 0.01, "seed": 371})

    def test_t68_fda_preserves_phase_and_transfers_luminance(self) -> None:
        rng = np.random.default_rng(371)
        src = rng.integers(10, 60, size=(64, 64, 3), dtype=np.uint8)
        sty = rng.integers(180, 240, size=(64, 64, 3), dtype=np.uint8)
        adapted, stats = t68.fda_swap_amplitude(src, sty, beta=0.05)
        self.assertEqual(adapted.shape, src.shape)
        self.assertGreater(stats["phaseCosine"], 0.99)
        self.assertGreater(float(adapted.mean()), float(src.mean()) + 20.0)

        with self.assertRaisesRegex(ValueError, "fda_beta_range"):
            t68.parameters({"beta": 0.5, "blendProb": 0.5, "seed": 371})

    def test_t69_set_contrastive_and_listmle_dustbin(self) -> None:
        emb = torch.tensor([[1.0, 0.0], [0.8, 0.6], [-0.5, 0.5], [-0.9, -0.1]], requires_grad=True)
        labels = torch.tensor([1.0, 1.0, 0.0, 0.0])
        loss_sc = t69.supervised_contrastive_loss(emb, labels, temperature=0.5)
        self.assertGreater(float(loss_sc.item()), 0.0)

        dustbin = torch.tensor(1.5, requires_grad=True)
        # Focused screen: index 1 is focused
        loss_focus = t69.screen_listmle_dustbin_loss(torch.tensor([-1.0, 3.0, 0.0]), torch.tensor([0.0, 1.0, 0.0]), dustbin)
        # No-focus screen: all labels 0 -> dustbin wins
        loss_nofocus = t69.screen_listmle_dustbin_loss(torch.tensor([-2.0, -1.5]), torch.tensor([0.0, 0.0]), dustbin)
        self.assertLess(float(loss_focus.item()), 0.3)
        self.assertLess(float(loss_nofocus.item()), 0.1)

        # Reject conflicting focus or cross-scene pairs
        with self.assertRaisesRegex(ValueError, "set_rank_cross_scene_pair"):
            t69.validate_screen_groups([{"candidates": [{"sceneId": "a", "focused": 1}, {"sceneId": "b", "focused": 0}]}])
        with self.assertRaisesRegex(ValueError, "set_rank_multiple_focused_targets"):
            t69.validate_screen_groups([{"candidates": [{"sceneId": "a", "focused": 1}, {"sceneId": "a", "focused": 1}]}])

    def test_t70_coord_ring_5ch_and_perimeter_strip(self) -> None:
        crop = np.zeros((128, 128, 3), dtype=np.uint8)
        crop[:16, :, 0] = 255  # Top border red
        tensor_5ch = t70.build_coord_5ch_crop(crop, body_width_px=1400.0, body_height_px=64.0, margin_ratio=0.16)
        self.assertEqual(tensor_5ch.shape, (128, 128, 5))
        # Center of crop is inside body (< 0), outer corner pixel center (0.5, 0.5) is near +0.97
        self.assertLess(float(tensor_5ch[64, 64, 3]), 0.0)
        self.assertGreater(float(tensor_5ch[0, 0, 3]), 0.95)
        self.assertGreater(float(tensor_5ch[0, 0, 4]), 0.9)

        strip = t70.unwarp_perimeter_strip(crop, strip_height=16, perimeter_width=128)
        self.assertEqual(strip.shape, (16, 128, 3))
        self.assertEqual(int(strip[:, :32, 0].mean()), 255)

    def test_t71_dipole_ring_recovers_light_hcf_and_rejects_standard(self) -> None:
        # B405-161 light-theme HCF profile: bg=244, ring=255, moat=17
        bg_light = np.array([242.0, 245.0, 240.0, 248.0])
        ring_light = np.array([255.0, 255.0, 255.0, 255.0])
        moat_light = np.array([17.0, 18.0, 17.0, 19.0])

        legacy = t71.score_dipole_ring_moat_profile(bg_light, ring_light, moat_light, kernel_variant="inner-moat-v1")
        self.assertFalse(legacy["passed"])

        dipole = t71.score_dipole_ring_moat_profile(bg_light, ring_light, moat_light, kernel_variant="dipole-ring-moat-v1")
        self.assertTrue(dipole["passed"])
        self.assertGreater(dipole["moatContrast"], 200.0)

        # Standard unfocused control on light background: no dark inner moat
        std_res = t71.score_dipole_ring_moat_profile(bg_light, bg_light, bg_light, kernel_variant="dipole-ring-moat-v1")
        self.assertFalse(std_res["passed"])

    def test_t72_counterfactual_twin_synthesis_and_audit_guard(self) -> None:
        params = t72.parameters({"twinFamily": "selected-tab-unfocused", "pairCount": 4, "seed": 371})
        res = t72.synthesize_counterfactual_twins({"role": "development"}, params)
        self.assertEqual(res["pairCount"], 4)
        p0 = res["pairs"][0]
        self.assertEqual(p0["positive"]["groupId"], p0["counterfactual"]["groupId"])
        self.assertTrue(p0["positive"]["targetFocused"])
        self.assertFalse(p0["counterfactual"]["targetFocused"])

        with self.assertRaisesRegex(ValueError, "counterfactual_audit_forbidden"):
            t72.synthesize_counterfactual_twins({"role": "audit"}, params)

    def test_t73_sahi_wbf_suppresses_truncated_tile_cards_and_keeps_small_controls(self) -> None:
        full_preds = [
            {"class": "collectionItem", "box": [100.0, 200.0, 500.0, 700.0], "score": 0.92},
        ]
        tile_preds = [
            # Small tabItem recovered in top-band tile
            {"class": "tabItem", "box": [300.0, 40.0, 410.0, 88.0], "score": 0.88, "tileBox": [0.0, 0.0, 1920.0, 220.0]},
            # Truncated large card filling >50% of tile (should be rejected by scale-gated-wbf)
            {"class": "sheet", "box": [100.0, 200.0, 500.0, 700.0], "score": 0.89, "tileBox": [0.0, 180.0, 640.0, 720.0]},
        ]
        fused = t73.scale_gated_wbf(full_preds, tile_preds, policy="scale-gated-wbf", iou_threshold=0.55, confidence=0.25)
        classes = {d["class"] for d in fused}
        self.assertEqual(classes, {"collectionItem", "tabItem"})

    def test_t74_distilled_coreml_compression_stays_under_5mb_and_reduces_flips(self) -> None:
        rng = np.random.default_rng(371)
        weights = rng.normal(0.0, 0.5, size=(1, 16))
        features = rng.normal(0.0, 1.0, size=(64, 16))
        teacher_logits = (features @ weights.T).squeeze(-1) + 1.7346

        naive = t74.saliency_palettize_and_margin_calibrate(weights, features, teacher_logits, mode="naive-palette6")
        distilled = t74.saliency_palettize_and_margin_calibrate(weights, features, teacher_logits, mode="margin-distilled-palette6")
        self.assertTrue(distilled["within5MBGate"])
        self.assertLessEqual(distilled["thresholdFlips"], naive["thresholdFlips"])
        self.assertLessEqual(distilled["maxProbabilityDelta"], naive["maxProbabilityDelta"] + 1e-6)

    def test_t75_kinematic_phase_scroll_and_action_cone(self) -> None:
        y, x = np.mgrid[0:64, 0:64]
        before = ((np.sin(x * 0.3) + np.cos(y * 0.3)) * 80 + 128).astype(np.float64)
        # Shift image up by 6 px (dy = -6)
        after = np.roll(before, shift=-6, axis=0)
        scroll = t75.estimate_fft_phase_scroll(before, after)
        self.assertAlmostEqual(scroll["dyScroll"], -6.0, delta=1.0)

        # Pressing Down when list scrolls up by (0, -60) while screen highlight stays at (400, 300)
        trans = t75.classify_kinematic_transition("down", (400.0, 300.0), (400.0, 300.0), (0.0, -60.0))
        self.assertEqual(trans["transitionState"], "viewport_scrolled_focus_stationary")
        self.assertTrue(trans["directionConsistent"])

        # Pressing Left when focus jumps Right -> invalid_direction_jump
        bad = t75.classify_kinematic_transition("left", (400.0, 300.0), (650.0, 300.0), (0.0, 0.0))
        self.assertEqual(bad["transitionState"], "invalid_direction_jump")
        self.assertFalse(bad["directionConsistent"])

    def test_t76_confident_label_auditor_trimodal_tiers(self) -> None:
        prim = [
            {"frameId": "f1", "class": "navigationBar", "box": [0, 0, 390, 44], "score": 0.82},
            {"frameId": "f1", "class": "textField", "box": [20, 100, 350, 140], "score": 0.45},
            {"frameId": "f1", "class": "button", "box": [300, 700, 340, 730], "score": 0.30},
        ]
        sec = [{"frameId": "f1", "class": "navigationBar", "box": [0, 1, 390, 44], "score": 0.79}]
        gt = []
        bodies = [{"frameId": "f1", "box": [0, 0, 390, 44]}]
        ocr = [{"frameId": "f1", "box": [24, 104, 200, 136]}]

        res = t76.audit_unmatched_predictions_trimodal(prim, sec, gt, bodies, ocr_boxes=ocr)
        self.assertFalse(res["autoRelabelApplied"])
        tiers = {r["class"]: r["tier"] for r in res["records"]}
        self.assertEqual(tiers["navigationBar"], "tier-a-missing-ground-truth")
        self.assertEqual(tiers["textField"], "tier-b-ambiguous-review-queue")
        self.assertEqual(tiers["button"], "tier-c-confirmed-hallucination")


if __name__ == "__main__":
    unittest.main()
