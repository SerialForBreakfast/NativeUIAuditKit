# ADR-0029 — Existing workflow tools versus the NUIAK template layer

Date: 2026-10-14.
Status: Proposed; adoption requires review.
Owner: research-host-NUIAK.
Related: [templates](ADR-0028-Reusable-Experiment-Templates.md), [implementation](Plans/ExperimentTemplates393.md), and [comparison](Plans/WorkflowComparison394.md).

## Decision proposed

Continue TEMPLATE393 and HCF389 independently of framework selection.
Keep the existing queue as execution authority. Add small reusable adapters without replacing active jobs.
Compare DVC with the existing approach before adopting another execution tool.
Consider MLflow separately for reporting. It does not replace readiness, approval, or scientific acceptance checks.
Do not install tools, migrate artifacts, configure remote storage, or start new services under this review.

## Evidence and limits

This review uses official documentation and source inspected on 2026-10-14.
It covers representative tools, not all prior art.
Documented features are not verified compatibility with NUIAK.
Effort ratings below are engineering estimates, not measured implementation times.
Version-specific installation and dependency licenses still require checks before any pilot.

Local source confirms these existing capabilities:

- The queue validates dependencies, hashes, authority, limits, and approvals.
- Shared evaluation caches verified inputs and preserves separate comparison outputs.
- Training validation currently permits restart, not checkpoint resume.
- Capture validation permits specific adapters and a specific target.
- HCF389 records missing export support and Vision qualification.

The checked `.venv-yolo` environment has no discoverable DVC, Snakemake, Metaflow, MLflow, or Prefect module.
This check does not prove absence from every environment or machine.
No alternative runtime benchmark ran. No efficiency claim follows from this review.

## Capability and cost comparison

| Option | Documented or observed capability | NUIAK work that remains | Cost and recommendation |
| --- | --- | --- | --- |
| Current queue plus templates | Observed hashes, approvals, bounded jobs, dependencies, and shared evaluation | Template preparation, qualified export, structured failures, adapter tests, and maintenance | Lowest migration cost; ongoing custom maintenance. Continue as control. |
| DVC | File-based stages, parameter dependencies, lock files, run cache, and experiment commands [1–3] | TTR ownership, native observations, data roles, approval bridge, evidence checks, and reports | Medium integration effort. Best first alternative for file-oriented stages. |
| Snakemake | Input/output rules, resources, conditional dependencies, and output checks [4] | Same domain checks; approved rule generation and queue ownership bridge | Medium-to-high migration effort. Strong option if rule authoring removes substantial code. |
| Metaflow | Python steps, stored artifacts, and resume from completed steps [5] | Flow wrappers, external artifact policy, TTR lifecycle, approval bridge, and scientific gates | Medium-to-high migration effort. Useful recovery model; avoid rewriting working jobs without evidence. |
| MLflow | Runs record parameters, metrics, and artifacts [6] | Everything that executes and qualifies jobs; reporting adapter and delivery reconciliation | Low-to-medium reporting integration, plus backend maintenance. Evaluate only if existing reports prove insufficient. |

### Platform fit

These are candidate designs, not tested deployments.

| Option | macOS and Linux worker | Simulator and Core ML | USB storage |
| --- | --- | --- | --- |
| Current queue | macOS path exists; Linux adapters require their own checks | Existing adapters remain Apple-host tasks | Existing verified storage policy remains authoritative |
| DVC | Official installation covers macOS and Linux [7] | Wrap native commands on an Apple host; DVC does not supply these capabilities | Test cache location, copy/link behavior, mount loss, and temporary capacity before corpus use |
| Snakemake | Local execution remains a candidate on both hosts; pin and test the selected release | Native Apple steps require the Apple worker; Linux execution cannot substitute | Test output staging and cleanup behavior on the mounted filesystem |
| Metaflow | Local Python execution is documented; NUIAK host compatibility remains untested | Native steps need an Apple-host adapter rather than a Linux container | Configure and test artifact placement; do not serialize the full corpus into each step |
| MLflow | Tracking can serve host-specific jobs without owning their execution | Log actual Apple results; do not infer parity from uploaded metrics | Store compact metadata separately; avoid copying every image into the tracking store |

No workflow framework makes Simulator capture or Vision inference portable to Linux.
compute-host-NUIAK can still train and score compatible inputs through the existing handoff.

### Recovery, cache, and concurrency

