# REAL543 — Independent application preparation

Owner: Maximum-mini-NUIAK. Reuse SDK539-APPS.
No application currently satisfies every independent benchmark gate.
Build success does not establish SDK correctness or model accuracy.

| Application | Source build | Runtime evidence | Next requirement |
| --- | --- | --- | --- |
| NewsTV | Pass | XCTest captures 1 pilot case; SDK returns 23 rectangles but reports inactivity | Resolve lifecycle disagreement, review pixel alignment and complete labels |
| Swiftfin | Pass | Not tested | Controlled Jellyfin content and SDK integration |
| WeatherFeels | Blocked | Not tested | Apple Metal toolchain; preserve shader behavior |
| Photo Guessing Game | Pass | Not installed or launched | SDK integration and runtime qualification |
| Fifth application | Not selected | None | Distinct source ancestry and reproducible tvOS build |

## Game source intake

Repository: https://github.com/geoffmyers/photo-guessing-game-tvos
Revision: `d1cfe353667c124672e9b7bf929feab35c69a46f`.
The repository declares GPL-3.0-or-later. Preserve its license.
The project has one SwiftUI application target and no external package dependencies.
The generic arm64 tvOS Simulator Debug build passes without source changes.
Private receipt: `reports/work/REAL543/photo-game-build-receipt.json`.
Private build log: `reports/work/REAL543/photo-game-build.log`.

The existing demo uses generated placeholders and named locations. It does not require personal photos.
Do not use the photo-library route or external geocoding for the controlled pilot.
Do not use repository screenshots as benchmark images.
The demo currently randomizes dates, UUIDs, answer choices, and photo order.
Placeholder colors use Swift hash values. Stable UUIDs alone do not make those colors reproducible.
Pin dates, identities, answer lists, photo order, calendar settings, and a stable color index before capture.
Keep the original view layout and focus behavior. Record any controlled-content changes in the source receipt.

## Predetermined game coverage

Select capture points before viewing model predictions.
Use these candidate flows after SDK and content qualification:

1. Player setup: player entry and game-mode controls.
2. Date game: year choices, month choices, and calendar grid.
3. Location game: country, state, and city choices.
4. Feedback: correct answer, incorrect answer, and next-turn control.
5. Completion: winner view and restart control.

Each flow retains one group identity across related screens.
Pilot flows cannot supply the later independent benchmark.
The game may provide fewer than 8 genuinely distinct qualification flows. Report that limit instead of duplicating flows.
Do not assume a genuine no-focus state exists. Verify it through active-scene evidence and human review.

## Remaining acceptance checks

- Audit source ancestry and training exposure before independent admission.
- Attach SDK hooks without changing the native focus behavior.
- Verify observed focus, visible bounds, clipping, and missing registrations.
- Review all visible controls without model predictions.
- Record ambiguous labels and incomplete coverage explicitly.
- Keep execution failures in the capture manifest.

Standard, shipped models, and the detached runner remain unchanged.


## Controlled game data — implemented

The Debug-only content mode fixes demo dates, identities, choices, ordering, calendar calculations, and placeholder colors.
It replaces photo-library loading with demo data while the mode is enabled.
Normal behavior and Release behavior remain unchanged.
Two separate process checks produce identical content output. The Simulator build passes.
The patch and checks are in `scripts/sdk539/photo-game/`.
Animations, confetti, runtime locale, SDK observations, and image alignment remain qualification requirements.
No application is installed or launched by this preparation step.

## October 30 readiness recheck

NewsTV repeats the bounded metadata trial with the published TTR helper.
All 3 observations remain inactive with unknown focus. Cleanup passes; no captures or navigation inputs occur.
The intended Simulator is ready with clear ownership.
The standard Simulator frontend path is absent in this Xcode installation. DeviceHub is present.
A supported foreground route remains unqualified. No system component is downloaded to bypass this gap.
The new evidence is sent through BigDog-Coordinator at cursor 1818. Forwarding remains unconfirmed.

## NewsTV capture progress

NUIAK's existing XCTest target now verifies foreground state and captures the initial controlled-content screen.
The test leaves no NewsTV process running. A second enrolled trial retains authenticated SDK geometry.
Two screenshots represent one predetermined case. Nine NewsTV cases remain planned.
A prediction-free draft contains 23 registered rectangles. Human review must verify full visible coverage and alignment.
SDK inactivity disagrees with XCTest foreground state. Focus remains unknown and unscored.
The application remains partially qualified. See REAL550 for exact receipts and the review link.

## Benchmark app approval — 2026-10-31

The maintainer approves NewsTV (MIT), Swiftfin (MPL-2.0), and Photo Guessing Game (GPL-3.0-or-later) as REAL543 benchmark apps.
These apps are evaluation-only. They do not supply training data. A separate training pool uses different apps.
Code licenses do not cover displayed media or text. Use controlled content: own images, openly licensed media, and fixed data.
WeatherFeels (MIT) stays a candidate. It needs the Metal toolchain, which is a system download that needs separate approval.

## 5th app candidates — public repository check, 2026-10-31

This check reads the public GitHub pages only. No source is cloned or built.

| Candidate | License | tvOS target | Build needs | Screens without content | Assessment |
|---|---|---|---|---|---|
| Moonlight (moonlight-stream/moonlight-ios) | GPL-3.0 | Yes, "Moonlight TV" | Xcode project, recursive Git submodules (moonlight-common, X1Kit), local signing team | Not documented. Streaming needs a host PC with Sunshine or GameStream | Smaller build. Host list, add-host entry, and settings may work without a host. Verify after source intake. |
| Provenance (Provenance-Emu/Provenance) | Project license plus GPL, LGPL, MIT, and BSD cores | Yes, "ProvenanceTV", tvOS 16+ | Xcode workspaces, Tuist, submodules, vendored cores, MoltenVK | Not documented. The library needs imported ROMs; no licensed homebrew content is listed | Large build. Content rights for a filled library are unresolved. |

Recommendation: do the source intake for Moonlight first. Keep Provenance as the reserve.
A Moonlight case set needs controlled screens without a host. A local Sunshine host is a separate decision.

