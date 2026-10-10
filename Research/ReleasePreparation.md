# Release preparation for TTR 0.4.3 RC

Owner: Maximum-mini-NUIAK. Date: October 8, 2026.
The maintainer confirms that 0.4.3 RC is the TTR version, not the NUIAK version.
Proposed NUIAK version: `2.1.0-rc.1`, subject to final API and scope review. Existing NUIAK tags reach `2.0.2`.
Do not create a tag or publish assets from this preparation task.

## Current decision

The existing bundled models can support TTR observer tests. They are not newly qualified models.
The public optional-download release is **not ready**. Manual publication cannot replace the missing implementation and acceptance checks.
Keep the existing bundled path as the possible RC fallback, subject to the maintainer's licensing decision.
Do not describe the fallback as model-free or as an automatic-download feature.

## Prepared and verified

- The exact resident inventory covers the iOS detector, tvOS detector, and FocusRing.
- The real CLI runs both detectors. FocusRing completes 13 crop predictions without errors.
- The standalone models manifest now includes the current resources and matches the root package's platform declarations.
- The standalone test loads all 3 models and validates detector manifests.
- Release tooling checks exact IDs, versions, tasks, domains, host evidence, hashes, notices, and bounded archive inventories.
- Deterministic ZIP preparation uses stored entries. Verification rejects unexpected paths, links, duplicate entries, and changed bytes.
- Publication validation requires an explicit approval reference. That reference does not itself prove legal permission.
- The repository audit reports suspected private values by location and count, without printing their contents.
- The audit supplies an exact review list for tracked files that current ignore rules exclude.
- The licensing guide no longer claims model-free inference or blanket downstream permission.
- The provenance table no longer repeats the personal values it describes as redacted.
- The resource-free runtime and explicit local provider pass retained-image comparisons against bundled defaults.
- The internal Swift installer uses native extraction and rejects the stale tvOS source through a parity check.
- Compilation uses a separate helper. Restart checks verify completed output and reject changed host identities.
- The integrated build and all 156 Swift tests pass. Actual signed TTR execution remains unqualified.
- A macOS 14 compile probe passes on macOS 27. Shipping minimum versions remain unchanged.

The first standalone test used the default build system and failed during code signing of copied resources.
The native Swift build passes without signing repairs or system changes. Preserve both logs.
This host result does not qualify all declared minimum OS versions.

## Blocking requirements

| Requirement | Current state | Next owner |
| --- | --- | --- |
| Exact source exports | iOS unresolved; Run 012 tvOS source passes 1-image parity; older source fails | Maximum-mini-NUIAK |
| FocusRing size | Selected source is 5,037,973 bytes; gate is 5,000,000 | Maximum-mini-NUIAK verifies prior compressed candidate and parity |
| Weight distribution | Explicit per-artifact decision missing | Maintainer reviews applicable terms |
| Model-free product | Resource-free product passes local tests; preview interface needs TTR review | Maximum-mini-NUIAK and Sillycon-TTR, 293-B/E |
| Local installer | Internal native installer passes local compilation and parity; lifecycle and sandbox checks remain | Maximum-mini-NUIAK implementation; TTR host test |
| Download path | Not implemented or qualified | Maximum-mini-NUIAK, 293-D |
| TTR agreement | Review request stored; latest amendment not confirmed forwarded | BigDog-Coordinator routes; Sillycon-TTR reviews |
| Consumer tests | No fresh model-free TTR build or installation result | Sillycon-TTR source; Maximum-mini-TTR consuming build |
| Public source scope | Research history and ignored tracked artifacts need disposition | Maintainer |
| Publication identity | Repository, visibility, final NUIAK version, and exact assets unresolved | Maintainer |

