# GitHub model draft — manual steps

**Do not publish this draft.** The final privacy scan finds personal information in the old Core ML file.
Use the [REVIEW306 instructions](ModelPublicationReview305.md) for the corrected model and source archives.

## Current result

The maintainer creates the draft and uploads all 3 assets.
Maximum-mini-NUIAK verifies matching GitHub asset digests and the exact target commit.
The initial create command stops with an asset-name conflict. A separate ZIP upload completes the draft without replacing other assets.
Do not repeat the creation steps below. They remain the original procedure for this handoff.
The draft remains unpublished. TTR can use the SMB pack while public licensing review remains open.

Repository: `SerialForBreakfast/NativeUIAuditKit`, verified public on October 9, 2026.
Proposed model tag: `models-review304`. GitHub reports no release with this tag at this check.
This tag is separate from NUIAK library versions and TTR 0.4.3 RC.
The commands use the existing published API commit. They do not include uncommitted focus work.
The agent prepares files only. The maintainer runs GitHub writes.

## 1. Verify local files

Run this from the repository root:

```sh
cd /Users/josephmccraw/Documents/GitHub/NativeUIAuditKit
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=scripts .venv-yolo/bin/python scripts/model_release.py verify \
  reports/work/RELEASE-304/delivery/entry.json \
  reports/work/RELEASE-304/delivery/nativeui-tvos-v3.0-review304.zip
(cd reports/work/RELEASE-304/delivery && shasum -a 256 -c SHA256SUMS)
```

Expect `verified: true`, `publicationApproved: false`, and 2 checksum passes.
If either command fails, stop. Do not upload changed files under the same identity.

## 2. Check for an existing draft

```sh
gh release view models-review304 \
  --repo SerialForBreakfast/NativeUIAuditKit \
  --json tagName,isDraft,url,assets
```

If a release exists, stop and inspect it. Do not replace its assets automatically.
If GitHub reports an authentication or network error, resolve that error before creation.
If GitHub reports `release not found`, continue.

## 3. Create the draft

This command uploads 3 named files. It does not publish them anonymously.
It may create the named remote tag as part of GitHub's release workflow.
No local commit, branch switch, merge, or model file in Git is required.

```sh
gh release create models-review304 \
  reports/work/RELEASE-304/delivery/nativeui-tvos-v3.0-review304.zip \
  reports/work/RELEASE-304/delivery/catalog-review.json \
  reports/work/RELEASE-304/delivery/SHA256SUMS \
  --repo SerialForBreakfast/NativeUIAuditKit \
  --target cc72583439f39ce8e7c9eaf5b8f48a9f104dcda0 \
  --title "NUIAK tvOS model — integration preview 304" \
  --notes-file reports/work/RELEASE-304/github-release-notes.md \
  --draft \
  --prerelease \
  --latest=false
```

If the command fails after upload starts, inspect the draft before retrying.
Do not use a wildcard or upload the outer SMB handoff archive.
The outer archive contains a reference screenshot and internal review material that this public draft excludes.

## 4. Inspect the draft

```sh
gh release view models-review304 \
  --repo SerialForBreakfast/NativeUIAuditKit \
  --json tagName,isDraft,isPrerelease,targetCommitish,url,assets
```

Check `isDraft: true` and `isPrerelease: true`.
Check the exact target commit and the 3 asset names.
Keep the draft unpublished. Send NUIAK the command output or draft URL.

## 5. Complete publication review

The remaining decision concerns model rights, not hosting.
The model records Ultralytics AGPL-3.0 terms. NUIAK does not establish compliance for TTR's intended distribution.
The maintainer approves applicable terms, required notices, and this exact public scope.
NUIAK then prepares the final approved catalog and verifies any changed archive.
Do not change `releaseStatus` to `approved` merely to pass a validator.

After that review, NUIAK supplies the final publish command and checks anonymous downloads against pinned hashes.
TTR then tests its actual download, compilation, offline reload, and failure handling.
Until publication, TTR can use the verified SMB pack for local model integration.

## Scope and evidence

The prepared model archive has SHA-256 `063d7c4c98e09997e086f494e330ea834ec3ab4cde1ec414394abe0f747b7e1a`.
The prepared catalog has SHA-256 `6f33605adb3f012e496a4f50d92f91bfbacb31772e315858c527600fcff7c00b`.
The checksums identify bytes. They do not prove licensing permission or model quality.
Draft preparation changes no model weights, API, navigation policy, or data roles.
