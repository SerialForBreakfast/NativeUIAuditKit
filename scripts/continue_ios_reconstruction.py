"""Explicit, no-retry r6 native continuation. Plans do not mutate the simulator.

Each execution phase requires --execute. Failed phases cannot be overwritten.
All host artifacts remain project-local; only the exact simulator container is used.
"""
import argparse
import json
import os
from pathlib import Path
import plistlib
import re
import shutil
import subprocess
import time

import corpus_retention as retention
import validate_reconstructed_corpus as v

ROOT = v.ROOT
TARGET = "F3EF9DB8-0B0F-4757-B653-D1628269F6FF"
BUNDLE = "com.nativeuiauditkit.generatorrunner"
PREFIX = ROOT / ".build/debug-output/p0c-resume/r6-verified-prefix"
DESTINATION = ROOT / "NativeUITrainer/reconstructed_corpora/ios-41class-r6"
PREFIX_COUNTS = {"train": 10140, "validation": 2400, "test": 1800}
PROBES = [f"{family}:19:probe-{i}" for family in
          ("UIKitControls", "ChromeCoverage", "DynamicTypeOverflow") for i in range(2)]


def write(path, value):
    with path.open("x") as stream:
        json.dump(value, stream, indent=2, sort_keys=True)


def local(path):
    path = Path(path).absolute()
    v.require(path.resolve() == path and path.is_relative_to(ROOT), "host_output_boundary")
    return path


def sources():
    paths = set()
    for folder in ("GeneratorRunner", "NativeUIDatasetGenerator"):
        paths.update(p for p in (ROOT / folder).rglob("*")
                     if p.is_file() and p.suffix in (".swift", ".pbxproj", ".plist", ".xcscheme")
                     and "xcuserdata" not in p.parts)
    paths.update(ROOT / "scripts" / name for name in
                 ("continue_ios_reconstruction.py", "validate_reconstructed_corpus.py", "corpus_retention.py"))
    return {str(p.relative_to(ROOT)): v.sha256(p) for p in sorted(paths)}


def plan(name, target=TARGET, prefix_audit=None):
    v.require(target == TARGET, "wrong_target")
    v.require(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", name), "unsafe_staging_name")
    v.require(not DESTINATION.exists(), "destination_collision")
    doc = v.read_json(PREFIX / "manifest.json")
    v.require(len(doc["entries"]) == 14340, "wrong_prefix_count")
    return {"version": "ios-reconstruction-r6-v1", "target": target, "stagingName": name,
            "prefix": str(PREFIX), "destination": str(DESTINATION), "sourceHashes": sources(),
            "prefixManifestSHA256": v.sha256(PREFIX / "manifest.json"),
            "prefixLedgerSHA256": v.sha256(PREFIX / "capture-ledger.json"),
            "expectedCounts": v.EXPECTED, "remaining": {"UIKitControls": 700,
            "UIKitForm": 700, "UIKitList": 700, "UIKitToggleForm": 300, "WizardStepFlow": 200},
            "probeIDs": PROBES, "generationTimeoutSeconds": 5400,
            "modelGates": "not_assessed", "trainingAuthorized": False,
            "prefixAudit": {"path": str(local(prefix_audit)), "sha256": v.sha256(local(prefix_audit))}
            if prefix_audit else None}


def check_pins(doc):
    v.require(doc["target"] == TARGET, "wrong_target")
    v.require(doc["sourceHashes"] == sources(), "source_changed")
    for name, key in (("manifest.json", "prefixManifestSHA256"),
                      ("capture-ledger.json", "prefixLedgerSHA256")):
        v.require(v.sha256(PREFIX / name) == doc[key], "prefix_changed:" + name)


def command(args, timeout=30):
    return subprocess.check_output(args, cwd=ROOT, text=True, timeout=timeout).strip()


def runtime():
    version = command(["xcodebuild", "-version"])
    v.require(version == "Xcode 26.6\nBuild version 17F113", "wrong_toolchain")
    inventory = json.loads(command(["xcrun", "simctl", "list", "devices", "available", "--json"]))
    matches = [(r, d) for r, ds in inventory["devices"].items() for d in ds if d["udid"] == TARGET]
    v.require(len(matches) == 1, "missing_or_ambiguous_target")
    r, device = matches[0]
    v.require(r == "com.apple.CoreSimulator.SimRuntime.iOS-26-5"
              and device.get("isAvailable") and device["state"] == "Booted"
              and device["deviceTypeIdentifier"] == "com.apple.CoreSimulator.SimDeviceType.iPhone-17-Pro",
              "wrong_or_unavailable_runtime")
    return {"toolchain": version, "runtime": r, "device": device}


def container():
    p = Path(command(["xcrun", "simctl", "get_app_container", TARGET, BUNDLE, "data"]))
    expected = Path.home() / "Library/Developer/CoreSimulator/Devices" / TARGET / "data/Containers/Data/Application"
    v.require(p.is_absolute() and p.resolve() == p and p.parent == expected and p.is_dir(),
              "invalid_container")
    return p


def enough_space(path, needed):
    v.require(shutil.disk_usage(path).free >= needed, "insufficient_staging_retrieval_space")


def copy_new(source, destination, exclude_finder=False):
    v.require(not destination.exists() and not destination.is_symlink(), "staging_collision")
    v.require(destination.parent.resolve() == destination.parent, "unsafe_staging_parent")
    v.require(source.resolve() == source and not any(p.is_symlink() for p in source.rglob("*")), "source_symlink")
    existing_parent = destination.parent
    while not existing_parent.exists():
        existing_parent = existing_parent.parent
    enough_space(existing_parent, sum(p.stat().st_size for p in source.rglob("*") if p.is_file()) + 2_000_000_000)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, destination, ignore=shutil.ignore_patterns(".DS_Store") if exclude_finder else None)
    for p in source.rglob("*"):
        v.require(not p.is_symlink(), "source_symlink")
        if p.is_file() and not (exclude_finder and p.name == ".DS_Store"):
            v.require(v.sha256(p) == v.sha256(destination / p.relative_to(source)), "copy_hash")


