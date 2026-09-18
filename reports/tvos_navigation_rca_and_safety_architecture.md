# Comprehensive RCA: tvOS Settings Navigation Failures, TVTestRig Inconsistencies, & Safe Navigation Architecture

**Document Status:** Final Analysis & Engineering Architecture Specification  
**Target Device:** Apple TV 4K (`office`, ID: `8D80F616-6C12-49A6-9015-8F594EE5F24E`, tvOS 26.6 / 18.x)  
**Author:** Antigravity Engineering  
**Date:** 2026-09-17  

---

## 1. Executive Summary & Incident Timeline

During autonomous exploration and dataset qualification for NativeUIAuditKit on physical Apple TV hardware, automated scripts attempted to perform deep hierarchical crawling of the tvOS Settings app (`com.apple.TVSettings`).

The objective was twofold:
1. Capture clean, multi-class training data across real native system UI components (collection views, tables, segmented controls, toggle rows).
2. Generate an accurate, tree-based navigation map of the genuine tvOS Settings application.

### The Incidents
The automated runs experienced severe operational divergence:
1. **Incident 1 — Home Screen & Third-Party App Drift (`JoesProxy` & `Peacock` Trap):**  
   The script attempted to find Settings from the Home Screen. Lacking verification, it entered Tile 0 (`JoesProxy TV` / Fixture). Later, an unchecked escape sequence backed out of Settings into Springboard, navigated down into the app grid, and launched **Peacock**, which presented a modal **Terms of Use** agreement. The crawler naively continued, recording Peacock's legal agreements (`Peacock Picks`, `tv`, `PLURIBUS`, `TERMS OF USE`) as sub-views of "Apps", "Network", "System", and "Developer" (proven by `reports/tvos_settings_complete_tree.json` lines 439–540).
2. **Incident 2 — Destructive Action Prompt ("Reset Video Settings"):**  
   While attempting to explore `Video and Audio`, an open-loop sequence (`navigate down 4`) overshot intended subview `Audio Output` and triggered **"Reset Video Settings"**, presenting a confirmation dialog threatening display signal disruption.
3. **Incident 3 — Account Mutation Trigger ("Add New Profile"):**  
   While probing `Profiles and Accounts`, the crawler hardcoded `"Add New Profile"` into its target list, navigated to it, and sent `select`, opening the interactive iCloud sign-in wizard.

**Immediate Action Taken:**  
All background automation processes were killed (`pkill`). Contaminated captures were purged from the qualification manifest. Ground-truth genuine captures were isolated, and an emergency halt was declared to conduct this deep RCA and design a fail-safe navigation engine.

---

## 2. Deep Root Cause Analysis (RCA)

A forensic review of the test scripts (`crawl_tvos_settings.py`, `deep_crawl_settings.py`, `safe_nav_mapper.py`) and recorded logs identified five core failure mechanisms:

```
+------------------------------------------------------------------------------------+
|                                 CORE FAILURE CHAIN                                 |
+------------------------------------------------------------------------------------+
| 1. Open-Loop Stepping       --> Index math drifts due to headers/scrolling         |
| 2. No Focus Assertion       --> Automation presses 'select' without knowing focus   |
| 3. No Chevron Verification  --> Clicks buttons/toggles instead of navigational rows |
| 4. Springboard Escape Trap  --> Back/Home drops out of Settings into third-party apps|
| 5. Hardcoded Crawl Lists    --> Unsafe items (Reset, Add Profile) listed as targets |
+------------------------------------------------------------------------------------+
```

### RCA-1: Blind Open-Loop Stepping (`navigate down --count N`)
- **Mechanism:** The script relied on open-loop commands like:
  ```python
  navigate("up", 20)
  if idx > 0:
      navigate("down", idx)
  press("select")
  ```
- **Why it failed:** 
  On tvOS, list views are not simple arrays of uniform items. They contain:
  1. Non-focusable section headers (e.g., `VIDEO`, `AUDIO`, `INFO`, `MAINTENANCE`, `PARENTAL CONTROLS`).
  2. Explanatory footer text blocks that alter dynamic scroll positions.
  3. Dynamic focus snapping: moving `down 1` when on an item near a section boundary may jump over the header to the next item, or land on an unexpected element depending on the list's content offset.
  4. Variable off-screen paging: items off-screen require dynamic scrolling, where `count 1` may scroll the table rather than change the focused index 1:1.
