# PER-01 evidence inventory and benchmark contract

## Delivered software

- `Research/schemas/perception-benchmark.v1.json` and
  `Research/schemas/perception-benchmark-v1.md` define the separate, versioned benchmark
  manifest and reviewed-label rubric.
- `scripts/perception_benchmark.py` validates identity, pixel boxes, reviewed-label origin,
  chevron/dialog/focus relations, journey and content leakage, and optional explicit-byte
  verification. It does not scan for replacement files or fabricate labels.

## Bounded inventory — 2026-09-21

Read-only inventory was limited to `dataset/tvos_captures/` and the named Office/simulator
reports. It found 44 PNGs, 40 JSON files, and 29 schema-v1 source sidecars whose declared
capture source is `realAppleTVTVTestRig`. Eight JSON sidecars contain an `isFocused: true`
field. Twenty-nine sidecars have empty `elements`, and result files are separate model output.

This is not an eligible benchmark: no completed P4-L bundle, completed-bundle receipt/index,
reviewed chevron-to-row labels, reviewed dialog semantics, or capture-correlated callback/frame
evidence is present. The known Office smoke remains blocked before capture by the producer's
container staging access. The inventory is therefore an exact lead list, not training truth.

## Verification

` .venv-yolo/bin/python scripts/test_perception_benchmark.py` — 5 passed.

## Outcomes

| Outcome | Status |
|---|---|
| Software verified | Passed (offline test-only coverage) |
| Data eligible | Not assessed; reviewed physical benchmark truth is absent |
| Integration qualified | Not assessed; no completed producer bundle |
| Model gate passed | Not applicable; no inference or training |

Coordination publication: not applicable. This is local offline inventory; no new peer
request or TVTestRig operation was authorized.
