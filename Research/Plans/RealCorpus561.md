# REALCORPUS561 — SDK-qualified real-app corpus for tvOS

Date: 2026-11-02. Owner: Maximum-mini-NUIAK. Task authority: Tasks.md, RC561. Parents: REAL543, REALAPP554, RA557-08.
Requested by the maintainer, 2026-11-02: "a much larger corpus of real-world open source app validation sets beyond just NewsTV
that have been validated with the SDK for their ability to produce accurate training data."
This plan admits no job, clones nothing and captures nothing until the maintainer decisions below are made.

## Goal

Build a corpus of open-source tvOS apps. In each app, TTR's TTRDiagnostics SDK reports control rectangles, classes and focus.
An app enters the corpus only after its SDK output passes a measured accuracy check against human review.
Then SDK output can label new frames of that app automatically, with a small audited sample instead of full review.

Target: at least 8 SDK-qualified apps, 60 distinct flows and 600 frames. NewsTV, Photo Guessing Game and Swiftfin count toward the target.

## Why the SDK check matters

The NewsTV pilot review confirmed 207 of 207 SDK rectangles. 1 app is not enough evidence that SDK labels are accurate in general.
SDK labels can fail in 4 ways. Each needs a measured gate:

1. Missing controls: a visible control has no registration.
2. Wrong geometry: the rectangle is offset, scaled, or covers the wrong layer (for example, the focus glow or the text only).
3. Wrong class: the SDK role does not match the visible control.
4. Wrong state: focus or visibility does not match the frame (NewsTV reported "inactive" scenes).

## SDK qualification gate (per app)

Capture 10 qualification frames from at least 4 flows. The maintainer reviews them with the validate-and-flag page (REALAPP554).

| Measure | Gate |
|---|---|
| Coverage: reviewed visible controls with an SDK rectangle | ≥ 95% |
| Geometry: SDK rectangle IoU against the reviewed box | median ≥ 0.90; ≥ 95% of boxes at IoU ≥ 0.75 |
| Class: SDK role equals the reviewed role (13 roles, ROLES559) | ≥ 98% |
| Focus: SDK focused control equals the reviewed focused control | 10 of 10 frames, or explicit "no focus" agreement |
| Pixel alignment: SDK coordinates map to captured pixels (scale, safe area, overscan) | exact mapping rule recorded |
| Stability: repeated capture of 1 frame gives the same SDK output | identical rectangles |

An app that fails stays evaluation-only with full human review, or leaves the corpus. Record the failure mode.
A qualified app then needs a sampled audit: 1 reviewed frame per 10 auto-labeled frames. A failed audit removes the qualification.

## Candidate apps

| App | UI | License | Content source | Value | Risk |
|---|---|---|---|---|---|
| NewsTV (have) | SwiftUI | per repo | bundled data | tabs, pills, cards | SDK scene reports inactive |
| Photo Guessing Game (have) | SwiftUI | GPL-3.0 | demo placeholders | game choices, grids | randomness must be pinned |
| Swiftfin (have) | SwiftUI | MPL-2.0 | Jellyfin server | media shelves, settings | needs a local server |
| Apple "tvOS media catalog app in SwiftUI" sample | SwiftUI | Apple sample license | bundled | shelves, lockups, buttons, search, sidebar tabs | close to generic patterns; audit training exposure |
| Provenance | UIKit and SwiftUI | BSD-3 | local ROM-free menus | game grids, settings, lists | large build; emulator cores |
| Moonfin tvOS | SwiftUI | per repo | Jellyfin or Emby server | media shelves, Top Shelf | needs a server |
| Plozz | SwiftUI | per repo | Jellyfin, Plex, Emby or local share | media browser | needs a server or share |
| Strimr | SwiftUI | per repo | Plex or Jellyfin | media browser | requires tvOS 26 |
| VLC for iOS/tvOS | UIKit (Obj-C, Swift) | GPL-2 / MPL-2 | local files | file lists, player | CocoaPods install needed |
| Apple-TV-Player (m3u IPTV) | UIKit | per repo | local m3u file | channel lists | low activity |

