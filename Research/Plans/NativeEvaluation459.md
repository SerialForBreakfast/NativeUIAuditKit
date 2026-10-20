# New native evaluation through existing templates

Owner: Maximum-mini-NUIAK. Standard remains first. HCF remains optional.

## Decision

Test the retained detectors and crop models on the six new development captures.
The previous detector gains 5 control selections but loses 6 robustness successes.
New control gains cannot override those retained losses.

Do not repeat recovery or training to repair report preparation.
Recovery completes in 94.15 s and verifies Standard restoration.
The original admission gates fail because their saved guard uses different JSON formatting.
The successors reconstruct the original serialization and require its exact recorded SHA-256 before admission.
They preserve the failed gates and reuse the completed recovery.
Both successor batches pass preparation checks against actual recovery receipts before submission.

## Experiment graph

| Stage | Jobs | Question and next decision |
|---|---:|---|
| T59 labels | 6 | Are observed controls, image hashes, groups, and focus states consistent? Reject invalid inputs. |
| T56 retained detector | 6 | Which controls does the retained detector miss at fixed settings? Establish the matched control. |
| T56 candidate detector | 6 | Does the candidate recover controls without losses on identical frames? Identify geometry and class failures. |
| T34 outline rules | 6 | Which controls have usable outline proposals? Report Standard and HCF separately. |
| T37 known-box scoring | 12 | Can each crop model select focus when measured boxes exist? Separate classification from proposal failures. |
| T57 complete-path scoring | 12 | Which detector and crop combinations preserve selections? Record wrong selections and abstentions. |
| T58 family reports | 4 | Do findings agree across buttons, rows, tabs, and positions? Choose the next bounded correction. |

The graph contains 52 diagnostic jobs. Each job retains the existing 800 s and 100 MB limits.
These limits are not runtime estimates. Dependent jobs do not count as ready work.
The catalog records are B405-242 through B405-248.
The existing batch compiler resolves producer outputs and pins each specification.
The detached runner owns execution. No shared runtime code changes are required.

## Controls and limitations

Keep detector input size at 640 pixels and confidence at 0.5.
Keep the original models, mapping, crop preprocessing, and measured boxes fixed.
Compare only identical membership. Preserve duplicate events without claiming independent support.
Incomplete control labels do not establish precision. Unmatched predictions are not confirmed false positives.
These six captures are development data. Do not convert them into the reserved training corpus.
They do not add verified no-focus coverage. Keep existing no-focus tests and the lost tab case binding.
No report grants model acceptance or navigation authority.

## Workflow correction

Preserve exact bytes when later checks bind a file hash. JSON equivalence is not byte equivalence.
Before admission, prepare the complete graph against available real receipts in an isolated output directory.
Keep source artifacts immutable. Use explicit successors after a failed admission.
Define reports with the scoring jobs, not after execution finishes.
Prepare training admission separately from development evaluation.

## Remaining training requirement

The six reserved producer drafts target 18 groups. Their gate still depends on recovery and target availability.
Captured images need label, geometry, ancestry, and role qualification before the matched detector fit.
Keep the existing 30-epoch, 2 h, 2 GiB training envelope. Do not treat this graph as ready overnight training.

## First execution and capacity finding

The first development capture completes in 224.47 s. Its retention receipt preserves 355 paths and all journal hashes.
Those paths contain 35 unique payloads totaling 192,737,077 bytes.
Their logical size totals 1,996,263,059 bytes because several paths reference identical content.
The compaction input check currently caps logical bytes at 2 GiB. Another capture can exceed this scan limit.
This is a NUIAK scan-limit issue, not a request to raise TTR's physical storage quota.
Qualify a unique-inode scan budget at a safe source-change boundary before calling the expanded capture graph unattended-ready.
Keep file-count, archive, free-space, hash, and TTR quota checks. Preserve all failed attempts.
Do not edit the pinned module while a capture uses it.
