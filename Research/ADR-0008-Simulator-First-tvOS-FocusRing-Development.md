# ADR-0008: Simulator-first tvOS FocusRing development and hardware transfer validation

- **Status:** Accepted
- **Date:** 2026-09-21
- **Deciders:** NativeUIAuditKit maintainer and architecture
- **Applies to:** TVTestRig fixture integration, SIM-DATA-01–05, FR-SIM-BASE,
  FR-SIM-CAND, FR-SIM-TTR, P4-L, FR-B, and FR-C
- **Related:** [SimulatorDatasets.md](Plans/SimulatorDatasets.md),
  [FocusRingSimulator.md](Plans/FocusRingSimulator.md),
  [OfficeFocusRing.md](Plans/OfficeFocusRing.md),
  [ADR-0007](ADR-0007-VoiceOver-Navigation-Focus-Alignment.md), and
  [CurrentState.md](CurrentState.md)

## Context

**2026-09-22 amendment:** [ADR-0009](ADR-0009-Direct-tvOS-Simulator-Generation.md)
adds an independent direct native generator. TTR repair is no longer a prerequisite
for all tvOS data/model development. The rules below continue to govern the TTR
lane; simulator-first and later physical-transfer qualification remain in force.

The earlier sequence permitted a narrow physical Office smoke before simulator
data was qualified. That coupled helper startup, local signing, app-workspace
export, device availability, capture leases, fixture transport, NUIAK intake,
crop extraction, and model behavior in one loop. Routine producer/consumer
interface defects then appeared to require physical hardware access.

The simulator lane is not yet qualified. Current evidence records a fixture that
resolves a native sample and settles, but screenshot output fails with Cocoa 513 /
EPERM, leaving zero accepted rows. That is a producer storage defect, not a reason
to substitute Office capture. FocusRing also needs large, controlled visual data:
focused/unfocused pairs, themes, scene families, and hard negatives. Simulator
fixtures provide reproducible starting state and deliberate rendering variants.

## Decision

### D1: Simulator is the mandatory first development and training lane

The required order is:

1. Validate a matching local signed TVTestRig app/helper.
2. Repair SIM-DATA-01 and produce one bounded completed simulator fixture bundle.
3. Have NUIAK validate receipt/index, hashes, schema, frame identity, focus pairs,
   16% crop geometry, split grouping, and rejection behavior offline.
4. Complete the simulator pilot and baseline the shipped FocusRing model.
5. Freeze the scale corpus, then train/evaluate one candidate only under separate
   training/export authority.
6. Use Office only for a separately authorized later transfer comparison of an
   already-qualified simulator pipeline and model.

Physical capture must not be used to discover missing fields, output-path errors,
crop-math defects, fixture recipe incompatibility, split leakage, or ordinary model
failures. Those are simulator/consumer-contract issues.

### D2: One bounded producer–consumer compatibility loop

NUIAK owns the acceptance contract and reports one actionable failure at a time:
the required producer capability, expected completed artifact, and observed consumer
rejection. TVTestRig owns implementation and its local self-test. The handoff is a
small completed simulator bundle plus receipt and hashes; NUIAK owns offline intake.

CLI stdout is reserved for a compact JSON result—stage, typed outcome, job ID,
receipt/hash values, and exported path. Diagnostics go to stderr. Raw PNGs, bundles,
and full telemetry are not stdout transport: TVTestRig transfers bounded chunks over
IPC and the CLI writes the completed export to the approved destination. This keeps
machine-readable control output small and prevents incomplete bytes from becoming
consumer evidence.

Shared status reports only current producer capability, consumer result, and next
owner. Detailed history remains in each repository's evidence reports.

### D3: Use app-owned fixture jobs; do not stage manually

When TVTestRig cannot directly write NUIAK's project, use `fixture prepare`,
`fixture run-job`, and `fixture export-job`. NUIAK does not write into TVTestRig's
container, create `HOME` workarounds, or promote partial export directories. A
successful prepare result is storage readiness only—not capture authorization or
dataset eligibility.

### D4: Hardware remains a transfer-validation gate

Office is deferred from normal development capture until simulator pilot, baseline,
and candidate evidence exist. A later physical run still requires fresh scheduling,
explicit authority, readiness, and cleanup. Simulator success does not establish
physical eligibility; physical success does not replace simulator evaluation.

## Consequences

Positive outcomes are reproducible interface failures without shared hardware,
balanced simulator data for training, and a compact repair request that TVTestRig
can test locally. The costs are retained physical-transfer risk and a hard
SIM-DATA-01 prerequisite: the screenshot-output EPERM must be repaired and shown
by a fresh bounded smoke. No unchanged retry or synthetic claim substitutes for it.

This ADR changes sequencing only. It does not authorize simulator boot, launch,
capture, training, export, Office use, signing changes, setting changes, or model
promotion. ADR-0007 continues to govern VoiceOver/navigation alignment; expected
exploration-mode decoupling is not a visual FocusRing error.

## Alternatives rejected

- **Physical-first debugging:** rejected because it couples reproducible format and
  pipeline defects to Office availability and lease coordination.
- **Simulator-only production claim:** rejected because simulator data cannot prove
  physical rendering transfer, capture eligibility, or navigation performance.
- **Independent producer/consumer protocol changes:** rejected because they create
  ambiguous incompatibilities; one completed artifact is the shared boundary.

## Execution

The next live tranche is SIM-DATA-01 recovery: repair the documented screenshot
output failure, produce one completed simulator smoke artifact, and validate it
through NUIAK's existing fail-closed intake/readiness tools. SIM-DATA-03 and
FR-SIM-BASE precede scale capture; FR-SIM-CAND and FR-SIM-TTR retain their own
training/comparison gates. Physical P4-L, FR-B, and FR-C are later transfer work.
Every handoff reports software verification, data eligibility, integration
qualification, and model-gate outcome independently.
