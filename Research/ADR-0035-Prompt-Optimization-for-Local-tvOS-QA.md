# ADR-0035 — Optimize prompts so that small local models can do tvOS QA through TTR

Proposed on 2026-11-22. Owner: Maximum-mini-NUIAK. Partner for TTR contract changes: Sillycon-TTR.
Status: proposed. Joe asked for this ADR in chat on 2026-11-22. Phases A and B are done (section 7, provisional).
This ADR authorizes no run, capture, training, TTR source change, physical device or model promotion. Each campaign below needs its own approval.

Related:
- [ADR-0016](ADR-0016-Evidence-Bound-Foundation-Model-Semantics.md): a Foundation Model as a report writer only.
- [ADR-0031](ADR-0031-Reinforcement-Learning-and-TTR-Iteration.md): a learned navigation policy.
- [QA666 results](../reports/work/QA666/README.md): local models on the TTR Fixture and on tvOS Settings.

## 1. Goal

A tester gives 2 inputs:
- a description of the app UI;
- the steps to reproduce a bug, or a QA check.

A small local model then controls TTR. It navigates the app, does the steps and reports whether each expected result occurred. The model runs on the Mac, with no cloud call.

The target models are as small as possible:
- the Apple on-device Foundation Model (Foundation Models framework);
- Ollama models: `gemma4:e4b` (8.0B), `qwen3.5` (9.7B) and `gemma4:12b` (11.9B), all Q4_K_M.

This ADR defines how to find the best prompt for each model, and how to measure bug detection.

## 2. Evidence that this ADR uses

All QA666 results are provisional. Joe has not reviewed them.

| Design | Fixture result (12 episodes) | Tokens | Model time |
|---|---|---|---|
| 1 full button plan per task, no host checks | 5 pass | not comparable | not comparable |
| 1 button per call, thinking on | 9 pass | 46,274 | 2,291 s |
| 1 button per call, completion check and confirmation | 10 pass | 86,705 | 4,064 s |
| Goal planner, thinking on | 5 pass | 34,537 | 2,165 s |
| **Goal planner, 4 fixes, thinking off** | **12 pass** | **8,464** | **99 s** |

Settings, with the goal planner and `gemma4:12b`: 7 of 8 pass, 3,391 tokens.

Lessons from these runs:
1. **Output format fails first.** With free JSON, `gemma4:e4b` invented step types. A host-built schema with few fields made every reply valid.
2. **The model must not choose buttons.** It plans goals (`focus X`, `activate X`, `back`). The host finds the route on TTR's map, explores edges that it does not know and checks each step. This split gave the best result at about 10 % of the tokens.
3. **Hidden reasoning is the main cost and the main stall.** With thinking on, `gemma4:12b` often used the full output limit and gave no answer. A structured goal plan works with thinking off.
4. **Small rule texts change results.** The progress rule fixed 1 stall. The off-screen rule ("the host can scroll and search; name the final target directly") fixed the wrong abstentions.
5. **A model's own "done" is not reliable.** A completion check gave false stops. TTR's native verdict, from the observed state, must decide the result.
6. **An image shows only what is visible.** In Settings S3, the image arm chose the last visible row, not the last row. The text arm with the host's row list passed.
7. **Temperature 0 repeats.** 3 runs of the same prompt gave the same plan. Repeats do not measure variation.

Local fact, checked on 2026-11-22: on Maximum-mini (macOS 27.0.1), `SystemLanguageModel.default` is available, and its context size is 8,192 tokens. Vision input for that model was not checked.

## 3. Decision

### 3.1 Split the work between the model and the host

The model does only the work that needs language:
- read the tester's steps and the UI description;
- turn each step into goal actions with a name for the target;
- state the expected result of each step in a fixed form;
- for a found difference, choose a bug category and write a short reason.

The host (NUIAK code with TTR) does all other work:
- observe the screen through TTR's native observation, OCR and NUIAK detections;
- find routes, explore unknown edges and press buttons through TTR's executor;
- compare each observation with the expected result;
- enforce the guards and the budgets;
- write the verdict.

The model never sends a raw button press. The host refuses Home, Select outside reviewed targets in Settings, and any value change.

