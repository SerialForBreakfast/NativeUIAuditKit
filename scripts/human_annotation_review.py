"""Local, diagnostic-only Labelme review bridge. No model loading or capture."""
import argparse
import base64
from collections import Counter
from datetime import datetime, timezone
import html
import io
import json
import math
from pathlib import Path
import shutil

from PIL import Image
from focus_dataset_contract import ROOT, FocusDataError, digest, image, local, pixel_digest, text
from photos_focus_pilot import (FLAGS, box, checked, envelope, fresh, identifier,
                                preview, raw_id, ref, require, sha, write)

INDEX = "human-review-index-v1"
BATCH = "human-review-batch-v1"
REVISION = "human-review-revision-v1"
FOCUS_REVISION = "human-review-revision-v2"
ROLE_SCHEMA = 'human-focus-roles-v1'
FOCUS_ROLES = ('tabItem', 'otherFocusable')
EDITOR = "5.2.1"
SHAPE_FLAGS = ("focused", "unfocused", "confirmed", "flagged", "rejected")
FRAME_FLAGS = ("reviewed", "settled", "content_approved")
CATEGORY = ROOT / "Research/schemas/category_map.json"


def read(path, limit=8*1024*1024):
    path = local(path)
    require(path.stat().st_size <= limit, "json_size_limit")
    def unique(items):
        result = {}
        for key, value in items:
            require(key not in result, "duplicate_json_key")
            result[key] = value
        return result
    return json.loads(path.read_text(), object_pairs_hook=unique,
                      parse_constant=lambda _: require(False, "nonfinite_json"))


def sealed(path, version):
    doc = read(path)
    require(doc.get("version") == version and
            doc.get("seal") == digest({k: v for k, v in doc.items() if k != "seal"}),
            "changed_or_unsupported_manifest")
    require(all(doc.get(k) == v for k, v in FLAGS.items()), "diagnostic_only")
    return doc


def timestamp(value):
    ns, wall = value["monotonic"]["nanoseconds"], value["wallClock"]
    require(type(ns) is int and ns >= 0 and type(wall) in (int, float)
            and math.isfinite(wall), "invalid_timestamp")
    return ns


def copy_ref(record, destination, limit=32*1024*1024):
    source = checked(ROOT, record, limit)
    shutil.copyfile(source, destination)
    require(sha(destination) == record["sha256"], "copy_changed")
    return ref(destination)


def taxonomy():
    return [c["name"] for c in read(CATEGORY)["categories"]]


def review_labels():
    return taxonomy() + ['focus:'+role for role in FOCUS_ROLES]


def control_label(control):
    return 'focus:'+control['focusRole'] if control.get('focusRole') else control['class']


def read_revision(path):
    version = read(path).get('version')
    require(version in (REVISION, FOCUS_REVISION), 'unsupported_review_revision')
    doc = sealed(path, version)
    for frame in doc['frames']:
        for control in frame['controls']:
            if control.get('focusRole') is not None:
                require(version == FOCUS_REVISION and control['focusRole'] in FOCUS_ROLES
                        and control.get('class') is None and control.get('roleSchema') == ROLE_SCHEMA,
                        'invalid_focus_role_mapping')
            else:
                require(control.get('class') in taxonomy(), 'invalid_detector_class')
    return doc


def binding(batch_id, frame):
    return {"batchID": batch_id, "frameID": frame["id"],
            "imageSHA256": frame["image"]["sha256"]}


def editor_document(batch_id, frame):
    shapes = []
    for number, c in enumerate(frame["proposals"], 1):
        x, y, w, h = c["bounds"]
        shapes.append(dict(label=c["class"], group_id=number, shape_type="rectangle",
                           points=[[x, y], [x+w, y+h]],
                           flags={k: (k == c["state"]) for k in SHAPE_FLAGS}))
    return dict(version=EDITOR, imagePath=frame["editorStem"]+".png", imageData=None,
                imageWidth=frame["size"][0], imageHeight=frame["size"][1], shapes=shapes,
                flags={k: False for k in FRAME_FLAGS}, nuiak=binding(batch_id, frame))


