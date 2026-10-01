# FDR021 CoreML candidate export — 2026-09-30

User requests docs/status and CoreML model. Authorizes local full encoder+head
trace/export/compile and parity on existing333development/retention crops, not
promotion, device actions, final challenge, retraining or dependency installation.
Use production crop paths and existing parity tolerance0.01 with zero decision
changes at0.5/0.70/0.85. Keep5,000,000-byte gate unchanged.

Selected head775requires pinned torchvision ImageNet MobileNetV3-small features,
avgpool, flatten, linear576→1; RGB/255 input, in-graph ImageNet normalization,
sigmoid probability and abs(probability-0.5)*2confidence. No classifier from the
ImageNet model. Pin complete trace and receipt to head+encoder+protocol hashes.
Prepare trace using existing training environment, convert via existing exporter
in the approved resident PyTorch2.7/coremltools9environment, which lacks torchvision.
No environment mutation. TorchScript cross-version acceptance must be demonstrated,
not assumed. Existing legacy export remains unchanged without explicit trace flags.

Observed FP16parity failed(max error0.21106). Preserve failed artifact and test
explicit FP32conversion of the same trace to isolate precision effects. This is
export verification, not changed weights/training/thresholds.5MBgate unchanged.

FP32 production parity also failed. Three largest errors have partial alpha in
the retained PNGs; direct CoreML RGB predictions match Torch. Verify all333 RGB
crops through direct CoreML and quantify alpha support. This isolates conversion
from production image handling. Do not silently change the shipped pixel-buffer
path or training pixels to manufacture parity; that compatibility repair needs
its own explicit scope and regression evidence.

Compare full PyTorch CPU outputs to cached MPS selected outputs, then CoreML CPU
through production crop/inference helper against the same CPU reference. Account
for every member, unchanged crop pixels and model identity. Preserve experimental
packages even if a size/parity gate fails. No latency equivalence/ANE claim.
