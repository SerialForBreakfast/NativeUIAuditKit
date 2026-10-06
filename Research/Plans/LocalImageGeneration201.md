# LOCAL-IMAGE-201 — local artwork feasibility, not model training

Maintainer requests high-priority Big Dog preparation and a corresponding local Mac
spike. Explicit installation approval is required on Big Dog. This tranche prepares
the setup decision; no downloads, installation, generation or new service authorized.
Tasks.md owns state; the portable worker contract is
[local-image201-request.yaml](../../reports/coordination/local-image201-request.yaml).

## Hardware and storage observations

October6 03:08UTC read-only checks: this host is **Mac mini M4,24GB**, not a separate
unknown laptop. Internal volume reports36GiB available; verified local APFS
`/Volumes/training-drive` reports1.7TiB available. These are point-in-time free-space
observations, not reserved capacity. No Draw Things or Mochi Diffusion app found at
the two conventional /Applications paths checked; not an exhaustive install search.
Big Dog previously qualified RTX2070SUPER8GB CUDA; its request asks for fresh RAM,
disk, GPU availability and resident-model inventory. Other Macs remain unverified.

## 201-BD — worker preparation

Worker adopts its own taskID under the linked request, high priority preparation
without interrupting existing work. Inspect resident dependencies and hardware,
select one pinned practical pipeline, assess exact model/base/software licences,
and deliver installation/download/storage commands for the maintainer to approve.
FP16/CUDA compatibility must be checked on this GPU; BF16/FP8 support is not assumed.
No image inference until explicit setup/pilot approval. Existing training permission
does not waive this installation gate.

## 201-MAC — preparation and storage decision

Inspect resident versions/tools and compare one macOS-native route (Draw Things
local-only or Apple's CoreML pipeline) with the same model family selected by BD.
Do not install both for exploration by default. Confirm whether model files/caches
can reside on approved USB without unsupported symlinks or silent home-directory
writes. Keep source/environments local; propose all required application/container
storage explicitly. Preserve at least20GiB internal and20GiB external headroom for
this proposed experiment, with actual model/cache/temp sizes known before approval.
These reserves are task planning limits, not permission to delete other files.
If the tool cannot meet storage/privacy constraints, report that before installation.

Acceptance: one exact version/model/setup proposal, rights/terms references, expected
memory/disk footprint with unknowns marked, supported output dimensions, reversible
paths, explicit network/setup needs and bounded pilot command/workflow. User approves
installation/execution before native app setup or weight retrieval. Read-only
feasibility can proceed without a runtime skill; actual generation must follow the
available generation tool/skill instructions and any later explicitly chosen local
workflow authority. No claim a proposed model has run here.

## Shared proposed pilot after setup approval

24individual artworks: six per poster, thumbnail, avatar and backdrop role. Reuse
the short role prompts/coverage concepts in [GeneratedMediaAssets](GeneratedMediaAssets.md),
but remove multi-panel generation instructions. Keep text, buttons, masks, focus
effects and annotations native/procedural; generated art never supplies UI labels.
Save expanded prompt, seed, exact model/settings, actual dimensions and original bytes.
Build contact sheets deterministically only for review. Retain failed outputs and
group all variants by content ancestry as development-only.

Use one supported resolution/aspect configuration per role, same24prompts/seeds
across machines where the model/runtime supports them. Matching seeds need not yield
identical cross-backend pixels. Report cold-load/warm times, memory/temp/disk, accepted
assets/hour, defects and review effort. Quality and latency are separate outcomes.
Proposed ceiling per machine:24outputs,2hours compute,1GiB outputs; weight/cache
storage separately budgeted. No model fine-tuning, concurrent training/GPU capture,
automatic retries or spending expansion. Compare to existing licensed/generated
assets before scaling; local generation is not automatically better or free.

## Sources checked

- [Apple CoreML Stable Diffusion](https://github.com/apple-aiml-research/ml-stable-diffusion)
  provides a native path; not measured on our machine.
- [SDXL-Lightning](https://huggingface.co/ByteDance/SDXL-Lightning)
  documents matching step/checkpoint/scheduler requirements and OpenRAIL++ terms.
- [Diffusers memory guidance](https://huggingface.co/docs/diffusers/main/optimization/memory)
  explains offloading; memory reduction can cost speed.
- [Draw Things](https://drawthings.ai/downloads/) is a candidate local runtime;
  local-only configuration and exact version still need qualification.

Next after preparation: maintainer reviews exact installation proposal, then one
bounded pilot. TTR receives only reviewed artwork/manifest through the existing
intake/receipt contract. No fabricated estimate of token savings or model benefit.