def validate_batch(path):
    if read(path).get('version') == 'human-recording-review-batch-v1':
        from human_recording_review import validate
        return validate(path)
    batch = sealed(path, BATCH)
    index = sealed(checked(ROOT, batch["index"]), INDEX)
    checked(ROOT, batch["categoryMap"])
    require(sha(CATEGORY) == batch["categoryMap"]["sha256"], "taxonomy_changed")
    for record in batch["rawEvidence"]:
        checked(ROOT, record)
    for frame in batch["frames"]:
        if frame["disposition"] == "imported":
            require(list(image(ROOT, frame["image"])) == frame["size"], "image_size_changed")
            checked(ROOT, frame["observation"])
    require(len(batch["frames"]) == len(index["frames"]), "batch_membership_changed")
    return batch


def import_batch(input_path, output):
    input_path = local(input_path)
    index = sealed(input_path, INDEX)
    output = local(output)
    if output.exists():
        batch = validate_batch(output / "batch.json")
        require(batch["index"]["sha256"] == sha(input_path), "changed_index")
        # No reset of mutable review work on repeated import.
        return batch
    output = fresh(output)
    identifier(index["id"])
    require(type(index["generation"]) is int and index["generation"] >= 0, "invalid_generation")
    frames = index["frames"]
    require(isinstance(frames, list) and 0 < len(frames) <= 256, "frame_limit")
    ids = [identifier(f["id"]) for f in frames]
    observations = [text(f["observationID"]) for f in frames]
    require(len(set(ids)) == len(ids) and len(set(observations)) == len(frames), "duplicate_membership")
    events = envelope(read(checked(ROOT, index["timeline"])), "timeline", {"session timeline"})
    session_id = raw_id(envelope(read(checked(ROOT, index["sessionStart"])), "session", {"session start"}))
    require(session_id == index["sessionID"] and events, "wrong_session")
    sequence = [e["sequenceNumber"] for e in events]
    require(sequence == list(range(1, len(events)+1)) and len({e["id"] for e in events}) == len(events),
            "incomplete_timeline")
    require(events[0]["kind"] == "sessionStarted" and events[-1]["kind"] == "sessionEnded", "unfinalized_timeline")
    times = [timestamp(e["timestamp"]) for e in events]
    require(times == sorted(times), "unordered_timeline")
    timeline_observations, commands = {}, {}
    for event in events:
        require(raw_id(event["sessionID"]) == session_id, "wrong_session")
        if event["kind"] in ("observation", "command"):
            require(event["deviceID"] == index["sourceDeviceID"], "wrong_target")
        if event["kind"] == "observation":
            for oid in event["observationIDs"]:
                oid = raw_id(oid)
                require(oid not in timeline_observations, "duplicate_observation")
                timeline_observations[oid] = event
        elif event["kind"] == "command":
            cid = raw_id(event["commandID"])
            require(cid not in commands, "duplicate_command")
            commands[cid] = event
        else:
            require(event["kind"] in ("sessionStarted", "sessionEnded"), "unsupported_timeline_event")
    require(set(timeline_observations) == set(observations), "timeline_membership_mismatch")
    pair_specs = index.get("pairs", [])
    require(len({identifier(p["id"]) for p in pair_specs}) == len(pair_specs), "duplicate_pair")
    for pair in pair_specs:
        require(len(pair["frames"]) == 2 and len(set(pair["frames"])) == 2
                and set(pair["frames"]) <= set(ids), "invalid_pair_membership")
        identifier(pair["controlID"])
    output.mkdir(parents=True)
    for name in ("raw", "editor", "sheets"):
        (output/name).mkdir()
    raw_evidence = [copy_ref(ref(input_path), output/"raw/index.json"),
                    copy_ref(index["timeline"], output/"raw/timeline.json"),
                    copy_ref(index["sessionStart"], output/"raw/session-start.json"),
                    copy_ref(ref(CATEGORY), output/"raw/category-map.json")]
    rows, pixel_owners = [], {}
    for number, spec in enumerate(frames, 1):
        row = dict(id=spec["id"], number=number, screen=identifier(spec["screen"]),
                   context=spec.get("context", ""), disposition="blocked", reasons=[],
                   observationID=spec["observationID"], proposals=spec.get("proposals", []),
                   nativeUnresolved=bool(spec.get("nativeEvidence")),
                   editorStem=f"{number:03d}-{spec['id']}")
        rows.append(row)
        try:
            row["image"] = copy_ref(spec["image"], output/"raw"/(spec["id"]+".png"), 24*1024*1024)
            row["observation"] = copy_ref(spec["observation"], output/"raw"/(spec["id"]+".json"))
            size = image(ROOT, row["image"])
            observation = envelope(read(checked(ROOT, row["observation"]), 32*1024*1024),
                                   "observation", {"observe capture"})
            require(raw_id(observation["id"]) == spec["observationID"], "wrong_observation")
            require(observation["sourceDeviceID"] == index["sourceDeviceID"], "wrong_target")
            require(observation["connectionGeneration"] == index["generation"], "wrong_generation")
            require(observation["providerID"] == "avfoundation-video" and
                    observation["orientation"] == "up" and observation["mimeType"] == "image/png",
                    "unsupported_capture")
            require(observation["dimensions"] == dict(width=size[0], height=size[1]), "wrong_dimensions")
            require(observation["freshness"]["status"] == "current", "stale_capture")
            require(base64.b64decode(observation["imageBase64"], validate=True) ==
                    checked(ROOT, row["image"]).read_bytes(), "inline_image_mismatch")
            captured, received = timestamp(observation["capturedAt"]), timestamp(observation["receivedAt"])
            event = timeline_observations[spec["observationID"]]
            require(times[0] <= captured <= received <= timestamp(event["timestamp"]) <= times[-1],
                    "capture_time_mismatch")
            preceding = [raw_id(v) for v in observation.get("precedingCommandIDs", [])]
            require(len(preceding) == len(set(preceding)), "duplicate_preceding_commands")
            require(all(commands[c]["sequenceNumber"] < event["sequenceNumber"] for c in preceding if c in commands),
                    "future_command_reference")
            row.update(size=list(size), capturedAt=observation["capturedAt"], receivedAt=observation["receivedAt"],
                       timelineSequence=event["sequenceNumber"], precedingCommandIDs=preceding,
                       unmappedCommandIDs=[c for c in preceding if c not in commands])
            for optional in ("status", "nativeEvidence"):
                if spec.get(optional):
                    record = copy_ref(spec[optional], output/"raw"/(spec["id"]+"-"+optional+".json"))
                    raw_evidence.append(record)
                    if optional == "status":
                        status = envelope(read(checked(ROOT, record)), "status", {"status"})
                        require(status["selectedDeviceID"] == index["sourceDeviceID"] and
                                raw_id(status["sessionID"]) == session_id, "wrong_status_binding")
            proposals = row["proposals"]
            require(len(proposals) <= 100 and len({identifier(c["id"]) for c in proposals}) == len(proposals),
                    "invalid_control_membership")
            for control in proposals:
                box(control["bounds"], size)
                require(control["class"] in taxonomy() and control["state"] in ("focused", "unfocused", "unknown"),
                        "invalid_proposal")
            row["pixelSHA256"] = pixel_digest(ROOT, row["image"])
            row["duplicateOf"] = pixel_owners.get(row["pixelSHA256"])
            pixel_owners.setdefault(row["pixelSHA256"], row["id"])
            row["disposition"] = "imported"
            shutil.copyfile(checked(ROOT, row["image"]), output/"editor"/(row["editorStem"]+".png"))
            write(output/"editor"/(row["editorStem"]+".json"), editor_document(index["id"], row))
            preview(checked(ROOT, row["image"]), output/"sheets"/(row["editorStem"]+".png"),
                    f"{number:03d} {row['id']} — PROPOSALS ONLY", proposals)
        except (ValueError, OSError, KeyError, TypeError) as error:
            row["disposition"] = "blocked"
            row["reasons"] = [str(error)]
    # Recheck every successfully copied raw byte before sealing, not a live directory scan.
    for record in raw_evidence:
        checked(ROOT, record)
    transitions = []
    previous = 1
    for oid, event in sorted(timeline_observations.items(), key=lambda item: item[1]["sequenceNumber"]):
        between = [e for e in events if previous < e["sequenceNumber"] < event["sequenceNumber"] and e["kind"] == "command"]
        transitions.append(dict(observationID=oid, commands=between,
                                gap="uncaptured_intermediate_states" if len(between) > 1 else "none_recorded",
                                outcomeVerified=False))
        previous = event["sequenceNumber"]
    batch = dict(version=BATCH, **FLAGS, id=index["id"], index=raw_evidence[0], categoryMap=raw_evidence[3],
                 rawEvidence=raw_evidence, sourceDeviceID=index["sourceDeviceID"], sessionID=session_id,
                 generation=index["generation"], frames=rows, pairs=pair_specs, transitions=transitions,
                 counts=dict(Counter(r["disposition"] for r in rows)), distinctPixels=len(pixel_owners),
                 completeFrameCandidates=False)
    write(output/"batch.json", batch, sealed=True)
    cards = [f'<h2>{r["number"]:03d} {html.escape(r["id"])}</h2><p>{html.escape(r["context"])}</p>' +
             (f'<img width="1000" src="sheets/{r["editorStem"]}.png">' if r["disposition"] == "imported"
              else f'<p>BLOCKED: {html.escape(str(r["reasons"]))}</p>') for r in rows]
    with (output/"review.html").open("x") as stream:
        stream.write('<!doctype html><meta charset="utf-8"><title>Human review</title><h1>Diagnostic proposals — not confirmed labels</h1>'+''.join(cards))
    return batch


