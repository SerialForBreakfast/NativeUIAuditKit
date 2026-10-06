# Run028 worker return accepted — October 6

Copied and hash-verified948,124bytes,15regular files/4,970,493expanded bytes.
Archive SHA256 `59973860c6244991030b96ff27a3cfc7e120d43183e29a20b81e7d3d5a902f30`.
Reviewed complete wrapper/tests; source hash matches executed identity
`47f44ad36dcdf61b40355f52d6cf9674813cad8e13b705c68bce0f2407a2db68`.
Nine tests independently pass0.105seconds, including owned-subprocess timeout.

All585prediction records validate against original manifests, content, checkpoint,
settings and geometry; zero empty/failed. Peer reports16.30seconds total, versus
15.98for027, not a training-speed comparison. CPU-only frozen merge and scoring
completed locally with unchanged non-page metrics. Both arms use the same retained
Mac first pass plus CUDA crop predictions: this is a matched hybrid comparison.

| Population | Page TP027→028 | FP027→028 | AP50:95 027→028 |
|---|---:|---:|---:|
| Training-fit216 |202→202|38→38|.545466→.546938|
| Development96 |72→75|16→14|.433172→.465028|
| Retained600 |533→543|24→24|.617944→.625048|

All treatment page metric rows exactly equal the registered all-MPS report. This
does not establish bytewise backend equality or independent final qualification.
Seven gates still fail. No promotion or additional inference/training occurred.

Local inputs: `artifacts/eval028-return01/worker198-eval028-return01/`; hashes and
timings in returned `evidence/terminal-final.json`, verified against each prediction.
The paired CPU error-report extension remains assigned, not yet received.

Independent useful result: [composition diagnostic](../IOS-STYLE-210/trailing-diagnosis.md)
recovers all216fit targets using existing predictions, without extra inference.
Next: implement/test that fixed composition, then evaluate frozen retained membership
once; do not tune against that evaluation. Prioritize native-focus admission when
TTR supplies source-binding evidence. Software verified; data roles unchanged;
worker prediction integration accepted; model gates failed.
