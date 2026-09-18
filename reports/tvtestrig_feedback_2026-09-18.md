# TVTestRig Feedback — Consolidated, from NativeUIAuditKit's Integration Attempts

**From:** NativeUIAuditKit (NUIAK)
**Purpose:** One consolidated list of every friction point NUIAK has hit while trying to use
TVTestRig as its training-data source, across both the earlier real-hardware RCA session and
today's tvOS Simulator session. Per our own working agreement, NUIAK does not modify TVTestRig
code — this is a request list, not a patch.
**Status of this document:** living — update in place as items resolve or new ones appear, rather
than writing a new dated file each time.

---

## 1. Current hard blocker: `aatv` cannot reach the coordinator app

**Severity: blocks everything downstream of it, including Simulator-only work that needs no
hardware at all.**

Repro (2026-09-18, tvOS 26.5 Simulator build 23L470, no real device involved):

```bash
# 1. Fixture app built and run cleanly on Simulator; GET /scene confirmed working with real data.
xcodebuild -scheme TVTestRigFixture -destination "platform=tvOS Simulator,id=<udid>" build
xcrun simctl install <udid> TVTestRigFixture.app
xcrun simctl launch <udid> com.showblender.TVTestRigFixture
curl http://127.0.0.1:8080/scene   # returns real, non-empty elements — this part works well

# 2. aatv CLI built cleanly from the TVTestRig macOS scheme.
xcodebuild -scheme TVTestRig -destination "platform=macOS" build

# 3. Coordinator app launched.
open TVTestRig.app --args --project /path/to/TVTestRig

# 4. Every aatv command against that project fails the same way, indefinitely:
aatv --project /path/to/TVTestRig status
# Error: serviceUnavailable
# "TVTestRig is unavailable. Open the TVTestRig app and keep it running, then retry."
```

The coordinator process is confirmed running (`ps aux` shows it alive, no crash log in
`~/Library/Logs/DiagnosticReports/`), but:
- It never shows up as a frontmost/visible app (`System Events` process list).
- `aatv status`, `aatv doctor`, `aatv logs path`, and `aatv fixture batch` all return the same
  generic `serviceUnavailable` with no further diagnostic.
- No amount of waiting (tried up to ~10s) changed the outcome.

**We don't know if this is an `open --args` launch-method problem, a missing permission prompt
silently blocking in a non-interactive launch context, a required Xcode-run-vs-standalone-launch
distinction, or something else.** We stopped guessing rather than poke at TVTestRig internals
blind. **Request:** either a documented "how to launch the coordinator so `aatv` can reach it"
step, or a fix so the coordinator is reachable however it's launched, or a clearer error message
that distinguishes "not running," "running but not yet ready," and "running but misconfigured."

## 2. `fixture batch`'s error reporting is misleading when the coordinator is unreachable

Before we added `--project` explicitly, the *same* underlying problem (coordinator unreachable)
surfaced as two different, specific-looking, and wrong errors:

```
# Attempt with a relative --recipes-dir, no --project:
Error: unsupportedCapability
Fixture batch harvest failed closed: recipesDirectoryMissing

# Attempt with absolute paths, no --project:
Error: unsupportedCapability
Fixture batch harvest failed closed: outputOutsideProject
```

Both of these read as real, actionable validation failures (bad recipes path; output escaping
the project root) — neither was true. We spent real time re-checking paths that were already
correct before realizing the actual cause was the coordinator connection (§1). **Request:** if
`unsupportedCapability` (or a coordinator-unreachable state) is the root cause, don't also emit
a specific-sounding secondary error that points somewhere else — surface the real cause first.

## 3. No documented Simulator quick-start for the harvest pipeline

Every doc we found frames the harvest pipeline in terms of the real "office" Apple TV. The tvOS
Simulator is a zero-risk, zero-contention path to *some* real (if synthetic) harvested data —
no hardware, no device-in-use conflicts, no signed-install step — and it already works for the
fixture app + `GET /scene` half of the pipeline (§ confirmed above). If `aatv fixture batch`
also works against the Simulator once §1 is resolved, that's a meaningfully lower-friction loop
for both of our teams than always needing real hardware. **Request:** a documented,
tested "harvest against the Simulator" path, even if it's explicitly marked as not
production-representative for final qualification.

## 4. On-disk harvest format changed twice in one day with no version signal