macOS supplies `/usr/bin/ditto` for ZIP archives. The bounded local extraction probe passes without any new dependency.
The probe checks archive bytes, declared members, paths, types, and limits before extraction. It verifies all extracted files afterward.
The probe uses a private new folder and the fixed executable path without a shell.
It does not invoke Archive Utility, install a model, or change activation state.
Qualify the same boundaries through Swift `Process` and TTR's actual sandbox before adoption in the application.
This macOS path does not establish an iOS installer. Keep cross-platform support unclaimed until tested.
Apple documents `ditto` for ZIP distribution. [Apple packaging guide](https://developer.apple.com/documentation/xcode/packaging-mac-software-for-distribution).
The Python preparation tool is not an application installer and adds no TTR runtime dependency.

## Repository audit

The current index contains 44,908 files. Existing ignore rules match 43,530 of them.
Most belong to training outputs and operational reports. Available tracked bytes total 923,455,033 at this audit.
Ignore rules do not remove files from the index or earlier commits.
The historical provenance report identifies personal information in earlier public commits. Current remote visibility is not reverified here.
A narrow pattern scan cannot clear history, binaries, screenshots, or every credential format.

Do not publish the whole checkout as a clean new release source.
Prefer an explicit source inventory for a separate model-release repository after approval.
Keep source notices, contracts, and release tooling in that repository. Attach approved model bytes as release assets.
A separate repository does not remove existing public history. Treat history remediation as a separate decision.

No file is deleted, moved, staged, or removed from Git by this tranche.
The local index review list is `reports/work/RELEASE-300/index-removal-review.paths`.
Its NUL-separated paths come from `git ls-files --cached --ignored --exclude-standard -z`.
Review all intentional exceptions before using that list. Preserve local originals and existing storage records.

## Manual review sequence

For immediate source review, use [TTRSourceReview.md](TTRSourceReview.md).
Its 42-path list excludes artifacts and unrelated experiments. No tag or release is needed for this preview.
Do not combine that source commit with the large index cleanup below.

### 1. Choose the RC scope

Choose one scope before tagging:

- Bundled baseline testing: use current artifacts, with explicit limitations and applicable distribution permission.
- Optional downloads: finish 293-B/C/D/E before calling the feature release-ready.

Approve the final NUIAK version separately from TTR 0.4.3 RC.
Approve the model-release repository name and visibility. Do not change the research repository's visibility as a substitute for review.
No ZIPFoundation approval is needed. Use the tested native macOS route for the first installer qualification.

### 2. Review model rights and evidence

Review each exact artifact's source, license, notices, size, supported host, and parity evidence.
Keep iOS 41-class weights and failed transition candidates out of the release.
Do not use historical synthetic scores as real-app qualification.
Record the decision in the approved catalog and retain the evidence reference.

### 3. Review Git changes

Run these read-only commands from this repository:

```sh
git status --short
git diff --check
git diff --stat
git diff -- NativeUIAuditKitModels/Package.swift PROVENANCE.md Research/LicensingArchitecture.md
git diff --cached --stat
```

Review new files separately; `git diff` does not show untracked content.
Do not use `git add .` or commit the entire research backlog for this release.
If you approve index cleanup, review this exact proposed command before running it:

```sh
git rm --cached --pathspec-from-file=reports/work/RELEASE-300/index-removal-review.paths --pathspec-file-nul
git diff --cached --stat
```

This removes selected paths from the index, not the working files. It does not clear Git history.
Do not add `--force` when Git reports a conflict. Review the affected staged changes instead.
History rewriting and force-pushing require a separate recovery plan and explicit approval.

### 4. Test the approved source

Run `scripts/verify_models_package_standalone.sh` for the bundled compatibility path.
Run the root offline build and tests with the repository's established cache settings.
Run `PYTHONPATH=scripts .venv-yolo/bin/python -m unittest scripts/test_model_release.py scripts/test_model_distribution_inventory.py`.
Run the actual optional consumer tests before an optional-download release. Local inference and installation tests now exist.
Network download tests and signed TTR tests remain required.
Require the exact source commit and clean intended release inventory before creating a tag.

### 5. Prepare a draft only after gates pass

These commands are templates for later manual execution, not current instructions to publish.
Set each variable to an approved exact value. The checks stop commands when values are absent.

```sh
: "${RELEASE_REPO:?Set the approved owner/repository}"
: "${RELEASE_TAG:?Set the approved exact tag}"
: "${RELEASE_NOTES:?Set the reviewed notes path}"
gh release create "$RELEASE_TAG" --repo "$RELEASE_REPO" --verify-tag \
  --draft --prerelease --title "$RELEASE_TAG" --notes-file "$RELEASE_NOTES"
```

The maintainer creates and pushes the reviewed tag separately. Do not reuse TTR's version as a NUIAK tag.
Attach only approved exact files. Do not upload directory globs, logs, training data, or the research checkout.

```sh
: "${MODEL_ARCHIVE:?Set one approved archive path}"
: "${MODEL_CATALOG:?Set the approved catalog path}"
: "${MODEL_CHECKSUMS:?Set the approved checksum file path}"
gh release upload "$RELEASE_TAG" --repo "$RELEASE_REPO" \
  "$MODEL_ARCHIVE" "$MODEL_CATALOG" "$MODEL_CHECKSUMS"
```

Enable release immutability where supported before publication.
Attach every asset to the draft before publishing. GitHub locks immutable release assets after publication.
[GitHub instructions](https://docs.github.com/en/code-security/concepts/supply-chain-security/immutable-releases).
Do not overwrite released bytes. Corrected artifacts receive a new version and catalog entry.

### 6. Qualify the TTR handoff

After explicit publication approval, verify downloaded bytes through the finished consumer path.
Require exact release URLs, checksums, NUIAK source commit, TTR source/build identity, and loaded model identities.
Test unavailable models, offline restart, denied storage, cancellation, changed bytes, and rollback.
For feedback mode, keep capture and transfer opt-in. Model agreement selects review cases; it does not create correct labels.
Record TTR's acceptance separately from coordinator storage and forwarding.

## Release claims

Software checks pass only for tested paths. Artifact release permission remains unresolved.
TTR optional-download integration remains unqualified. Model-quality gates remain unchanged.
No new model, navigation authority, automatic feedback collection, or public upload occurs in this tranche.