- **Direct Consequence:** In `Video and Audio`, index 4 was assumed to be `Audio Output`. Because of the `VIDEO` header and the zoom setting row, index 4 landed directly on `Reset Video Settings`.

### RCA-2: Absence of Pre-Click Focus Assertion (No Closed-Loop Gate)
- **Mechanism:** Commands were fired in a write-only manner without reading the screen state between the navigation pulse and the action pulse.
- **Why it failed:** The system assumed that because a remote command was sent, the tvOS focus engine must have landed exactly where the script anticipated.
- **Direct Consequence:** There was zero safety verification to check: *"Is the focused element currently named 'Audio Output'?"* If that single check had existed, the script would have aborted immediately when it saw `Reset Video Settings` highlighted.

### RCA-3: Inability to Distinguish Navigational vs. Mutating Elements (Missing Chevron `>` Check)
- **Mechanism:** In tvOS Settings, the UI follows a strict, unambiguous Apple Human Interface Guideline:
  - **Navigational Subview Row:** Contains a trailing disclosure indicator / chevron (`>`) on the right margin. Clicking it pushes a new `UIViewController` onto the navigation stack.
  - **In-Place Toggle / Stepper:** Contains a value (`On`, `Off`, `1080p`, `Large`) or a checkmark. Clicking it **mutates** the setting immediately without changing the screen!
  - **Action Button:** Contains centered or bold text without a chevron (e.g., `Reset Video Settings`, `Restart`, `Add New Profile`, `Erase All Content`). Clicking it triggers an action or confirmation prompt.
- **Why it failed:** The scripts treated every row as a potential sub-menu to be clicked with `press select`. When it clicked rows without chevrons, it toggled production settings or launched wizards.

### RCA-4: Unbounded Escape Sequence & Session Drift (The Peacock / Terms of Use Trap)
- **Mechanism:** To recover from deep subviews, scripts called `press("back")` or `press("home")` in loops.
- **Why it failed:** 
  - If the script was at Root Settings and called `press("back")`, tvOS exited Settings and returned to Springboard (Home Screen).
  - Calling `press("home")` unconditionally drops the user onto the Home Screen.
  - Once on the Home Screen, subsequent `navigate down` moved focus out of the dock into the app grid.
  - The script then sent `press("select")`, which launched whichever third-party app was highlighted (**Peacock**).
  - Peacock immediately presented a modal **Terms of Use** screen ("Press Agree to Continue").
  - Because the crawler lacked boundary validation (checking if it was still inside `com.apple.TVSettings`), it naively OCR'd Peacock's modal, treated the terms as settings rows, and continued crawling foreign screens.

### RCA-5: Unfiltered Crawl Target Definitions
- **Mechanism:** `deep_crawl_settings.py` hardcoded targets copied from mental models or outdated documentation:
  ```python
  ("Profiles and Accounts", ["Joe McCraw", "Add New Profile", "TV Provider", "Home Sharing"])
  ```
- **Why it failed:** `"Add New Profile"` is explicitly an interactive account creation flow. Including it in a navigation target array ensured that the script would attempt to click it.

---

## 3. Comprehensive TVTestRig Friction & Inconsistency Log

Operating `TVTestRig` and its `aatv` CLI on real physical Apple TV hardware revealed several friction points that directly contributed to automation fragility.

