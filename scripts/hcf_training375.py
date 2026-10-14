"""HCF375: train on HCF and Standard examples through resident training code (ASD-STE100).

Corrections against the first HCF375 registration (PROGRAM384 R2, queue trust repair 2026-10-13):
- The detector links each image into its own role folder. The first version used a leftover loop variable,
  so every image went to `images/development` and the training split was empty.
- The detector validates on the calibration role. Development frames stay out of checkpoint selection,
  because the later comparison scores them.
- The crop model uses fixed-last selection, because no calibration crops exist. It trains on unique
  (pixel hash, label) crops: HCF374 finds 615 unique training crops among 8,000 rows.
- Existing output folders are refused, never removed.
"""
import os
import csv
from pathlib import Path
import research_queue as q
import hcf_study371 as study

OUT = None


def crop():
    """Train the MobileNetV4 crop classifier on unique HCF and Standard training crops."""
    study.OUT = OUT
    cfg = q.load(OUT / "config.json")
    document, = study.dependency("crops.json")
    rows = document["rows"]
    q.require({r["role"] for r in rows} == {"train", "development"}, "training_roles")
    groups = {}
    for row in rows:
        q.require(groups.setdefault(row["group"], row["role"]) == row["role"], "training_group_leak")
        q.require(q.digest(Path(row["path"])) == row["sha256"], "training_crop_changed")
    reference = cfg["initialization"]
    path = q.ROOT / reference["path"]
    q.require(q.digest(path) == reference["sha256"], "training_initialization_changed")
    from train_focus_ring_detector import train_native_hcf
    result = train_native_hcf(rows, path, OUT, progress=study.progress, profile="balanced",
                              selection="fixed-last", deduplicate=True)
    q.save(OUT / "fit.json", dict(
        **result,
        modelAccepted=False,
        profile="balanced",
        membershipSHA256=q.text_digest(rows),
        initialization=reference,
    ))
    q.save(OUT / "model.json", dict(path=str(OUT / "final.pt"), sha256=q.digest(OUT / "final.pt"), kind="crop"))


def detector():
    """Train YOLO11n on HCF and Standard training frames. Validate on the calibration role."""
    study.OUT = OUT
    cfg = q.load(OUT / "config.json")
    document, = study.dependency("admission.json")
    patience = cfg.get('patience', 10)
    q.require(type(patience) is int and patience in (0, 10), 'detector_patience_invalid')
    q.require(document.get('trainingAdmitted') is True, 'detector_training_not_admitted')
    study.validate_groups(document['cases'])
    root = study.verify_storage(document["storage"])
    dataset = root / cfg["datasetFolder"]
    q.require(not dataset.exists(), "detector_dataset_exists")
    rows = [r for r in document["rows"] if r["role"] in ("train", "calibration")]
    q.require({(r["role"], r["profile"]) for r in rows} ==
              {("train", "hcf"), ("train", "standard"), ("calibration", "hcf"), ("calibration", "standard")},
              "detector_training_roles")
    for role in ("train", "calibration"):
        (dataset / "images" / role).mkdir(parents=True)
        (dataset / "labels" / role).mkdir(parents=True)
    for row in rows:
        source = Path(row["path"])
        q.require(q.digest(source) == row["sha256"], "detector_image_changed")
        os.link(source, dataset / "images" / row["role"] / (row["id"] + ".png"))
        x, y, w, h = row["boxes"][row["focus"]]
        width, height = row["width"], row["height"]
        label = f"0 {(x + w / 2) / width:.9f} {(y + h / 2) / height:.9f} {w / width:.9f} {h / height:.9f}\n"
        with (dataset / "labels" / row["role"] / (row["id"] + ".txt")).open("x") as stream:
            stream.write(label)
    counts = {role: sum(1 for r in rows if r["role"] == role) for role in ("train", "calibration")}
    import yaml
    with (dataset / "dataset.yaml").open("x") as stream:
        yaml.safe_dump(dict(path=str(dataset), train="images/train", val="images/calibration",
                            names={0: "focused_control"}), stream)
    ref = cfg["initialization"]
    initialization = q.ROOT / ref["path"]
    q.require(q.digest(initialization) == ref["sha256"], "detector_initialization_changed")
    from train_yolo import train_native_hcf
    options = {'patience': patience} if 'patience' in cfg else {}
    best = train_native_hcf(dataset / "dataset.yaml", initialization, OUT, study.progress, weights="best", **options)
    with (OUT / 'detector/results.csv').open() as stream:
        raw_history = [{key.strip(): value for key, value in row.items()} for row in csv.DictReader(stream)]
    history = [dict(epoch=int(row['epoch']), trainLoss=sum(float(row[key]) for key in
                    ('train/box_loss', 'train/cls_loss', 'train/dfl_loss'))) for row in raw_history]
    q.require(history, 'detector_history_missing')
    q.save(OUT / 'history.json', history)
    q.require(best.is_file(), "detector_checkpoint_missing")
    q.save(OUT / "model.json", dict(path=str(best), sha256=q.digest(best), kind="detector"))
    q.save(OUT / "fit.json", dict(
        modelAccepted=False,
        profile="balanced",
        frames=counts,
        epochs=len(history),
        epochsMaximum=30,
        patience=patience,
        membershipSHA256=q.text_digest(rows),
        initialization=ref,
        selection="best-calibration-fitness",
        resumeStateSaved=True,
        resumeQualified=False,
    ))


def decision():
    """Keep the existing decision and cite the exact comparison reports."""
    import hcf_compare371
    hcf_compare371.OUT = OUT
    hcf_compare371.decision()
    q.save(OUT / 'sources.json', [item for dep in q.load(OUT / 'dependencies.json') for item in dep['outputs']])
