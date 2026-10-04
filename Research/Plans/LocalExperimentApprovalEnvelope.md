# Approved: local experiment tranches, not individual launches

October2 amendment: maintainer explicitly removed time constraints until further
notice and requested continued training. Approved local training experiments may
record `wallTimeLimit: null`; fixed epoch/hypothesis scope and2GiB output limits
remain. This supersedes the five/thirty-minute defaults below, not the other
permissions or a requirement to keep long runs observable and finite in work units.

October 1, 2026. Adopted by the maintainer: “I approve the whole experiment
tranches. Do the next steps.” This governs assigned local experiment tranches,
not unattended work or an unlimited experiment loop. FDR023 retains its original
single-run authorization.

## Why change

The current workflow asks again when an implementation tranche reaches model
execution, even for a short local head fit on already-admitted cached data. This
protects against unbounded retries but creates unnecessary human coordination.
The safety boundary should be the agreed experiment tranche and its budget, not
each command or machine-generated approval file.

## Default envelope

When the maintainer assigns a local model-experiment tranche that includes training,
authorize up to three explicitly motivated comparisons, at most five minutes of
training each and thirty minutes total wall time, with at most 2 GiB new outputs.
Use existing local dependencies, admitted corpus and specified development/retention
sets. State the hypothesis and intended differences before execution. Do not turn
the allowance into an automatic parameter sweep or spend unused runs without reason.

A recoverable launch-context failure before any updates does not need another
scientific-experiment approval: preserve evidence, verify zero updates, obtain any
required platform permission and recover within the existing budget. An interrupted
or ambiguous partially trained run must not be silently treated as never started.

The agent handles logging, pins, per-run authorization records derived from the
tranche approval, preflight, execution, evaluation and handoff without repeated
human confirmation. A failed result leads to diagnosis; a subsequent run must test
a documented correction or hypothesis within the assigned scope and remaining budget.
Approval is not needed for routine offline tests, metadata preparation or retained
prediction analysis already within the assignment.

Ask again only for scope/budget expansion, paid compute, new downloads, new encoding
or backbone training not included in the tranche, unadmitted data, changed split or
selection policy, protected-test access, device operations, external uploads,
destructive cleanup, export, release or model promotion. Existing restrictions
remain unchanged unless their specific scope is explicitly granted.

## Adoption

AGENTS.md and the worker workflow now recognize tranche-derived authorization.
Run-approval generators must distinguish explicit single-run approval from
an in-budget tranche-derived authorization; retain exact machine-bound protocol
checks. Do not simply remove the approval check or claim old approvals apply to
new protocols. Historical “separate assignment/approval” wording is satisfied by
an explicitly assigned tranche containing model execution within this envelope.
# Standing approval update — October 3, 2026

Maintainer grants standing local training approval, citing available USB storage.
This supersedes repeated per-run approval requirements, not experiment design,
logging, data eligibility, output isolation or separate capture/export/promotion
authority. PREP103's fixed change/ranker comparisons may proceed after their data
admission prerequisites are satisfied; the pending exact40 CALIBRATION102 role
change is not implied by general training permission. Preserve old68/5roles,
existing122approved derived negatives and all
final-holdout exclusions. Record actual per-run authority in machine protocols.
Future unrelated role changes remain explicit decisions; training approval is not
permission to consume final evaluation as training or to accept uncertain labels.