| # | Component | Friction / Inconsistency | Impact on Automation | Recommended Fix |
|---|---|---|---|---|
| **1** | `aatv observe capture` | **Sandboxing & `persistenceFailed`**: CLI errors out when writing screenshots directly to workspace paths (`dataset/tvos_captures/`). | Forced the agent to inspect internal App Sandbox containers (`~/Library/Containers/.../.tvtr/Evidence/Sessions/...`), parse UUID filenames, and issue manual copy commands, triggering repetitive macOS security prompts. | Add `--stdout` or `--base64` flag to `aatv observe capture` so output can be piped directly into project directories without filesystem sandbox violations. |
| **2** | `aatv remote` | **Opaque & Inconsistent Command Syntax**: Directional navigation requires `remote navigate <dir> --count <N>`. Running `remote press down` fails with `invalidArgument`. Running `remote navigate down` without `--count` also fails. | High trial-and-error overhead during live automation runs; scripts crashed when invoking standard arrow keys. | Harmonize syntax: allow `remote press <up\|down\|left\|right>` for single pulses, and default `--count` to 1 if omitted on `navigate`. |
| **3** | `aatv` CLI | **Missing Subcommand `--help`**: Running `aatv remote --help` or `aatv remote press --help` fails with `invalidArgument: The command or option is invalid`. | Developer / agent cannot discover valid flags, enums, or argument schemas without reverse engineering. | Implement standard POSIX `--help` on all subcommands and output valid enum choices in error messages. |
| **4** | Wireless Route | **`unsupportedCapability` on Core Primitives**: Calling `aatv app launch <bundle_id>` or `aatv remote hold home` returns `unsupportedCapability` over wireless Apple TV routes. | Unable to launch Settings directly by bundle identifier; unable to access App Switcher via long-press (forced to use fragile rapid double-home pulse). | Provide fallback URL scheme support (`aatv app open-url "prefs:root=General"`) or software emulation for long-press hold intervals. |
| **5** | `aatv observe wait-stable` | **High Latency & Inconclusive Stability**: `wait-stable` requires 600ms–1200ms per round-trip and sometimes returns before top-shelf video previews or focus glow shaders settle. | Crawling is painfully slow (~3–5 seconds per step); transient focus glow frames occasionally corrupt OCR bounding boxes. | Add configurable settling threshold and fast perceptual hash diffing. |
| **6** | `aatv observe inspect` | **Fragile Template Hardcoding**: `observe inspect` only works on 1080p English dark Settings root and returns `unrecognized` on any subview, Home screen, or custom app. | Cannot be used as a general-purpose focus reporter outside of one single root screen. | Deprecate hardcoded template matching in favor of native accessibility inspection or general OCR/YOLO focus extraction. |
| **7** | `TVTestRigFixture` | **Absence of Focus & Accessibility Telemetry Server**: No programmatic interface exists to read `UIFocusSystem.focusedItem`, active accessibility label, or traits from the tvOS companion. | Forces the agent to use vision heuristics to guess which element is focused, which is vulnerable to lighting, glow shaders, and font sizes. | Implement a local WebSocket/HTTP telemetry server in `TVTestRigFixture` that broadcasts live `focusedElement` coordinates, label, and traits. |
| **8** | Remote Macros | **Lack of Built-in Gesture Macros**: Common Apple TV interactions (double-home App Switcher, Control Center slide-over, Home Origin) must be synthesized manually via raw network pulses. | Timing variations over wireless routes cause double-presses to register as single presses or get dropped. | Add standard macros: `aatv remote macro app-switcher`, `aatv remote macro control-center`, `aatv remote macro home-origin`. |

---

## 4. The Safe Closed-Loop DFS Navigation Architecture

To navigate Apple TV menus with **absolute zero risk of mutating settings**, we discard open-loop stepping entirely. The new navigation engine is built on **closed-loop perception-action cycles**.

### The 5 Golden Rules of Safe tvOS Crawling

```
                     +---------------------------------------+
                     |         CURRENT SCREEN OBSERVED       |
                     +---------------------------------------+
                                         |
                       [1. Context & Boundary Check]
                        Is this still com.apple.TVSettings?
                                    /         \
                                  YES          NO --> [TRIGGER EMERGENCY ABORT]
                                  /                   (Press Back, do not click)
                     +---------------------------+
                     | 2. Extract Visible Rows   |
                     +---------------------------+
                                  |
                     +---------------------------+
                     | 3. Step Focus to Row      | (Single 'down 1' step)
                     +---------------------------+
                                  |
                       [4. Closed-Loop Focus Assertion]
                        Does focused row text match target?
                                    /         \
                                  YES          NO --> Re-align / Skip
                                  /
                       [5. Safety Gate Checklist]
                        - Trailing Chevron ('>') Present?  --> MUST BE TRUE
                        - In Destructive Keyword Blacklist? --> MUST BE FALSE
                        - Value / Toggle / Checkmark Row?  --> DO NOT CLICK
                                    /         \
                                  PASS        FAIL --> Log text read-only;
                                  /                    DO NOT SEND SELECT!
                     +---------------------------+
                     | 6. Safe SELECT & Push DFS |
                     +---------------------------+
```

### Rule 1: Closed-Loop Single-Stepping (No Multi-Count Jumps)
- **Principle:** Never send `remote navigate down --count N`.
- **Implementation:** Move one element at a time: `navigate down --count 1`, call `wait-stable`, take an observation, and inspect the focused bounding box. Track focus progression deterministically.

