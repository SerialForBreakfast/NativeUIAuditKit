# Queue reporting through LittleDog

> Historical research record. Results retain their stated scope and limits.
> Host names are public aliases. Local evidence and execution records remain private.
> This publication does not revalidate earlier results or approve a model.

Status: approved design and peer implementation request; integration remains unverified.
Date: 2026-10-13.
Task: QUEUE-SYNC-01.

## Outcome

### Implementation checkpoint — 2026-10-14 UTC

`scripts/research_reporting.py` now reads queue records into a separate SQLite outbox.
It does not write execution records or use the dashboard mutation token.
Events retain job, specification, attempt, and result identities.
Repeated snapshots do not create duplicate events. Later observations append events.
Uncertain delivery requires receipt lookup with the original event ID.
The transport remains injected for tests. No remote transport is configured.

21 focused tests pass for local persistence, duplicate handling, uncertain receipts, and restart recovery.
These tests do not qualify a remote receiver or either worker display.
Real completed attempts enter the local outbox. Remote delivery remains pending.

worker-host-Coordinator has no new reply after cursor 622 at this check.
The existing QUEUE-SYNC-01 review still needs the receiver API, recipient, routing receipt, and source revisions.
Do not create another assignment or use the executable-task importer for reporting.
Continuous reporting waits for independent checks against the confirmed receiver.
The 10 s, 30 s, and 60 s delivery targets remain unmeasured.

The outbox bounds retained payload bytes. SQLite metadata and journal space need a separate disk reserve during rollout.
Credential rejection, unsupported schemas, sequence gaps, and hostile display rendering need receiver qualification.

Show NUIAK experiments in the LittleDog menubar app and worker host dashboard without adding another executor.
Keep completed attempts on worker host for later review and planning.
Keep HCF execution unchanged during this work.

The maintainer requests LittleDog on peer host to prepare tasks and implement the peer changes.
Use `peer-host-LittleDog` as the display name pending confirmation of its enrolled identity.
Do not infer its routing identity from this display name.

## Verified starting point

- `scripts/research_queue.py` records immutable specifications and separate attempts.
- Its summary includes questions, decision rules, requirements, dependencies, progress, evidence type, and approval state.
- `scripts/research_dashboard_server.py` serves authenticated state on loopback.
- The local controller retains execution ownership and checks approval hashes before dispatch.
- The existing coordinator client supports message storage, listing, status lookup, and read acknowledgment.
- The inspected source does not establish a qualified LittleDog import contract or worker host task event API.

The existing dashboard token permits changes. Do not give this token to a reporting client.
Do not expose port 8765 to other machines.

## Ownership

| Component | Owns | Does not own |
| --- | --- | --- |
| research-host-NUIAK | Job specifications, approvals, attempts, execution, and independent result review | Remote service changes |
| peer-host-LittleDog | Imported task display, delivery state, and local recovery | Experiment approval, retries, training, or result acceptance |
| worker-host-Coordinator | Durable event receipt, task history, dependency view, and dashboard projection | Replacement of repository queues |

Use the existing authenticated transport and worker service where they support this contract.
If a new service or credential is required, return its exact requirement before deployment.
Do not use an LLM for routine event forwarding.

## Integration design

Publish a sanitized snapshot first. Follow it with durable task events.
Run the publisher outside the execution process. Network failures must not stop experiments.
LittleDog imports the same identities that worker host stores. It must not create independent copies of task ownership.

Prefer one durable worker host event store with LittleDog and the dashboard as views.
If LittleDog relays events, require a worker host receipt before marking remote delivery complete.
Keep the relay independent of the visible menubar window. Closing the window must not lose events.

Each event contains:

- Schema version, producer identity, queue identity, event ID, and sequence number.
- Task ID, job ID, specification hash, attempt ID, and source revision.
- State, observation time, current step, completed units, and optional total units.
- Human-readable test, question, decision rule, priority, dependencies, and exact blocker.
- Evidence type, verification state, and model acceptance as separate fields.
- For completion: exit status, elapsed time, result hash, and approved artifact references.

Progress remains unknown when the worker reports no total. Do not infer percentages from elapsed time.
Show ETA only from comparable measured attempts. Include its range and sample count.
Keep timestamps for display. Use producer sequence numbers to order updates.

## Recovery and security

- Save each event locally before sending it.
- Use at-least-once delivery with deduplication by producer, queue, and event ID.
- Reject a reused event ID with different content.
- Persist receiver acknowledgment only after durable storage.
- Retry transient failures with bounded backoff and jitter.
- Reconcile uncertain sends by their original IDs. Do not create another execution attempt.
- Recover gaps from retained events or a versioned snapshot with a sequence watermark.
- Keep attempts immutable. Corrections and verification changes append new events.
- Mark an old heartbeat as stale, not failed or complete.
- Preserve terminal events during outages. Coalesce progress only under a documented storage policy.
- Bound local storage and payload sizes. Alert on reporting failure without blocking experiment execution.
- Authenticate the producer and restrict it to its namespace.
- Accept metadata only. Exclude credentials, personal paths, screenshots, model weights, and raw logs.
- Escape displayed text. Reject unsupported schemas and arbitrary commands or paths.

This phase has no remote start, stop, cancel, retry, approval, or model promotion.
Existing local controls remain unchanged.

