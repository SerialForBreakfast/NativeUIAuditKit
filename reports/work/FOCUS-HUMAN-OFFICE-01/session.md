# Supervised Office focus session — stopped; recorder gap blocks scaling

2026-09-28, current NUIAK TTR consumer worker. User authorized capture while operating
Office through TTR controls. Agent sends no navigation. Initial bounded block:
Home focus switch and return, then choose next non-sensitive surface together;
first verify GUI command retention before expanding collection. No audio recording,
inference, training, account/settings mutation or automatic frame watcher.

Runtime: same Max TTR PID61937/matching helper as LOCAL-OFFICE-CAPTURE-01.
Preflight16:10:05Z: Office already user-connected, no active session/lease, capture
provider idle. Preserve the user's preexisting connection at eventual cleanup.

Owned session: E006872D-54F2-4022-BCA6-196D7BA3928F.
Owned lease:762E6A29-65C5-43C8-8CAB-4C6D8E6BD4E9;
client:nuiak-human-office-20260928-01; target:8D80F616-6C12-49A6-9015-8F594EE5F24E.
Session and lease were held during the supervised checkpoints. After the maintainer
rejected per-button chat, session-stop.json confirms finalization and timeline-final
contains sessionEnded. release-final.json confirms owned video/control release;
lease-final.json has no reservation, provider-final.json is idle/not warm.
status-final.json has no active session/command/observation and queue0; the user's
original control connection remains connected. No disconnect/navigation sent.

Frame001:1920x1080 PNG, observed Home with Photos enlarged/focused (agent visual
assessment; human confirmation pending). SHA256:
`69ccecd019d0e95502a9bad0ca674d4d61c954b8efabafcfd6078556fce1a23c`.
Original inline receipt frame-001.json and frame-001.png retained/gitignored.
Observation6FA016CA-6B81-4E42-AE93-600C88B8E421, estimated age55ms/current,
Office source/generation2. Timeline001 confirms sessionStarted and observation
with artifact path. Pre-session precedingCommandIDs exist but are not this
session's demonstrated transitions; do not reconstruct their action labels.

First operator task completed: user replied "done. Music is focused" after the
requested single Right press. Frame002 received and visually inspected: Music
enlarged/captioned, Photos no longer enlarged. SHA256:
`e79323df02af5cb961616bf17a631ecf5b9eb8b6dfa478e69455421a1c8a697e`.
Observation2CEA77CA-3C8D-4C18-A11B-A46897B93A8D,1920x1080,
same Office/generation2, estimated age78ms/current;181ms total capture call.
Timeline002 contains sequence3 `press.right`, completed,47ms,
command989B577D-F9A4-419F-937D-9DDBF46D59C2. Frame002 explicitly references
that command in precedingCommandIDs. This verifies actual GUI-input retention
for this event, not every control or automatic transition recording. Capture
occurred about48.69s after command completion; this is operator/chat turnaround,
not UI settling time. Two checkpoint images do not measure animation duration.

Return task completed: user confirmed Photos focused (worded "selected"). Timeline
shows `press.left`, not Select, completed36ms, command
E330D5D0-34F7-426F-A4F8-D08640A97913. Frame003 explicitly references this command:
observationB1836894-A5A2-4FE8-A6FA-28B3D3348808, same Office/generation2,
1920x1080,current/estimated age82ms,157ms capture call. SHA256
`50a6be45cac6c189d4e4628983a034d3ce6a61fb003daca6822da0d8572368b5`.
Original frame003 and timeline003 retained. This closes Photos→Music→Photos
checkpoint sequence, not continuous motion/settling measurement.

Operator asks about TTR Vision OCR validation. Read-only adjacent source inspection
finds VisionTextRecognizer/VNRecognizeTextRequest and explicit inspect/assertion
paths; exact source/running-binary binding remains unverified. Actual capture
receipts/timeline here contain pixels, IDs and input events, not OCR results.
Runtime reports NUIAK disabled. Do not infer that all OCR is disabled from that,
or that OCR ran merely because pixels were captured. No OCR/focus model enabled
or invoked here. Desired follow-up: persist text/confidence/bounds tied to each
exact image and keep OCR-derived identity distinct from human focus labels.

Photos opening completed: user confirmed Welcome to Photos, View Only Shared
Albums focused. Frame004 visually agrees: lower white button focused, upper
View All iCloud Photos gray/unfocused. Timeline sequence7 retains completed
`press.select`,97ms, command23D13337-1F34-4B92-AB53-CCBBF2D78FC0;
frame004 references that command. Observation17F95E61-CCD1-4AA0-94F7-9380D3C57540,
same Office/generation2,1920x1080,current/estimated age56ms,87ms capture call.
SHA256 `9f6c26c669ebb8dab9d587df752e9094ad79922b1e6f4e0fa334cb6528155f6c`.
Original frame004/timeline004 retained. Idle warning sequence1 was acknowledged
through the exact owned lease keepalive; returned state held, no takeover/reconnect.