def prefix_evidence(doc):
    ref = doc.get("prefixAudit")
    if ref:
        path = local(ref["path"])
        v.require(v.sha256(path) == ref["sha256"], "changed_audit")
        audit = v.read_json(path)
    else:
        audit = v.validate(PREFIX, PREFIX_COUNTS)
    v.require(audit["manifestSHA256"] == doc["prefixManifestSHA256"]
              and audit["captureLedgerSHA256"] == doc["prefixLedgerSHA256"]
              and audit["validatorSHA256"] == v.sha256(Path(v.__file__))
              and audit["schemaSHA256"] == v.sha256(v.SCHEMA)
              and audit["generatorSHA256"] == v.sha256(v.GENERATOR)
              and audit["splitCounts"] == PREFIX_COUNTS
              and audit["manifestEntries"] == 14340
              and all(m["valid"] for m in audit["members"]), "incompatible_prefix_audit")
    errors = audit["errors"]
    v.require(not errors or (len(errors) == 1 and errors[0]["error"] == "unindexed_members"
              and all(Path(p).name == ".DS_Store" for p in errors[0]["members"])), "invalid_prefix")
    inv = retention.inventory(PREFIX, exclude_finder_metadata=True)
    by_name = {m["path"]: m["sha256"] for m in inv["members"]}
    expected = {"manifest.json", "capture-ledger.json"}
    if "balance_report.md" in by_name:
        expected.add("balance_report.md")
    for row in audit["members"] + audit["rejectedDuplicates"]:
        image = row["path"]
        annotation = str(Path(image).with_suffix(".json"))
        expected.update((image, annotation))
        v.require(by_name.get(image) == row["imageSHA256"] and
                  by_name.get(annotation) == row["annotationSHA256"], "audited_member_changed")
    v.require(set(by_name) == expected, "audit_membership_changed")
    return audit, inv


def run_logged(args, work, name, timeout):
    log = work / (name + ".log")
    env = dict(os.environ, TMPDIR=str(work / "tmp"),
               CLANG_MODULE_CACHE_PATH=str(work / "module-cache"),
               SWIFT_MODULECACHE_PATH=str(work / "module-cache"))
    started = time.monotonic()
    with log.open("x") as output:
        process = subprocess.Popen(args, cwd=ROOT, env=env, stdout=output, stderr=subprocess.STDOUT)
        try:
            code = process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            process.terminate()  # Only the xcodebuild process created by this invocation.
            try:
                process.wait(timeout=20)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=20)
            write(work / (name + "-result.json"), {"timeout": True, "pid": process.pid,
                  "cleanup": "native_test_state_unresolved", "seconds": time.monotonic() - started})
            raise RuntimeError("timeout_preserved_no_retry:" + name)
    result = {"command": args, "exitCode": code, "seconds": time.monotonic() - started,
              "logSHA256": v.sha256(log)}
    write(work / (name + "-result.json"), result)
    v.require(code == 0, "command_failed:" + name)
    return log


