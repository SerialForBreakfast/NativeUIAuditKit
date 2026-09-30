# Static-human experiment verification

Owner Codex; clean checkout observed at start. No other worker edits overwritten.

- `scripts/focus_human_static_experiment.py --output .../frozen-ready`: actual
  admission freezes790native crops,138human auxiliary crops,18retention and315
  development crops. Original453-member protocols remain untouched.64exclusions
  preserved. Whole-session reservation includes derivatives; human observations
  remain human-reviewed, never native or paired ground truth.
- Source verification: all2,132inventory references plus original frame/crop hashes,
  decoded pixels, protected metadata and production crop references. No challenge
  images decoded. Existing reserved-pixel checks receive an explicit scoped amendment.
- Actual trainer `--preflight` for both arms: exit0, launchEligible true; matching
  protocol `f2eca5bd9644f2f6497820e7763362f4046527ec5e90fd5836c1c6b4c0682316`.
  No model imported by preparation/preflight. Runtime package identity is read from
  installed metadata; actual MPS is checked again in each launch process.
- Focused tests:29pass (`focused-tests.log`), covering new role/membership/leakage,
  stale approval, matched schedule/forward counts/frame mass, CPU fixture head
  updates, deadline rejection, fourteen-frame amendment and unchanged legacy
  paired/pretrained/representative/inventory behavior. Synthetic test inputs, not
  previous reports, exercise negative cases.
- Additional learning/sampling/extension/retention regression tests:41pass
  (`legacy-tests.log`);70Python tests total.
- Offline `swift build` and `swift test`: exit0;14XCTest+109SwiftTesting tests pass.
  Build/test caches and logs project-local. No package resolution/network requested.
- Execution wrappers enforce30epochs/1800seconds per arm and refuse repeated launch.
  Only owned child processes can be terminated on deadline. No export, promotion,
  device operation, new capture, installation or training-data upload.
- `compare.py` replays every saved prediction through the existing metric function,
  checks identical initial predictions and feature identities, compares a common
  completed budget and re-verifies source bytes. Exit0: all20,646predictions
  (333validation members ×31snapshots ×2arms) reproduced; feature receipts and
  initial predictions exactly equal; common budget30epochs. All source bytes and
  frame/crop checks pass after execution. No best.pt exists for either arm.

All assigned software, admission, two-run execution and comparison deliverables
are complete for review. Model qualification failed, which is an experiment
outcome rather than an unfinished implementation. No safe remaining execution is
authorized beyond this two-arm scope; the next geometry intake is separately listed.

Earlier `frozen/` is a preparation checkpoint before the final trainer receipt
change; never executed. `frozen-ready/` alone is the launched protocol.
