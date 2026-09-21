---
name: tvos-safe-navigation
description: >-
  Use this skill when automating Apple TV navigation, crawling tvOS apps, or
  operating remote controls via TVTestRig or aatv to ensure safe, closed-loop
  traversal without mutating system settings.
---

# tvOS Safe Navigation & Traversal Protocol

First read [TVTestRig operation](../tvtestrig/SKILL.md) and its interface reference.
This NUIAK supplement retains the stricter physical-device navigation boundaries;
current runtime schemas take precedence over historical syntax examples below.
Do not run simulator diagnostics or mapping while the user has paused simulators.
Verify runtime location locally before routing work to another computer.
Discovery/control/capture/focus readiness and resource ownership are separate checks.
Native accessibility may omit chevrons: record that as an unresolved boundary, not
permission to weaken physical Select restrictions or invent a route from pixels.

This skill governs autonomous navigation, remote control automation, and UI hierarchy exploration on physical Apple TV hardware and tvOS simulators. It enforces closed-loop perception, strict safety guardrails, and deterministic backtracking to prevent system mutations or session drift.

---

## The 5 Golden Rules of tvOS Automation

Every automated navigation script must strictly follow these rules:

### 1. Closed-Loop Single-Stepping (No Multi-Count Jumps)
- **NEVER** use open-loop multi-step commands like `remote navigate down --count N` followed blindly by `remote press select`.
- Section headers (`VIDEO`, `AUDIO`, `MAINTENANCE`), descriptive footers, and off-screen scrolling cause index counts to drift unpredictably.
- **ALWAYS** step one item at a time: `navigate down 1` -> call `observe wait-stable` -> capture frame -> inspect focused element.

### 2. Mandatory Disclosure Chevron (`>`) Gate Before `select`
- **NEVER** press `select` on a row or button without visual confirmation.
- In tvOS, **only rows with a trailing disclosure chevron (`>`) lead to sub-views**.
- Rows lacking chevrons are **in-place value toggles, steppers, or direct action buttons**:
  - Record their labels and values into the hierarchy tree as **read-only leaf nodes**.
  - **Never send `select`** to rows lacking chevrons during navigation sweeps.

### 3. Strict Destructive Keyword Blacklist
Never send `select` to any element whose OCR text or accessibility label matches this pattern:

```python
import re
FORBIDDEN_KEYWORDS = re.compile(
    r"\b(Reset|Erase|Format|Update|Delete|Remove|Sign Out|Add Profile|Add New|"
    r"Purchase|Restore|Terms|Agree|Offload|Restart|Sleep|Calibrate|Check HDMI)\b",
    re.IGNORECASE
)
```

If matched:
- Record as `type: "destructive_blacklisted"` in reports.
- Advance focus without clicking.

### 4. Boundary Lock ("Settings Jail" / App Context Lock)
- Maintain an explicit DFS navigation stack: `[Root, Category, Subview]`.
- Verify the header title or breadcrumb on every frame to confirm the active app is still the target (e.g. `com.apple.TVSettings`).
- **NEVER send `remote press home` during active menu traversal.** If the app escapes to Springboard, subsequent clicks will launch random third-party apps (e.g. Peacock) and pop modal Terms of Use dialogs.
- If an unexpected modal ("Cancel / OK") or foreign screen appears, immediately send `remote press back` to dismiss it, or halt execution.

### 5. Verified Backtracking
- When backtracking from a subview: send `remote press back` once.
- Call `observe wait-stable` and verify that the screen title has returned to the expected parent on the stack.
- If not returned, retry `back` once. If still unresolved, halt.

---

## TVTestRig / `aatv` Syntax Reference

The `aatv` CLI has strict argument requirements:

| Intent | Command Pattern | Notes |
|---|---|---|
| Single Step Direction | `aatv remote navigate <up\|down\|left\|right> --count 1 --device-id <ID>` | **Do not** use `remote press down` (fails with `invalidArgument`). |
| Press Button | `aatv remote press <home\|select\|back> --device-id <ID>` | Valid buttons for `press`: `home`, `select`, `back`. |
| Settle & Observe | `aatv observe wait-stable --json` | Returns when perceptual hash settles. |
| Connect Device | `aatv device connect --device-id <ID> --timeout-ms 10000 --json` | Must connect before remote commands. |
| Session Status | `aatv session status --json` | Verify connection and selected device. |

---

## Standard Closed-Loop Navigation Routine (Python Reference)

```python
import time, re, subprocess

def safe_step_down(target_label, max_steps=15):
    for step in range(max_steps):
        # 1. Step 1 item down
        run_aatv(["remote", "navigate", "down", "--count", "1", "--device-id", DEVICE_ID])
        
        # 2. Wait for focus glow and scroll physics to settle
        run_aatv(["observe", "wait-stable", "--json"])
        
        # 3. Read current focused element via OCR / Vision
        img_path = get_latest_screenshot()
        focus_item = detect_focused_element(img_path)
        
        # 4. Check target
        if target_label.lower() in focus_item.text.lower():
            # Check safety gates before clicking!
            if FORBIDDEN_KEYWORDS.search(focus_item.text):
                print(f"HAZARD: {focus_item.text} is blacklisted! Aborting select.")
                return False
            if not focus_item.has_trailing_chevron:
                print(f"LEAF: {focus_item.text} has no chevron (>). Recording value only.")
                return False
            
            # Safe to enter subview
            run_aatv(["remote", "press", "select", "--device-id", DEVICE_ID])
            time.sleep(0.5)
            run_aatv(["observe", "wait-stable", "--json"])
            return True
            
    print(f"Target '{target_label}' not found after {max_steps} steps.")
    return False
```

---

## What Works vs What Doesn't

| What Works | What Fails (Do Not Repeat) |
|---|---|
| Single-step directional pulses (`--count 1`). | Open-loop jumps (`--count 4`, `--count 8`). |
| Checking for trailing `>` before pressing `select`. | Assuming every list item is a pushable menu. |
| Verifying screen header text matches parent stack before and after back. | Looping `remote press back` or `remote press home` to recover. |
| Explicit keyword blacklist regex. | Relying on hardcoded target arrays from memory. |
| Isolating captures to dedicated project folders (`dataset/tvos_captures/`). | Writing outside package boundary or trusting raw container UUIDs. |
