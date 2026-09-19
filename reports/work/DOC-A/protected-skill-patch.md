# DOC-A protected skill patch proposal

The permitted repository documentation now scopes `.scaleFill` and `eval_map.swift`
to the historical Create ML / Vision path. The protected
`.agents/skills/nativeui-model-workflow/SKILL.md` should receive the equivalent edit:

> Replace blanket YOLO guidance with: shipped YOLO/CoreML inference uses its letterbox
> preprocessing path; `.scaleFill` and `swift scripts/eval_map.swift` apply only to the
> historical Create ML/Vision evaluator. Never use `MLObjectDetector.evaluation(on:)`.

No protected-skill file was changed because DOC-A requires its explicit approved filesystem
authority. This proposal cites AGENTS.md, Research/WorkerKnowledge.md K-07, and the shipped
architecture/inference path.