### 3.2 Treat each prompt as a versioned artifact

A prompt is a template with fixed slots. Each slot has a few variants. The prompt ID is the sha256 of the template text and the selected variants. Every run records the prompt ID, the model, its quantization, the reasoning mode and the output schema.

| Slot | Variants to test |
|---|---|
| Role and task frame | short (1 sentence); with the host split explained |
| UI description | image (960 px); compact text (focused control, visible controls, OCR); compact text and the host's map (all registered controls, including controls not visible); NUIAK detections as text |
| Steps to reproduce | the tester's text; host-normalized numbered steps |
| Rules | off-screen rule; progress rule; forbidden actions as a list; "abstain if the target is absent" |
| Expected result form | none; 1 fixed field per step (`focusedLabel`, `screenTitle`, `controlPresent`, `activationCount`) |
| Output schema | goal plan (`plan-schema-v1`); goal plan with expected results (new `qa-plan-schema-v1`) |
| Examples | 0; 1 short example from a different app |
| Reasoning | off; on with a fixed output limit |

The UI description must fit the smallest context. For the Foundation Model, prompt, description and answer together must stay below 8,192 tokens. Measure the token count of each variant before a run.

### 3.3 Detect bugs with an oracle, not with the model's opinion

Each step gets an expected result in a fixed form. The host compares it with TTR's observation after the step. A difference is a **candidate bug**. The model does not decide that a bug exists.

| Bug category | Who detects it |
|---|---|
| Focus lost (no focused control) | host, from TTR focus |
| Focus trap (a move does not leave a region, and the map has an exit) | host, from the map and the press record |
| Wrong destination (title or focused label differs from the expected result) | host comparison |
| Activation with no effect, or 2 effects | host, from TTR's activation evidence |
| Back does not return to the expected screen | host comparison |
| Expected control absent | host, from SDK controls, NUIAK detections and OCR |
| Missing or wrong accessibility label | host, from SDK labels; model only for "label does not describe the visible text" |
| Unclear or wrong visible text | model, as `inference` (ADR-0016 rules) |

The model may add a reason and a category for a candidate bug. Its text is advisory. A report always separates `verified` differences from model `inference`.

### 3.4 Measure on a fixed benchmark with seeded bugs

Prompt selection needs tasks with a known answer, including tasks with a known bug.

- **Pass tasks:** the 6 Fixture tasks and the 4 Settings tasks of QA666. Add tasks until there are at least 30 independent tasks on at least 5 screens or apps.
- **Bug tasks:** the same apps with 1 known bug in each. Sillycon-TTR owns the Fixture. NUIAK asks Sillycon-TTR for Fixture variants with seeded bugs, for example a removed focus guide, a wrong destination or a missing label. Each variant needs its own build hash and a ground-truth bug record.
- **Absent tasks:** the target or bug does not exist. The correct result is abstain or "no bug".
- **Data roles:** split the tasks by app or screen into a development set and a held-out set. Prompt search uses only the development set. The held-out set is scored once for each final prompt.
- **Variation:** temperature 0 repeats. To measure variation, use 2 paraphrases of each task text, and 3 runs at temperature 0.3 for the final prompts only.

