# Full-screen read-through 40

Continue39: implement versioned direct-read full-screen training, preserving the
2000train/500evaluation native26 membership. Original images remain read-only;
labels, temporary files and all outputs remain project-local. A custom resident
Ultralytics dataset supplies in-memory labels and avoids adjacent image caches.
Training sees training members only. Fixed last-epoch weights are evaluated once
after completion; evaluation cannot select epochs or checkpoints. Preserve v1.

Verification: unit adversarial cases, resident dataset/transform exercise, exact
corpus input qualification, offline Swift build/test. No draft admission is turned
into approval. Record separate input-ready and execution-ready states.

Companion: inspect the iOS page-dot capture path and prepare a bounded real-view
geometry check across counts and sizes. Native capture requires an executable,
project-contained output route; retain any exact runtime blocker separately.

The native26 source remains one renderer with held-out configuration groups, not
an independent real-app benchmark. Fixed operating point: confidence0.25, IoU0.5;
report TP/FP/FN and exact-frame success, not only aggregate accuracy.