Exclude apps that need a live service account (Twitch, YouTube, broadcast streams): their content changes and needs credentials.
Check license, activity and build before intake. Older list entries (iCook TV, Telemat) likely fail current SDKs.

## Steps

### C1 — Source intake (about 1 h per app)
Clone the pinned revision into `dataset/real_apps/sources/<app>`. Record license, revision, dependencies and a build receipt (REAL543 format).
Audit training exposure: no app pixels or layouts in synthetic training; note generic patterns (Apple sample).
Build for the tvOS Simulator with project-local caches. No CocoaPods or other installs without approval.

### C2 — Controlled content (0.5–3 h per app)
Pin data, randomness, dates and order (Photo Guessing Game rules). Media-server apps need 1 shared local Jellyfin server with generated media.

### C3 — SDK hooks (1–3 h per app)
Add TTRDiagnostics registration as in `scripts/sdk539/newstv/`. Keep app behavior and focus unchanged.
Keep each patch, vendored file hashes and build receipt in `scripts/sdk561/<app>/`.

### C4 — SDK qualification (1 h agent, about 15 min maintainer review per app)
Capture 10 frames. Draft review from SDK output. Maintainer validates and flags. Compute the gate table. Record pass or fail.

### C5 — Corpus capture (1–2 h per qualified app)
Capture flows with TTR, write SDK labels, run the 1-in-10 audit. Group frames by flow; keep pixel-unique frames only.

### C6 — Data roles
Assign roles by app, never by frame: at least 3 apps form a frozen holdout (RA554-13). The others are development, or training if approved (decision D2).

## Maintainer decisions

- D1: approve Git clones of the candidate repositories (source only, built locally). AGENTS.md grants no new download authority.
- D2: data role. Current rule: real apps are evaluation-only. Option: SDK-qualified apps outside the holdout become training sources.
- D3: approve a local Jellyfin server install for the 4 media-server apps, or skip those apps.
- D4: approve CocoaPods for VLC, or skip VLC.

## Decisions — maintainer, 2026-11-02

- D1: approved. Clone all candidates except VLC (source only, built locally).
- D2: approved. SDK-qualified apps outside the frozen holdout (at least 3 apps) may supply training data.
  This replaces the "real apps are evaluation-only" rule for qualified apps only. Holdout apps and the spent NewsTV pilot stay out of training.
- D3: approved. Install a local Jellyfin server with generated media.
- D4: VLC skipped.

## Direction change — maintainer, 2026-11-02 (later)

"How well can we make a corpus of 100 varied screens from these open source apps not for training but validation and analysis."
- D2 is withdrawn for this corpus. All real-app frames are evaluation-only (validation and analysis). No real-app pixels enter training.
- Target: 100 layout-distinct screens. A focus move on the same layout does not count as a new screen.
- Labels: draft boxes from the accessibility hierarchy (XCUITest element frames) or the SDK, then maintainer validate-and-flag review.
  SDK qualification stays for apps where focus truth matters. It is not a gate for entry into the validation corpus.

Screen estimate (layout-distinct, before capture; unverified):

| Source | Screens | Condition |
|---|---|---|
| NewsTV | 10 | have |
| Photo Guessing Game | 8 | pinned demo content |
| Apple tvOS media catalog sample | 8 | source download |
| Swiftfin, Moonfin, Plozz, Strimr | 40–48 | local Jellyfin with generated media; Strimr needs tvOS 26 |
| Provenance | 6–8 | menus and settings only; no ROM download |
| Apple-TV-Player | 4 | local m3u file |
| tvOS Simulator system apps (Settings, Search) | 10–15 | read-only navigation (tvos-safe-navigation); no settings change |
| Total | 86–101 | |

Intake state: Plozz (278ba3a) and Strimr (3c876fb) are cloned. Provenance is a partial folder from an interrupted clone. Moonfin is not cloned.

