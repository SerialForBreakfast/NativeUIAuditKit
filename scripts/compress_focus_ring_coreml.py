"""One isolated weight-only int8 export; never trains or promotes a model."""
import argparse
import json
from pathlib import Path

from export_focus_ring_coreml import export_paths, package_size_report, utc_now
from focus_ring_baseline import artifact_digest


def preflight(package, report, destination, identity, expected):
    report_path, destination = export_paths(report, destination, identity)
    package = Path(package).absolute()
    if any(p.is_symlink() for p in [package, *package.parents]):
        raise ValueError("symlink_package_path")
    from focus_dataset_contract import local
    local(package)
    if package == destination or package in destination.parents:
        raise ValueError("source_output_overlap")
    package_size_report(package)
    if artifact_digest(package) != expected:
        raise ValueError("source_package_changed")
    original = json.loads(report_path.read_text())
    if original.get("releaseEligible") is not False:
        raise ValueError("experimental_source_required")
    if Path(original["mlpackage"]).resolve() != package:
        raise ValueError("source_report_mismatch")
    if original.get("experimentalID") == identity:
        raise ValueError("distinct_identity_required")
    return package, destination, original


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("package", "source-report", "source-sha256", "output-dir", "experimental-id"):
        parser.add_argument("--" + name, required=True)
    args = parser.parse_args()
    package, destination, original = preflight(args.package, args.source_report,
        args.output_dir, args.experimental_id, args.source_sha256)
    import coremltools as ct
    config = ct.optimize.coreml.OptimizationConfig(global_config=
        ct.optimize.coreml.OpLinearQuantizerConfig(mode="linear_symmetric",
            dtype="int8", granularity="per_channel", weight_threshold=2048))
    source = ct.models.MLModel(str(package), skip_model_load=True)
    metadata = source.user_defined_metadata
    if (metadata.get("checkpointSHA256") != original["checkpointSHA256"] or
        metadata.get("modelID") != "focus-ring-experimental-" + original["experimentalID"] or
        metadata.get("releaseEligible") != "false"):
        raise ValueError("source_metadata_mismatch")
    compressed = ct.optimize.coreml.linear_quantize_weights(source, config=config)
    compressed.user_defined_metadata.update(dict(metadata))
    compressed.user_defined_metadata["modelID"] = "focus-ring-experimental-" + args.experimental_id
    compressed.user_defined_metadata["compression"] = "int8-linear-symmetric-per-channel-threshold2048"
    compressed.user_defined_metadata["sourcePackageSHA256"] = args.source_sha256
    destination.mkdir(parents=True, exist_ok=False)
    output = destination / "FocusRingDetector.mlpackage"
    compressed.save(str(output))
    if artifact_digest(package) != args.source_sha256:
        raise ValueError("source_changed_during_compression")
    result = {**original, **package_size_report(output), "generatedAt": utc_now(),
        "experimentalID": args.experimental_id, "mlpackage": str(output),
        "method": "FP16-to-int8-weight-only/per-channel/linear-symmetric/threshold2048",
        "coremltoolsVersion": ct.__version__, "sourcePackageSHA256": args.source_sha256,
        "packageSHA256": artifact_digest(output), "releaseEligible": False}
    with (destination / "focus_ring_detector_training_report.json").open("x") as stream:
        json.dump(result, stream, indent=2)
    print(json.dumps(result), flush=True)
    return 0 if result["size_gate_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
