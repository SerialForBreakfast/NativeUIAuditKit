# DIAG227 — cached error diagnosis and native ancestry

Completed both analyses without new inference/training, threshold changes, label
edits or capture. Existing matcher and exact-pixel hashing reused. All41class totals
reconcile to retained accepted022/035reports;2400membership/settings/checkpoint
contracts validated. Main diagnosis11.624seconds; artifacts remain local/ignored.

## What changed in035

- Tiny labels (<16pixels minimum side at640):TP839→1629, with798gains/8losses.
 16–32pixel labels:5905→6738. Unmatched label proposals376→1188; duplicate label
 proposals17→82; localization-overlap547→548. Missing annotations are one possible
 explanation of unmatched proposals, not an established label correction.
- Large listRow:TP487→581,132gains/38losses. Duplicate FP6→68,
 localization-overlap22→212, other-class overlap257→485, unmatched814→1188.
 Geometric overlap categories are not proof of semantic class confusion.
- All19lost progressView instances are <16pixels. All19 still have a same-class
 IoU>=.5proposal in035, but its confidence falls below unchanged.25operating point.
- PageControl gains149 and loses39 matches, net110TP. All39lost cases likewise
 retain qualifying geometry below.25. Raising resolution is not the first supported
 explanation for these specific losses. AP still worsens: count gain at one threshold
 does not establish better ranking across the confidence range.
- Toggle operating matches are unchanged (1387), whileAP declines. Do not describe
 this as missing control geometry merely from aggregate AP.

The proposal-availability analysis is per-GT, not unique greedy association; both
are retained separately. No threshold was selected on inspected retained data.
Reports: artifacts/diagnosis.json and proposal-diagnosis.json, with case IDs/boxes,
input pins, matched-size strata and representative unmatched proposals.

## Native companion

30endpoints across repair09/failures08 yield26unique decodedRGBA pixel hashes.
Two exact-pixel groups each contain three copies: repair-cal02, diagnostic repair-
cal01 and failure08/cal-03, focused and unfocused respectively. Observed focus agrees.
Old body metadata says unavailable; repaired metadata supplies measured bounds.
This is repair history, not evidence two measured boxes disagree. Preserve all
originals; keep groups together and exclude diagnostic versions from admission.
No automatic deletion, split reassignment or near-duplicate/independence claim.
Detailed artifact native-audit.json retains metadata conflicts conservatively;
this reviewed disposition explains their noncontradictory meaning.

## Decision and next substantial tranche

Prioritize cached label/FP review and confidence-ranking diagnosis over another
architecture or resolution run. Recommended bounded next experiment design:
1. Review distinct training-source examples of unmatched label/listRow predictions
   with original annotations; freeze an independently justified correction ledger
   only for confirmed errors. Never move these inspected evaluation images to train.
2. On existing training/development roles, compare confidence ordering for tiny
   progress/page controls; preserve.25audit settings. Establish whether training
   imbalance or label inconsistency is supported before choosing another replay mix.
3. Reconcile TTR capture-era source bindings for the corrected tab groups, then
   plan matched artwork/background variations under205/206. No new collection yet.

Software: reused validators/matcher pass actual-report reconciliation. Data roles
unchanged. Integration: no live runtime; peer receipt follows separately. Model gate
not assessed/passed; no promotion. No production code modified; unchanged full Swift
test evidence reused. Preserve pre-existing work and training artifacts; no Git writes.

## Peer delivery

Published and parsed/read back `/Volumes/SharedStatusFile/nuiak/diag227.json`:
1994 bytes, SHA256
`e6bbf29d81a3fc452495e1c66eebf759665fc8da6b6d6d6c15513594c070ab8b`.
Links the existing EVIDENCE223 request and INTAKE225 receipts; asks for retained
capture-era source binding, not recapture. TTR's inspected status still described
receipt discovery as pending, so this follow-up explicitly identifies the receipt
location. Publication is verified; acknowledgment and admission remain separate.
