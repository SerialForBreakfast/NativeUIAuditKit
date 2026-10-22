"""One isolated weight-only int8 or 6-bit export; never trains or promotes a model."""
import argparse
import json
from pathlib import Path

# B405-128: frozen compression settings. `palette6` uses the uniform look-up table because the
# k-means mode needs scikit-learn, which .venv-coreml does not contain. Grouped channels need spec version 9. `int8` is the default and keeps the HCF396 output unchanged.
METHODS = {
    "int8largest": ("int8-largest-weight-only-v1",
                    "FP16-to-int8-largest-weight-only/per-channel/linear-symmetric"),
    "int8": ("int8-linear-symmetric-per-channel-threshold2048",
             "FP16-to-int8-weight-only/per-channel/linear-symmetric/threshold2048"),
    "palette6": ("palette6-uniform-grouped16-threshold2048",
                 "FP16-to-6-bit-palette-weight-only/per-grouped-channel-16/uniform/threshold2048"),
}


def largest_weight(metadata):
    """Choose by size, then name. Evaluation scores never enter selection."""
    if not metadata:
        raise ValueError("no_compressible_weights")
    return min(metadata, key=lambda name: (-metadata[name].val.size, name))


def compression_config(ct, method, metadata=None):
    if method not in METHODS:
        raise ValueError("unknown_compression_method")
    if method == "int8largest":
        name = largest_weight(metadata or {})
        return ct.optimize.coreml.OptimizationConfig(global_config=None,
            op_name_configs={name: ct.optimize.coreml.OpLinearQuantizerConfig(
                mode="linear_symmetric", dtype="int8", granularity="per_channel", weight_threshold=2048)})
    if method == "palette6":
        return ct.optimize.coreml.OptimizationConfig(global_config=
            ct.optimize.coreml.OpPalettizerConfig(mode="uniform", nbits=6,
                granularity="per_grouped_channel", group_size=16, weight_threshold=2048))
    return ct.optimize.coreml.OptimizationConfig(global_config=
        ct.optimize.coreml.OpLinearQuantizerConfig(mode="linear_symmetric",
            dtype="int8", granularity="per_channel", weight_threshold=2048))

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
    parser.add_argument("--method", choices=sorted(METHODS), default="int8")
    args = parser.parse_args()
    package, destination, original = preflight(args.package, args.source_report,
        args.output_dir, args.experimental_id, args.source_sha256)
    import coremltools as ct
    source = ct.models.MLModel(str(package), skip_model_load=True)
    weights = (ct.optimize.coreml.get_weights_metadata(source, weight_threshold=2048)
               if args.method == "int8largest" else None)
    config = compression_config(ct, args.method, weights)
    metadata = source.user_defined_metadata
    if (metadata.get("checkpointSHA256") != original["checkpointSHA256"] or
        metadata.get("modelID") != "focus-ring-experimental-" + original["experimentalID"] or
        metadata.get("releaseEligible") != "false"):
        raise ValueError("source_metadata_mismatch")
    compress = (ct.optimize.coreml.palettize_weights if args.method == "palette6"
                else ct.optimize.coreml.linear_quantize_weights)
    compressed = compress(source, config=config)
    compressed.user_defined_metadata.update(dict(metadata))
    compressed.user_defined_metadata["modelID"] = "focus-ring-experimental-" + args.experimental_id
    compressed.user_defined_metadata["compression"] = METHODS[args.method][0]
    compressed.user_defined_metadata["sourcePackageSHA256"] = args.source_sha256
    destination.mkdir(parents=True, exist_ok=False)
    output = destination / "FocusRingDetector.mlpackage"
    compressed.save(str(output))
    if artifact_digest(package) != args.source_sha256:
        raise ValueError("source_changed_during_compression")
    result = {**original, **package_size_report(output), "generatedAt": utc_now(),
        "experimentalID": args.experimental_id, "mlpackage": str(output),
        "method": METHODS[args.method][1],
        "coremltoolsVersion": ct.__version__, "sourcePackageSHA256": args.source_sha256,
        "packageSHA256": artifact_digest(output), "releaseEligible": False}
    if weights is not None:
        name = largest_weight(weights)
        result["compressedWeight"] = dict(name=name, elements=int(weights[name].val.size),
                                         selection="largest-element-count-then-name-v1")
    with (destination / "focus_ring_detector_training_report.json").open("x") as stream:
        json.dump(result, stream, indent=2)
    print(json.dumps(result), flush=True)
    return 0 if result["size_gate_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
