# TTR source preview — manual Git handoff

Owner: Maximum-mini-NUIAK. Recipient: Sillycon-TTR. Date: October 8, 2026.
This preview adds optional inference and internal installation tools. It is not a public model release.
TTR can review a pinned source commit without a release tag or downloadable model archive.

## Scope

- `NativeUIAuditKitRuntime` exposes explicit local providers without bundled model resources.
- `NativeUIAuditKit` retains bundled defaults through the same runtime implementation.
- Shared model contracts move to a resource-free target.
- The internal installer verifies archives, compiles through a fixed helper, and verifies completed installations after restart.
- The internal selection store supports activation, rollback, and protected inference calls.
- Removal moves unused installations into a recovery folder. It does not delete model bytes.
- Missing optional focus produces an unavailable receipt. It does not silently select a heuristic.

The file list is `scripts/ttr_source_review.paths`. It includes 2 deleted paths whose contents move to the shared target.
It excludes model bytes, datasets, reports, credentials, training experiments, and unrelated documentation changes.
Existing Git history still contains large artifacts. This source commit does not remove them.
The GitHub repository is public. Review every selected diff before pushing.

## Manual source steps

Run these commands from the repository root. Stop if the index contains unrelated staged changes.

```sh
git status --short
git diff --cached --stat
git diff --check
cat scripts/ttr_source_review.paths
git switch -c codex/optional-models-ttr-preview
git add -A --pathspec-from-file=scripts/ttr_source_review.paths
git diff --cached --check
git diff --cached --stat
git diff --cached --name-status
git diff --cached
```

The staging command changes only listed paths. It also stages their deletions.
It does not clear unrelated staged changes. Do not run `git add .`.
If the branch already exists, inspect it before selecting another branch name.
After reviewing the staged source, make the commit:

```sh
git commit -m "Add optional model runtime and verified local lifecycle"
git rev-parse HEAD
```

After approving these exact source files for the public repository, push only this branch:

```sh
git push -u origin codex/optional-models-ttr-preview
```

Give Sillycon-TTR the full commit hash and branch name.
Do not create a release or tag yet. Do not change repository visibility.
Do not push model archives, diagnostic reports, or unrelated research commits as part of this handoff.
Review the branch history if its base changes before publication.

## TTR integration boundary

The public preview interface is `NativeUIModelProviding` with `NativeUILocalModelProvider` and `NativeUILocalDetector`.
Create a new session when the selected model changes. Keep model selection fixed during each session.
Use [the digest contract](ModelDigestContract.md) to verify local artifact identity.
The host supplies trusted expected hashes, manifests, and metadata. Self-reported download hashes do not establish trust.
TTR owns folder access, its interface, and both consumers of focus results.
Use the same selection in `NUIAKFeatureController` and `FocusDetectorService`.
Missing models mean unavailable, not a numeric score of zero.
Keep model results in observer mode. Do not use this preview to authorize navigation.

The installer, compiler helper, and selection store remain internal.
They supply executable evidence and a reference for host integration, not supported external installation APIs.
The selection store holds one writer lock for its lifetime. All removal uses that store.
Its protected callback covers loading and inference. Do not return a live session from that callback and then remove its files.
Keep the callback open for the complete session lifetime if a host retains the model.
The host explicitly disables a selection and releases the rollback version before either can be removed.
Interrupted installation claims remain for explicit review. The store does not take them over automatically.

Current shipping manifests require macOS 15. The source probe targets macOS 14 but runs on macOS 27.
Do not change TTR's macOS 14 minimum from this evidence alone.
Use a separate preview harness on macOS 15 or later while resolving the shared minimum.
Actual macOS 14 execution and signed TTR sandbox behavior remain unverified.
Process isolation does not establish a security sandbox for arbitrary models.

## Verification and remaining release work

The current offline build and all 161 Swift tests pass on macOS 27.0.1, arm64.
The final dependency-free probe also passes. These results cover the working tree, not a future edited commit.

Run the offline Swift build and tests with the repository's project-local cache settings.
Run `bash scripts/verify_model_free_consumer.sh` for a dependency-free source probe without model files.
Run `bash scripts/verify_models_package_standalone.sh` for bundled compatibility.
Real source parity tests run only when the resident training export exists. A skipped test is not a parity pass.
The retained tvOS comparison covers 1 image and 25 detections. It does not establish general model accuracy.

Before an optional-download release, finish explicit downloads, trusted catalog integration, and both signed TTR variants.
Also verify exact model sources, broader parity, package sizes, distribution rights, and supported host versions.
The maintainer selects the NUIAK release version separately from TTR 0.4.3 RC.
The proposed `2.1.0-rc.1` remains unapproved. Do not tag it from this preview.