def bool_flags(flags, required):
    require(isinstance(flags, dict) and set(flags) == set(required) and
            all(type(v) is bool for v in flags.values()), "invalid_review_flags")


def parse_editor(batch, frame, path):
    return parse_editor_document(batch, frame, path, read(path))


def parse_editor_document(batch, frame, path, doc):
    """Validate saved or proposed editor data through the same admission checks."""
    require(doc.get("version") == EDITOR, "unsupported_editor_version")
    require(doc.get("nuiak") == binding(batch["id"], frame), "changed_image_binding")
    require(doc.get("imagePath") == frame["editorStem"]+".png" and doc.get("imageData") is None and
            [doc.get("imageWidth"), doc.get("imageHeight")] == frame["size"], "changed_image_metadata")
    checked(ROOT, dict(path=str((path.parent/doc["imagePath"]).relative_to(ROOT)), sha256=frame["image"]["sha256"]))
    bool_flags(doc.get("flags"), FRAME_FLAGS)
    shapes = doc["shapes"]
    require(isinstance(shapes, list) and len(shapes) <= 100, "control_limit")
    groups, controls = set(), []
    original = {n: c["id"] for n, c in enumerate(frame["proposals"], 1)}
    for shape in shapes:
        gid = shape["group_id"]
        require(type(gid) is int and 0 < gid <= 100000 and gid not in groups, "invalid_control_id")
        groups.add(gid)
        require(shape["shape_type"] == "rectangle" and shape["label"] in review_labels(), "invalid_shape_or_class")
        points = shape["points"]
        require(isinstance(points, list) and len(points) == 2 and
                all(isinstance(p, list) and len(p) == 2 for p in points) and
                all(type(v) in (int, float) and math.isfinite(v) for p in points for v in p), "invalid_bounds")
        (x, y), (x2, y2) = points
        # Floating-point transforms can put an on-edge corner ~1e-14px outside.
        # Normalize numeric dust only; meaningful out-of-frame boxes still fail.
        def edge(value, limit):
            if -1e-7 <= value < 0: return 0.0
            if limit < value <= limit+1e-7: return float(limit)
            return value
        x, x2 = (edge(v, frame['size'][0]) for v in (x,x2))
        y, y2 = (edge(v, frame['size'][1]) for v in (y,y2))
        bounds = [min(x, x2), min(y, y2), abs(x2-x), abs(y2-y)]
        box(bounds, frame["size"])
        flags = shape["flags"]
        bool_flags(flags, SHAPE_FLAGS)
        state = "focused" if flags["focused"] else "unfocused" if flags["unfocused"] else "unknown"
        reasons = []
        if flags["focused"] and flags["unfocused"]: reasons.append("conflicting_focus")
        if state == "unknown": reasons.append("unknown_focus")
        if not flags["confirmed"]: reasons.append("unconfirmed")
        if flags["flagged"]: reasons.append("flagged")
        if not all(doc["flags"].values()): reasons.append("frame_unconfirmed")
        if frame["nativeUnresolved"]: reasons.append("native_evidence_unresolved")
        if frame["duplicateOf"]: reasons.append("duplicate_pixels")
        disposition = "rejected" if flags["rejected"] else "blocked" if reasons else "reviewed"
        controls.append(dict(id=original.get(gid, f"new-{gid}"), groupID=gid, bounds=bounds,
                             **{"class": shape["label"]}, state=state, disposition=disposition, reasons=reasons))
        if shape['label'].startswith('focus:'):
            controls[-1].update({'class': None, 'focusRole': shape['label'].split(':', 1)[1],
                                 'roleSchema': ROLE_SCHEMA})
    require(set(original) <= groups, "missing_control_use_rejected_flag")
    require(len({c["id"] for c in controls}) == len(controls), "ambiguous_control_identity")
    if sum(c["state"] == "focused" and c["disposition"] != "rejected" for c in controls) > 1:
        for c in controls:
            if c["disposition"] != "rejected":
                c["disposition"] = "blocked"
                c["reasons"].append("multiple_focused_controls")
    return controls