| Option | Recovery and reuse | Concurrency and duplicates |
| --- | --- | --- |
| Current queue | Verified completed attempts and explicit successors; training restart only | Existing runner lock and immutable IDs; template registration needs recovery tests |
| DVC | Reproduction follows dependencies; run cache reuses matching stage results [2–3] | Do not equate caching with exactly-once side effects. Keep outer queue ownership and stable identities. |
| Snakemake | Declared outputs and dependency rules guide recomputation [4] | Resource declarations do not replace Simulator ownership. Test interrupted outputs and overlapping requests. |
| Metaflow | Resume reuses completed step results [5] | Step resume is not optimizer resume. Test delivery replay and duplicate external effects explicitly. |
| MLflow | Stores run evidence, not job recovery [6] | Use stable NUIAK attempt IDs when logging. Repeated logging must not create duplicate scientific results. |

Capture, settings changes, uploads, and consumer actions have side effects.
Do not automatically retry these operations without checking ownership and their existing receipts.

### Licensing, installation, and maintenance

| Tool | Core license from official source | Remaining review |
| --- | --- | --- |
| DVC | Apache-2.0 [8] | Pin release, dependencies, notices, telemetry settings, and storage behavior |
| Snakemake | MIT [9] | Pin release and plugins; inspect dependencies and executable workflow imports |
| Metaflow | Apache-2.0 [10] | Pin release; inspect extensions and optional cloud dependencies |
| MLflow | Apache-2.0 [11] | Pin release; inspect backend, authentication, dependencies, and artifact access |

These licenses do not grant rights to datasets or model weights.
Keep required notices when distributing included software. Review actual distributed dependencies before packaging.
DVC's older repository URL redirects to `treeverse/dvc`; record the selected release rather than assuming an old owner or version.
No installation or dependency resolution occurs in this documentation tranche.

## Security and execution ownership

Treat workflow definitions as executable code, even when they use YAML.
Accept reviewed templates and constrained parameters, not arbitrary commands from messages.
Keep credentials and machine paths outside public specifications.
Use local-only storage for the comparison. Configure no cloud destination or tracking endpoint.
Check telemetry defaults and disable telemetry for the isolated pilot where supported [12].
Do not expose the dashboard mutation token or change worker certificates.
Do not deserialize untrusted model or framework artifacts.
The existing queue owns approval, resource claims, and process termination during the pilot.
An alternative tool runs only inside a bounded test job, not as a competing scheduler.
Failure of optional reporting does not stop experiments.

## Deferred alternatives

Prefect documents persisted results, cache policies, and transactional cache behavior [13].
These patterns are useful. Adoption adds another orchestration layer whose benefit remains unmeasured.
Kubeflow documents component artifacts and caching, with Kubernetes-based pipeline execution [14].
That infrastructure does not solve our native Apple execution requirements. Defer it unless a measured scale requirement emerges.
Neither deferred option receives an installation, license-compliance, or security qualification in this review.

## Practices to adopt without migration

- Declare input, parameter, code, and environment identities before dispatch.
- Cache verified outputs rather than successful process exits.
- Save resolved configurations before execution.
- Preserve step outputs separately from training resume state.
- Separate execution, evidence validity, and model acceptance.
- Measure preparation effort and recovery, not only raw runtime.
- Keep reusable steps small enough to test positively and negatively.

## Review outcome

DVC is the first comparison candidate because its file-based stages closely match current adapters.
This is a design judgment, not a measured superiority claim.
[WORKFLOW394](Plans/WorkflowComparison394.md) defines the controlled comparison and adoption gate.
Until that gate passes, TEMPLATE393 remains the implementation path.

The approved runtime pilot now passes matching outputs and bounded recovery checks.
See [WORKFLOW394 results](Workflow394Results.md).
The pilot does not establish reduced maintenance or justify migration. Keep the current queue and small templates.

## Official sources

1. [DVC stage definitions](https://doc.dvc.org/user-guide/pipelines/defining-pipelines)
2. [DVC pipeline execution](https://doc.dvc.org/user-guide/pipelines/running-pipelines)
3. [DVC run cache](https://doc.dvc.org/user-guide/pipelines/run-cache)
4. [Snakemake rules](https://snakemake.readthedocs.io/en/latest/snakefiles/rules.html)
5. [Metaflow debugging and resume](https://docs.metaflow.org/metaflow/debugging)
6. [MLflow tracking](https://www.mlflow.org/docs/latest/tracking/)
7. [DVC installation](https://doc.dvc.org/install)
8. [DVC license](https://github.com/treeverse/dvc/blob/main/LICENSE)
9. [Snakemake license](https://snakemake.readthedocs.io/en/stable/project_info/license.html)
10. [Metaflow source and license](https://github.com/Netflix/metaflow)
11. [MLflow license](https://github.com/mlflow/mlflow/blob/master/LICENSE.txt)
12. [DVC configuration](https://doc.dvc.org/user-guide/project-structure/configuration)
13. [Prefect caching](https://docs.prefect.io/v3/concepts/caching)
14. [Kubeflow pipeline architecture](https://www.kubeflow.org/docs/components/pipelines/concepts/pipeline/)