## Work packages

| ID | Owner | Deliverable | Acceptance |
| --- | --- | --- | --- |
| SYNC-A | peer-host-LittleDog and worker-host-Coordinator | Inspect existing APIs and freeze one compatible event contract | Return source revisions, exact entrypoints, routing identities, and supported fields |
| SYNC-B | research-host-NUIAK | Read-only export and durable publisher using existing queue records | No changed specifications, approvals, execution order, or active worker modules |
| SYNC-C | peer-host-LittleDog | Task import, running-task display, stale-state display, and reconnect recovery | Same IDs and attempts appear once; completed tasks leave the active list |
| SYNC-D | worker-host-Coordinator | Durable history and live dashboard view | Stored receipts survive restart; history retains failed and corrected attempts |
| SYNC-E | All owners | One bounded end-to-end qualification | Independent source-to-store-to-display comparison passes |

SYNC-A may start now under this maintainer request.
LittleDog may implement peer changes within existing repository permissions and execution grants.
Missing grants block deployment, not the design or local tests.
SYNC-B needs the peer contract. Do not change active pinned execution code to add reporting.

## Qualification

Use labeled test events for transport tests. Never present them as experiment results.
Then import one existing real completed attempt and one running attempt without rerunning either job.

Test duplicate events, changed duplicate payloads, out-of-order delivery, sequence gaps, and unknown schemas.
Test disconnection, sender restart, receiver restart, lost acknowledgment, and disk exhaustion.
Test revoked credentials, hostile display text, stale progress, and missing result evidence.
Check that reporting failure does not change local execution.
Check that completion does not imply scientific validity or model acceptance.

Initial service targets:

- Show a running-state change within 10 s while connected.
- Deliver terminal events within 30 s while connected.
- Recover retained events within 60 s after reconnect for the bounded test set.
- Create zero duplicate tasks or attempts from retries.
- Lose zero terminal events across tested restart cases.

Measure these targets. Do not claim them before the test.
Record event lag, duplicate suppression, recovered events, storage use, and manual interventions.

## Feedback for research

Store the question, comparison, result support, gains, lost previous successes, and next decision when available.
Missing metrics remain missing. Do not convert a successful process exit into an accuracy score.
worker host can suggest priorities from this history. Suggestions do not change approved local work.

## Handoff state

The request asks worker-host-Coordinator to forward the contract to peer-host-LittleDog.
Require the recipient and forwarded request ID before claiming delivery.
Require owner acceptance before claiming implementation has started.

The full request is `nuiak-queue-sync-01-20261014-v1`, stored at cursor 583.
The coordinator routes its unstructured text to review, not execution.
The second envelope uses an unsupported state and also enters review.
The corrected envelope is `nuiak-queue-sync-01-20261014-v3`, stored and read back at cursor 589.
It uses `pending` and links both corrections to the original contract.
Forwarding, final envelope validation, and owner acceptance remain unconfirmed.
No experiment code or running job changes during this handoff.

## Source and routing check — 2026-10-13

The local LittleDog app checkout reports revision `c1e6b6cc9b7f8db475a84aeca844f74c37d43663`.
This does not establish the revision deployed on peer host.

`MenuBarApp/DevelopmentClient/task_ingress.py` imports `project.workflow-1` packets for execution.
It prepares tasks in the host queue and can execute them when authorized.
Do not use this path for NUIAK reporting.

`MenuBarApp/Sources/TaskQueueStatus.swift` reads `queue.sqlite`, schema 2, with write access.
It exposes cancellation and queue controls. It expects local execution claims.
Do not write external research attempts into this database to make them appear in the app.
LittleDog needs a separate read-only view for externally executed tasks.

The coordinator command reference reports scope `deployment-specific reporting scope`.
The receipt for cursor 589 reports `wrong_project`, not forwarding.
The corrected project request is `nuiak-queue-sync-source-check-20261014-v1`, stored at cursor 603.
Its receipt reports `unknown_task`, review `review-54749b493dd447871b6b7776`.
No LittleDog or worker host owner accepts this assignment in the messages read through cursor 605.

worker-host-Coordinator needs to register or map QUEUE-SYNC-01 and forward the request to the enrolled LittleDog recipient.
LittleDog needs to return its read-only import contract before NUIAK connects a publisher.
The reply must name the endpoint or CLI, schema, credential scope, receipt, deduplication behavior, and replay cursor.

Live restart and duplicate tests remain blocked by this missing receiver contract.
No reporting service is installed. No compatibility or recovery test is claimed as passed.
The local dashboard still reports continuous execution of `trust-replay-01-v1` without a runner error.

### Follow-up check

The coordinator confirms review `review-54749b493dd447871b6b7776` remains open at cursor 618.
Its owner is worker-host-Coordinator. Its revision is 0, with no resolution or accepted work.
The documented message protocol permits NUIAK to send only to the coordinator.
The separate LittleDog development identity is not NUIAK's identity. Do not reuse its credentials.
Request `nuiak-queue-sync-owner-action-20261014-v1` adds structured blocker feedback at cursor 619.
It asks the existing owner to register or map this task and return the receiving contract.
If the owner cannot act, the maintainer needs to open worker-host-Coordinator and request resolution of that review.
No new assignment, transport, service, or execution attempt replaces this unresolved request.
