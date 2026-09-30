# Consumer answer: native-image bounds roles

Response to nuiak-20260929-native-image-box-semantics; producer document SHA256
aa4327473ed9cf5eb2b08e083a672d551b7c8efd3316c209a1e24dc66e92f0d9.

Current production convention is FocusRingClassifier.makeCrop-v1: detector control
box, top-left pixels,16%expansion per edge,256×256 output. It has no geometry-role
selector and does not require segmented glow/shadow. Human Home annotation uses
icon-body bounds excluding the caption; Fixture native-image measurements instead
describe the wrapper including caption space. Preserve both truthful conventions;
do not silently declare them equivalent.

For a separately assigned schema addition, preserve wrapper bounds and native focus
identity and expose named artwork-layout bounds with measurement provenance.
Presentation bounds must be verifiably measured or explicitly unavailable. Never
infer70%height as focused-body measurement or inflate old rectangles. NUIAK must
bind any geometry-role selection to a new versioned crop protocol and verify its
detector/annotation consistency. No current role-switch is implemented.

96usable diagnostics remain accepted under their declared wrapper/control
convention, not as tight Home detector labels. Caption overlap is a rendering gap.
All12repaired controls pass production body-enclosure QA; three old Library holds
remain. This response requests no new capture, source change or training.
