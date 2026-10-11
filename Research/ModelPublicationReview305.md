# REVIEW306 publication review and manual steps

Owner: Maximum-mini-NUIAK. Review date: 2026-10-09.
This document records technical evidence. It does not give legal advice.

## Decision

Technical source preparation is complete. The maintainer reviews the final inventory before public publication.
Use REVIEW306 for the public model. REVIEW304 and REVIEW305 contain personal information inside the old Core ML file.
Preserve those old archives privately. Do not publish their model ZIPs.
REVIEW306 uses the tested re-export from the sanitized checkpoint.
The maintainer has already selected the free AGPL path. Do not request that decision again.

Separate these release decisions:

- Maximum-mini-NUIAK supplies the model, applicable terms, notices, and source access.
- Sillycon-TTR reviews its application distribution and dependencies.
- The maintainer publishes reviewed artifacts through GitHub.

An unanswered TTR question does not prevent NUIAK from preparing its own complete release.
It does prevent a claim that TTR's application distribution is cleared.
Do not require every potential consumer to approve NUIAK's release.

## Source requirements

AGPL section 1 defines source as the preferred form for modification.
It includes scripts needed to generate, install, run, and modify the covered work.
The definition excludes qualifying system libraries and certain unmodified general-purpose tools.
Do not require an entire Python environment merely because training uses it.
Section 6(d) permits network distribution with equivalent source access and clear directions.
Source access remains the distributor's responsibility. [License text](https://www.gnu.org/licenses/agpl-3.0.en.html).

Ultralytics states that its trained models use AGPL by default.
Its guidance also describes obligations for larger works that use its models.
Treat this as upstream's position, not an independent ruling about TTR. [Upstream guidance](https://www.ultralytics.com/license).

## Concrete findings

| Item | Finding | Remaining action |
| --- | --- | --- |
| Model archive | REVIEW306 includes full notices and the privacy-corrected export | Preserve its new identity |
| Historical source | Trainer, exporter, generator, category map, and templates included | Preserve the source archive |
| Export library | Selected source matches resident package records | Preserve source and version evidence |
| Training library | 2 files differ from package records; supplement includes dated modification notices | Preserve both notices and original hashes |
| Editable checkpoint | Sanitized copy removes 5 paths; all 503 tensor storage files remain unchanged | Review the prepared source supplement |
| Source access | Both source archives exist locally | Publish reviewed source beside REVIEW306 |
| TTR application | Coordinator stores the question; forwarding remains unverified | Obtain the distribution response or escalate routing |

The checkpoint hash remains `4b726875488842540b9f43eb5cd5ce4f2bd55b2a7cb936404957e3aef8d3fa3c`.
Static inspection uses `pickletools`; it does not execute checkpoint contents.
Do not upload this checkpoint unchanged.
The editable supplement supplies the model form omitted from the initial source archive.
Its historical exporter produces a Core ML model that matches all 25 retained detections, with 0 mismatches.
This is a tested modification and export path, not a claim of exact historical training reproduction.

The experiment log dates both image-read fixes to 2026-09-09.
The affected files are `ultralytics/data/base.py` and `ultralytics/utils/patches.py`.
The current source archive preserves their current bytes.
The log does not prove those exact bytes ran during Run 012.

## Complete the editable source package

Maximum-mini-NUIAK completes these actions without changing the shipped model:

1. Preserve the original checkpoint and its hash.
2. Make a separate copy with personal paths removed from metadata.
3. Compare every tensor name, shape, type, and value with the original.
4. Record each metadata change without publishing personal paths.
5. Include the source, model configuration, and dated modification notices needed to use the copy.
6. Test the documented export procedure with resident tools and a new output directory.
7. Compare outputs with the retained model reference.
8. Give the source supplement a new name and hash.

Do not overwrite either existing archive.
Do not load an untrusted checkpoint to perform this process.
Do not claim byte-identical export unless the comparison proves it.
Exact reproduction of training is a separate claim from complete source access.

The supplement is `nativeui-tvos-editable-source-review305.zip`, with 5,495,045 bytes.
Its SHA-256 is `36318403371b09265049c1a7a91ac85d17399672aa16b67bcc732de3b8031cbd`.
It includes the sanitized checkpoint, exporter, notices, instructions, privacy receipt, and native replay receipt.
The initial privacy receipt predates export. The native replay receipt supplies the later export result.
The source review does not certify legal compliance for every downstream application.

## Manual GitHub preparation

The following commands prepare a private draft only.
They do not approve public publication or TTR's application distribution.
Do not upload the entire output directory. It contains private diagnostics.

First verify the 6 prepared artifacts:

```sh
cd /Users/josephmccraw/Documents/GitHub/NativeUIAuditKit
(cd reports/work/RELEASE-305/public306 && shasum -a 256 -c SHA256SUMS)
gh release view models-review306 \
  --repo SerialForBreakfast/NativeUIAuditKit \
  --json tagName,isDraft,url,assets
```

If the release exists, inspect its assets before any upload.
If GitHub reports an access or network error, stop.
Only if GitHub confirms that the release does not exist, create the draft:

```sh
gh release create models-review306 \
  reports/work/RELEASE-305/public306/nativeui-tvos-v3.0-review306.zip \
  reports/work/RELEASE-305/public306/nativeui-tvos-source-review305.zip \
  reports/work/RELEASE-305/public306/nativeui-tvos-editable-source-review305.zip \
  reports/work/RELEASE-305/public306/catalog-review.json \
  reports/work/RELEASE-305/public306/source-audit.json \
  reports/work/RELEASE-305/public306/source-supplement-receipt.json \
  reports/work/RELEASE-305/public306/SHA256SUMS \
  --repo SerialForBreakfast/NativeUIAuditKit \
  --target cc72583439f39ce8e7c9eaf5b8f48a9f104dcda0 \
  --title "NUIAK tvOS model — integration preview 306" \
  --notes-file Research/ModelReview305ReleaseNotes.md \
  --draft --prerelease --latest=false
```

If creation partly succeeds, inspect the draft before retrying.
Do not use `--clobber` or replace REVIEW304.
The target identifies the existing public runtime API. It does not include uncommitted release tooling.

## Public publication gate

Before publication, record all these results:

- The editable model source passes privacy and tensor checks.
- The release includes usable source instructions and all required notices.
- The maintainer accepts the exact distribution scope and asset inventory.
- The catalog stays `review-only` for this integration preview, without deployment approval.
- The release notes link every required source asset beside the model.

The agent does not run release publication commands.
After the maintainer accepts this exact preview scope, inspect the draft before publication:

```sh
gh release view models-review306 \
  --repo SerialForBreakfast/NativeUIAuditKit \
  --json tagName,isDraft,isPrerelease,targetCommitish,url,assets
```

Check all 7 asset names and their hashes against the local inventory.
Keep `review-only` for this integration preview. Public access does not approve deployment or navigation.
If the reviewed draft matches, the maintainer can publish the preview:

```sh
gh release edit models-review306 \
  --repo SerialForBreakfast/NativeUIAuditKit \
  --draft=false --prerelease --latest=false
```

After publication, verify anonymous downloads and hashes.
Ask Sillycon-TTR to test download, import, offline reload, and rejected corrupt files.
Keep TTR's application release decision separate from these technical tests.