def require_test_pass(log, method):
    text = log.read_text()
    v.require(re.search(r"Test Case .*" + re.escape(method) + r".* passed", text)
              and not re.search(r"Test Case .*" + re.escape(method) + r".* skipped", text),
              "test_not_executed_or_skipped")


def retrieve_completed(work, doc):
    """Recovery of completed evidence never invokes a native test or recapture."""
    result = v.read_json(work / "generate-result.json")
    v.require(result.get("exitCode") == 0 and not result.get("timeout"), "generation_incomplete")
    log = work / "generate.log"
    v.require(v.sha256(log) == result["logSHA256"], "generation_log_changed")
    require_test_pass(log, "testRemainingReconstructionQualification")
    current = container() / "Documents/reconstruction" / doc["stagingName"]
    v.require(not (current / "generation-failed.txt").exists(), "persisted_failure")
    v.require(len(v.read_json(current / "manifest.json")["entries"]) == 16940, "partial_run")
    copy_new(current, DESTINATION)
    write(work / "retrieval.json", {"initialContainer": v.read_json(work / "staged.json")["container"],
          "retrievedFrom": str(current), "destination": str(DESTINATION),
          "cleanup": "no_status_overrides_created; test_window_cleanup_completed"})


def test(work, phase, klass, method, environment, timeout):
    runfiles = [p for p in (work / "DerivedData/Build/Products").glob("*.xctestrun")
                if not p.name.startswith("nua-")]
    v.require(len(runfiles) == 1, "ambiguous_xctestrun")
    base = plistlib.loads(runfiles[0].read_bytes())
    targets = [t for config in base.get("TestConfigurations", []) for t in config["TestTargets"]]
    if not targets:
        targets = [t for t in base.values() if isinstance(t, dict) and "TestBundlePath" in t]
    v.require(len(targets) == 1, "ambiguous_test_targets")
    targets[0].setdefault("EnvironmentVariables", {}).update(environment)
    path = runfiles[0].parent / ("nua-" + phase + ".xctestrun")
    with path.open("xb") as stream:
        plistlib.dump(base, stream)
    log = run_logged(["xcodebuild", "test-without-building", "-xctestrun", str(path),
        "-destination", "platform=iOS Simulator,id=" + TARGET, "-parallel-testing-enabled", "NO",
        "-resultBundlePath", str(work / (phase + ".xcresult")),
        "-only-testing:GeneratorRunnerTests/" + klass + "/" + method], work, phase, timeout)
    require_test_pass(log, method)


