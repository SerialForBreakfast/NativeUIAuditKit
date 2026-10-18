# EXP418-18 — Submodular Facility-Location and BADGE Coreset Selection (`SubmodCoreset`, `B405-246` / Template `T84`)

Owner: `Maximum-mini-NUIAK`. Date: 2026-10-17. Track: `tvOS generation` (`TGEN`) and `iOS generation` (`IGEN`). Priority: `P0`.
Parent task: `PAPER417-SUBSET` / `B405-181` / `B405-184` / `B405-197`. Template: `T84` (`submodular_coreset_subset418.run`).

---

## 1. Goals and SOTA Foundation

### Observed Bottleneck
In [Tasks.md](file:///Volumes/training-drive/data/NUIAK/project/NativeUIAuditKit/Tasks.md) (`PAPER417-SUBSET`, `B405-181`, `B405-184`, `B405-197`) and [ResearchSources417.md](file:///Volumes/training-drive/data/NUIAK/project/NativeUIAuditKit/Research/Plans/ResearchSources417.md) (`OR08 BADGE`, `PM04 GRAD-MATCH`, `PM09`, `HF06`), `Maximum-mini-NUIAK` identified a P0 preparation requirement:
- We need a deterministic, reusable subset producer (`PAPER417-SUBSET`) that selects an exact quota of training groups (`7,200` samples total, `3,600` per label) while keeping all derivatives, reversals, and profile counterparts of a scene inside the same `groupId` (`HN05`).
- We must compare four principled selection strategies at **identical training exposure** (`B405-181`, `B405-197`):
  1. Uniform random group sampling (`random`).
  2. Family-balanced quota sampling (`balanced`).
  3. High-scene-diversity / low-views-per-scene vs low-scene-diversity / high-views-per-scene (`B405-197`).
  4. **Uncertainty + Diversity Coreset Selection (`BADGE` + Submodular Facility Location)** (`B405-181`, `B405-184`).

Naive uncertainty sampling picks near-duplicate crops from the same ambiguous scene (`RD04`), while full-network gradient matching (`PM04`) has high extraction overhead (`PM09`).

### SOTA Method: Last-Layer BADGE Gradient Embeddings + Lazier-Than-Lazy Greedy Submodular Maximization
This experiment combines two SOTA active-subset algorithms with near-zero compute overhead:
1. **Last-Layer Hallucinated Gradient Embedding (`BADGE`)** (Ash et al., *Deep Batch Active Learning by Diverse, Uncertain Gradient Lower Bounds*, ICLR 2020):
   For any sample $i$ with penultimate `1280-d` feature vector $\phi(x_i) \in \mathbb{R}^{1280}$, predicted probability $p_i = \sigma(z_i)$, and true label $y_i \in \{0, 1\}$, the exact gradient of the binary cross-entropy loss with respect to the final linear weights $w$ is simply:

$$g_i = \nabla_w \mathcal{L}_{\text{BCE}}(x_i, y_i) = (p_i - y_i) \cdot \phi(x_i) \in \mathbb{R}^{1280}$$

   Notice that:
   - The **norm** $\|g_i\|_2 = |p_i - y_i| \cdot \|\phi(x_i)\|_2$ measures **model uncertainty / error magnitude**.
   - The **direction** $g_i / \|g_i\|_2$ encodes **visual and geometric feature identity**.
   - Computing $g_i$ requires **zero backward passes** and reuses cached penultimate features in `< 0.5 s` (`PM09`)!
2. **Group-Constrained Monotone Submodular Facility Location + Diversity Maximization** (Mirzasoleiman et al., *Lazier Than Lazy Greedy*, AAAI 2015):
   Aggregate sample embeddings to the scene-group level $\bar{g}_G$ and maximize the submodular Facility-Location objective over candidate group subsets $\mathcal{S} \subseteq \mathcal{U}$ subject to exact family and cardinality quotas $K$:

$$F(\mathcal{S}) = \sum_{u \in \mathcal{U}} \max_{s \in \mathcal{S}} \text{sim}(\bar{g}_u, \bar{g}_s) + \lambda_{\text{unc}} \sum_{s \in \mathcal{S}} \log\bigl(1 + \|\bar{g}_s\|_2^2\bigr)$$

   Because $F(\mathcal{S})$ is monotone submodular, the **Lazy Greedy algorithm with priority-queue marginal gain caching** finds a $(1 - 1/e)$-optimal subset of `7,200` samples in **under 1.5 seconds on CPU**!

---

## 2. Controlled Test Design

- **Pinned Dataset**: Full training pool of synthetic and native training groups (`role == "training"` strictly verified). All 4 arms produce exactly `7,200` samples (`3,600` focused, `3,600` unfocused) at fixed seed `371`.
- **Arms**:
  1. `random-groups` (Control): Uniform random selection of whole scene groups.
  2. `family-balanced`: Stratified sampling across control families (`B405-181`).
  3. `scene-breadth-vs-depth`: Maximum unique scene groups (1 view per group) vs repeated views per group at equal `7,200` sample count (`B405-197`).
  4. `submod-badge-coreset`: Submodular Facility-Location + BADGE gradient coreset selection (`B405-181`, `B405-184`).
- **Decision Rules**:
  - **Supported**: `submod-badge-coreset` (or `scene-breadth`) achieves higher native control and hard-case selection accuracy on the 8 `T57` development sets at the exact same `7,200`-sample / `30`-epoch training budget, with selection overhead `< 5 s`.
  - **Contradicted**: Neither `submod-badge-coreset` nor `scene-breadth` beats `family-balanced` at equal exposure.
  - **Inconclusive**: Verify that group-split integrity (`HN05`) and exact label quotas pass before running the `T06` fits.
  - **Regression Gate**: Reject any subset that splits a `groupId` across roles, admits non-training data, or violates impossible quota checks (`PAPER417-SUBSET`).

---

## 3. What This Tells `Maximum-mini-TTR`, `Sillycon-TTR`, and `Maximum-mini-NUIAK`

1. **For `Maximum-mini-TTR` (`B405-197`)**: Answers whether future Fixture capture tranches should render **more unique layout seeds (1 focus state per seed)** or **complete focus-traversal sweeps (8–12 focus states per seed)**.
2. **For `Maximum-mini-NUIAK` (`PAPER417-SUBSET`, `B405-181`, `B405-184`)**: Fulfils the P0 `PAPER417-SUBSET` task and unblocks `B405-181`, `B405-184`, `B405-189`, `B405-190`, and `B405-197` with a single verified producer.

---

## 4. New Template Contract (`T84`)

Register `T84` in [`scripts/hcf_templates395.py`](file:///Volumes/training-drive/data/NUIAK/project/NativeUIAuditKit/scripts/hcf_templates395.py) at an idle runner boundary:

```python
"T84": (
    {"poolManifest", "targetCount", "seed"},
    {"selectionStrategy", "familyQuotas", "maxViewsPerGroup", "uncertaintyWeight"},
    "submodular_coreset_subset418.run",
    "artifact",
    "diagnostic",
),
```

---

## 5. Implementation Plan and Reference Code

### Step 1 — Lazy Greedy Submodular + BADGE Coreset Selector (`scripts/submodular_coreset_subset418.py`)

```python
"""T84 adapter: Submodular Facility-Location and BADGE Coreset Selector (PAPER417-SUBSET)."""
from __future__ import annotations

import heapq
import numpy as np


def compute_badge_group_embeddings(
    features: np.ndarray,
    probs: np.ndarray,
    labels: np.ndarray,
    group_ids: list[str],
) -> tuple[list[str], np.ndarray, np.ndarray]:
    """Computes L2-normalized mean BADGE gradient direction and uncertainty norm per groupId."""
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
) -> list[int]:
    """Selects k_groups maximizing submodular Facility Location + uncertainty bonus via Lazy Greedy."""
    n = sim_matrix.shape[0]
    assert 1 <= k_groups <= n
    current_max_sim = np.zeros(n, dtype=np.float32)
    selected: list[int] = []
    # Max-heap stores (-marginal_gain, last_updated_step, candidate_idx)
    heap: list[tuple[float, int, int]] = []
    for idx in range(n):
        gain = float(np.sum(np.maximum(sim_matrix[:, idx], 0.0)) + uncertainty_weight * uncertainty_bonus[idx])
        heapq.heappush(heap, (-gain, 0, idx))

    for step in range(k_groups):
        while True:
            neg_gain, updated_at, cand = heapq.heappop(heap)
            if updated_at == step:
                selected.append(cand)
                current_max_sim = np.maximum(current_max_sim, sim_matrix[:, cand])
                break
            recomputed = float(
                np.sum(np.maximum(sim_matrix[:, cand] - current_max_sim, 0.0))
                + uncertainty_weight * uncertainty_bonus[cand]
            )
            heapq.heappush(heap, (-recomputed, step, cand))
    return selected
```

### Step 2 — Verification
- Create `scripts/test_submodular_coreset_subset418.py` to verify that `T84` preserves whole-group integrity (`0` split `groupId`s), rejects impossible quotas with a descriptive error (`PAPER417-SUBSET` acceptance rule), and beats uniform random selection in facility-location coverage on synthetic clusters.
