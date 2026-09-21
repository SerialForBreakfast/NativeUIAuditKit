# TTR skill adoption

Adopted the user-supplied portable revision 3 as the repository-local
`.agents/skills/tvtestrig/` skill with its two linked references from the adjacent
TVTestRig skill package. The pasted SKILL.md and upstream entrypoint matched SHA256
`5502b8aa27ac0dee02540aab533e713c09f4a78e9accdfd50e51307ebd9f2d4d`.

AGENTS.md now routes TTR operations through it first. Updated the NUA fixture supplement
to require actual settled focus, declared schemas, fixture labels, physical/simulator
separation and owned cleanup. Prediction files are diagnostics, never labels.
Navigation supplement preserves stricter NUA physical Select restrictions and gives
current runtime syntax precedence over historical examples.

The skill-creator guide shaped the concise NUA supplement rather than duplicating the
producer manual. All three quick_validate.py runs passed; git diff --check passed.
This validates packaging, not hardware readiness. No global skill/plugin configuration
or producer source was modified. Current simulator pause remains binding.
