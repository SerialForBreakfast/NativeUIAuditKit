"""Check standalone annotation coverage for two qualified UIKit families."""
from collections import Counter
from pathlib import Path
import research_queue as q
from experiment_templates import checked, pin

OUT = None
CONTROL_TYPES = dict(slider="slider", segmentedControl="segmentedControl",
    activityIndicator="activityIndicator", progressView="progressView", pageControl="pageControl",
    toggle="toggle", secureTextField="secureField", resetButton="secondaryButton",
    navigationBar="navigationBar")
CONTROL_LABELS = ("sliderLabel", "segmentLabel", "activityLabel", "progressLabel",
                  "pageLabel", "toggleLabel", "secureLabel")


def completeness(family, elements):
    """Return missing or conflicting supplied annotations. Do not infer boxes."""
    visible = [e for e in elements if not e.get("excluded")]
    ids = [e["id"] for e in visible]
    q.require(len(ids) == len(set(ids)), "ios_annotation_duplicate_id")
    actual = {e["id"]: e["elementType"] for e in visible}
    if family == "UIKitControls":
        expected = dict(CONTROL_TYPES, **{k: "label" for k in CONTROL_LABELS})
    else:
        q.require(family == "UIKitToggleForm", "ios_annotation_family")
        switches = sorted(k for k in actual if k.startswith("toggle_"))
        q.require(4 <= len(switches) <= 12, "ios_annotation_toggle_count")
        q.require(set(switches) == {f"toggle_{i}" for i in range(len(switches))},
                  "ios_annotation_toggle_identity")
        headers = [k for k in actual if k.startswith("sectionHeader_")]
        expected = dict(navigationBar="navigationBar", ctaButton="primaryButton")
        expected.update({k: "toggle" for k in switches})
        expected.update({f"rowLabel_{i}": "label" for i in range(len(switches))})
        # Missing headers are a failed annotation contract, not evidence of no headers.
        expected.update({f"sectionHeader_{i}": "label" for i in range(max(2, len(headers)))})
        q.require(len(headers) <= 3, "ios_annotation_header_count")
    problems = [dict(id=k, expected=v, actual=actual.get(k))
                for k, v in expected.items() if actual.get(k) != v]
    problems.extend(dict(id=k, expected=None, actual=actual[k]) for k in actual.keys() - expected.keys())
    return problems


def review(manifest_path, summary_path):
    manifest = q.load(manifest_path)
    summary = q.load(summary_path)
    q.require(manifest["version"] == "ios-native-capture-manifest-v1", "ios_annotation_manifest")
    q.require(summary["sourcesMatchBuild"], "ios_annotation_source_drift")
    q.require(not summary["bodyChecks"]["failingFamilies"], "ios_annotation_geometry")
    rows = manifest["rows"]
    q.require(rows and len({r["id"] for r in rows}) == len(rows), "ios_annotation_duplicate_frame")
    groups = {}
    hashes = {}
    findings = []
    counts = Counter()
    for row in rows:
        q.require(row["role"] == "training" and row["trainingEligible"] is False,
                  "ios_annotation_role")
        q.require(row["status"] == "eligible" and not row["reasons"] and not row["rejectedLabels"],
                  "ios_annotation_rejected_frame")
        q.require(groups.setdefault(row["group"], row["role"]) == row["role"], "ios_annotation_group_leak")
        for key in ("image", "sidecar"):
            ref = row[key]
            path = q.local_path(manifest_path.parent, ref["path"])
            q.require(q.digest(path) == ref["sha256"], "ios_annotation_payload_changed")
        sidecar = q.load(q.local_path(manifest_path.parent, row["sidecar"]["path"]))
        problems = completeness(row["family"], sidecar["elements"])
        findings.extend(dict(frame=row["id"], **p) for p in problems)
        counts.update(e["elementType"] for e in sidecar["elements"] if not e.get("excluded"))
        q.require(hashes.setdefault(row["image"]["sha256"], row["group"]) == row["group"],
                  "ios_annotation_duplicate_group")
    return dict(version="ios-annotation-qualification-v1",
        outcome="contradicted" if findings else "supported", frames=len(rows), groups=len(groups),
        uniqueImages=len(hashes), classCounts=dict(counts), findings=findings,
        geometryQualified=True, annotationContractPassed=not findings,
        trainingAdmitted=False, modelAccepted=False,
        nextAction="Repair the named annotation contract." if findings else
                   "Verify evaluation exclusions and prepare complete trainer membership.",
        limitation="Source-specific annotation contract. This is not independent visual accuracy or training admission.")


def run():
    spec = q.load(OUT.parents[2] / "spec.json")
    deps = q.dependency_inputs(spec, OUT.parents[4])
    q.require(len(deps) == 1 and len(deps[0]["outputs"]) == 2, "ios_annotation_dependency")
    result = review(checked(deps[0]["outputs"][0]), checked(deps[0]["outputs"][1]))
    q.save(OUT / "benchmark_summary.json", result)
    q.save(OUT / "artifact-receipt.json", dict(version="research-artifact-v1",
        outputs=[dict(path="benchmark_summary.json", sha256=q.digest(OUT / "benchmark_summary.json"))]))


def specification(ident, producer, queue=q.QUEUE):
    parent = q.load(queue / "jobs" / producer / "spec.json")
    q.require(parent.get("template", {}).get("id") == "T46", "ios_annotation_producer")
    return dict(version="research-spec-v2", id=ident, task="FLOW478-01", owner="Maximum-mini-NUIAK",
        kind="screen", authority="diagnostic", jobKind="artifact",
        hypothesis="Explicit standalone labels close the measured annotation omission.",
        question="Do all supported visible controls and standalone labels satisfy the source annotation contract?",
        controlledComparison="Keep source groups and images fixed. Compare missing labels with the repaired export.",
        decisionRule="Missing or conflicting annotations reject the label contract. Never infer training admission.",
        nextActionByOutcome=dict(supported="Prepare complete membership with evaluation exclusions.",
                                 contradicted="Repair the exact named annotations."),
        inputs=[pin(Path(__file__))],
        dependencies=[dict(job=producer, specSHA256=q.text_digest(parent),
                           outputs=["manifest.json", "benchmark_summary.json"])],
        evidence=dict(reads=[], artifactReceipt="artifact-receipt.json"),
        adapter=dict(type="python-callable", steps=["ios_annotation_contract478.run"],
                     outputAttributes=["ios_annotation_contract478.OUT"]),
        limits=dict(timeoutSeconds=800, maxOutputBytes=100_000_000, maxAttempts=1))
