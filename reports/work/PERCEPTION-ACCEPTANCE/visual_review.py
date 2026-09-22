"""Materialize the architect's 44-image visual triage against the byte audit.

Review classifications below are explicit observations from contact sheets and the
full-resolution Settings image, not filename-inferred labels or detector output.
No box/focus ground truth, source attestation, or training approval is produced.
"""
import hashlib
import json
from collections import Counter
from pathlib import Path

root = Path(__file__).resolve().parent
audit = json.loads((root/"audit.json").read_text())
special = {
    "office_app_switcher.png": "app-switcher",
    "office_app_switcher_sweep.png": "app-switcher",
    "office_home_top_right.png": "app-switcher",
    "office_session2_switcher.png": "app-switcher",
    "office_session2_switcher_card2.png": "app-switcher",
    "office_fixture_main.png": "fixture-diagnostic-screen",
    "office_folder_screen.png": "home-folder",
    "office_live_01.png": "video-content",
    "office_photos_focused_shared.png": "photos-welcome",
    "office_pluto_loaded.png": "photos-welcome",
    "office_pluto_app.png": "loading-spinner",
    "office_screen_opened.png": "account-picker-sensitive",
    "office_tvos_settings_main.png": "settings-list",
}
home = {
    "office_bottom_grid.png", "office_bottom_next.png", "office_bottom_r3.png",
    "office_dock_fixture.png", "office_grid_target.png", "office_home_col5.png",
    "office_home_initial.png", "office_home_step01.png", "office_home_step02.png",
    "office_home_step03.png", "office_r1c2.png", "office_r1c4.png", "office_r1c6.png",
    "office_r2c1.png", "office_r2c2.png", "office_r2c3.png", "office_r2c4.png",
    "office_r2c5.png", "office_r2c6.png", "office_r3c5.png", "office_r3c6.png",
    "office_r4c6.png", "office_r5c6.png", "office_row1.png", "office_row2_col5.png",
    "office_row3_col5.png", "office_row4_col5.png", "office_row5_col5.png",
    "office_session2_home.png", "office_settings_target.png", "office_shelf_up6.png",
}
records = {r["image"]["path"]: r["image"] for r in audit["captures"]["captures"]}
records.update({r["path"]: r for r in audit["captures"]["orphans"]})
assert set(records) == set(special) | home
assert not set(special) & home
members = []
for name, image in sorted(records.items()):
    category = special.get(name, "home-grid-or-shelf")
    members.append({"path": name, "sha256": image["sha256"],
                    "pixelSHA256": image["pixelSHA256"], "integrityValid": image["valid"],
                    "visualCategory": category, "reviewKind": "agent-visual-triage-not-gold-annotation",
                    "disposition": "privacy-review-required" if category == "account-picker-sensitive" else "inspection-only",
                    "benchmarkEligible": False, "trainingEligible": False,
                    "reason": "missing-reviewed-boxes-and-journey/source-review; no frame-correlated focus truth"})
report = {"version": "perception-evidence-review-v1", "auditSHA256": hashlib.sha256((root/"audit.json").read_bytes()).hexdigest(),
          "reviewedImages": len(members), "reviewMethod": "all 44 contact-sheet images; Settings additionally full resolution",
          "categories": dict(Counter(m["visualCategory"] for m in members)), "members": members,
          "rawSidecarLabelSupport": 0, "qualifiedBenchmarkCases": 0, "qualifiedTrainingPairs": 0,
          "knownIncidentSupport": {"about-name-chevron": 0, "delete-siri-history-dialog": 0},
          "quarantine": "logical only; no source files moved, deleted or relabeled",
          "scope": "Flat supplied directory only. No new evidence elsewhere inferred absent.",
          "retention": "Existing local evidence retained unchanged; no images copied to SMB."}
destination = root/"visual-review.json"
with destination.open("x") as stream: json.dump(report, stream, indent=2, sort_keys=True)
print(json.dumps({"images": len(members), "categories": report["categories"]}))