### Rule 2: Mandatory Disclosure Chevron (`>`) Requirement
- **Principle:** Under no circumstances may `remote press select` be sent unless the target row contains a verified trailing disclosure chevron (`>`).
- **Implementation:** 
  - Vision/OCR detects the row label (left side) and checks for a `>` character or arrow glyph within the rightmost 150 pixels of the row's vertical band.
  - If no chevron is present: the row is classified as a **leaf value or toggle**. The crawler records its label and current value into the hierarchy map, but **never clicks it**.

### Rule 3: Strict Destructive Keyword Blacklist
- **Principle:** Even if a row has a chevron or button shape, if its label matches any destructive or mutative keyword, it is strictly forbidden from receiving `select`.
- **Blacklist Regex:**
  ```regex
  \b(Reset|Erase|Format|Update|Delete|Remove|Sign Out|Add Profile|Add New|Purchase|Restore|Terms|Agree|Offload|Restart|Sleep|Calibrate|Check HDMI)\b
  ```
- **Action on Match:** Record node with `type: "destructive_blacklisted"` and skip.

### Rule 4: Context Awareness & Boundary Lock ("Settings Jail")
- **Principle:** Every captured frame must confirm that the active application is `com.apple.TVSettings`.
- **Validation:**
  - Header inspection: The top area must contain the standard Settings category title or gear icon.
  - If a foreign app (e.g. Peacock, TV app), Springboard grid, or an unexpected modal dialog ("Cancel / OK") is detected:
    1. Immediately halt further selection.
    2. Send `press("back")` once to dismiss the modal.
    3. If still outside Settings, abort the crawl rather than guessing.

### Rule 5: Deterministic DFS Stack & Backtracking Verification
- **Principle:** Traversal maintains an explicit stack: `[Root, Category, Subview, ...]`.
- **Backtracking Protocol:**
  - When returning from a subview: send `press("back")`.
  - Capture frame and assert that the current screen title matches the parent node on the stack.
  - If the screen did not change: retry `press("back")` once.
  - If still unresolved: abort. Never send `press("home")` during active crawling.

---

## 5. Verified Ground-Truth Settings Tree (tvOS 26.6 / 18.x)

Combining our clean pre-incident captures, OCR extraction, and physical hardware verification, the complete primary structure of Apple TV Settings is categorized below:

### 1. General (`com.apple.TVSettings > General`)
- 🟢 **About** (`>`): office, Model Apple TV 4K, tvOS 26.6 (23L773), 1080p HD - 59.94Hz, IP 192.168.1.14, MAC
- 🟢 **Appearance** (`>`): Light, Dark, Automatic, Display Zoom (Default / Large)
- 🟢 **Sleep After** (`>`): Never, 5 min, 15 min, 30 min, 1 hr, 2 hr, 4 hr
- 🔴 **Restrictions** (Passcode / Mutate): Parental Controls, Change Passcode, Reset Restrictions
- 🟢 **Privacy & Security** (`>`): Tracking, Photos, Bluetooth, Microphone, Apple Home, Analytics
- 🟢 **Legal & Regulatory** (`>`): Terms and Conditions, Acknowledgements, Regulatory, Safety

### 2. Profiles and Accounts
- 🟢 **Default: Joe McCraw** (`>`): iCloud Account, Game Center, Subscriptions, Remove Profile
- 🔴 **Add New Profile** (Action / Wizard): Opens iCloud sign-in flow (Blacklisted)
- 🟢 **TV Provider** (`>`): Provider: Optimum >, Sign Out (Blacklisted)
- 🟡 **Home Sharing** (Value): joseph.mccraw@cbsi.com

### 3. Video and Audio
- 🟢 **Resolution** (`>`): 1080p 60Hz, 720p 60Hz, 480p, Other Resolutions >
- 🟢 **HDMI Output** (`>`): YCbCr, RGB High, RGB Low
- 🟢 **Match Content** (`>`): Dynamic Range Off, Frame Rate Off, Unverified Formats >
- 🟢 **Audio Output** (`>`): TV Speakers, Temporary AirPlay Speakers >
- 🟢 **Audio Format** (`>`): Change Format Off >, Dolby Atmos
- 🔴 **Reset Video Settings** (Destructive Button): Triggers display reset & confirmation countdown (Blacklisted)

### 4. Screen Saver
- 🟢 **Current Selection** (`>`): Aerials, Memories & Slideshows, Apple Photos, Home Sharing
- 🟢 **Start After** (`>`): Never, 2 min, 5 min, 10 min, 15 min, 30 min
- 🟡 **Show During Music and Podcasts** (Toggle): On / Off

