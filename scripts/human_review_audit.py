"""Offline revision/crop audit and review queues; never loads a model or edits labels."""
import argparse
from collections import Counter, defaultdict
import html
import json
from pathlib import Path
import random

from PIL import Image, ImageChops, ImageDraw, ImageStat

import human_annotation_review as h
from focus_dataset_contract import expanded_box
from focus_runtime import RUNTIME_PREPROCESSING


def groups(records):
    grouped = defaultdict(list)
    for identity, digest in records:
        grouped[digest].append(identity)
    return [v for _, v in sorted(grouped.items()) if len(v) > 1]


def overlap(a, b):
    x, y = max(a[0], b[0]), max(a[1], b[1])
    right, bottom = min(a[0]+a[2], b[0]+b[2]), min(a[1]+a[3], b[1]+b[3])
    return max(0, right-x)*max(0, bottom-y)


def audit(revision_path, crop_path, *, seed=42, per_screen=1):
    h.require(type(seed) is int and type(per_screen) is int and 0 < per_screen <= 256, "invalid_sampling")
    revision_path, crop_path = h.local(revision_path), h.local(crop_path)
    revision = h.sealed(revision_path, h.REVISION)
    h.require(revision["reviewer"]["kind"] in ("human", "software-test")
              and revision["reviewer"]["confirmedBatch"] is True, "missing_review_attestation")
    batch_path = h.checked(h.ROOT, revision["batch"])
    batch = h.validate_batch(batch_path)
    h.require(len({f["id"] for f in batch["frames"]}) == len(batch["frames"]), "duplicate_frame_identity")
    for frame in batch["frames"]:
        h.identifier(frame["id"])
        h.identifier(frame["screen"])
    crop = h.sealed(crop_path, "human-review-crop-qa-v1")
    h.require(crop["revision"] == h.ref(revision_path) and crop["batch"] == revision["batch"], "wrong_crop_revision")
    h.require(crop["preprocessing"] == RUNTIME_PREPROCESSING, "wrong_crop_preprocessing")
    h.require([f["id"] for f in revision["frames"]] == [f["id"] for f in batch["frames"]], "revision_membership")
    snapshots = revision["editorSnapshots"]
    expected_names = [f["editorStem"]+".json" for f in batch["frames"] if f["disposition"] == "imported"]
    h.require([Path(r["path"]).name for r in snapshots] == expected_names, "snapshot_membership")
    snapshot_by_name = {Path(r["path"]).name: h.checked(h.ROOT, r) for r in snapshots}
    issues, frames, samples, raw_refs = [], [], [], []
    def issue(kind, members, detail, severity="review"):
        issues.append(dict(kind=kind, samples=sorted(members), detail=detail, severity=severity))
    for frame, reviewed in zip(batch["frames"], revision["frames"]):
        h.require(reviewed["image"] == frame.get("image") and reviewed["screen"] == frame["screen"], "changed_frame_binding")
        row = dict(id=frame["id"], screen=frame["screen"], candidateCoverage="unknown", image=frame.get("image"),
                   controls=len(reviewed["controls"]), disposition=reviewed["disposition"])
        frames.append(row)
        if frame["disposition"] != "imported":
            issue("input_blocked", [frame["id"]], ", ".join(frame["reasons"]), "hard")
            continue
        path = snapshot_by_name[frame["editorStem"]+".json"]
        controls = h.parse_editor(batch, frame, path)
        if revision["reviewer"]["kind"] == "software-test":
            for c in controls:
                if c["disposition"] == "reviewed":
                    c["disposition"] = "blocked"
                c["reasons"].append("software_test_not_human")
        h.require(controls == reviewed["controls"], "revision_controls_disagree_with_snapshot")
        disposition = "blocked"
        if controls and all(c["disposition"] in ("reviewed", "rejected") for c in controls):
            disposition = "reviewed" if any(c["disposition"] == "reviewed" for c in controls) else "rejected"
        h.require(disposition == reviewed["disposition"], "frame_disposition_mismatch")
        row["pixelSHA256"] = h.pixel_digest(h.ROOT, frame["image"])
        row["focusCounts"] = dict(Counter(c["state"] for c in controls if c["disposition"] != "rejected"))
        raw_refs.append(frame["image"])
        proposed = {p["id"]: p for p in frame["proposals"]}
        for c in controls:
            sample = dict(frameID=frame["id"], screen=frame["screen"], **c)
            sample["id"] = frame["id"]+":"+c["id"]
            sample["controlID"] = c["id"]
            x1, y1, x2, y2 = expanded_box(c["bounds"], frame["size"])
            sample["visibleNeighborBoxes"] = sum(overlap([x1, y1, x2-x1, y2-y1], n["bounds"]) > 0
                                                  for n in controls if n["id"] != c["id"])
            original = proposed.get(c["id"])
            sample["proposalBoundsMaxDeltaPixels"] = max(abs(a-b) for a, b in zip(original["bounds"], c["bounds"])) if original else None
            samples.append(sample)
            if c["disposition"] == "blocked":
                issue("annotation_pending", [sample["id"]], ", ".join(c["reasons"]), "hard")
        active = [c for c in controls if c["disposition"] != "rejected"]
        for n, left in enumerate(active):
            for right in active[n+1:]:
                smaller = min(left["bounds"][2]*left["bounds"][3], right["bounds"][2]*right["bounds"][3])
                if overlap(left["bounds"], right["bounds"])/smaller > .8:
                    issue("overlapping_boxes", [frame["id"]+":"+c["id"] for c in (left, right)],
                          "More than 80% of smaller box overlaps; nesting may be legitimate. Triage only.")
    expected = [s["id"] for s in samples if s["disposition"] != "rejected"]
    h.require(revision["frameCounts"] == dict(Counter(f["disposition"] for f in frames))
              and revision["controlCounts"] == dict(Counter(s["disposition"] for s in samples)), "revision_counts_mismatch")
    h.require([c["id"] for c in crop["crops"]] == expected and crop["expected"] == len(expected)
              and crop["completed"] == len(expected), "incomplete_or_duplicate_crop_membership")
    by_id = {s["id"]: s for s in samples}
    for record in crop["crops"]:
        h.image(h.ROOT, record["crop"], (256, 256))
        sample = by_id[record["id"]]
        sample["crop"] = record["crop"]
        sample["pixelSHA256"] = h.pixel_digest(h.ROOT, record["crop"])
    frame_groups = groups((f["id"], f["pixelSHA256"]) for f in frames if "pixelSHA256" in f)
    crop_groups = groups((s["id"], s["pixelSHA256"]) for s in samples if "pixelSHA256" in s)
    for members in frame_groups:
        issue("duplicate_frame_pixels", members, "Exact decoded pixels; retained, not independent diversity.", "info")
    for members in crop_groups:
        states = {by_id[k]["state"] for k in members}
        classes = {by_id[k]["class"] for k in members}
        conflict = len(states) > 1 or len(classes) > 1
        issue("duplicate_crop_label_conflict" if conflict else "duplicate_crop_pixels", members,
              "Exact decoded crops; conflicting labels require adjudication." if conflict else "Repeated crop pixels; do not count as independent examples.",
              "hard" if conflict else "info")
    near = []
    thumbnails = {}
    for frame in frames:
        if "pixelSHA256" not in frame:
            continue
        with Image.open(h.checked(h.ROOT, frame["image"])) as im:
            thumbnails[frame["id"]] = im.convert("RGB").resize((64, 36), Image.Resampling.BILINEAR)
    for n, a in enumerate(frames):
        for b in frames[n+1:]:
            if a["screen"] != b["screen"] or a["id"] not in thumbnails or b["id"] not in thumbnails:
                continue
            if a["pixelSHA256"] == b["pixelSHA256"]:
                continue
            distance = sum(ImageStat.Stat(ImageChops.difference(thumbnails[a["id"]], thumbnails[b["id"]])).mean)/3
            if distance <= 2:
                near.append(dict(frames=[a["id"], b["id"]], meanAbsoluteRGBDifference=distance))
                issue("near_duplicate_frames", [a["id"], b["id"]], f"64x36 RGB mean difference {distance:.4f}/255 <=2; heuristic only, preserve both states.")
    h.require([p["id"] for p in revision["pairs"]] == [p["id"] for p in batch["pairs"]], "pair_membership")
    for pair, spec in zip(revision["pairs"], batch["pairs"]):
        h.require(all(pair[k] == spec[k] for k in ("id", "frames", "controlID")), "changed_pair_binding")
        members = [by_id.get(f+":"+spec["controlID"]) for f in spec["frames"]]
        valid = all(s and s["disposition"] == "reviewed" for s in members)
        valid = valid and {s["state"] for s in members} == {"focused", "unfocused"}
        valid = valid and len({s["class"] for s in members}) == 1 and len({s["screen"] for s in members}) == 1
        h.require(pair["disposition"] == ("reviewed" if valid else "blocked"), "pair_disposition_mismatch")
        if not valid:
            issue("pair_pending", [f+":"+spec["controlID"] for f in spec["frames"]], "Missing, conflicting or unreviewed pair member.", "hard")
    strata = defaultdict(list)
    for frame in frames:
        strata[frame["screen"]].append(frame["id"])
    rng = random.Random(seed)
    random_queue = []
    for screen, ids in sorted(strata.items()):
        random_queue.append(dict(screen=screen, denominator=len(ids), selected=sorted(rng.sample(sorted(ids), min(per_screen, len(ids))))))
    severity_order = {"hard": 0, "review": 1, "info": 2}
    for n, item in enumerate(sorted(issues, key=lambda r: (severity_order[r["severity"]], r["kind"], r["samples"])), 1):
        item["id"] = f"issue-{n:03d}"
    issues.sort(key=lambda r: r["id"])
    inventory = [h.ref(revision_path), revision["batch"], h.ref(crop_path), *snapshots, *raw_refs, *batch["rawEvidence"],
                 *[c["crop"] for c in crop["crops"]]]
    for record in inventory:
        h.checked(h.ROOT, record)
    return dict(version="human-review-audit-v1", **h.FLAGS, inputs=inventory, reviewer=revision["reviewer"],
                frames=frames, samples=samples, pairs=revision["pairs"], issues=issues,
                exactFrameDuplicateGroups=frame_groups, exactCropDuplicateGroups=crop_groups, nearDuplicates=near,
                randomQueue=dict(seed=seed, perScreen=per_screen, unit="frame", strata=random_queue),
                coverage=dict(screens=dict(Counter(f["screen"] for f in frames)), classes=dict(Counter(s["class"] for s in samples)),
                              states=dict(Counter(s["state"] for s in samples)), appearance="unknown",
                              sourceSessions=1, sessionID=batch["sessionID"], sourceDeviceID=batch["sourceDeviceID"],
                              candidateCoverage="unknown", crossCorpusLeakage="not_assessed_no_external_role_manifests",
                              activeReviewerSeconds=None),
                counts=dict(frames=len(frames), controls=len(samples), crops=len(crop["crops"]),
                            distinctCropPixels=len({s["pixelSHA256"] for s in samples if "pixelSHA256" in s}),
                            issueSeverities=dict(Counter(i["severity"] for i in issues))),
                limitations=["Diagnostic-only; no independent accuracy estimate or new training eligibility.",
                             "Near-duplicate/overlap heuristics identify review candidates, not proven label errors.",
                             "No automatic new pair or native identity inferred from repeated local IDs."])


