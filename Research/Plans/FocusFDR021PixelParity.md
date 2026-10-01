# FDR021 pixel-buffer compatibility repair

User continuation authorizes local production preprocessing repair and frozen333
development/retention parity, preserving shipped behavior. No training, promotion,
device actions or other-repository edits. Owner: Codex; packet FDR021-PIXEL-PARITY.

Inspect actual straight/premultiplied RGBA versus opaque-buffer bytes. Define a
versioned candidate metadata contract for RGB alpha-discard semantics matching
the existing saved PNG/PIL RGB training input. Missing metadata retains the legacy
path exactly; unknown explicit contracts fail closed. Keep16%/256crop unchanged.
Export a fresh FP32 package from the same sealed trace with the new metadata;
compile and test via production classifier, no CLI-only inference workaround.

Acceptance: exact candidate input RGB hashes versus retained333crops; probability
error<=0.01 with zero flips at0.5/0.70/0.85, repeated transparent/opaque generated
tests, malformed input/contract rejection, legacy behavior regression, offline
Swift build/tests and exporter tests. Preserve prior failed evidence and package.
Record actual timings and identities. TTR handoff specifies required consumer
source and metadata; local parity is not proof of a TTR build or device/ANE pass.

Implementation choice: `inputPixelContract=png-straight-rgb-v1`. Use an in-memory
lossless ImageIO PNG roundtrip to obtain the same straight RGB bytes used in
retained PNG/PIL training. Copy RGB to opaque BGRA explicitly (no redraw/blending).
This prioritizes exact parity over an unproven faster unpremultiplication formula;
measure overhead before optimizing. Unknown decoder layouts fail closed. No disk
PNG writes and no crop geometry change. Absent metadata uses unchanged legacy code.
