# REVIEW304 model rights and attribution

Owner: Maximum-mini-NUIAK. Review date: October 9, 2026.
This is a technical evidence review, not a legal opinion.
The maintainer selects the distribution path. Obtain qualified legal advice if the combined-work scope remains uncertain.

## Maintainer decision

The maintainer selects the free, open-source AGPL compliance path for this model distribution.
This decision does not approve public publication or relicense all NUIAK and TTR source files.
Preserve existing MIT notices. Prepare the required model terms, source access, and attribution for review.
Use [the release checklist](ModelOpenSourceReleasePlan.md) for the remaining work.

## Verified local evidence

| Item | Evidence |
| --- | --- |
| Model | `nativeui-tvos-v3.0`, resident Run 012 source |
| Prepared ZIP SHA-256 | `063d7c4c98e09997e086f494e330ea834ec3ab4cde1ec414394abe0f747b7e1a` |
| Training checkpoint SHA-256 | `4b726875488842540b9f43eb5cd5ce4f2bd55b2a7cb936404957e3aef8d3fa3c` |
| Current initialization file SHA-256 | `0ebbc80d4a7680d14987a577cd21342b65ecfd94632bd9a8da63ae6417644ee1` |
| Saved training arguments | `pretrained: true`, `yolo11n.pt`, 25 epochs, seed 0 |
| Bundled compiled metadata | Author Ultralytics; license AGPL-3.0; version 8.4.153; coremltools 9.0 |
| Current resident Ultralytics | 8.4.124; this is not proof of the training-era version |
| Resident export environment | `.venv-coreml` contains Ultralytics 8.4.153, matching the model metadata |
| NUIAK root license | MIT, copyright 2026 RA11y Contributors |
| Maximum-mini-TTR checkout license | MIT, copyright 2026 Joe |

The initialization hash identifies today's file, not a verified training-era file.
The Run 012 export passes retained-image parity with the bundled model. That does not resolve license obligations.
The separate export environment explains the observed version difference. Installed files alone do not prove an unchanged historical environment.
Its AGPL license text exactly matches the preserved license copy.
The training arguments and provenance indicate pretrained initialization. Do not describe this detector as trained from scratch.

## What the primary sources establish

Ultralytics states that its trained models use AGPL-3.0 by default.
Its guidance offers an Enterprise option for uses that do not meet its open-source conditions.
This is upstream's stated position, not an independent legal ruling about TTR. [Ultralytics terms](https://www.ultralytics.com/license).

AGPL sections 4–6 cover notices, modified works, and distribution with corresponding source.
Section 6(d) describes equivalent network access to source beside object-code distribution.
The full terms determine the applicable requirements. Attribution alone is insufficient. [AGPL text](https://www.gnu.org/licenses/agpl-3.0.en.html).

Commercial use is not itself prohibited by AGPL. The applicable conditions still need review.
A public GitHub repository does not automatically establish compliance with those conditions.
Separate downloads and optional loading do not establish a license exemption.
Do not claim that an MIT label alone clears a combined NUIAK/TTR distribution.

## Prepared notices

`THIRD_PARTY_NOTICES.md` credits Ultralytics and identifies NUIAK's training and export work.
`Licenses/AGPL-3.0.txt` is a byte-identical copy from the resident Ultralytics distribution.
Its SHA-256 is `0d96a4ff68ad6d4b6f1f30f713b18d5184912ba8dd389f86aa7710db079abcb0`.
Copying the license text does not assert that the resident tool version made these weights.
Existing MIT notices remain intact. No repository license changes.

The uploaded review ZIP remains unchanged. Its notice is not a complete public licensing package.
The release packer currently permits 1 notice file. A final archive can combine attribution and complete applicable license text there.
Alternatively, a tested catalog extension can allow a dedicated license directory. Do not weaken path validation.
Any new archive requires new hashes and another exact-archive test.

## Open requirements and owners

1. The maintainer selects the AGPL-compliant path. The remaining review defines its scope for NUIAK and TTR.
2. Sillycon-TTR supplies its intended distribution terms, source availability, and relevant third-party restrictions.
3. Maximum-mini-NUIAK identifies exact training/export source versions and relevant modifications.
4. Maximum-mini-NUIAK prepares a reviewed source inventory and durable access instructions for the selected path.
5. Maximum-mini-NUIAK assembles final notices and tests the revised archive and catalog.
6. The maintainer publishes only after that evidence supports the chosen path.

The published API commit contains the trainer, generator, and dataset export scripts.
It does not prove those files match the training-era revisions or form complete corresponding source.
Do not publish the whole research checkout, personal paths, screenshots, or data merely to fill this gap.
Preserve original configuration files. Create sanitized release copies when needed and record any changes.

## Choices for the maintainer

- Choose the open-source path and review the applicable combined-work obligations for both projects.
- Use a separate license that explicitly covers these models and the intended NUIAK/TTR distribution.
- Keep this model out of public distribution while investigating a suitably licensed alternative.

No purchase, provider contact, public upload, or relicensing occurs in this review.
Do not claim a blanket testing exemption for the existing SMB transfer. Review recipient rights and obligations under the selected path.
Model quality, distribution permission, and actual TTR integration remain separate decisions.
