# Queued Fixture generation

> Historical research record. Results retain their stated scope and limits.
> Host names are public aliases. Local evidence and execution records remain private.
> This publication does not revalidate earlier results or approve a model.

## Contract

Generation is a producer job in the existing research queue. It is not a separate execution service.
The user approves this work through the queue-generation request.

1. Freeze the target, listener, installed binary hashes, recipes, expected counts, and data role.
2. Submit the producer with `authority: capture` and `generation352.run`.
3. Give each consumer the producer ID, specification hash, and required output names.
4. Let the background runner execute the producer.
5. Release consumers only after the producer completes and all recorded output hashes match.

The producer uses the existing Fixture HTTP interfaces and exact-UUID Simulator screenshots.
The target is `[local resource identifier]`. The listener is `http://127.0.0.1:8080`.
The producer does not install, restart, change HCF, or use physical devices.
The limit is 800 s and 100 MB. Each specification permits 1 attempt.
All related scenes remain development data. Capture completion does not approve training.

## Failure handling

The producer shares the existing Fixture lock. It creates a recovery marker before capture.
Cancellation gives capture up to 30 s to restore the scene and record cleanup.
If cleanup remains unresolved, the marker blocks later producers. A killed process cannot establish successful cleanup.
Do not remove a recovery marker without checking the recorded target, scene, focus, and ownership.
Failed producers do not release consumers. The runner does not retry them automatically.
New attempts require explicit review. Completed specifications and results remain unchanged.

The queue writes resolved output hashes into `dependencies.json` for each consumer.
Consumers check the producer receipt, image bytes, plan hash, counts, and observed labels again.
Dependencies can refer to unsubmitted producers. Such consumers remain blocked.
The queue rejects dependency cycles and paths outside its allowed storage.

## First live batch

The batch increases poster bodies from 80 px to 160 px.
It compares native and combined effects at the existing corner positions.
The producer expects 10 frames and 6 endpoint pairs.
Four consumers compare movement, content changes, repeated frames, and timing.
The models and their original preprocessing remain unchanged.

The producer stops after 26.29 s with `settle_timeout`.
It retains 9 frames. The native case completes all 5 frames.
The combined case stops before its settled content endpoint.
The producer restores the original recipe and focus. All 4 consumers remain blocked.
The failed attempt does not establish why the final endpoint fails its observation checks.
Future failures now retain a passive observation before cleanup to improve diagnosis.
No successful dataset or model improvement is claimed for this batch.

## Checks and next work

The focused suite passes 99 tests, including 4 producer lifecycle tests.
The offline native Swift build passes. Swift tests pass: 173 Swift Testing tests and 14 XCTest tests.
The default Xcode build path remains separate from this native Swift verification.

Next, inspect the failed scene requirements and qualify a revised producer with complete failure telemetry.
Then run its dependent comparisons without changing the original model crops.
Do not turn this failure into an automatic recapture loop.

The coordinator stores the result at cursor 385 and confirms the request ID on readback.
Recipient acknowledgment and forwarding remain unconfirmed.
peer-host-TTR reports that its separate HCF pilot still needs a user folder selection.
No new HCF artifact is offered.

Measured work: capture takes 26.29 s; the Swift build takes 2.67 s; Swift Testing takes 52.58 s.
The main focused suite takes 27.24 s. These times exclude implementation and coordination.
