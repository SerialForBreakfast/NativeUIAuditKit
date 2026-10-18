"""T72 adapter: Failure-Guided Counterfactual Minimal-Pair Twin Synthesis."""
from __future__ import annotations

import copy
import research_queue as q
from template_adapters395 import document, resolve_inputs

OUT = None
FAMILIES = ("wide-toggle-confuser", "selected-tab-unfocused", "decorative-static-border")


def parameters(values: dict) -> dict:
    q.require(
        isinstance(values, dict)
        and set(values) == {"twinFamily", "pairCount", "seed"},
        "counterfactual_parameters",
    )
    family = values["twinFamily"]
    count = values["pairCount"]
    seed = values["seed"]
    q.require(family in FAMILIES, "counterfactual_family_unknown")
    q.require(isinstance(count, int) and not isinstance(count, bool) and 1 <= count <= 500, "counterfactual_pair_count")
    q.require(isinstance(seed, int) and not isinstance(seed, bool) and seed > 0, "counterfactual_seed")
    return dict(twinFamily=family, pairCount=int(count), seed=int(seed))


def synthesize_counterfactual_twins(failure_report: dict, params: dict) -> dict:
    """Compiles minimal-pair counterfactual twin recipes sharing identical groupId, layout seed, and geometry."""
    q.require(
        failure_report.get("role") in ("training", "development") and failure_report.get("role") != "audit",
        "counterfactual_audit_forbidden",
    )
    family = params["twinFamily"]
    pair_count = params["pairCount"]
    base_seed = params["seed"]
    pairs = []

    for idx in range(pair_count):
        layout_seed = base_seed + idx * 17
        group_id = f"cf-{family}-seed-{layout_seed}"
        base_scene = {
            "groupId": group_id,
            "layoutSeed": layout_seed,
            "role": "training",
            "trainingEligible": True,
            "theme": "dark" if idx % 2 == 0 else "light",
            "targetBox": [120, 240, 680, 64],
            "backgroundSeed": layout_seed + 3,
        }
        twin_a = copy.deepcopy(base_scene)
        twin_b = copy.deepcopy(base_scene)
        twin_a["twinId"] = f"{group_id}-pos"
        twin_b["twinId"] = f"{group_id}-cf"

        if family == "wide-toggle-confuser":
            twin_a.update(elementClass="toggle", rightAccessory="uiswitch", focused=False)
            twin_b.update(elementClass="listRow", rightAccessory="chevron-or-picker", focused=False)
            causal_var = "rightAccessory"
        elif family == "selected-tab-unfocused":
            twin_a.update(elementClass="tabItem", selectedTab=0, focusedTarget="tab-0", targetFocused=True)
            twin_b.update(elementClass="tabItem", selectedTab=0, focusedTarget="content-card-0", targetFocused=False)
            causal_var = "focusedTarget"
        else:
            twin_a.update(elementClass="collectionItem", staticBorderPt=0, hcfFocusRing=True, targetFocused=True)
            twin_b.update(elementClass="collectionItem", staticBorderPt=4, hcfFocusRing=False, targetFocused=False)
            causal_var = "hcfFocusRing_vs_staticBorderPt"

        pairs.append({
            "pairId": f"pair-{idx:04d}",
            "groupId": group_id,
            "causalVariable": causal_var,
            "positive": twin_a,
            "counterfactual": twin_b,
        })

    verify_twin_invariants(pairs)
    return {
        "version": "counterfactual-twin-synthesis-v1",
        "parameters": params,
        "pairCount": len(pairs),
        "pairs": pairs,
        "modelAccepted": False,
    }


def verify_twin_invariants(pairs: list[dict]) -> None:
    """Verifies that every twin pair shares identical groupId, layoutSeed, role, theme, and targetBox."""
    q.require(isinstance(pairs, list) and len(pairs) > 0, "counterfactual_empty_pairs")
    for pair in pairs:
        pos = pair["positive"]
        cf = pair["counterfactual"]
        for key in ("groupId", "layoutSeed", "role", "theme", "targetBox", "backgroundSeed"):
            q.require(pos.get(key) == cf.get(key), f"counterfactual_invariant_broken:{key}")
        q.require(pos != cf, "counterfactual_identical_twins")


def run() -> None:
    cfg = q.load(OUT.parents[2] / "spec.json")["template"]
    params = parameters(cfg["parameters"])
    refs = resolve_inputs(cfg, OUT)
    report = document(refs["failureReport"])
    result = synthesize_counterfactual_twins(report, params)
    result["inputs"] = refs
    q.save(OUT / "benchmark_summary.json", result)
    q.save(
        OUT / "artifact-receipt.json",
        {
            "version": "research-artifact-v1",
            "outputs": [{"path": "benchmark_summary.json", "sha256": q.digest(OUT / "benchmark_summary.json")}],
        },
    )
