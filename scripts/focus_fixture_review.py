"""Numbered review sheets for retained TTR crops. No capture, inference or approval."""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from focus_dataset_contract import ROOT, digest, local, member, pixel_digest, validate_manifest
from focus_mixed_assembly import reference, checked


def prepare(manifests, output):
    output = local(output)
    if output.exists(): raise ValueError("output_collision")
    paths = sorted(map(local, manifests))
    if not paths or len(set(paths)) != len(paths): raise ValueError("missing_or_duplicate_manifests")
    docs = []
    for path in paths:
        doc = json.loads(path.read_text())
        if doc.get("version") != "1.5" or doc.get("sourceKind") != "simulatorFixture":
            raise ValueError("review_requires_ttr_simulator_manifest")
        validate_manifest(doc, path.parent)
        docs.append((path, doc))
    output.mkdir(parents=True, exist_ok=False)
    records, pages = [], []
    font = ImageFont.load_default(size=16)
    pixels = {}
    for path, doc in docs:
        root = local(ROOT/doc["sourceRoot"])
        refs = reference(path)
        for start in range(0, len(doc["pairs"]), 4):
            pairs = doc["pairs"][start:start+4]
            page = Image.new("RGB", (600, 380+len(pairs)*290), "#252525")
            draw = ImageDraw.Draw(page)
            draw.text((12, 8), doc["corpusID"], font=font, fill="white")
            first = member(root, pairs[0]["frames"]["focused"]["path"])
            with Image.open(first) as original:
                preview = original.convert("RGB"); preview.thumbnail((576, 324))
                page.paste(preview, (12, 35))
            draw.text((12, 358), "Native focused (left) / unfocused (right)", font=font, fill="white")
            for offset, pair in enumerate(pairs):
                number = len(records)+1
                y = 382+offset*290
                draw.text((12, y), f"{number:03d} {pair['pair_id']} {pair['elementID']}", font=font, fill="white")
                record = {"number":number, "corpusID":doc["corpusID"], "pairID":pair["pair_id"],
                          "manifest":refs, "frames":{}, "crops":{}, "labelSource":pair["labelSource"]}
                for role, x in (("focused", 12), ("unfocused", 312)):
                    crop = member(path.parent, pair[role+"_crop"])
                    with Image.open(crop) as im: page.paste(im.convert("RGB"), (x, y+26))
                    frame = pair["frames"][role]
                    frame_path = member(root, frame["path"])
                    for kind, source in (("frames", frame_path), ("crops", crop)):
                        ref = reference(source)
                        key = (ref["path"], ref["sha256"])
                        if key not in pixels: pixels[key] = pixel_digest(ROOT, ref)
                        record[kind][role] = {**ref, "pixelSHA256":pixels[key]}
                    record["frames"][role]["bounds"] = frame["bounds"]
                records.append(record)
            name = f"sheet-{len(pages)+1:03d}.png"
            page.save(output/name)
            pages.append({"file":name, "sha256":hashlib.sha256((output/name).read_bytes()).hexdigest(),
                          "numbers":[r["number"] for r in records[-len(pairs):]]})
    for record in records:
        checked(record["manifest"])
        for kind in ("frames", "crops"):
            for r in record[kind].values(): checked({k:r[k] for k in ("path", "sha256")})
    inventory = {"version":"focus-fixture-review-inventory-v1", "pairs":records, "pages":pages,
                 "trainingApproval":False, "reviewStatus":"pending-agent-visual-review",
                 "pairCount":len(records), "frameFiles":len({r["path"] for p in records for r in p["frames"].values()}),
                 "distinctFramePixels":len({r["pixelSHA256"] for p in records for r in p["frames"].values()}),
                 "distinctCropPixels":len({r["pixelSHA256"] for p in records for r in p["crops"].values()})}
    inventory["seal"] = digest(inventory)
    with (output/"inventory.json").open("x") as stream: json.dump(inventory, stream, indent=2, allow_nan=False)
    return inventory


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifests", nargs="+", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        doc = prepare(args.manifests, args.output)
        print(json.dumps({k:doc[k] for k in ("pairCount","frameFiles","distinctFramePixels","distinctCropPixels","trainingApproval","seal")}))
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.exit(2, str(error)+"\n")


if __name__ == "__main__": main()
