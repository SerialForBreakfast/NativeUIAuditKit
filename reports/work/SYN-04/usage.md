# Corpus planner

Run from the repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 .venv-yolo/bin/python scripts/focus_corpus_planner.py \
  --inventory reports/work/FOCUS-CORPUS-03/delivery/inventory.json \
  --output reports/work/SYN-04/artifacts/new-plan
```

This rechecks existing file/pixel integrity, roles and coverage through the inventory
implementation, then writes `plan.json`, `collection.md` and an empty
`lineage-catalog-template.json`. Outputs must be new project-local paths. No model,
producer connection, capture, training, feature encoding or crop generation runs.

Default first-wave request: 480 matched pairs across 60 variation/theme/role slots.
`--pairs-per-slot 8` changes collection targets only. A slot can have several actual
recipes; it does not assert that one scene supports eight controls. The six existing
production scene minima still total 6,000 pairs. This wave is not production readiness.

## Binding actual recipe proposals

Use `--lineage-catalog PATH` once source-reviewed recipe files exist locally. The
catalog is **NUIAK-local planning metadata, not TTR's wire schema**. Translate actual
producer ancestry into this format after review; do not ask TTR to implement a
second transport or make up source groups just to fill it.

Top-level fields:

- `version`: `focus-corpus-lineage-catalog-v1`.
- `baselineProtocol`: exact `{path, sha256}` copied from the generated template.
- `recipes`: explicit entries; an empty list correctly leaves all slots unbound.

Each recipe entry contains:

| Field | Meaning |
| --- | --- |
| `id` | Unique stable proposal identity |
| `slotID` | Exact requested slot from plan.json |
| `intendedRole` | training or validation, matching the slot |
| `priorUse` | new, training, development, retention, protected, held, or unknown |
| `recipe` | Exact local JSON `{path, sha256}`; bytes verified, unqualified producer schema not interpreted |
| `relationshipsKnown` | Explicit boolean; false remains blocked |
| `sourceGroups`, `layoutGroups` | Nonempty reviewed ancestry keys; neither seed nor color is sufficient |
| `componentGroups`, `assetGroups` | Optional template-specific/asset reuse keys, not generic framework names |
| `nearDuplicateGroups` | Optional reviewed similarity relationships; no automatic perceptual search is claimed |
| `relatedSampleIDs` | Optional exact retained sample IDs with known relationships |
| `relatedRecipeIDs` | Optional other proposal IDs; transitive links preserved |
| `contentSHA256` | Optional exact byte/decoded-pixel hashes for overlap checking |
| `review` | Hash-bound local evidence reference supporting relationship declarations |

All list-valued fields contain unique nonempty strings; missing optional lists are
empty. Source keys match retained sourceID/sourceSessionID/relatedGroup values;
layout keys match known intrinsicGroup/family values. Use exact relatedSampleIDs
where the producer uses a different namespace. Unknown comparisons stay unknown.

Training and validation requests share coverage goals, **not source implementations**.
Using the same template under different seeds or new group names is not independent
validation. Catalog checks verify declarations and known conflicts, not their factual
truth; external source review and eventual admission are still necessary.

Every recipe receives a disposition. Connected unknown/invalid/conflicting proposals
are blocked together. Known identical recipe bytes/content cannot cross roles; even
a corrupt recipe must not remove its known source-group links from the graph.
Existing development examples cannot become training additions. Held/protected and
retention use cannot be repurposed. No candidate is training-eligible from this plan.

`proposed-source-separated` means only that supplied reviewed declarations contain
no detected conflict. `sourceIndependenceEstablished` remains false. Source membership
is not changed and no approval file is created. New pixel/crop/native quality and
physical-transfer checks remain downstream requirements.

After actual delivery, reuse the existing importer/crop validator and INTAKE-AUDIT-01
random-plus-exception review. Do not reannotate retained examples merely to fill slots.
