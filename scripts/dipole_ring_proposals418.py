"""T71 adapter: Concentric Signed Moat-Ring Dipole Filter for theme-invariant HCF ring proposals."""
from __future__ import annotations

import math
import numpy as np
import research_queue as q
from template_adapters395 import document, resolve_inputs

OUT = None
VARIANTS = ("inner-moat-v1", "dipole-ring-moat-v1", "dipole-adaptive-quantile-v1")


def parameters(values: dict) -> dict:
    q.require(
        isinstance(values, dict)
        and set(values) == {"kernelVariant", "dipoleZMin", "moatContrastMin"},
        "dipole_parameters",
    )
    variant = values["kernelVariant"]
    z_min = values["dipoleZMin"]
    moat_min = values["moatContrastMin"]
    q.require(variant in VARIANTS, "dipole_variant_unknown")
    q.require(
        isinstance(z_min, (int, float)) and not isinstance(z_min, bool) and math.isfinite(z_min) and 0.5 <= z_min <= 10.0,
        "dipole_z_min_range",
    )
    q.require(
        isinstance(moat_min, (int, float)) and not isinstance(moat_min, bool) and math.isfinite(moat_min) and 5.0 <= moat_min <= 200.0,
        "dipole_moat_contrast_range",
    )
    return dict(kernelVariant=variant, dipoleZMin=float(z_min), moatContrastMin=float(moat_min))


def score_dipole_ring_moat_profile(
    bg_luma: np.ndarray,
    ring_luma: np.ndarray,
    moat_luma: np.ndarray,
    kernel_variant: str = "dipole-ring-moat-v1",
    dipole_z_min: float = 2.0,
    moat_contrast_min: float = 35.0,
) -> dict[str, object]:
    """Evaluates a 4-side concentric (background, outer-ring, inner-moat) luminance profile."""
    q.require(
        bg_luma.shape == ring_luma.shape == moat_luma.shape and bg_luma.size >= 4,
        "dipole_profile_shape",
    )
    q.require(kernel_variant in VARIANTS, "dipole_variant_unknown")

    if kernel_variant == "inner-moat-v1":
        # Legacy fixed-160 brightness gate: fails when background is light (>= 160)
        bg_dark_enough = bool(np.mean(bg_luma) < 160.0)
        ring_bright = bool(np.mean(ring_luma) >= 180.0)
        moat_dark = bool(np.mean(ring_luma - moat_luma) >= moat_contrast_min)
        passed = bg_dark_enough and ring_bright and moat_dark
        return {
            "passed": passed,
            "dipoleZ": float(np.mean(ring_luma - bg_luma)),
            "moatContrast": float(np.mean(ring_luma - moat_luma)),
            "sideSupport": float(np.mean((ring_luma >= 180.0) & (bg_luma < 160.0))),
        }

    # Signed Moat-Ring Dipole Filter:
    # 1. Outer ring must be near-white specular highlight (luma >= 235)
    # 2. Inner moat must be dark relative to the outer ring (ring - moat >= moat_contrast_min) and darker than background
    # 3. Signed dipole energy combines (ring - moat) with positive (ring - bg) normalized by local variation
    ring_minus_moat = ring_luma - moat_luma
    ring_minus_bg = np.maximum(ring_luma - bg_luma, 0.0)
    bg_minus_moat = np.maximum(bg_luma - moat_luma, 0.0)

    noise_floor = max(float(np.std(bg_luma)), 8.0)
    dipole_energy = 0.65 * ring_minus_moat + 0.35 * np.maximum(ring_minus_bg, bg_minus_moat)
    dipole_z = float(np.mean(dipole_energy) / noise_floor)
    moat_contrast = float(np.mean(ring_minus_moat))

    per_side_valid = (ring_luma >= 235.0) & (ring_minus_moat >= moat_contrast_min) & (moat_luma <= 90.0)
    quantile = 0.60 if kernel_variant == "dipole-adaptive-quantile-v1" else 0.75
    side_support = float(np.mean(per_side_valid))
    passed = bool(dipole_z >= dipole_z_min and moat_contrast >= moat_contrast_min and side_support >= quantile)
    return {
        "passed": passed,
        "dipoleZ": round(dipole_z, 4),
        "moatContrast": round(moat_contrast, 4),
        "sideSupport": round(side_support, 4),
    }


def evaluate_manifest(manifest: dict, params: dict) -> dict:
    rows = manifest.get("rows", [])
    q.require(isinstance(rows, list) and len(rows) > 0, "dipole_manifest_empty")
    results = []
    for row in rows:
        bg = np.asarray(row["bgLuma"], dtype=np.float64)
        ring = np.asarray(row["ringLuma"], dtype=np.float64)
        moat = np.asarray(row["moatLuma"], dtype=np.float64)
        score = score_dipole_ring_moat_profile(
            bg,
            ring,
            moat,
            kernel_variant=params["kernelVariant"],
            dipole_z_min=params["dipoleZMin"],
            moat_contrast_min=params["moatContrastMin"],
        )
        profile = row.get("profile", "hcf")
        no_focus = bool(row.get("noFocus", False))
        expected_proposal = (profile == "hcf") and (not no_focus)
        results.append({
            "id": row["id"],
            "theme": row.get("theme", "dark"),
            "profile": profile,
            "noFocus": no_focus,
            "proposed": score["passed"],
            "expectedProposal": expected_proposal,
            "dipoleZ": score["dipoleZ"],
            "moatContrast": score["moatContrast"],
            "sideSupport": score["sideSupport"],
        })

    light_hcf = [r for r in results if r["profile"] == "hcf" and not r["noFocus"] and r["theme"] == "light"]
    dark_hcf = [r for r in results if r["profile"] == "hcf" and not r["noFocus"] and r["theme"] == "dark"]
    false_alarms = [r["id"] for r in results if not r["expectedProposal"] and r["proposed"]]
    return {
        "version": "dipole-ring-proposals-v1",
        "parameters": params,
        "rows": results,
        "lightHcfRecalled": sum(r["proposed"] for r in light_hcf),
        "lightHcfTotal": len(light_hcf),
        "darkHcfRecalled": sum(r["proposed"] for r in dark_hcf),
        "darkHcfTotal": len(dark_hcf),
        "falseAlarmIds": false_alarms,
        "modelAccepted": False,
    }


def run() -> None:
    cfg = q.load(OUT.parents[2] / "spec.json")["template"]
    params = parameters(cfg["parameters"])
    refs = resolve_inputs(cfg, OUT)
    manifest = document(refs["manifest"])
    result = evaluate_manifest(manifest, params)
    result["inputs"] = refs
    q.save(OUT / "benchmark_summary.json", result)
    q.save(
        OUT / "artifact-receipt.json",
        {
            "version": "research-artifact-v1",
            "outputs": [{"path": "benchmark_summary.json", "sha256": q.digest(OUT / "benchmark_summary.json")}],
        },
    )
