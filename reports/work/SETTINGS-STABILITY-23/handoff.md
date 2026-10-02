# Settings stability — useful improvement with explicit limits

October2,2026. Completed local implementation, retained-pixel experiment,
content-change guard, action-level accounting and verification.

| Outcome | Result |
|---|---|
|Software verified|105 Python tests; clean offline Swift build;134 Swift tests|
|Data eligible|Existing reviewed development inputs reused; new corpus admission pending|
|Integration qualified|Actual local CLI/native-crop replay passes; live TTR integration unqualified|
|Model gate passed|Not assessed; this is a fixed pixel-rule experiment|

## Result

On identical five same-screen recorded Settings pairs (50 controls,48 with unique
semantic matches), compare:

| Rule | Correct | Wrong | Abstained among48 | Decision coverage of50 |
|---|---:|---:|---:|---:|
|Previous combined signal|4|0|44|8%|
|Plus near-identical pixel stability|33|0|15|66%|
|Plus broad-highlight change guard|33|0|15|66%|

The29new correct decisions identify unchanged focus. Both real moves remain correct:
Notifications→AirPlay and Apple Home, and Motion→Audio Descriptions. Two controls
remain unmatched. This small, repeatedly examined development set is not independent
accuracy evidence; these results do not replace the shipped focus model.

## Why the change helps

The old rule only recognized exactly identical crops as unchanged. Small rendering
differences therefore left many unchanged rows undecided. The new optional experiment
measures absolute RGB differences after existing reciprocal tracking and production
crop generation. It requires small mean,95th-percentile,changed-pixel fraction and
maximum differences simultaneously. Signed brightness cancellation cannot satisfy it.

The first stress run passed8/9cases and exposed a pre-existing weakness: replacing
content inside a row looked like arriving focus. A third fixed arm requires a large
same-direction luminance change across all four central-body quadrants before issuing
an arrival/departure. It rejects that false arrival, preserves the real moves, and
passes9/9generated cases: identical, small noise, scrolling, highlight, dimming,
scrolling highlight, content change, global illumination and duplicate texture.
The guard was designed after that failure; this is development validation, not a
fresh independent test. It is deliberately Settings-specific and can reject valid
growth-only or thin-outline focus changes elsewhere.

## Action-level result and remaining failures

The companion action aggregator reports switches only with one arrival and one
departure, unchanged only when every included decision is unchanged, and otherwise
abstained/ambiguous/incomplete. It uses decisions, never expected labels, to select an
outcome. All five full-screen results remain incomplete because endpoint completeness
was not established; both VoiceOver pairs additionally lack one unique text match.

Of15remaining scored abstentions, three are tracking failures and12have pixels that
exceed the conservative stability limits. Nine of those12are in378→386; differences
around text and adjacent content warrant alignment/context investigation before any
threshold relaxation. Exact measurements are retained per control. Similar pixels
cannot prove unchanged focus when an app provides weak or invisible focus styling.

## Evidence and execution

- [Fixed scope and policies](../../../Research/Plans/SettingsStability23.md).
- [Final retained comparison](retained-final/result.json), including action outcomes,
  source-bound baseline, per-control metrics and runtime/implementation hashes.
- [Final generated stress](stress-final/result.json); [initial failed stress](stress/result.json).
- [105 Python tests](tests.log), [Swift build](swift-build.log), [134 Swift tests](swift-test.log).
- CLI: `scripts/settings_focus_stability.py --semantics <sealed-semantics.json> --output <new-directory>`;
  generated experiment: `--stress --output <new-directory>`.
- Existing dirty tranche22 changes preserved. No threshold sweep; three fixed arms
  used the same membership. Earlier outputs remain as iteration evidence.

TTR status checked: producer is working on controlled transitions. It acknowledged
the exact DATA64 receipt and reports removing its shared duplicate while preserving
source data. No response to transition22semantic-contract was present in that snapshot.
This local rule has not been dispatched into TTR control or promoted.

## Next substantial tranche

1. Highest priority: sampled review of the prepared eight structural frames and
   source-role approval, then exact admission, encoding and the assigned matched
   training comparison. The prepared review is the human dependency.
2. Ready local follow-up: diagnose378→386alignment and neighbor contamination with
   pixel overlays, and test isolated row-body versus context measurements on fixed
   cases. Preserve this comparison as the development baseline.
3. After TTR supplies semantic-ID repair/visibility clarification, replay all16native
   transition pairs and test this rule on their content/scroll negatives. Broad
   runtime release requires new validation beyond the two real moves here.
