"""Check actual host-test packets, corruption cases, renamed IDs and final train tensors."""
import argparse
import copy
import hashlib
from collections import Counter, defaultdict
from pathlib import Path

from PIL import Image
import research_queue as q
from detector_training419 import prepare, TRAIN_ONLY_VERSION
from framework_projection604 import tvos_classes
from ios_native_form_projection607 import project
from milestone_readback604 import decode_batch
from ios_native_capture_t46 import measure_bodies
from qpacket_import604 import _iou_edge
from template_inputs398 import pin


def attachments(folder):
    pairs = defaultdict(dict)
    for report in q.load(folder / "manifest.json"):
        for item in report["attachments"]:
            file = folder / item["exportedFileName"]
            key = item["suggestedHumanReadableName"].split("_")[0]
            q.require(file.suffix not in pairs[key], "duplicate_attachment")
            pairs[key][file.suffix] = file
    return pairs


def challenges(doc, image, other):
    def reject(bad, png, reason):
        try:
            project(bad, png)
        except ValueError as exc:
            if reason == str(exc):
                return reason
            raise
        raise ValueError("accepted corrupted evidence: " + reason)
    results = [reject(doc, other, "frame_identity")]
    for mutation, reason in [
        ("duplicate", "duplicate_identity"), ("stale", "observation_identity"),
        ("missing_owner", "invalid_owner"), ("lost_owner", "caption_inventory"),
        ("lost_control", "target_inventory"), ("unknown", "unknown_construction"),
        ("shifted_child", "owner_geometry"), ("bad_box", "body_geometry"),
        ("secure_button", "secure_conflict")]:
        bad = copy.deepcopy(doc)
        rows = bad["objects"]
        child = next(o for o in rows if o["owner"] is not None)
        button = next(o for o in rows if o["id"] == child["owner"])
        if mutation == "duplicate": rows.append(dict(button))
        elif mutation == "stale": child["scene"] += "-old"
        elif mutation == "missing_owner": child["owner"] = "absent"
        elif mutation == "lost_owner": child["owner"] = None
        elif mutation == "lost_control": rows.remove(next(o for o in rows if o["secure"]))
        elif mutation == "unknown": button["primitive"] = "UIView"
        elif mutation == "shifted_child": child["edges"] = [1, 1, 4, 4]
        elif mutation == "bad_box": button["edges"][0] = -1
        elif mutation == "secure_button": button["secure"] = True
        results.append(reject(bad, image, reason))
    return results


def membership(rows):
    return dict(version=TRAIN_ONLY_VERSION, trainingAdmitted=True,
                calibrationPolicy="none-fixed-last-training-diagnostics", names=tvos_classes(), rows=rows)


def signature(targets):
    return sorted((r["class"], r["secure"], tuple(r["bounds"])) for r in targets)


def pixel_hash(image):
    with Image.open(image) as im:
        return hashlib.sha256(str(im.size).encode() + im.convert("RGBA").tobytes()).hexdigest()


def verify(folder, output):
    pairs = attachments(folder)
    families = ["UIKitForm", "SwiftUIForm607"]
    q.require(set(pairs) == {f"{f}-{v}" for f in families for v in (0,1)}, "capture_inventory")
    summary, admitted, primaries = {}, [], {}
    for family in families:
        other = next(f for f in families if f != family)
        for v in (0,1):
            name = f"{family}-{v}"
            img, facts = pairs[name][".png"], pairs[name][".json"]
            doc = q.load(facts)
            q.require(doc["family"] == family, "capture_family")
            observations = project(doc, img)
            targets = [r for r in observations if r["disposition"] == "target"]
            rejected = challenges(doc, img, pairs[other+"-0"][".png"])
            row = dict(id=name, group=f"{family}:{doc['seed']}", role="train", trainingEligible=True,
                       labelsComplete=True, image=pin(img), controls=targets, width=doc["width"], height=doc["height"])
            ds, _ = prepare(membership([row]), output / name)
            decoded = decode_batch(ds, tvos_classes())[name]["boxes"]
            tensor_signature = sorted((b["cls"], tuple(b["box_src_px"])) for b in decoded)
            edges = []
            for c in targets:
                best = min((b for b in decoded if b["cls"] == c["class"]),
                           key=lambda b: _iou_edge(c["bounds"],b["box_src_px"])[1])
                edges.append(_iou_edge(c["bounds"],best["box_src_px"])[1])
                decoded.remove(best)
            q.require(not decoded and max(edges)<1, "tensor_mismatch")
            ids = {o["id"] for o in observations}
            snapshot = (doc["image"], signature(targets), tensor_signature)
            if v == 0:
                primaries[family] = (snapshot, ids)
                admitted.append(row)
            else:
                original, old_ids = primaries[family]
                q.require(original == snapshot and ids.isdisjoint(old_ids), "rename_changed_result")
            pixel_elements = [dict(id=t["id"], elementType=t["class"], knownIssues=[], excluded=False,
                                   boundsPixels=dict(zip(("x","y","width","height"),t["bounds"]))) for t in targets]
            pixel_checks = measure_bodies(img, dict(image=dict(scale=3),elements=pixel_elements))
            for item in pixel_checks:
                if item["elementType"] == "textField":
                    q.require(item.get("v2",item)["status"] == "tight", "input_pixel_geometry")
            summary[name] = dict(facts=pin(facts), pixelChecks=pixel_checks, targetCounts=dict(Counter(r["class"] for r in targets)),
                                 dispositions=observations, maxEdgePx=max(edges), rejected=rejected)
    historical = q.load(q.ROOT/"reports/work/REPAIR478/ios-toggles-membership-v2.json")["exclusion"]
    inv_path = q.ROOT/historical["path"]
    q.require(q.digest(inv_path)==historical["sha256"], "inventory_hash")
    inv = q.load(inv_path)
    q.require(inv["integrityPassed"] and not inv["errors"], "inventory_invalid")
    used = {r["pixelSHA256"] for r in inv["members"]}
    groups = {f"{r['family']}:{r['seed']}" for r in inv["members"]}
    for folder606 in ("frames", "training-frames"):
        for img in (q.ROOT/"reports/work/IOS606"/folder606).glob("*.png"):
            used.add(pixel_hash(img))
            profile = q.load(img.with_suffix(".json"))["generatorProfile"]
            groups.add(f"{profile['templateFamily']}:{profile['seed']}")
    selected = []
    for row in admitted:
        pix = pixel_hash(q.ROOT/row["image"]["path"])
        eligible = pix not in used and row["group"] not in groups
        summary[row["id"]]["eligibleAfterExclusions"] = eligible
        if eligible: selected.append(row)
        used.add(pix)
        groups.add(row["group"])
    q.save(output/"readback.json",summary)
    if selected: q.save(output/"membership.json",dict(membership(selected),exclusion=historical))
    print("Eligible captures:",[r["id"] for r in selected])
    print("Maximum decoded edge error:",max(s["maxEdgePx"] for s in summary.values()))


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("attachments",type=Path)
    p.add_argument("output",type=Path)
    args=p.parse_args()
    verify(args.attachments.resolve(),args.output.resolve())
