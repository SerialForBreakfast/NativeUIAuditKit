# ADR-0031 - Reinforcement learning and the TVTestRig iteration loop

Date: 2026-10-28
Status: Proposed; documentation only. No capture, training, or action authority granted.
Owners: NUIAK owns perception, admission, and model evaluation. TVTestRig (TTR) owns environment integration, navigation permissions, capture, and recovery.

## Context

We want tvOS navigation to improve from experience, including difficult focus,
OS-owned surfaces, and VoiceOver (VO) conditions. Better detection alone does not
teach an agent which action to take next. Conversely, successful navigation does
not prove that every detected box, focus estimate, or accessibility claim is correct.

This decision extends [opt-in feedback](ADR-0024-Opt-In-Model-Feedback.md),
[screen context](ADR-0022-Screen-Context-for-Focus-and-Navigation.md), and the
[TTR integration contract](TVTestRigIntegrationContract.md). Reuse the existing
[experiment templates](ADR-0028-Reusable-Experiment-Templates.md) and queue;
do not build another scheduler, capture stack, or training service.

The regular checkout inspected for this ADR is at `4f0a9f5a`.
TTR source and live capabilities were not inspected for this decision. Historical
integration documents are not proof of current producer support. `Tasks.md`,
referenced by older records, is absent in this checkout; the stages below are
proposed work packets, not a replacement status queue or completed assignments.

## Decision

Introduce a separate, optional navigation policy, not reinforcement learning (RL)
inside the current detector. Freeze perception during the first policy experiments.
Start with deterministic baselines and imitation learning; introduce bounded
simulator RL only if those baselines leave a measured sequential-decision gap.

| Component | Initial learning method | Feedback needed |
| --- | --- | --- |
| Element detector, visual focus, transition models | Supervised correction and targeted data acquisition | Qualified boxes, focus identities, and transition labels |
| Navigation policy | Behavioral cloning, then expert correction; conditional RL experiment | Goal-conditioned episodes, actions, verified outcomes, and rewards |
| Capture selection | Versioned sampling and coverage rules | Failures, uncertainty, and an unbiased ordinary-case sample |

Human corrections and hard-negative mining are not automatically RL. DAgger is
interactive imitation learning: query an expert on learner-visited observations
and aggregate corrected actions. Task rewards become relevant when optimizing
sequences of actions, rather than individual detection labels.

Keep tvOS perception artifacts and policy artifacts independently versioned.
Possible later shared encoders or joint training require a new matched experiment;
neither combining weights nor end-to-end RL is part of this decision.

## Environment and ownership boundary

TTR remains the sole executor. A policy proposes one bounded action; TTR independently
validates permissions and executes or rejects it. Reward never overrides a denied
action. No policy directly invokes device commands or expands the allowed surface.

A tooling-only adapter should expose a Gymnasium-compatible `reset` / `step`
interface once the producer capabilities are verified. This does not add Python,
training dependencies, or mutable policy state to the Swift library or its tests.
Use an established RL implementation for the eventual algorithm, not a custom
optimizer. Algorithm and package selection follow measured environment throughput
and reset reliability; PPO is not selected merely because it is familiar.

The initial task is a goal-conditioned, partially observed navigation problem:

- Observation: deployable detections, estimated visual focus, permitted context,
  uncertainty, recent actions, and timestamps. Missing or stale evidence is explicit.
- Goal: a specified target in an approved fixture, such as focusing a named control.
- Actions: bounded directional presses, qualified Back/Select where safe, wait,
  and abstain/stop. Each environment declares its supported subset and durations.
- Oracle: independent fixture/native observations or reviewed outcomes used for
  labels and rewards, never silently supplied as pixel-only policy features.
- Lifecycle: verified start state, action acknowledgement, bounded settle/observe,
  outcome verification, and recorded termination or truncation.

Pixel-only and native-assisted policies are separate experiments. Privileged oracle
state, target coordinates, future frames, and after-state truth cannot leak into
policy features. A fixture stable ID is a goal identity, not a visual localization
answer. Ground-truth-box policies may be diagnostic upper bounds only.

Reset means restoring an approved fixture to a verified state, not erasing a
Simulator or changing global settings. Stop on ownership loss, expired consent,
unknown application, capture mismatch, observation timeout, or failed recovery.
Record interruptions as truncations; do not fabricate terminal success or failure.

## Reward and safety contract

Begin with independently verified terminal goal success plus a small action/time
cost. Declare exact coefficients, horizon, timeout, and success predicates before
running an experiment. Report raw success separately from shaped return.

If sparse rewards prevent learning, test progress shaping as a separate factor.
Use a verified fixture graph, not detector confidence or pixel change, to establish
progress. Test cycles, repeated Select, waiting forever, early stopping, and oracle
failure as reward-hacking cases. Unknown verification cannot award success.

Denied actions are prevented by a hard safety layer, not merely penalized.
The first pilot excludes purchases, accounts, text entry containing private data,
pairing, destructive settings, and protected playback. OS surfaces require their
own explicit allowlists and restoration plans; owning a Simulator is not blanket
permission to explore every screen.

VO focus, visual focus, selection, and spoken/announcement behavior remain distinct.
A screenshot cannot by itself qualify speech correctness or VO navigation order.
Run separate accessibility profiles only where capture and outcome verification
are supported. Mark missing simulator or native evidence unsupported/unknown;
real-device qualification covers the intended physical Apple TV behavior.

## Episode artifact contract

Extend tooling through a separately versioned episode envelope, not a silent
change to annotation sidecars. Agree exact producer fields before implementation.
Each episode needs:

