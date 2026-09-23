"""Materialize frozen agent-reviewed labels; no prediction file is consumed.

Full-resolution review: both Photos frames and Settings (excluded for privacy).
All 44 triage contact-sheet members re-reviewed for disposition and scene type.
Home/switcher/folder negatives cover row-disclosure chevrons and true dialogs only,
not arbitrary arrow artwork or focus boxes. No native callbacks are claimed.
"""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
from perception_benchmark import validate_manifest, verify_evidence, inventory
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
TRIAGE = ROOT / "reports/work/PERCEPTION-ACCEPTANCE/visual-review.json"
# Top-left pixel xywh of the visible rounded button fill, not its shadow.
PHOTOS = {
    "office_photos_focused_shared.png": ([[318, 601, 500, 66], [308, 679, 520, 75]], "shared"),
    "office_pluto_loaded.png": ([[314, 597, 508, 74], [312, 683, 512, 66]], "all"),
}
NEGATIVE_SCENES = {"home-grid-or-shelf", "home-folder", "app-switcher"}
REASONS = {
    "account-picker-sensitive": "privacy-review-required; no identity transcription",
    "settings-list": "privacy-review-required; management text; chevron lead not admitted",
    "video-content": "video imagery, no scoped UI relation truth",
    "fixture-diagnostic-screen": "diagnostic UI, unsupported relation/focus truth",
    "loading-spinner": "transitional image; not stable perception evidence",
}


def build():
    review = json.loads(TRIAGE.read_text())
    cases, dispositions = [], []
    for member in review["members"]:
        path = ROOT / "dataset/tvos_captures" / member["path"]
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != member["sha256"]:
            raise ValueError("changed_reviewed_bytes:" + member["path"])
        with Image.open(path) as picture:
            picture.load(); width, height = picture.size
        category = member["visualCategory"]
        admitted = category in NEGATIVE_SCENES or member["path"] in PHOTOS
        labels = {"origin": "reviewedVisual", "rows": [], "chevrons": [], "dialog": None, "focus": None}
        case_id = Path(member["path"]).stem
        if member["path"] in PHOTOS:
            if (width, height) != (1920, 1080): raise ValueError("changed_review_dimensions")
            boxes, focus = PHOTOS[member["path"]]
            labels["rows"] = [{"id": ident, "box": box} for ident, box in zip(("all", "shared"), boxes)]
            labels["focus"] = {"elementID": focus, "frameID": case_id, "basis": "visualAppearanceOnly"}
        disposition = {"path": str(path.relative_to(ROOT)), "sha256": digest,
            "pixelSHA256": member["pixelSHA256"], "category": category,
            "developmentReviewEligible": admitted, "trainingEligible": False,
            "independentEvaluationEligible": False,
            "reason": "reviewed visual development labels only; historical source unverified" if admitted else REASONS[category]}
        dispositions.append(disposition)
        if not admitted: continue
        cases.append({"caseID": case_id, "sourceKind": "reviewedNativeCapture",
            "imagePath": str(path.relative_to(ROOT)), "imageSHA256": digest,
            "width": width, "height": height, "journeyID": "legacy44-unknown-journey",
            "splitGroup": "legacy44-unknown-journey", "partition": "development",
            "trainingEligible": False, "sourceIdentityStatus": "unverified",
            "journeyEvidence": "unknown-conservatively-grouped", "privacyReview": "local-review-cleared",
            "reviewer": "NUIAK agent visual review 2026-09-22 (not independent human review)",
            "reviewScope": "visible row-disclosure chevrons and true dialogs; focus only where labeled",
            "focusUnknown": labels["focus"] is None, "labels": labels})
    if len(dispositions) != 44: raise ValueError("changed_triage_membership")
    manifest = {"formatVersion": "perception-benchmark-v1", "cases": cases}
    checked = validate_manifest(manifest)
    verification = verify_evidence(checked)
    return manifest, {"formatVersion": "perception-reviewed-dispositions-v1",
        "triageSHA256": hashlib.sha256(TRIAGE.read_bytes()).hexdigest(),
        "members": dispositions, "verification": verification, "inventory": inventory(checked),
        "modelInference": "not_run", "trainingEligible": False}


if __name__ == "__main__":
    outputs = [HERE / name for name in ("manifest.json", "dispositions.json", "predictions.json")]
    overlays = ROOT / ".build/debug-output/per-data-overlays"
    if any(p.exists() for p in outputs) or overlays.exists(): raise SystemExit("output_collision")
    manifest, dispositions = build()
    predictions = {"formatVersion": "perception-predictions-v1", "status": "unavailable", "reason": "inference not assigned; reviewed labels are not predictions"}
    for path, data in zip(outputs, (manifest, dispositions, predictions)):
        with path.open("x") as stream: json.dump(data, stream, indent=2)
    overlays.mkdir(parents=True)
    for case in manifest["cases"]:
        if not case["labels"]["focus"]: continue
        with Image.open(ROOT / case["imagePath"]) as source:
            picture = source.convert("RGB"); draw = ImageDraw.Draw(picture)
            for row in case["labels"]["rows"]:
                x, y, w, h = row["box"]
                color = "lime" if row["id"] == case["labels"]["focus"]["elementID"] else "red"
                draw.rectangle((x,y,x+w,y+h), outline=color, width=3)
            picture.save(overlays / (case["caseID"] + ".png"))
    print(json.dumps(dispositions["inventory"]))
