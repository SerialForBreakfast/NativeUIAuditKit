# PEER148 — reliable worker model-result transfer software

Software verified; data admission/integration qualification/model gates not assessed
by this transport task. No training, capture, model promotion or external deletion.

Extended existing shared_transfer.py, not another reconciler. Strict version1 keeps
TVTestRig-only semantics. Version2 names TVTestRig or joe-big-dog/NUIAK explicitly;
sender namespace, returned receipt addressee and cleanup receipt identity follow that
binding. Unknown peers/versions, cross-peer namespace substitution and mismatched
hashes fail closed. NUIAK can only clean its own shared copy with a matching receipt
and still-verified original. Receipt validation never admits a model for training.

The real145transaction now uses v2 and its exact expected worker receipt path.
Actual CLI inspect verifies both4213441byte copies and SHA256
17f5b8f8537816ed62fd0103ce75ac0fffc56c06bc48355dcbc8a9c98d80491f.
Read-only cleanup preflight correctly returns matching_receipt_required; no removal
performed. No fake result transaction was created for a nonexistent worker artifact.

SMB fallback: only ENOTSUP from exclusive rename, same parent under verified share,
no symlinks/existing target. Existing verified stage passes to Foundation move helper;
post-move hash verification remains mandatory. Other errors retain evidence and fail.
Actual helper tested locally for successful move and preservation of both source and
existing destination on collision. No unrelated rename or permission workaround.

36focused Python tests pass (includes inherited regression cases); offline Swift build
and142native checks pass in .build/peer148-{build,test}.log. Tests cover both protocols,
worker receive/publish/receipt/cleanup, wrong peer/hash, lost original, dry runs,
operation rejection, partial staging, fallback restriction and actual helper collisions.
No original request or peer namespace modified. Existing unrelated work preserved.

Next model-improvement tranche: evaluate returned CUDA candidates when available;
in parallel assess the existing iOS Run013 per-class failures and eligible coverage
addon for a focused detector improvement, rather than treating one peer dependency
as a global stop. No recurring status polling installed by this task.