Training sources reviewed (2026-11-02):
- No public annotated tvOS screen dataset exists in the search results.
- ScreenSpot (Apache-2.0) has iOS and macOS screens, but each image labels 1 target only. Incomplete labels make it unusable for detector training.
- GUIrilla (real macOS) is CC-BY-NC-4.0: non-commercial only. MolmoPoint-GUISyn is synthetic and carries third-party model terms.
- RICO and MobileViews are Android (already rejected in NativeUIElementDetection §15).
- Apple's Figma UI kits list iOS, macOS, watchOS and visionOS, not tvOS. Use needs Apple's design-resources license. Do not use them for training until that license is read.
- Recommended training sources: the synthetic generator, the TTR Fixture, and SwiftUI component code rendered with `captureFrame` (labels by construction).

## Time

Intake and SDK work: about 4–8 h per app. For 7 new apps: about 30–50 h of agent work, over several sessions.
Maintainer review: about 15 min per app for qualification, plus audits. Slow steps: builds, server setup, capture.

## Intake status and open conflict — 2026-11-02 01:40 (Maximum-mini-NUIAK, original session)

Ownership: the original session owns RC561 intake in `dataset/real_apps/sources`; the forked session stopped writing there.

| App | Revision | State |
|---|---|---|
| Apple tvOS media catalog sample | zip sha256 b234e9bb… | builds unchanged (scheme TVCatalog) |
| Strimr | 3c876fba | blocked: prebuilt binary frameworks (FFmpegBuild, LibDovi, LibTrueHD, Sentry); build stopped, fetched Sentry binary removed from `.build` |
| Plozz | 278ba3ad | blocked: 4 binary targets in Package.swift, and XcodeGen install |
| Apple-TV-Player | d9ad0866 | blocked: CocoaPods |
| Provenance | b6069a29 (shallow) | not built; `provenance-src` is a duplicate (2.6 GB) |
| Moonfin | — | excluded: tvOS repository gone; Moonfin-Core is Flutter |

Jellyfin: `/Applications/Jellyfin.app` already exists (installed 2025-11-01). No install was needed or made.

Open conflict: D2 (this session: qualified non-holdout apps may supply training data) and the "Direction change" above
(forked session: validation-only, 100 layout-distinct screens) are both recorded as maintainer direction. The maintainer must confirm which applies.

## Decision — maintainer, 2026-11-02: prebuilt media frameworks

"Allow prebuilt FFmpeg." Strimr and Plozz may use the prebuilt binary frameworks that their own package manifests pin (FFmpeg, LibDovi, LibTrueHD).
Record each fetched framework name, URL and checksum in the build receipt. Fetch them only through the app's own manifest.
This decision does not approve the XcodeGen install for Plozz, CocoaPods for Apple-TV-Player, or other tools. (Superseded for XcodeGen: the maintainer approved XcodeGen in the original session at 07:30; see the next section.)
Real-app frames stay evaluation-only.

## Decisions and intake — 2026-11-02 07:45 (original session)

Maintainer answers: validation-only, about 100 layout-distinct screens (the "Direction change" stands; D2 withdrawn);
prebuilt binary frameworks allowed for Strimr and Plozz only; XcodeGen approved (installed, 2.46.0); CocoaPods not approved, so Apple-TV-Player is skipped;
`provenance-src` deleted (duplicate of `provenance`, b6069a29).

Jellyfin: `/Applications/Jellyfin.app` is the Jellyfin client from the App Store (1.7.0), not a server. It is unchanged.
The server (cask 12.4) is installed in `.build/rc561/apps/Jellyfin.app`. `.build/rc561/run-jellyfin.sh` runs it with project-local data,
config, cache and logs, bound to 127.0.0.1:8096 with remote access, UPnP and discovery off.
Test user `rc561-test` (generated password in ignored `.build/rc561/jellyfin-test-user.json`). Libraries: Movies and Shows, internet metadata off.
Media: `scripts/rc561_media.py` → `dataset/real_apps/jellyfin-media` (24 movies, 2 series, 24 episodes, generated, seed 561, 6.8 MB).