def execute_phase(phase, work, doc):
    check_pins(doc)
    observed = runtime()  # Fail before any staging/capture if CoreSimulator is unavailable.
    write(work / (phase + "-runtime.json"), observed)
    if phase == "retrieve":
        retrieve_completed(work, doc)
        return
    if phase == "build":
        audit, inv = prefix_evidence(doc)
        write(work / "prefix-validation.json", audit)
        write(work / "prefix-inventory.json", inv)
        enough_space(ROOT, inv["totalBytes"] * 3 + 10_000_000_000)
        run_logged(["xcodebuild", "build-for-testing", "-project", "GeneratorRunner/GeneratorRunner.xcodeproj",
          "-scheme", "GeneratorRunnerTests", "-destination", "platform=iOS Simulator,id=" + TARGET,
          "-derivedDataPath", str(work / "DerivedData"), "-configuration", "Debug",
          "CODE_SIGNING_ALLOWED=NO", "CODE_SIGNING_REQUIRED=NO"], work, "build", 900)
        apps = list((work / "DerivedData/Build/Products/Debug-iphonesimulator").glob("GeneratorRunner.app"))
        v.require(len(apps) == 1, "missing_matching_app")
        app = apps[0]
        info = plistlib.loads((app / "Info.plist").read_bytes())
        v.require(info["CFBundleIdentifier"] == BUNDLE, "wrong_app_identity")
        write(work / "build-identity.json", {"bundle": BUNDLE, "sourceHashes": doc["sourceHashes"],
              "files": {str(p.relative_to(app)): v.sha256(p) for p in app.rglob("*") if p.is_file()}})
        command(["xcrun", "simctl", "install", TARGET, str(app)], 120)
        write(work / "installed-container.json", {"container": str(container())})
        return
    v.require((work / "build-identity.json").is_file(), "build_not_pinned")
    app = Path(command(["xcrun", "simctl", "get_app_container", TARGET, BUNDLE, "app"]))
    identity = v.read_json(work / "build-identity.json")
    for name, digest in identity["files"].items():
        v.require(v.sha256(app / name) == digest, "installed_build_changed:" + name)
    stage_name = doc["stagingName"]
    if phase == "stride":
        before = container()
        previous = {p.name for p in (before / "Documents").glob("uikit-stride-probe-*")}
        test(work, phase, "GenerateDatasetTests", "testUIKitControlSeedStrideVisiblyVaries",
             {"NUA_RECONSTRUCTION_RUN_NAME": stage_name + "-qualification"}, 600)
        after = container()
        outputs = [p for p in (after / "Documents").glob("uikit-stride-probe-*") if p.name not in previous]
        v.require(len(outputs) == 1, "missing_or_ambiguous_stride_output")
        copy_new(outputs[0], work / "stride-capture")
        v.require(len(list((work / "stride-capture").glob("*.png"))) == 64, "stride_count")
        write(work / "stride-accepted.json", {"beforeContainer": str(before), "afterContainer": str(after),
              "images": 64, "distinctPerProfile": 32})
    elif phase == "generate":
        v.require((work / "stride-accepted.json").is_file(), "native_stride_not_qualified")
        retention.verify(v.read_json(work / "prefix-inventory.json"), PREFIX)
        initial = container()
        parent = initial / "Documents/reconstruction"
        parent.mkdir(exist_ok=True)
        stage = parent / stage_name
        enough_space(parent, v.read_json(work / "prefix-inventory.json")["totalBytes"] * 3 + 5_000_000_000)
        copy_new(PREFIX, stage, exclude_finder=True)
        write(work / "staged.json", {"container": str(initial), "staging": str(stage)})
        try:
            test(work, phase, "GenerateDatasetTests", "testRemainingReconstructionQualification",
                 {"NUA_RECONSTRUCTION_RUN_NAME": stage_name}, 5400)
        except Exception:
            # Resolve again even on failure; never assume installation preserves the UUID.
            current = container() / "Documents/reconstruction" / stage_name
            if current.is_dir():
                copy_new(current, work / "failed-generation")
            raise
        retrieve_completed(work, doc)
    elif phase == "probes":
        catalog = work / "catalog-v2.json"
        v.require(catalog.is_file(), "freeze_independent_catalog_first")
        test(work, phase, "VisualProbeBatchTest", "testExplicitVisualProbeBatch", {
            "NUA_PROBE_EXECUTION": "approved-development-probe", "NUA_PROBE_SIMULATOR_UUID": TARGET,
            "NUA_PROBE_CATALOG": str(catalog), "NUA_PROBE_CATALOG_SHA256": v.sha256(catalog),
            "NUA_PROBE_CASE_IDS_JSON": json.dumps(PROBES), "NUA_PROBE_OUTPUT_NAME": stage_name}, 300)
        copy_new(container() / "Documents/visual-probes" / stage_name, work / "visual-probes")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=["plan", "preflight", "build", "stride", "generate", "retrieve", "probes"])
    parser.add_argument("--work", required=True, type=Path)
    parser.add_argument("--name", default="ios-r6-20260923")
    parser.add_argument("--target", default=TARGET)
    parser.add_argument("--prefix-audit", type=Path)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    work = local(args.work)
    if args.phase == "plan":
        v.require(not work.exists(), "work_collision")
        doc = plan(args.name, args.target, args.prefix_audit)
        work.mkdir(parents=True)
        write(work / "plan.json", doc)
        print(json.dumps(doc, indent=2))
        return
    doc = v.read_json(work / "plan.json")
    v.require(args.target == doc["target"], "wrong_target")
    check_pins(doc)
    if args.phase == "preflight":
        print(json.dumps(runtime(), indent=2))
        return
    v.require(args.execute, "explicit_execution_required")
    for name in ("tmp", "module-cache"):
        (work / name).mkdir(exist_ok=True)
    execute_phase(args.phase, work, doc)
    print("completed", args.phase, flush=True)


if __name__ == "__main__":
    main()