Metrics for each prompt and model:
- task pass rate (TTR's native verdict);
- bug recall (seeded bugs found) and false bug rate (candidate bugs on pass tasks);
- correct abstentions on absent tasks;
- forbidden actions (the limit is 0) and false stops;
- calls, prompt and output tokens, model time, peak memory.

### 3.5 Search prompts in stages

1. **Baseline.** Freeze the QA666 planner prompt (`turns-26`) as P0. Score P0 on the full development set for each model.
2. **1 slot at a time.** Change 1 slot, keep the others at P0, and score. Keep a change only if it improves the pass rate or bug recall with no increase in forbidden actions. Record every result, also the failures.
3. **Combine.** Combine the kept changes. Test the combination, because 2 good changes can conflict.
4. **Failure-driven text.** For each remaining failure, write 1 rule text that names the observed fault. Test it as a new slot variant. Do not add a rule without a failure that it addresses.
5. **Optional automatic search.** If stages 2–4 stop improving, a larger local model may propose prompt changes from the failure records. The same development scoring decides. No cloud model writes or scores prompts without Joe's approval.
6. **Held-out check.** Score the best prompt for each model once on the held-out set. Report both sets.

A prompt is the best for a model only on the measured set. A new app family needs a new held-out check.

### 3.6 Choose the smallest model that meets the acceptance rule

Test the models from smallest to largest:
1. Apple Foundation Model, text arm only, guided generation of the plan schema.
2. `gemma4:e4b`.
3. `qwen3.5`.
4. `gemma4:12b` (the QA666 reference).

Acceptance rule for a model and prompt (proposed; Joe sets the final values):
- held-out task pass rate at least 0.9;
- seeded bug recall at least 0.8, false bug rate at most 0.1;
- 0 forbidden actions;
- median model time per task at most 30 s.

If a small model fails, record the failing slot and the failure type. Do not lower the rule to make a model pass.

For the Foundation Model:
- Use guided generation (`@Generable` types) for the plan schema. This gives valid output without a JSON parser repair.
- Check `SystemLanguageModel.default.availability` before each campaign. Record the OS build, because the model can change with the OS.
- Do not give it tools that send input. Tools may only read host state, for example "list the registered controls".

## 4. Alternatives

| Alternative | Reason not chosen now |
|---|---|
| The model chooses each button | QA666: more tokens, stalls and false stops. Keep it as a baseline only. |
| Image only | It cannot name controls off the screen (Settings S3). Keep it as 1 variant of the UI description slot. |
| Train or fine-tune a small model for QA | Needs data that does not exist yet. Successful episodes from this ADR can become demonstrations for ADR-0031. |
| A cloud model | Not local. Use TTR's earlier cloud run only as a reference value. |
| The model decides that a bug exists | Not reliable (QA666 false completions). The oracle comparison decides. |

## 5. Consequences

- Most work is host code and benchmark tasks, not model calls. The host split makes small models usable, but each new app needs a TTR map or SDK observations.
- Seeded bug Fixtures need Sillycon-TTR work. Until they exist, NUIAK can measure task pass rate and abstention, but not bug recall.
- Prompt results depend on the model build. Ollama model updates and OS updates need a rerun of the held-out check.
- A prompt record with an ID, a slot list and scores lets another worker reproduce a result.

## 6. Phases and decisions

| Phase | Work | Decision at the end | Needs |
|---|---|---|---|
| A | Prompt record and slot templates in `scripts/qa666/`; token count of each variant; offline tests | Which variants fit 8,192 tokens. **Done 2026-11-22: all fit (section 7).** | Local code only |
| B | Expected-result schema and host comparison; offline tests with saved QA666 observations | Does the oracle find the known differences in saved runs. **Done 2026-11-22: yes, 109 of 109 explained (section 7).** | Local code only |
| C | Benchmark: 30 tasks on at least 5 screens or apps; development and held-out split | Benchmark frozen | Task authoring; TTR maps for new apps |
| D | Request seeded-bug Fixture variants from Sillycon-TTR | Bug tasks available | Joe's approval of the request; Sillycon-TTR work |
| E | Stages 1–4 of the prompt search, smallest model first | Best prompt for each model on the development set | Joe's approval of each campaign and its budget |
| F | Held-out check and report | Does a small model meet the acceptance rule | Joe's review |

Phases A and B needed no TTR change. Phase E uses the TTR QA worktree and the Simulator, within the guards of QA666.

## 7. Results of phases A and B (2026-11-22, provisional)

Joe in chat, 2026-11-22: "A b and the adr". Both phases are offline. They made no model call and used no TTR, because the arm F fit was using the GPU.

### Phase A: prompt record and token counts

Code:
- [prompt_slots.rb](../scripts/qa666/prompt_slots.rb): 2 families (`fixture-planner`, `settings-planner`), the slots of section 3.2, prompt ID and config ID.
- [prompt_token_report.rb](../scripts/qa666/prompt_token_report.rb) and [fm_token_count.swift](../scripts/qa666/fm_token_count.swift): the token report.
- [test_prompt_slots.rb](../scripts/qa666/test_prompt_slots.rb): 11 tests.

Results:
- **P0 is the current planner text.** P0 rebuilds all 22 saved planner requests of runs `turns-26`, `turns-27a`, `turns-27b` and `settings-01` byte for byte (12 image, 10 text). `GoalPlanner.instruction` and `SettingsQA.instruction` now call P0. The 33 earlier QA666 tests still pass.
- **Every single-slot variant fits the Foundation Model.** Its context is 8,192 tokens. The largest variant (`compact-p0` with `qa-plan`) needs 2,376 tokens, including 1,095 prompt tokens, 257 schema tokens and a 1,024-token answer reserve. The largest saved plan answer used 45 tokens.
- **Guided generation adds the schema to the context:** 171 tokens for `plan-schema-v1` and 257 for `qa-plan-schema-v1`.
- **Foundation Model counts predict `gemma4:12b` counts.** On 175 saved text requests, `gemma4:12b tokens = 1.0004 × FM tokens + 14`. The leave-one-run-out error is 0.23 % on average and 0.97 % at most. An estimate from characters is worse (23 % at most). The image adds about 223 `gemma4:12b` tokens (median of 112 requests).
- **Screen size limits the descriptor, not the template.** On Fixture screens, a full control entry costs 54 tokens on average (101 at most). An id and label only (`compact-min`) cost 17 (20 at most). The OCR text costs up to 115. After the template, schema and answer reserve, about 6,000 tokens are left. That is about 60 full controls at the largest size, or about 300 id-and-label entries. This is an estimate from 6 small screens, not a measurement of a large screen.

Not done:
- `gemma4:e4b` and `qwen3.5` have 3 and 1 saved text requests, which is too few for a fit. They need 1 measured count each when no fit uses the GPU.
- The Foundation Model's vision input was not checked. Its image variants count only the text part.

### Phase B: expected-result oracle

Code:
- [expectation_oracle.rb](../scripts/qa666/expectation_oracle.rb): task-level and step-level checks.
- [task_expectations.json](../scripts/qa666/task_expectations.json): expected end states of the 10 QA666 tasks.
- [oracle_replay.rb](../scripts/qa666/oracle_replay.rb): the replay.
- [test_expectation_oracle.rb](../scripts/qa666/test_expectation_oracle.rb): 11 tests, including a regression test on the saved runs.

The oracle reports 3 kinds of finding:
- state differences (candidate bugs or agent faults);
- agent claims (`false_completion`, `missed_completion`, `wrong_abstention`, `missed_abstention`);
- information (presses that changed nothing).

Replay on all 109 saved QA666 episodes with a native verdict (101 Fixture, 8 Settings), against TTR's native verdict:

| Check | Native pass, oracle met | Native fail, oracle difference | Disagreements |
|---|---|---|---|
| State only | 58 | 50 | 1 |
| State and claim | 52 | 51 | 6 |

The 7 disagreements have known causes:
- **1 state disagreement** (`tasks-13`, Absent Airplane compact): the state was correct with 0 inputs, but the model gave no explicit abstention. TTR's Fixture verdict requires the abstention claim. The oracle reports it as `missed_abstention`.
- **6 claim disagreements:** TTR passed the episode, and the model never answered `done` (the 4,000-token stalls of `turns-15` to `turns-24`). TTR's Fixture verdict does not require `done`. The oracle reports `missed_completion`, which is correct.

So the oracle finds every difference that TTR's graders find, and it keeps the model's claims apart from the observed state.

Limits:
- The expectations are task-level ground truth, not model expectations. No model has produced `qa-plan-schema-v1` output yet.
- The differences in these runs are agent faults. The Fixture and Settings had no seeded bug, so bug recall is still not measured (phase D).
- The step-level check (`check_step`) has only synthetic tests.

## 8. Open questions for Joe

1. Are the acceptance values in 3.6 correct?
2. Which real apps, other than the Fixture and Settings, may NUIAK use for tasks?
3. May NUIAK send the seeded-bug Fixture request to Sillycon-TTR?
4. May a larger local model propose prompt changes in stage 5?
