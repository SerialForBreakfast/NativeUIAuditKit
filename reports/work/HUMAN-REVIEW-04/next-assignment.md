# Next assignment: matched real-control coverage, not another blind run

Proposal for maintainer prioritization; no capture or training launched.

1. **Home artwork versus focus:** both models miss3/4 focused controls; candidate
   falsely selects15/92 negatives. Collect Photos-like light artwork and colorful
   Music/red/orange/Podcasts-like tiles in both states, with neighbors retained and
   focus moved elsewhere. Initial target12 usable pairs spanning several controls
   and genuinely different surrounding layouts/background contexts. Do not count
   repeatedly visiting the same Home screen as independent sources.
2. **Native Photos-style buttons:** candidate misses all3 focused crops while shipped
   passes both explicit pairs. Initial target6 pairs across distinct button layouts
   and widths, focused-white/unfocused-gray matched states, surrounding competitors.
   Existing reviewed Photos frames stay development-only; new examples need separately
   approved human-label training admission and source-role assignment.
3. **Native Settings-style rows:** both miss the one focused General row. Initial
   target6 pairs across different rows/screens with wide geometry and neighboring
   rows retained. Do not infer a broad failure rate from this single positive.

These24 pairs are collection targets, not new qualification thresholds. Prioritize
diversity and correct matched labels over fulfilling counts with repeats. Fixture
variants can complement real controls after native geometry/focus validation; they
do not substitute for evidence that the model transfers to actual OS screens.

Before collection: qualify the low-friction TTR action-linked recorder/importer so
the human navigates through TTR and reviews a batch, without chat after each press.
Record before/input/settled-after correlation, actual command outcome, target/session,
original pixels/hashes, per-frame geometry and label provenance. Handle no-ops and
missing intervals explicitly. Transport success does not establish focus labels.
This is the existing recorder assignment, not a new TTR protocol request.

Acceptance: human-reviewed/native-observed states distinguished; each matched control
identified across frames; complete valid bounds; production crop QA; duplicates and
conflicts accounted; partition/source reservations fixed before training; no overlap
with this regression session or protected evaluation. Unknown independence stays
diagnostic. Captured future data is not automatically admitted to training.

Training requires a separate candidate-data role policy and execution approval.
Then use short, bounded experiments with these regression checks in addition to
the existing retention floor—not as a replacement for it. Independent qualification
and deployment verification remain separate. No circular dependency: capture-tool
integration and source planning can advance without better weights; training waits
for admitted data, not for autonomous navigation to collect it.
