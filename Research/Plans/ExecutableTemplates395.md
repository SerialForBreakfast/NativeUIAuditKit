# TEMPLATE395 — executable HCF adapters

## Fixed geometry adapters

T31 fits one inset mapping from named development groups. It rejects overlapping groups, duplicate images across partitions, and invalid geometry.
T32 reports fitting and evaluation results separately. It also reports exact Standard prediction preservation.
Both adapters pass positive and negative cases through the real queue. See [HCF401](HCF401.md).

Owner: research-host-NUIAK.
Related: [ADR-0028](../ADR-0028-Reusable-Experiment-Templates.md), [HCF389](HCF389.md), and [TEMPLATE393](ExperimentTemplates393.md).

## Scope

Use the existing queue. Do not add a scheduler.
Keep Standard models unchanged. HCF remains optional.
Software qualification does not establish model accuracy or approve navigation.

The compiler accepts `hcf-template-description-v1`.
Each description names its question, decision, template, inputs, parameters, dependencies, and owner.
Capture and training descriptions also require their existing authority contracts.
Inputs use paths and SHA-256 hashes, or named outputs from pinned dependencies.
The compiler rejects unknown fields and operations. Descriptions cannot contain shell commands.

## Implemented bindings

| Template | Executable work | Minimum check | Remaining qualification |
| --- | --- | --- | --- |
| T01 | Inventory retained evidence | Count frames and groups; reject duplicate IDs | No new efficacy claim |
| T02 | Preserve frozen groups and roles | Reject changed roles and pixel overlap across roles | Reserve new groups only for approved campaigns |
| T03 | Use the existing native producer | Require verified captures and restoration | Simulator denies the current USB screenshot path |
| T04 | Admit retained native evidence | Recheck observed focus, images, and labels | New captures need the same checks |
| T05 | Make production crops | Preserve source images and frozen membership | Extend only when a new crop contract is approved |
| T06 | Train the existing crop model | Run a tiny fixed training check; reject mismatched membership | This binding does not qualify detector training or checkpoint resume |
| T07 | Score retained crops | Use real predictions and fixed preprocessing | Known-box results do not measure proposal performance |
| T08 | Report predictions | Preserve raw counts and missing measurements | Add task-specific reports through versioned bindings |
| T09 | Select an export candidate | Reject lost successes and mismatched checkpoints | Selection permits export checks, not model promotion |
| T10 | Convert and compile Core ML | Preserve source weights; enforce the existing size limit | Current conversion exceeds the 5 MB limit |
| T11 | Compare PyTorch with Vision | Use production crops; reject score or decision differences | Real candidate parity waits for eligible export |
| T12 | Measure Apple runtime | Require parity first; record actual repeated timings | Initial binding measures CPU only |
| T13 | Build an optional bundle | Verify package files, parity, runtime, and license input | Public release needs model provenance and license review |
| T14 | Check a consumer receipt | Reject changed bundle, membership, scores, or backend | TTR must confirm the proposed receipt format and return real inference |

All 14 identifiers have callable adapters. Their first supported variants are deliberately narrow.
An adapter's existence does not mean every architecture, producer, or consumer is qualified.

## Authoring and dispatch

Run `scripts/hcf_templates395.py catalog` to list the required inputs and parameters for each binding.
The catalog describes callable contracts. It does not mark native or model qualification complete.

1. Choose a supported template and a question that changes a decision.
2. Pin existing inputs. Name missing producer outputs as dependencies.
3. Set one controlled change and its bounded budget.
4. Run `scripts/hcf_templates395.py preview DESCRIPTION` with the resident Python environment.
5. Run the same command with `register` after review.
6. Approve each immutable job through the existing approval command.
7. Let the detached runner execute it.
8. Review the result before preparing a successor.

Registration never approves or starts execution.
Repeated registration accepts only identical specifications.
Changed inputs or implementation hashes require an explicit successor.
Do not edit a submitted specification to hide a failure.

Use retained prepared tensors for compatible scoring jobs.
Reuse verified dependency outputs instead of repeating preparation.
Keep controls and candidate comparisons separate even when they share preparation.

## Qualification levels

1. Contract tests use explicit software fixtures and controlled failures.
2. Queue tests verify dispatch, receipts, dependencies, and failed attempts.
3. Native and model tests use actual captures, checkpoints, and Apple runtime outputs.
4. Consumer tests verify TTR against the exact delivered package.

Never substitute level 1 or level 2 for level 3 or level 4.
Expected failures pass a software check only when the adapter returns the required failure.
They do not make the underlying capture or model job successful.

The queue records `template-result.json` for adapter completion or failure.
Artifact jobs also provide `artifact-receipt.json` with exact output hashes.
Training, capture, and evaluation keep their existing evidence requirements.
Every qualification result keeps `modelAccepted` false.

## Current findings

The first connected batch completes inventory, frozen groups, retained admission, crop preparation, tiny training, and candidate selection.
The training check runs 30 epochs on 5 accepted training crops after duplicate removal.
Its trainer reports 0 development crops. This is a dispatch check, not a useful model comparison.
Do not use this checkpoint as a candidate improvement.

Core ML conversion produces 5,038,115 bytes. The existing limit is 5,000,000 bytes.
The export attempt fails correctly and preserves the package for diagnosis.
Do not increase the limit or call that export qualified.

Native capture fails with Cocoa error 513 and underlying EPERM at the USB screenshot path.
A bounded successor tests the documented stdout option. This Simulator treats `-` as a filename and also fails.
The implementation restores the original capture path. Both failed attempts remain available.
No new native HCF data qualifies from these attempts.

## Remaining work

| Priority | Task | Result required |
| --- | --- | --- |
| P0 | T395-NATIVE | Qualify an approved screenshot writer or staging path without changing system privacy settings |
| P1 | T395-SIZE | Test a bounded size correction against the same weights; preserve decisions and the existing size limit |
| P1 | T395-PARITY | Run actual Vision parity and timing after export passes |
| P1 | T395-CONSUMER | Confirm TTR's receipt contract and verify observation-only inference |
| P2 | T395-VARIANTS | Add detector and verified-resume variants only with explicit positive and negative qualification |
| P2 | T395-EFFICIENCY | Compare shared preparation with separate preparation using identical predictions and measured setup costs |

Software fixtures cannot unblock native or model prerequisites.
Missing native data does not block retained-data scoring or software qualification.

## Evidence

Local evidence lives under `reports/work/TEMPLATE395/` and the existing queue's `template395*` jobs.
Private records and generated artifacts remain outside public source control.
All 79 focused checks pass for contracts, native dispatch, export, parity, timing, packaging, and consumer failures.
The integrated Swift check passes 14 XCTest tests and 174 Swift Testing tests.
See the local qualification reports for exact attempts and logs.

Earlier software attempts remain historical when their pinned test sources change.
Explicit successors qualify the current sources. Do not refresh old pins or erase failed attempts.
The latest scoring and report jobs reproduce the prior 16-crop report exactly across 1 development group.
Coordinator storage confirms the TTR update at cursor 672. Forwarding and peer acceptance remain unverified.