def finish(batch_path, output, *, reviewer, reference, reviewer_kind, confirm_batch):
    require(confirm_batch and reviewer_kind in ("human", "software-test"), "explicit_completion_required")
    text(reviewer); text(reference)
    batch = validate_batch(batch_path)
    directory, output = local(batch_path).parent, fresh(output)
    expected = {f["editorStem"]+suffix for f in batch["frames"] if f["disposition"] == "imported" for suffix in (".png", ".json")}
    require({p.name for p in (directory/"editor").iterdir()} == expected, "editor_membership_mismatch")
    output.mkdir(parents=True)
    (output/"editor-snapshot").mkdir()
    rows, snapshots = [], []
    for frame in batch["frames"]:
        row = dict(id=frame["id"], screen=frame["screen"], image=frame.get("image"),
                   disposition="blocked", reasons=list(frame["reasons"]), controls=[])
        rows.append(row)
        if frame["disposition"] != "imported": continue
        source = directory/"editor"/(frame["editorStem"]+".json")
        snapshot = output/"editor-snapshot"/source.name
        snapshots.append(copy_ref(ref(source), snapshot, 8*1024*1024))
        # Validate the exact captured editor snapshot, with the bound image beside it.
        shutil.copyfile(checked(ROOT, frame["image"]), snapshot.with_suffix(".png"))
        try:
            row["controls"] = parse_editor(batch, frame, snapshot)
            # Also detect tampering of the working image, not only immutable original.
            checked(ROOT, dict(path=str((directory/"editor"/(frame["editorStem"]+".png")).relative_to(ROOT)),
                               sha256=frame["image"]["sha256"]))
            if reviewer_kind == "software-test":
                for c in row["controls"]:
                    if c["disposition"] == "reviewed": c["disposition"] = "blocked"
                    c["reasons"].append("software_test_not_human")
            if not row["controls"]: row["reasons"].append("no_reviewed_controls")
            elif all(c["disposition"] in ("reviewed", "rejected") for c in row["controls"]):
                row["disposition"] = "reviewed" if any(c["disposition"] == "reviewed" for c in row["controls"]) else "rejected"
            else: row["reasons"].append("controls_pending")
        except (ValueError, OSError, KeyError, TypeError) as error:
            row["controls"] = []
            row["reasons"].append(str(error))
    pairs = []
    by_id = {f["id"]: f for f in rows}
    for spec in batch["pairs"]:
        a, b = [by_id[i] for i in spec["frames"]]
        controls = [next((c for c in f["controls"] if c["id"] == spec["controlID"]), None) for f in (a, b)]
        valid = (a["screen"] == b["screen"] and all(c and c["disposition"] == "reviewed" for c in controls)
                 and {c["state"] for c in controls} == {"focused", "unfocused"}
                 and len({control_label(c) for c in controls}) == 1)
        pairs.append(dict(**spec, disposition="reviewed" if valid else "blocked",
                          reason=None if valid else "incomplete_or_conflicting_pair"))
    version = FOCUS_REVISION if any(c.get('focusRole') for f in rows for c in f['controls']) else REVISION
    revision = dict(version=version, **FLAGS, batch=ref(local(batch_path)), editorSnapshots=snapshots,
                    reviewer=dict(id=reviewer, reference=reference, kind=reviewer_kind,
                                  completedAt=datetime.now(timezone.utc).isoformat(), confirmedBatch=True),
                    frames=rows, pairs=pairs, completeFrameCandidates=False,
                    frameCounts=dict(Counter(f["disposition"] for f in rows)),
                    controlCounts=dict(Counter(c["disposition"] for f in rows for c in f["controls"])))
    validate_batch(batch_path)
    write(output/"revision.json", revision, sealed=True)
    return revision


