# NATIVE-88 — frozen failure decomposition

No training, admission, capture, threshold tuning or promotion. Prior work preserved.

| Outcome | Evidence |
|---|---|
| Software verified |19focused Python tests; offline Swift build/134tests|
| Data eligible |Existing68train/5exposed development unchanged|
| Integration qualified |Frozen checkpoint replay on all73pairs;49old predictions match within1e-6|
| Model gate passed |Not assessed; no independent final set|

All5wrong Settings endpoints have the correct box at rank2. Four selected boxes
are below100px largest extent; one is an enclosing780×471region. Size is descriptive,
not a safe rejection rule. Settings still2/5paired; correct proposal coverage is not
sufficient ranking evidence. Shared-frame occurrences are correlated, not five
independent failures.

Replayed frozenDTM018change head with frozenDTM020boxes. Old44train:44/44correct
change andjoint; new24train:21/24; exposedSettings:5/5change,2/5joint. Zero
abstentions. Overall65/68joint train versus57/68withDTM013control. This diagnostic
composition does not replace DTM020's primary fixed-control report or train a model.
Remaining change errors:rich-table-compact-light-s31-p2-directional,
rich-table-wide-dark-s31-p2-directional,rich-table-wide-light-s31-p2-directional.

Existing49encoded pairs reused after record/source checks; only24new pairs encoded.
Initial full diagnostic2.410s; r2rechecks final membership guards. No native setup or
crop calls. Source/model hashes retained in diagnostic-r2/diagnostic.json; checkpoint
identity and old-output parity verified. Every joint count includes confidence
abstention, not merely raw label correctness.

Commands: diagnose_native88.py --output reports/work/NATIVE-88/diagnostic-r2;
unittest test_native88,test_native86,test_size81,test_rank75,test_batch79
(19tests/1.258s); offline Swift build/test. Logs .build/native88-*; all exit0.
Generated tests cover missing predictions, nonfinite probabilities, confidence
abstention and descriptive rank/size summaries. Actual model replay is separate.

TTR status read from verifiedSMB: latest snapshot2026-10-04T01:07:49Z requests
exact-host cleanup diagnostics and notes producer work on small controls/distractors.
No new runtime-ready evidence or acknowledgment of84found in inspected fields.
No status write: this local diagnosis does not change that existing producer action.
No restart or stale-status hardware assumption. Runtime request remains independent.

Next substantial tranche: pair-aware candidate evidence using both frames and
automatic correspondence, retaining no-op/scroll separation and never injecting
truth boxes. Compare against frozenDTM020before committing to another model design.
Separately review3change misses, then reserve genuine unseen app/journey groups before
claiming generalization. Do not hard-filter small candidates without small-positive
coverage; do not choose a threshold on the five exposed Settings examples.
