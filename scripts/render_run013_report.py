#!/usr/bin/env python3
"""Render retained evaluation JSON only; never loads a model or changes metrics."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports/work/IOS-R013-EVAL"


def number(value):
    return "unavailable" if value is None else f"{value:.4f}"


def table(headers, rows):
    return ["| " + " | ".join(headers) + " |",
            "| " + " | ".join("---" for _ in headers) + " |"] + [
            "| " + " | ".join(str(v) for v in row) + " |" for row in rows]


def main():
    data = json.loads((OUT / "evaluation.json").read_text())
    baseline = data["baseline"]
    populations = data["populations"]
    lines = ["# Run013 evaluation metrics", "",
        "Source: [evaluation.json](evaluation.json). Custom all-point interpolated VOC AP,",
        "not official COCO/Ultralytics AP. Values are fractions; unsupported classes are",
        "unavailable and excluded from supported-class macro means, never imputed as zero.",
        "Precision/recall and TP/FP/FN use confidence ≥0.25 and IoU ≥0.50; AP uses all",
        "exported detections (confidence ≥0.001). Per-class AP50–95 averages ten thresholds.", "",
        "Only the 2,000 identical withheld cases support Run009→Run013 deltas. The",
        "400 addon cases are within-family diagnostics; 2,400 combined is supplementary.",
        "The historical original-corpus 0.586 has no numerical delta here.", ""]
    lines += table(["Population", "Images", "Classes", "mAP50", "mAP70", "mAP90", "mAP50–95"], [
        [label, report["imageCount"], report["supportedClasses"]] + [number(report["metrics"][k]) for k in
            ("map50", "map70", "map90", "map50_95")]
        for label, report in [("Run009 withheld",baseline)] + [("Run013 "+k,v) for k,v in populations.items()]])
    for label, report in [("Run009 withheld",baseline)] + [("Run013 "+k,v) for k,v in populations.items()]:
        lines += ["", "## " + label, ""]
        lines += table(["Class", "GT boxes", "AP50", "AP70", "AP90", "AP50–95", "Precision", "Recall", "TP", "FP", "FN"], [
            [r["class"], r["support"]] + [number(r[k]) for k in ("ap50","ap70","ap90","ap50_95","precision","recall")]
            + [r[k] for k in ("tp","fp","fn")] for r in report["perClass"]])
        lines += ["", "### Per-family supported-class means", ""]
        lines += table(["Family", "Images", "Classes", "mAP50", "mAP70", "mAP90", "mAP50–95"], [
            [f,r["imageCount"],r["supportedClasses"]] + [number(r["metrics"][k]) for k in
            ("map50","map70","map90","map50_95")] for f,r in report["perFamily"].items()])
    lines += ["", "## Identical-input class deltas (Run013 minus Run009)", ""]
    old = {r["class"]:r for r in baseline["perClass"]}
    supported = [r for r in populations["withheld"]["perClass"] if r["support"]]
    supported.sort(key=lambda r:r["ap50"]-old[r["class"]]["ap50"])
    lines += table(["Class", "Support", "ΔAP50", "ΔAP70", "ΔAP90", "ΔAP50–95"], [
        [r["class"],r["support"]] + [number(r[k]-old[r["class"]][k]) for k in ("ap50","ap70","ap90","ap50_95")]
        for r in supported])
    lines += ["", "## Identical-input family deltas", ""]
    lines += table(["Family", "ΔmAP50", "ΔmAP70", "ΔmAP90", "ΔmAP50–95"], [
        [f] + [number(r["metrics"][k]-baseline["perFamily"][f]["metrics"][k]) for k in
        ("map50","map70","map90","map50_95")]
        for f,r in populations["withheld"]["perFamily"].items()])
    lines += ["", "## Misses, false positives and confusion", "",
        "Class-specific FP/FN above are the operating-point counts. The association",
        "below is class-agnostic, one-to-one and diagnostic only; it does not redefine AP.",
        "Background→class means unmatched prediction; class→background means unmatched GT.",
        "Full family/class metrics and bounded image-level examples are in evaluation.json.", ""]
    for pop in ("withheld", "addon"):
        report=populations[pop]
        lines += ["### " + pop, ""]
        errors=sorted((r for r in report["confusion"] if r["truth"]!=r["predicted"]),key=lambda r:-r["count"])
        lines += table(["Truth", "Predicted", "Count"],[[r[k] for k in ("truth","predicted","count")] for r in errors[:20]])
        lines += ["", "Representative examples (manifest order, not a new sample or ranked severity):", ""]
        lines += table(["Image ID", "Truth", "Prediction"], [[r[k] for k in ("imageID","truth","predicted")] for r in report["errorExamples"][:15]])
        lines += [""]
    with (OUT / "metrics.md").open("x") as handle:
        handle.write("\n".join(lines)+"\n")
    print(OUT / "metrics.md")


if __name__ == "__main__":
    main()