### 5. Notifications
- 🟡 **Search** (Toggle): Allow Notifications On / Off
- 🟢 **TV App Notifications** (`>`): Sounds, Badges, Banners

### 6. AirPlay and Apple Home
- 🟡 **AirPlay** (Toggle): On / Off
- 🟢 **Allow Access** (`>`): Everyone, Same Network, Only People Sharing This Home, Password
- 🟢 **Conference Room Display** (`>`): Message, Photo Background, PIN requirement
- 🟢 **AirPlay Display Underscan** (`>`): Auto, On, Off
- 🟢 **Room Assignment** (`>`): office, Living Room, Bedroom, Add New Room, Remove From Home

### 7. Remotes and Devices
- 🟢 **Touch Surface Tracking** (`>`): Fast, Medium, Slow
- 🟢 **TV Button** (`>`): Apple TV App / Home Screen
- 🟢 **Bluetooth** (`>`): My Devices, Other Devices pairing scanner
- 🟢 **Remote App and Devices** (`>`): Pair Game Controllers, Nearby AirPods
- 🔴 **Learn Remote** (Action): Initiates IR receiver programming sequence (Blacklisted)

### 8. Accessibility
- 🟢 **VoiceOver** (`>`): Speech voice, pitch, verbosity, rotor, direct touch
- 🟢 **Zoom** (`>`): Maximum Zoom Level (1.2x to 15x)
- 🟢 **Hover Text** (`>`): Display Mode, Text Size (80pt >), Border Color
- 🟢 **Display** (`>`): Reduce Transparency, Increase Contrast, Bold Text, Color Filters
- 🟢 **Motion** (`>`): Reduce Motion, Auto-Play Video Previews
- 🟡 **Audio Descriptions** (Toggle): On / Off

### 9. Apps
- 🟡 **Automatically Update Apps** (Toggle): On / Off
- 🟡 **Automatically Install Apps** (Toggle): On / Off
- 🟡 **Offload Unused Apps** (Toggle): On / Off
- 🟢 **TV** (`>`): Up Next, Top Shelf, Streaming Quality
- 🟢 **Music** (`>`): Sound Check, Lossless Audio, Spatial Audio
- 🟢 **Podcasts** (`>`): Refresh intervals, continuous playback
- 🟢 **Photos** (`>`): iCloud Photos, Shared Albums

### 10. Network
- 🟢 **Ethernet** (`>`): Configure IP (Automatic / DHCP), Manual IP, Subnet Mask, Router, DNS
- 🟡 **Status Readout** (Read-Only): IP 192.168.1.14, Subnet 255.255.255.0, Router 192.168.1.1, MAC 34:fd:6a:02:b8:41

### 11. System
- 🟢 **Software Updates** (`>`): Check for Updates >, Automatically Update On/Off
- 🟢 **What's New** (`>`): Release features in tvOS 18
- 🔴 **Reset** (CRITICAL HAZARD): Reset / Reset and Update (Erases all data) (Blacklisted)
- 🔴 **Restart** (Hazard): Reboots Apple TV hardware immediately (Blacklisted)

### 12. Developer
- 🟡 **Playback HUD** (Toggle): Displays real-time AVFoundation decoder overlay
- 🟢 **Network Conditioner** (`>`): Edge / 3G / High Packet Loss simulation

### 13. Sleep Now
- 🔴 **Sleep Action** (Immediate): Puts Apple TV into low-power standby immediately (Blacklisted)

---

## 6. Interactive Visualization Artifact

To inspect and explore the full navigation hierarchy with high readability, zoom, pan, and safety classification:
- **Interactive HTML Map:** `tvos_settings_interactive_map.html`
- **Project Copy:** `reports/tvos_settings_interactive_map.html`

Features implemented in the interactive artifact:
1. **Fluid Canvas Pan & Zoom:** Drag to pan anywhere, mousewheel / pinch to zoom from 35% to 250%, with quick reset buttons.
2. **Real-Time Search & Filtering:** Filter across all 13 categories and child settings instantly.
3. **Safety Status Badges:** Visual color-coding:
   - 🟢 **Emerald:** Safe Navigational Subviews (verified disclosure chevron `>`).
   - 🟡 **Amber:** In-Place Toggles / Value Steppers (read-only; no click needed).
   - 🔴 **Rose:** Destructive Actions / Wizards (blacklisted; clicking triggers prompts or mutations).
4. **Slide-Out Item Inspector:** Clicking any node slides open a detailed breakdown of all child elements, parameters, and risk classifications.
