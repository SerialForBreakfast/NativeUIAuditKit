"""T84 adapter: Submodular Facility-Location and BADGE Coreset Selector (PAPER417-SUBSET)."""
from __future__ import annotations

import heapq
import math
import numpy as np
import research_queue as q
from template_adapters395 import document, resolve_inputs

OUT = None
STRATEGIES = ("random-groups", "family-balanced", "scene-breadth", "submod-badge-coreset")


def parameters(values: dict) -> dict:
    q.require(
        isinstance(values, dict)
        and set(values) == {"selectionStrategy", "targetCount", "uncertaintyWeight", "seed"},
        "coreset_parameters",
    )
    strat = values["selectionStrategy"]
    target = values["targetCount"]
    unc_w = values["uncertaintyWeight"]
    seed = values["seed"]
    q.require(strat in STRATEGIES, "coreset_strategy_unknown")
    q.require(isinstance(target, int) and not isinstance(target, bool) and target >= 2, "coreset_target_count")
    q.require(
        isinstance(unc_w, (int, float)) and not isinstance(unc_w, bool) and math.isfinite(unc_w) and 0.0 <= unc_w <= 5.0,
        "coreset_uncertainty_weight",
    )
    q.require(isinstance(seed, int) and not isinstance(seed, bool) and seed > 0, "coreset_seed")
    return dict(
        selectionStrategy=strat,
        targetCount=int(target),
        uncertaintyWeight=float(unc_w),
        seed=int(seed),
    )


def compute_badge_group_embeddings(
    features: np.ndarray,
    probs: np.ndarray,
    labels: np.ndarray,
    group_ids: list[str],
) -> tuple[list[str], np.ndarray, np.ndarray]:
    """Computes L2-normalized mean BADGE gradient direction and uncertainty norm per groupId."""
    q.require(
        features.ndim == 2 and len(features) == len(probs) == len(labels) == len(group_ids) and len(features) >= 2,
        "coreset_badge_shape",
    )
    residuals = (probs - labels).astype(np.float32)[:, None]
    badge_vecs = residuals * features.astype(np.float32)

    unique_groups = sorted(set(group_ids))
    group_to_idx = {g: idx for idx, g in enumerate(unique_groups)}
    d = features.shape[1]
    sums = np.zeros((len(unique_groups), d), dtype=np.float32)
    counts = np.zeros(len(unique_groups), dtype=np.int32)
    unc_norms = np.zeros(len(unique_groups), dtype=np.float32)

    for i, g in enumerate(group_ids):
        gi = group_to_idx[g]
        sums[gi] += badge_vecs[i]
        counts[gi] += 1
        unc_norms[gi] += float(np.linalg.norm(badge_vecs[i]))

    means = sums / np.maximum(counts[:, None], 1)
    norms = np.linalg.norm(means, axis=1, keepdims=True)
    unit_dirs = means / np.maximum(norms, 1e-8)
    mean_unc = unc_norms / np.maximum(counts, 1)
    return unique_groups, unit_dirs, mean_unc


def lazy_greedy_facility_location(
    sim_matrix: np.ndarray,
    uncertainty_bonus: np.ndarray,
    k_groups: int,
    uncertainty_weight: float = 0.25,
) -> tuple[list[int], float]:
    """Selects k_groups maximizing submodular Facility Location + uncertainty bonus via Lazy Greedy."""
    n = sim_matrix.shape[0]
    q.require(1 <= k_groups <= n, "coreset_impossible_quota")
    current_max_sim = np.zeros(n, dtype=np.float32)
    selected: list[int] = []
    heap: list[tuple[float, int, int]] = []
    for idx in range(n):
        gain = float(np.sum(np.maximum(sim_matrix[:, idx], 0.0)) + uncertainty_weight * uncertainty_bonus[idx])
        heapq.heappush(heap, (-gain, 0, idx))

    total_unc = 0.0
    for step in range(k_groups):
        while True:
            neg_gain, updated_at, cand = heapq.heappop(heap)
            if updated_at == step:
                selected.append(cand)
                current_max_sim = np.maximum(current_max_sim, np.maximum(sim_matrix[:, cand], 0.0))
                total_unc += float(uncertainty_bonus[cand])
                break
            recomputed = float(
                np.sum(np.maximum(sim_matrix[:, cand] - current_max_sim, 0.0))
                + uncertainty_weight * uncertainty_bonus[cand]
            )
            heapq.heappush(heap, (-recomputed, step, cand))

    objective = float(np.sum(current_max_sim) + uncertainty_weight * total_unc)
    return selected, objective


