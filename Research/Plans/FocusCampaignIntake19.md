# Campaign intake — one measured-body review

October 1, 2026. Extend the existing batch reviewer and audit selector, not a new
annotation format or model pipeline. New campaign CLI accepts the exact local TTR
coverage-plan response, explicit completed bundle roots, protected metadata and a
fresh output. Match all usable recipe hashes and native target IDs to planned cases;
reject duplicate/extra/partial coverage rather than silently claim completion.
Legacy bundle and human-review seals remain unchanged.

Use `fixture_batch_review.prepare` once across all bundles with rendered-body bounds
and native visibility. All crop checks precede one prefilled review. Add optional
family × target-focus-state stratification to the existing sealed audit, requiring
every planned stratum represented in the eligible population. Uniform sample per
stratum, deterministic seed, disclosed denominators/inclusion probabilities; retain
exception review separately and never claim independent-source confidence.

No template bounds substitute for measured geometry; target identity must resolve
once per frame. Exact duplicate pixels with matching labels must not demand repeated
review; conflicting native labels on identical pixels require explicit accounting.
Do not alter human annotations, source roles or admission. All shared renderer
ancestry remains grouped. A separate role decision remains necessary before training.

Resume only a completed, hash-bound output whose plan, inputs, implementation and
immutable outputs are unchanged; human edits in the review workspace are preserved.
Interrupted runs remain incomplete and cannot be promoted by finding some files.
Support actual CLI and negative cases (tampered source/output, unexpected/missing/
duplicate recipe, insufficient strata), end-to-end crop/editor integration, retained
input replay and offline package tests. Model performance is not a result of this task.

## Run and review

After hash-verified receipt/extraction, supply the retained planner response and
each completed flat bundle root to the one campaign command (repeat `--bundle`):

```sh
PYTHONDONTWRITEBYTECODE=1 .venv-review/bin/python scripts/fixture_campaign_intake.py \
  --plan <project-local-plan.json> --bundle <bundle-root> --bundle <another-root> \
  --protected <existing-protected-membership.json> --output <new-project-local-output> \
  --count 8 --seed 42
```

Use the actual protected-membership metadata, not an empty placeholder. The tool
accepts up to 128 cases/bundles (256 frames), requires complete planned membership,
and never treats a partial delivery as the full campaign. Each family must have an
eligible focused and unfocused target frame. Eight samples means one per state for
each of four families; it is a usability default, not statistical certification.
Default exception review is zero; findings remain in the audit. Increase
`--exception-limit` explicitly if additional targeted inspection is justified.
Unresolved native body geometry blocks preparation rather than silently substituting
wrapper bounds. Missing eligible strata also block a completed review.

The command prints the single queue path and writes `campaign-review.md`. Open all
selected frames together with the existing editor (do not use `--batch-index`):

```sh
PYTHONDONTWRITEBYTECODE=1 .venv-review/bin/python scripts/human_review_editor.py \
  <output>/attempt-001/audit/review/batch.json \
  --queue <output>/attempt-001/audit/combined-queue.json \
  --runtime <new-project-local-runtime-directory>
```

Use the attempt referenced by the returned queue, which can differ after an
interruption. Follow AnnotationStartup.md for native Qt startup; an offscreen test
does not qualify the visible Cocoa launch. Review bounds including focus growth,
focus state, clipping and completeness. Finish review saves diagnostic annotations;
it neither admits data nor trains. Human edits survive an identical-command resume.
Changed inputs/implementation require a fresh output; never delete the old review to
force a resume. Completed output membership and hashes are checked as well as the
completion seal. A stale lock requires establishing that its owning process ended.

## Verified result

See [FOCUS-CAMPAIGN-INTAKE-19](../../reports/work/FOCUS-CAMPAIGN-INTAKE-19/handoff.md).
Generated software fixtures exercise 48 cases and 192 production crops. They are
not live TTR pixels, training candidates or a performance benchmark. Live consumer
acceptance still requires the producer's captured originals and sampled review.