def render(report, output):
    """Static local queues and contact sheets of existing production crops."""
    frame_links = []
    for frame in report["frames"]:
        members = [s for s in report["samples"] if s["frameID"] == frame["id"] and "crop" in s]
        if not frame.get("image"):
            continue
        with Image.open(h.checked(h.ROOT, frame["image"])) as im:
            overlay = im.convert("RGB")
        draw = ImageDraw.Draw(overlay)
        for s in members:
            x, y, w, height = s["bounds"]
            color = "lime" if s["state"] == "focused" else "cyan"
            draw.rectangle((x, y, x+w, y+height), outline=color, width=3)
            draw.text((x+3, y+3), str(s["groupID"]), fill="black", stroke_width=2, stroke_fill=color)
        overlay.thumbnail((1280, 720))
        overlay.save(output/(frame["id"]+"-context.png"))
        sheet = Image.new("RGB", (256*4, max(1, (len(members)+3)//4)*292), "white")
        draw = ImageDraw.Draw(sheet)
        for n, s in enumerate(members):
            x, y = (n%4)*256, (n//4)*292
            with Image.open(h.checked(h.ROOT, s["crop"])) as im:
                sheet.paste(im.convert("RGB"), (x, y))
            draw.text((x+4, y+258), f"{s['id']}  {s['state']}\n{s['class']}", fill="black")
        sheet.save(output/(frame["id"]+"-crops.png"))
        frame_links.append(f"<h2 id='{html.escape(frame['id'])}'>{html.escape(frame['id'])} — {html.escape(frame['screen'])}</h2>"
                           f"<img width='960' src='{frame['id']}-context.png'><p><a href='{frame['id']}-crops.png'>Production crop sheet</a></p>"
                           f"<code>--frame {html.escape(frame['id'])}</code>")
    def linked(identity):
        frame_id = identity.split(":")[0]
        return f"<a href='#{html.escape(frame_id)}'>{html.escape(identity)}</a>"
    targeted = "".join(f"<li>{i['id']} [{i['severity']}] {html.escape(i['kind'])}: "
                       + ", ".join(linked(s) for s in i['samples']) + " — " + html.escape(i['detail'])+"</li>" for i in report['issues'])
    sampled = "".join(f"<li>{html.escape(r['screen'])}, {len(r['selected'])}/{r['denominator']}: "
                      + ", ".join(linked(s) for s in r['selected'])+"</li>" for r in report['randomQueue']['strata'])
    page = "<!doctype html><meta charset='utf-8'><title>Human review audit</title><style>body{font:16px system-ui;max-width:1100px;margin:30px auto}img{max-width:100%}li{margin:12px 0}</style>"
    page += "<h1>Human review audit — development diagnostics</h1><p>No model inference. Heuristics are review cues, not proven errors. Original labels remain unchanged.</p>"
    page += f"<h2>Seeded frame audit (seed {report['randomQueue']['seed']})</h2><ul>{sampled}</ul><h2>Targeted queue</h2><ul>{targeted or '<li>No detected issues.</li>'}</ul>"
    page += "<p>Open the existing labeling app with its batch.json and the indicated --frame ID. Correct, use Finish review for a new revision, then rerun this audit and crop QA. Do not edit frozen snapshots.</p>"
    page += "".join(frame_links)
    (output/"review.html").write_text(page)


def run(revision, crops, output, seed=42, per_screen=1):
    output = h.fresh(output)
    output.mkdir(parents=True)
    try:
        report = audit(revision, crops, seed=seed, per_screen=per_screen)
        render(report, output)
        for record in report["inputs"]:
            h.checked(h.ROOT, record)
        h.write(output/"audit.json", report, sealed=True)
        return report
    except (ValueError, OSError, KeyError, TypeError) as error:
        h.write(output/"failure.json", dict(version="human-review-audit-failure-v1", **h.FLAGS,
                                           error=str(error), completed=False, inputs=[str(revision), str(crops)]), sealed=True)
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("revision")
    parser.add_argument("crops")
    parser.add_argument("output")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--per-screen", type=int, default=1)
    args = parser.parse_args()
    try:
        print(json.dumps(run(args.revision, args.crops, args.output, args.seed, args.per_screen)["counts"]))
    except (ValueError, OSError, KeyError, TypeError) as error:
        parser.exit(2, f"Audit blocked: {error}\n")