- Episode/group identity, task and goal definition, seed, fixture revision, domain,
  OS/build, accessibility profile, and verified starting/reset observations.
- Capture receipts, frame hashes and timestamps, bracket evidence, source dimensions,
  coordinates, and explicit gaps. Temporal bracketing is not atomic frame identity.
- Policy/perception/preprocessing identities and the exact inputs visible at each step.
- Proposed, allowed, executed, and acknowledged actions as separate records, including
  safety overrides, durations, settling evidence, and expert interventions.
- Independent outcome/reward evidence, component rewards, reward version, terminal
  versus truncated status, rejection reasons, and unknown labels.
- Behavior-policy identity and action probability when available; record unavailable
  probabilities honestly. Do not claim unbiased off-policy evaluation without support.
- Consent/retention scope, sampling probability, review/admission state, and assigned
  data role. Received or structurally valid episodes are not automatically trainable.

Store bulk screenshots/episodes outside this package through approved storage.
Preserve immutable originals and correction ancestry. No automatic uploads.

## Recurring iteration loop

1. Inventory existing TTR capture, reset, remote-input, observer, and replay capabilities
   at a pinned producer revision. Return a capability matrix and exact missing adapters.
2. Define one bounded task family and reserve independent journey/layout groups for
   training, development, and final audit before collection or threshold tuning.
3. Collect baseline/expert episodes with TTR. Include random ordinary cases as well
   as selected failures; retain denominators, rejected episodes, and coverage gaps.
4. Validate receipts and temporal alignment, review labels and rewards, then admit
   only eligible groups. Separate perception errors from planning and execution errors.
5. Retrain perception from qualified corrections when needed. Train a separate policy
   from expert actions. A perception change creates a newly pinned comparison condition.
6. Compare fixed candidates on development tasks; request targeted TTR captures for
   supported missing conditions. Reuse verified artifacts rather than recapturing all data.
7. Freeze the candidate and inference settings; run the untouched audit and retained
   regressions, then export and verify the actual consumer inference path if deploying.
8. TTR first runs observer-only shadow inference, then separately approved bounded
   execution. Return a receipt and failure summary; retain the previous artifact for rollback.

Use existing capture, qualification, training, comparison, export, and consumer
verification templates where executable variants exist. Add typed adapters only for
missing episode/policy work. Each cycle has explicit compute, action, storage, and
wall-time limits. No run, recurrent automation, peer message, or model promotion is
authorized by adopting this ADR. Never update weights during a qualification episode.

## Delivery stages and gates

| Stage | Work packet | Required evidence before proceeding |
| --- | --- | --- |
| A: contract and replay | NUIAK specifies episode validation; TTR owner confirms producer capabilities. Replay retained episodes without actions. | Positive/negative offline fixtures; rejection of stale frames, malformed actions, reward leakage, unsupported versions, and interrupted episodes |
| B: simulator baseline | TTR supplies approved list/grid/modal fixtures with verified resets and expert traces. Compare deterministic navigation and behavioral cloning. | Reproducible tasks; bounded recovery; independently verified outcomes; measured throughput and error breakdown |
| C: expert correction | Collect expert corrections on learner-visited development states under approved bounded control. | Reviewed expert labels; intervention counts; comparison against the same baseline and retained successes |
| D: conditional simulator RL | If a measured gap remains, run a fixed-budget RL comparison with frozen perception, actions, and rewards. | Preregistered numeric success/non-regression/safety/latency limits; reward-hacking tests; gains across independent seeds and task groups |
| E: physical Apple TV | Shadow the frozen candidate, then explicitly approved scripted qualification. No open-ended device exploration. | Device/OS/VO coverage; sim-to-real report; independently verified outcomes; stop/recovery receipts and rollback |

For the first pilot, propose a 100-step episode ceiling and 200 development episodes
per candidate. These are ceilings for review, not evidence of statistical sufficiency
or execution approval. Select sample size and independent seed count from baseline
variability, desired detectable improvement, and available budget before training.

Offline replay checks contracts and scores recorded behavior; it cannot reveal the
counterfactual next screen after an unexecuted action. A learned simulator or fixture
graph can support diagnostics, but does not substitute for interactive native testing.
Do not train offline RL from sparse historical logs without action-coverage and
reward-validity analysis. DAgger requires expert access on newly visited states.

## Qualification and consequences

Measure independently verified goal success, actions/time to success, loops, wrong
activations, interventions, abstentions, recovery, and safety violations. Report task
support, uncertainty intervals, seeds, and simulator/device/accessibility strata.
Count every assigned episode, including failures and truncations; do not improve
success rates by dropping difficult resets or observations.

Keep perception metrics alongside navigation metrics: detector recall, focus errors,
false transitions, and retained successes. A policy improvement cannot waive detector
release gates. Keep related episodes, reverse paths, templates, assets, and derivatives
in one split group. Never recycle final-audit failures into training without retiring
that audit and reserving a genuinely untouched replacement.

Advantages: measurable task-level learning, actionable TTR failures, and separately
releasable perception/policy improvements. Costs: expert labels, reliable resets,
independent reward verification, native interaction time, and additional qualification.
If deterministic navigation or imitation meets the task requirements, stop there.
RL is an optional experiment, not a requirement for improving the existing models.

## References

- [RL concepts: observations, actions, rewards, and policies](https://spinningup.openai.com/en/latest/spinningup/rl_intro.html).
- [DAgger: interactive imitation and dataset aggregation](https://imitation.readthedocs.io/en/stable/algorithms/dagger.html).
- [Gymnasium environment lifecycle and termination/truncation API](https://gymnasium.farama.org/api/env/).