FIX-SYNTH-06's `aatv fixture batch` output layout changed **twice on 2026-09-18** underneath us:
first from a `synth-<n>.png`/`synth-<n>.json` one-file-per-frame layout to
`<id>_unfocused.png`/`<id>_focused.png`/`<id>_metadata.json` triples, in the same day, without a
`schema_version`/`schemaVersion` bump in the JSON payload (it stayed at `1` across the change).
We caught this only by re-reading `FixtureBatchHarvestEngine.swift` from scratch each time — a
consumer relying on the documented spec (which described a third, different layout from either
implementation) would have silently ingested the wrong fields. **Request:** bump
`schema_version` whenever the on-disk layout or field set changes, even during active
development — it's the only reliable signal a downstream consumer has that "re-check your
assumptions" is needed.

## 5. Two key-naming conventions coexist in the same payload with no stated precedence

Live `GET /scene` output (confirmed 2026-09-18) includes both harvest snake_case keys
(`element_id`, `taxonomy_class`, `normalized_bounds`, `pixel_bounds`) and NUA-alias keys (`id`,
`taxonomyRole`, `normalized_rect`, `native_pixel_rect`) simultaneously, for the same element.
Good for compatibility, but there's no stated contract for which is authoritative, or whether
both are guaranteed to always agree and both keep being emitted going forward. NUIAK's ingestion
script currently reads only the snake_case set (confirmed correct via
`HarvestSceneElement.encode(to:)` in source) — but that required reading source, not docs.
**Request:** a short note (even just a code comment near the dual-encode) on which set is
canonical and whether the alias set is a permanent contract or a transitional shim.

## 6. Real hardware harvest has still never been run (tracked, not new)

Not new today, but the standing blocker for anything beyond the Simulator: `Docs/Testing/
2026-09-18-nua-harvest-unblock.md` in TVTestRig is explicit that no live "office" harvest has
been executed. Full detail lives in NUIAK's own `Tasks.md` (TASK-6a-10). Listed here only so
this document is a complete picture of every open item, not because it needs restating in depth.

---

## Carried forward from the earlier real-hardware RCA session

Full detail and context: [`tvos_navigation_rca_and_safety_architecture.md`](tvos_navigation_rca_and_safety_architecture.md)
§3 ("Comprehensive TVTestRig Friction & Inconsistency Log"). Status column added here since
some of these may already be resolved by the FIX-SYNTH work — we have not re-verified each one.

| # | Issue | Status as of 2026-09-18 |
|---|---|---|
| A | `aatv observe capture` sandboxing/`persistenceFailed` writing to workspace paths directly | Not re-verified this session |
| B | `aatv remote` inconsistent syntax (`navigate <dir> --count <N>` required; `press down` / bare `navigate down` fail) | Not re-verified this session |
| C | Missing `--help` on subcommands | **Appears resolved** — `aatv --help`, `aatv fixture --help`, `aatv fixture batch --help` all returned clear, correct usage today |
| D | `unsupportedCapability` on core primitives (`app launch`, `remote hold home`) over wireless routes | Possibly related to §1/§2's `unsupportedCapability`, but that was over a Simulator+local-HTTP path, not wireless — likely a distinct occurrence of the same error code, not confirmed the same root cause |
| E | `observe wait-stable` high latency (600–1200ms/step) | Not re-verified this session |
| F | `observe inspect` fragile hardcoded template matching (only the 1080p English dark Settings root) | Not re-verified this session |
| G | `TVTestRigFixture` lacked a focus/accessibility telemetry server | **Resolved** — this is exactly what FIX-SYNTH-02 shipped; confirmed working live today |
| H | No built-in gesture macros (double-home app switcher, Control Center slide-over) | Not re-verified this session |

---

## What's working well (worth saying, not just the friction list)

- `FixtureRecipe`/`ProceduralSceneBuilder`/kitchen-sink archetypes (FIX-SYNTH-01/04) produced a
  real, populated `GET /scene` response on the very first try on the Simulator — media_shelf
  recipe, 8 elements, correct 1920×1080 frame size, full per-element geometry.
  Full-frame `GET /scene` no longer returns empty `elements` (the fix explicitly aimed at
  unblocking NUIAK, per the commit that shipped it, worked).
- `aatv --help` and subcommand `--help` are now genuinely useful — a real improvement over the
  RCA-era complaint (item C above).
- The on-disk format, once correctly identified from source, is internally consistent and
  matches the documented coordinate convention (`[xMin, yMin, xMax, yMax]`, top-left origin) —
  NUIAK's ingestion script needed zero changes to its coordinate math across either format
  revision, only to file-discovery/field-name logic.

---

*Session artifacts referenced above: tvOS 26.5 Simulator (build 23L470, device `Apple TV 4K
(3rd generation) (at 1080p)`), `TVTestRigFixture` app_version 1.0. Simulator was booted with the
maintainer's explicit go-ahead after an earlier session accidentally read from a pre-existing,
unrelated simulator instance — noted here as the reason this document tracks exact OS
build/version per the maintainer's standing instruction to always know which OS build produced
any data.*