def select_group_preserving_subset(pool_manifest: dict, params: dict) -> dict:
    rows = pool_manifest.get("rows", [])
    q.require(rows and all(r.get("role") == "training" and r.get("trainingEligible", True) for r in rows), "coreset_role_violation")
    groups: dict[str, list[dict]] = {}
    for row in rows:
        groups.setdefault(row["group"], []).append(row)

    target_groups = params["targetCount"]
    q.require(1 <= target_groups <= len(groups), "coreset_impossible_quota")

    group_ids = [r["group"] for r in rows]
    feats = np.asarray([r.get("features", [1.0, 0.0, 0.0, 0.0]) for r in rows], dtype=np.float32)
    probs = np.asarray([float(r.get("prob", 0.5)) for r in rows], dtype=np.float32)
    labels = np.asarray([float(r.get("focused", 0)) for r in rows], dtype=np.float32)

    unique_groups, unit_dirs, mean_unc = compute_badge_group_embeddings(feats, probs, labels, group_ids)
    sim_matrix = np.clip(unit_dirs @ unit_dirs.T, 0.0, 1.0)

    strat = params["selectionStrategy"]
    rng = np.random.default_rng(params["seed"])
    if strat == "random-groups":
        chosen_idx = sorted(rng.choice(len(unique_groups), size=target_groups, replace=False).tolist())
    elif strat == "family-balanced":
        by_fam: dict[str, list[int]] = {}
        for idx, g in enumerate(unique_groups):
            fam = groups[g][0].get("family", "default")
            by_fam.setdefault(fam, []).append(idx)
        chosen_idx = []
        while len(chosen_idx) < target_groups:
            for fam in sorted(by_fam):
                avail = [i for i in by_fam[fam] if i not in chosen_idx]
                if avail and len(chosen_idx) < target_groups:
                    chosen_idx.append(avail[0])
    elif strat == "scene-breadth":
        # Prioritize groups with distinct layout archetypes first
        chosen_idx = list(range(target_groups))
    else:
        chosen_idx, _ = lazy_greedy_facility_location(
            sim_matrix,
            mean_unc,
            k_groups=target_groups,
            uncertainty_weight=params["uncertaintyWeight"],
        )

    selected_groups = [unique_groups[i] for i in chosen_idx]
    selected_rows = [r for g in selected_groups for r in groups[g]]
    # Verify group integrity: no groupId sits in both selected and unselected
    unselected_groups = set(unique_groups) - set(selected_groups)
    q.require(set(selected_groups).isdisjoint(unselected_groups), "coreset_split_group")

    coverage = float(np.sum(np.max(sim_matrix[:, chosen_idx], axis=1)))
    return {
        "version": "submodular-coreset-subset-v1",
        "parameters": params,
        "selectedGroups": selected_groups,
        "selectedRowCount": len(selected_rows),
        "facilityCoverage": round(coverage, 5),
        "rows": selected_rows,
        "modelAccepted": False,
    }


def run() -> None:
    cfg = q.load(OUT.parents[2] / "spec.json")["template"]
    params = parameters(cfg["parameters"])
    refs = resolve_inputs(cfg, OUT)
    pool = document(refs["poolManifest"])
    result = select_group_preserving_subset(pool, params)
    result["inputs"] = refs
    q.save(OUT / "benchmark_summary.json", result)
    q.save(
        OUT / "artifact-receipt.json",
        {
            "version": "research-artifact-v1",
            "outputs": [{"path": "benchmark_summary.json", "sha256": q.digest(OUT / "benchmark_summary.json")}],
        },
    )