Up task completed: user confirmed View All iCloud Photos focused. Frame005
visually agrees; Shared Albums is gray/unfocused. Same two controls remain visible
in frames004/005, supplying two candidate same-control focused/unfocused pairs
from one screen family, not two independent sources. Bounds/crop QA still pending.
Observation370B96C2-9C03-4B78-9FB4-FFE31D00278F, same Office/generation2,
1920x1080,current/estimated age59ms,136ms capture call. SHA256
`e79797ba296879d0be5a38136ccd537609d0ff774a75e9ef7c2ba16e7aa45c06`.
Timeline sequence9: press.up,completed33ms, command
DF39B275-871E-48CB-879A-04F7D6AE4AF6; frame005 references that exact command.

Boundary task completed: user reported pressing Up. Frame006 visibly retains
View All iCloud Photos focused and Shared Albums unfocused; this is agent visual
assessment, not additional human outcome confirmation. Timeline sequence11:
press.up,completed25ms, commandF578407F-B3D3-470F-B4A7-B9D324505E6F.
After-frame references that command; observation04E02DCF-F39B-44C8-8284-A4AEB0B8E799,
same Office/generation2,1920x1080,current/estimated age45ms,99ms capture call.
SHA256 `36656b0cbb1dd97eeb66e61ac90c0753afcea5de7bef08a12506af37940c5bd6`.
Record as completed input with visually unchanged focus / boundary-consistent
outcome, not proof of underlying OS input handling. Different PNG hashes do not
imply different focus or establish new training diversity. Retain as sequence
evidence; do not count this repeated focus state as a new independent example.

Back task completed: user confirmed Photos selected after Back; frame007 visibly
shows Home with Photos focused, not activation. Timeline sequence13: press.back,
completed88ms, commandE75AAECA-4CA2-4BFE-A6D7-8426D0A4248C. Frame007 references
that exact command; observation98F5EEC1-EDC0-471E-B46F-5B767EAA21B2,
same Office/generation2,1920x1080,current/estimated age77ms,136ms capture call.
SHA256 `e431617ea905f7c078bce367ee41af500075ff692e7bbe06c8076c6e9ef56ca9`.
Repeated Home state retained as return-path evidence, not additional diversity.

Settings setup completed: user confirmed General focused; frame008 visually agrees.
ObservationA57F1B66-FF36-4EAF-865A-44791DBD5546, same Office/generation2,
1920x1080,current/estimated age56ms,94ms capture call. SHA256
`f55a0e2bd4a287bd4a16078049ee64a54a0033d402721e685a048e4b31c8caa5`.
Timeline sequences15–17 contain completed Right, Up, Select with no intervening
observation/image artifacts. Sequence18 is the General checkpoint. Frame008
references all3 command IDs; this does not provide separate after-images for each.
The route's intermediate focus images were NOT retained by this session workflow.

Operator explicitly asks for every movement as potential training evidence.
Current mechanism is chat-paced checkpoint capture, not an action-triggered recorder.
Need input-linked before/after frames per human TTR action, bounded settling and
gap/overlap reporting before claiming complete transitions. Fresh raw examples
still need confirmed focus/bounds, deduplication, crop QA and explicit admission;
animation or repeated states are not automatically useful independent samples.
Do not claim to reconstruct missing frames from button events. Collection stopped;
no automatic capture watcher has been started. [Required workflow repair](../../../Research/Plans/TTRActionLinkedCapture.md).
Do not claim continuous recording, exact settling latency or GUI-event retention
before evidence exists. Review bounds/states and intended data role before admission.
Current count:8 frames,9 recorded inputs;6 visually changed checkpoint intervals
and1 visually unchanged focus interval. The Settings setup interval contains3
inputs and missing intermediate images. Candidate matched-control focus
examples for Photos/Music, bounds/crop review pending;0 admitted training examples.

Final integrity check: all8 PNGs decode at1920x1080, all source IDs match Office,
8 distinct RGB pixel hashes,9 command/8 observation events and sessionEnded.
Pixel differences do not imply8 distinct screen/focus situations. Original images
and final timeline are preserved locally; no producer artifacts deleted.
Software suite not assessed/no code changes; data diagnostic-only pending review;
integration passed for checkpoints/event retention but failed full per-input
collection expectation; model gate not assessed. No new collection requested.