def crop_qa(batch_path, output, revision_path=None):
    from focus_runtime import identity, bounded_batches, invoke, RUNTIME_PREPROCESSING
    batch, output = validate_batch(batch_path), fresh(output)
    revision = None
    if revision_path:
        revision = read_revision(revision_path)
        require(revision["batch"] == ref(local(batch_path)), "wrong_revision_batch")
        for record in revision["editorSnapshots"]: checked(ROOT, record)
    items = []
    for frame in batch["frames"]:
        if frame["disposition"] != "imported": continue
        controls = frame["proposals"] if revision is None else next(f["controls"] for f in revision["frames"] if f["id"] == frame["id"])
        for c in controls:
            if c.get("disposition") == "rejected": continue
            items.append(dict(id=frame["id"]+":"+c["id"], path=str(checked(ROOT, frame["image"])),
                              sha256=frame["image"]["sha256"], bounds=c["bounds"]))
    runtime = identity()
    output.mkdir(parents=True)
    records = []
    for group in bounded_batches(items):
        reply = invoke(group)  # Deliberately no model argument.
        for row in reply["results"]:
            raw = base64.b64decode(row["png"], validate=True)
            im = Image.open(io.BytesIO(raw)); im.load()
            require(im.format == "PNG" and im.size == (256, 256), "wrong_crop_dimensions")
            path = output/(row["id"].replace(":", "--")+".png")
            with path.open("xb") as stream: stream.write(raw)
            records.append(dict(id=row["id"], crop=ref(path)))
    require([r["id"] for r in records] == [i["id"] for i in items], "incomplete_crops")
    require(identity() == runtime, "runtime_changed")
    for pair in batch["pairs"]:
        members = [next((r for r in records if r["id"] == f+":"+pair["controlID"]), None) for f in pair["frames"]]
        if all(members):
            sheet = Image.new("RGB", (512, 256))
            for n, record in enumerate(members):
                with Image.open(checked(ROOT, record["crop"])) as im: sheet.paste(im.convert("RGB"), (n*256, 0))
            sheet.save(output/(pair["id"]+"-pair.png"))
    report = dict(version="human-review-crop-qa-v1", **FLAGS, batch=ref(local(batch_path)),
                  revision=ref(local(revision_path)) if revision_path else None,
                  labelStatus="revision_diagnostics" if revision else "proposals_only", runtime=runtime,
                  preprocessing=RUNTIME_PREPROCESSING, expected=len(items), completed=len(records), crops=records)
    write(output/"crop-qa.json", report, sealed=True)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("import"); p.add_argument("index"); p.add_argument("output")
    p = sub.add_parser("validate"); p.add_argument("batch")
    p = sub.add_parser("finish"); p.add_argument("batch"); p.add_argument("output")
    p.add_argument("--reviewer", required=True); p.add_argument("--reference", required=True)
    p.add_argument("--reviewer-kind", required=True, choices=("human", "software-test"))
    p.add_argument("--confirm-batch", action="store_true")
    p = sub.add_parser("crop-qa"); p.add_argument("batch"); p.add_argument("output"); p.add_argument("--revision")
    args = parser.parse_args()
    try:
        if args.command == "import": result = import_batch(args.index, args.output)
        elif args.command == "validate": result = validate_batch(args.batch)
        elif args.command == "finish":
            result = finish(args.batch, args.output, reviewer=args.reviewer, reference=args.reference,
                            reviewer_kind=args.reviewer_kind, confirm_batch=args.confirm_batch)
        else: result = crop_qa(args.batch, args.output, args.revision)
        print(json.dumps({k: v for k, v in result.items() if k in
                          ("version", "counts", "frameCounts", "controlCounts", "distinctPixels", "expected", "completed")}, indent=2))
    except (ValueError, OSError, KeyError, TypeError) as error:
        parser.exit(2, f"Review blocked: {error}\n")


if __name__ == "__main__":
    main()
