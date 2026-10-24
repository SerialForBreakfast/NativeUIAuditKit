# TTR SDK: requirements for training data

Date: 2026-10-22. Owner: Maximum-mini-NUIAK.

## Status and boundary

The supplied SDK document is an implementation plan, not a delivered capability inventory.
This review proposes additions to that plan. It does not authorize TTR source changes.
Maximum-mini-TTR runs approved campaigns. Maximum-mini-NUIAK owns dataset intake and model decisions.
Standard remains unchanged. HCF remains optional. SDK labels remain separate from model predictions.

## Reuse the planned features

The plan already includes actual focus, preferred focus, stable identities, content revisions, hierarchy, selection, visibility, geometry, and clipping.
It also includes lifecycle events, transport gaps, snapshot coverage, and instrumentation overhead tests.
Do not request those features again as new work.

NUIAK can use these observations to produce control boxes, paired focus labels, state tags, and grouped datasets.
Preferred focus describes intent. Only observed focus supplies the focus label.
Hierarchy helps identify containers and children. It does not establish complete detection annotations by itself.
The SDK must not supply inference inputs during screenshot-only qualification. Keep labels available to the evaluator only.

## Source verification — October 24, 2026

SDK502 finds explicit focus states in committed local TTR source `cf17ed0e`.
`sdk packet` exports screenshot-bound observations with `focusKnown` and optional `focusID`.
The NUIAK review-only consumer passes software tests. Existing native packets are requested for independent qualification.
Do not request a duplicate focus-state implementation before testing this interface.
Per-class annotation completeness and dataset ancestry remain separate requirements.
See [source contract and remaining dependency](SDKPacket502.md).

## Proposed additions, in priority order

| Priority | Requirement | Acceptance check | Work enabled |
|---|---|---|---|
| P1 | Bind each screenshot to a snapshot interval, layout revision, content revision, run, and control identities. Report timing uncertainty. | Deliberately change layout during capture. Reject the mismatched annotation or mark it unavailable. | Reliable moving-background and before/after comparisons. |
| P1 | Export explicit focus states: known control, observed no focus, and unavailable observation. | Test nil focus, disconnected telemetry, and missing registration. They produce distinct outcomes. | No-focus training without treating missing telemetry as a negative label. |
| P1 | Export per-frame annotation coverage and exclusions by class and region. | An unregistered visible control makes the affected coverage incomplete. It does not become background truth. | Complete detector labels and safe partial-label exclusions. |
| P1 | Add typed condition tags with value, source, observation time, and evidence reference. Separate requested conditions from observed conditions. | Selected-but-unfocused requires observed selection and observed focus elsewhere. Missing evidence produces unknown. | Difficult-negative slices and targeted data generation. |
| P1 | Publish a versioned dataset bundle with pixel hashes, geometry units, taxonomy mappings, group ancestry, and expected/accepted/rejected counts. | Duplicate delivery does not duplicate membership. Changed bytes and unsupported schemas fail with named reasons. | Automatic ingestion from short campaign requests. |
| P2 | Export visible geometry separately from layout geometry. Include occlusion and clipping evidence when available. | Cover partial clipping, overlays, focused scaling, recycled cells, and transformed controls. | Localization diagnosis without inconsistent box definitions. |
| P2 | Preserve content provenance, usage permissions, and redaction status in the export. | Excluded or unknown-rights assets cannot enter an approved training manifest silently. | Safe use of mock content and third-party app corpora. |
| P2 | Add optional intervention records for controlled twins. Name the changed factor and unchanged recipe/content identities. | A content-only change preserves the observed focus identity. Unexpected changes invalidate the pair. | Motion, focus, selection, and appearance separation. |

These additions extend existing SDK concepts. They do not require a new transport or navigation engine.
The first useful delivery is a local file export from the planned independent sample. Streaming can follow later.

## Condition labels that remain missing

The current retained review does not identify decorative borders, bright artwork, or selected-but-unfocused controls with verified condition evidence.
Recipe names and requested visual presets are not observed labels.
For decorative borders, retain the app-supplied semantic tag and its rendered region separately from observed focus.
For bright artwork, retain the content identity and a defined pixel measurement instead of an unqualified brightness label.
For selected-but-unfocused, retain the native selected state and the frame-bound actual focus state.
Maximum-mini-NUIAK can derive the final condition only when the required evidence is present.

## Minimal producer acceptance batch

1. Export one list and one grid with duplicate labels and recycled cells.
2. Include a focus move, a no-op, content motion without focus movement, and observed no focus.
3. Include selected-but-unfocused, decorative-border, and bright-artwork controls with explicit evidence.
4. Include one missing annotation and one stale snapshot as deliberate failures.
5. Ingest both configurations through the same NUIAK adapter without another script.
6. Preserve ancestry across pairs, repeated frames, templates, content revisions, and related seeds.
7. Compare SDK-enabled and SDK-disabled behavior before claiming independent app qualification.

This batch is a proposed SDK acceptance test. It is not additional capture approval.
Keep current session-reuse captures separate. Their approval covers four existing transition campaigns only.
