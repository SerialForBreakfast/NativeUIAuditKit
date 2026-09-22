# P0-C: resolve frozen seed count versus distinct images

## Evidence

The preserved r2 partial capture has 3,520 manifested members, including 104
duplicate decoded-pixel groups. None crosses splits in this partial sample; this
does not prove the complete corpus would be isolated. Examples include ActionSheet
seeds 11704/11752 and 11708/11964. Both the pre-existing validator and the hardened
validator reject duplicates. No member has been silently removed or repartitioned.

Native navigation/search annotation defects found by visual review have targeted
fixes and bounded real-render tests. Repeating the original full sweep would still
fail the distinct-image gate even with those fixes.

## Authorized next tranche: retain counts with expanded deterministic variants

Maintainer selected this option on 2026-09-22 UTC. It changes the frozen
seed/variation definition rather than merely repairing serialization.

1. Freeze a new corpus version/configuration, retaining the 41-class category map,
   native-only scope, family allocation and target split counts 12,340/2,400/2,200.
2. Inventory duplicate-prone family parameter spaces. Add meaningful deterministic
   layout/content/style variants where seeds alone repeat; no watermark, noise,
   timestamp or invisible metadata trick to manufacture unique hashes.
3. Use a bounded, deterministic candidate schedule with explicit attempt limits.
   Preserve rejected candidates and reasons outside accepted membership. Exhausted
   variation space is a blocker, not permission to lower a count or retry forever.
4. Check decoded content globally; reject cross-split collisions and retain all
   variants of a family in its existing partition. Do not move groups to meet quotas.
5. Pin the complete generation configuration and source before a fresh full run.
   Preflight every family/profile and the changed variant space first. Never use
   model predictions or failures to select held-out cases.
6. Render into a new corpus path; audit all raw/accepted/rejected counts, paired
   geometry, source metadata, class/style coverage and duplicate/leakage results.
7. Perform representative visual review and a recorded recovery drill, then hand off
   corpus eligibility separately from P1-B inference or any training authorization.

Implementation policy: each requested slot retains its profile/accessibility/split
configuration. Candidate seed = original seed + attempt × 1,000,000, attempts 0–31.
Compare decoded RGBA pixels (not PNG metadata) against all accepted images. Preserve
every rejected duplicate PNG/sidecar and a ledger binding it to the existing accepted
member; never count it toward the requested slot. Exhaustion fails the run. Expand
the loading-overlay's meaningful backdrop hue/contrast range because its old dark
background collapsed distinct dim-alpha values into identical black pixels. This
is genuine appearance variation, not watermarks/noise or metadata-only uniqueness.

Maintainer observed fixed connectivity/battery icons while time varies. Source
confirms ChromeCoverage hardcodes cellularbars, wifi and battery.75percent while its
time is separately randomized; the launcher sets actual simulator status only once.
For the new version, painted chrome must consume the same status configuration as
its sidecar. Exercise independent signal/Wi-Fi/battery variations with a fixed clock
and fixed content to prove visual variation is not merely a time change. Battery
means charge level/state, not battery health. These are synthetic glyphs and do not
prove real network state, exact physical-system chrome or status-state recognition.

Alternative: explicitly approve a smaller canonical deduplicated version. Preserve
the complete raw inventory, every rejected/duplicate member and its relation to the
retained member; freeze revised per-split counts before evaluation. This is a new
baseline, not an undisclosed shortening of an existing holdout.

Both options still require visual/source review, independent backup authorization,
and a new Run 009 baseline assignment. Neither restores the historical 0.586 corpus
or authorizes training, TTR operations or model promotion.
