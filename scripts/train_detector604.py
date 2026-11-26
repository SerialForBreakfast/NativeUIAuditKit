"""RESET604 T3.1 / T3.2 / T4.1: Train 12-role (or 12-role + focused) YOLO11 detector from pretrained weights.

Follows RESET604 rules:
- Initializes from pretrained COCO weights (`yolo11n.pt` or `yolo11s.pt`), never shipped synthetic weights.
- Uses 100 epochs and default Ultralytics learning-rate schedule (`lr0=0.01`, `lrf=0.01`, `optimizer='auto'`),
  with UI-coordinate-safe geometry (`fliplr=0`, `flipud=0`, `degrees=0`, `mosaic=0`, `amp=False`).
- Reuses `detector_training419.prepare` for strict pixel/group/label validation and `research_execution_policy.TRAINING_SECONDS` (43,200 s).
- Exports shipping Core ML `.mlpackage` (NMS enabled, FP16) for immediate `tvbench.py eval` scoring.
"""
import argparse
import contextlib
import json
import os
import signal
import subprocess
import threading
import time
from pathlib import Path
import yaml

import detector_training419 as t
import research_execution_policy as policy
import research_queue as q

OUT = None
PRETRAINED_ALLOWED = {'yolo11n.pt', 'yolo11s.pt', 'yolo11m.pt', 'yolo11l.pt', 'yolo11x.pt'}
DEFAULT_OUT = q.ROOT / 'reports/work/RESET604/runs'


def validate_config(weights, epochs, imgsz, seed, allow_non_pretrained=False):
    wpath = Path(weights)
    if not allow_non_pretrained:
        q.require(wpath.name in PRETRAINED_ALLOWED, f'train604_must_start_from_pretrained:{wpath.name}')
    q.require(wpath.is_file(), f'train604_weights_missing:{wpath}')
    q.require(isinstance(epochs, int) and 1 <= epochs <= 300, f'train604_invalid_epochs:{epochs}')
    q.require(imgsz in (640, 960), f'train604_invalid_imgsz:{imgsz}')
    q.require(isinstance(seed, int) and seed > 0, f'train604_invalid_seed:{seed}')


@contextlib.contextmanager
def _training_watchdog(max_seconds):
    """Enforce a hard wall-clock timeout via SIGALRM/ITIMER_REAL on Unix main threads."""
    use_alarm = (
        hasattr(signal, 'SIGALRM')
        and hasattr(signal, 'setitimer')
        and threading.current_thread() is threading.main_thread()
        and max_seconds is not None
        and max_seconds > 0
    )
    if not use_alarm:
        yield
        return

    def _on_timeout(signum, frame):
        raise TimeoutError(f'train604_timeout:{max_seconds}s')

    prev_handler = signal.getsignal(signal.SIGALRM)
    signal.signal(signal.SIGALRM, _on_timeout)
    signal.setitimer(signal.ITIMER_REAL, float(max_seconds))
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0.0)
        signal.signal(signal.SIGALRM, prev_handler)


# TRAIN666 H2 arm B: Ultralytics HSV, scale and translate defaults are already on; `mosaic` adds mosaic and shuffled
# square batches (`rect=True` disables both). Flips and rotation stay off: UI geometry has a fixed orientation.
AUGMENTATION = {
    'none': dict(rect=True, mosaic=0),
    'mosaic': dict(rect=False, mosaic=1.0, close_mosaic=10),
}


def run_training(membership_path, out_dir, weights=q.ROOT / 'yolo11n.pt', epochs=100, imgsz=640,
                 seed=371, lr0=0.01, batch=8, patience=0, allow_non_pretrained=False, export_coreml=False,
                 max_seconds=policy.TRAINING_SECONDS, augmentation='none'):
    """Prepare validated YOLO dataset and execute training run with receipt + policy guard."""
    weights = Path(weights).resolve()
    membership_path = Path(membership_path).resolve()
    validate_config(weights, epochs, imgsz, seed, allow_non_pretrained=allow_non_pretrained)
    q.require(augmentation in AUGMENTATION, f'train604_invalid_augmentation:{augmentation}')
    q.require(max_seconds is not None and float(max_seconds) > 0, f'train604_invalid_max_seconds:{max_seconds}')
    out_dir = Path(out_dir).resolve()
    q.require(not (out_dir / 'detector').exists(), f'train604_output_exists:{out_dir}')
    q.require(not (out_dir / 'train-receipt.json').exists(), f'train604_receipt_exists:{out_dir}')
    out_dir.mkdir(parents=True, exist_ok=True)

    os.environ['YOLO_CONFIG_DIR'] = str(q.ROOT / 'NativeUITrainer/.ultralytics')
    os.environ['MPLCONFIGDIR'] = str(q.ROOT / 'NativeUITrainer/.mplconfig')
    os.environ['TORCH_HOME'] = str(q.ROOT / 'NativeUITrainer/.torch')
    os.environ['YOLO_OFFLINE'] = 'true'

    membership = q.load(membership_path)
    dataset_yaml, counts = t.prepare(membership, out_dir)

    from ultralytics import YOLO
    model = YOLO(str(weights))
    t0 = time.monotonic()
    with _training_watchdog(float(max_seconds)):
        model.train(
            data=str(dataset_yaml),
            epochs=epochs,
            patience=patience,
            batch=batch,
            imgsz=imgsz,
            device='mps',
            workers=0,
            project=str(out_dir),
            name='detector',
            exist_ok=False,
            seed=seed,
            deterministic=True,
            optimizer='auto',
            lr0=lr0,
            lrf=0.01,
            pretrained=True,
            plots=False,
            save=True,
            cache=False,
            amp=False,
            mixup=0,
            copy_paste=0,
            fliplr=0,
            flipud=0,
            degrees=0,
            **AUGMENTATION[augmentation],
        )
    wall_seconds = round(time.monotonic() - t0, 3)

    args_yaml = out_dir / 'detector/args.yaml'
    resolved_args = None
    if args_yaml.is_file():
        loaded_args = yaml.safe_load(args_yaml.read_text()) or {}
        resolved_args = {
            k: loaded_args.get(k)
            for k in ('epochs', 'imgsz', 'seed', 'optimizer', 'lr0', 'lrf', 'amp', 'batch', 'rect', 'deterministic', 'mosaic', 'close_mosaic')
            if k in loaded_args
        }

    best_pt = out_dir / 'detector/weights/best.pt'
    last_pt = out_dir / 'detector/weights/last.pt'
    receipt = dict(
        version='reset604-train-v2',
        membership=dict(path=str(membership_path), sha256=q.digest(membership_path)),
        counts=counts,
        classes=membership['names'],
        initWeights=dict(path=str(weights), sha256=q.digest(weights)),
        epochs=epochs,
        imgsz=imgsz,
        seed=seed,
        lr0=lr0,
        augmentation=augmentation,
        policyMaxSeconds=policy.TRAINING_SECONDS,
        enforcedMaxSeconds=float(max_seconds),
        wallSeconds=wall_seconds,
        resolvedTrainArgs=resolved_args,
        bestPt=dict(path=str(best_pt), sha256=q.digest(best_pt)) if best_pt.is_file() else None,
        lastPt=dict(path=str(last_pt), sha256=q.digest(last_pt)) if last_pt.is_file() else None,
    )

    if export_coreml and best_pt.is_file():
        coreml_py = q.ROOT / '.venv-coreml/bin/python'
        q.require(coreml_py.is_file(), 'train604_coreml_venv_missing')
        cmd = [
            str(coreml_py), str(q.ROOT / 'scripts/export_yolo_coreml.py'),
            '--weights', str(best_pt), '--imgsz', str(imgsz), '--output', str(out_dir / 'coreml'),
        ]
        subprocess.run(cmd, check=True)
        exported_pkgs = list((out_dir / 'coreml').glob('*.mlpackage'))
        receipt['coremlPackage'] = str(exported_pkgs[0]) if exported_pkgs else None

    q.save(out_dir / 'train-receipt.json', receipt, replace=False)
    return receipt


def queue_run():
    """Detached queue adapter for T107 (43,200 s policy, fixed-epoch RESET604 detector fits)."""
    import csv
    import shutil
    from template_adapters395 import document, resolve_inputs

    q.require(OUT is not None, 'train604_queue_out_unset')
    spec = q.load(OUT.parents[2] / 'spec.json')
    refs = resolve_inputs(spec['template'], OUT)
    config = document(refs['configuration'])
    q.require(config.get('initialization') == refs['initialization'], 'train604_config_init_mismatch')

    epochs = int(config.get('epochs', 100))
    imgsz = int(config.get('imgsz', 640))
    seed = int(config.get('seed', 371))
    lr0 = float(config.get('lr0', 0.01))
    batch = int(config.get('batch', 8))
    patience = int(config.get('patience', 0))
    export_coreml = bool(config.get('exportCoreML', False))
    augmentation = config.get('augmentation', 'none')
    # `best`: Ultralytics best.pt, chosen by calibration-split fitness (TRAIN666 W4). `last`: the D1 fixed-last rule.
    selection = config.get('selection', 'last')
    q.require(selection in ('last', 'best'), f'train604_invalid_selection:{selection}')

    init_path = q.ROOT / refs['initialization']['path']
    mem_path = q.ROOT / refs['membership']['path']
    receipt = run_training(
        mem_path,
        OUT,
        weights=init_path,
        epochs=epochs,
        imgsz=imgsz,
        seed=seed,
        lr0=lr0,
        batch=batch,
        patience=patience,
        export_coreml=export_coreml,
        max_seconds=policy.TRAINING_SECONDS,
        augmentation=augmentation,
    )
    results_csv = OUT / 'detector/results.csv'
    history = []
    if results_csv.is_file():
        with results_csv.open() as stream:
            rows = [{k.strip(): v for k, v in row.items()} for row in csv.DictReader(stream)]
        history = [
            dict(epoch=int(r['epoch']), trainLoss=sum(float(r[k]) for k in ('train/box_loss', 'train/cls_loss', 'train/dfl_loss')))
            for r in rows
        ]
    ckpt = OUT / f'detector/weights/{selection}.pt'
    if selection == 'last' and not ckpt.is_file():
        ckpt = OUT / 'detector/weights/best.pt'
    q.require(ckpt.is_file(), 'train604_checkpoint_missing')
    shutil.copyfile(ckpt, OUT / 'final.pt')
    q.save(OUT / 'history.json', history, replace=True)
    q.save(OUT / 'fit.json', dict(
        version='reset604-fit-v1',
        epochs=epochs,
        imgsz=imgsz,
        seed=seed,
        lr0=lr0,
        augmentation=augmentation,
        selection=selection,
        initialization=refs['initialization'],
        membership=refs['membership'],
        counts=receipt['counts'],
        modelAccepted=False,
        metricsStatus='provisional',
        receipt='train-receipt.json',
    ), replace=True)
    q.save(OUT / 'benchmark_summary.json', dict(
        version='reset604-fit-v1',
        epochs=epochs,
        frames=receipt['counts'],
        modelAccepted=False,
        decision='Score the exported Core ML package on TVBench development. Training completion is not acceptance.',
    ), replace=True)
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--membership', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--weights', type=Path, default=q.ROOT / 'yolo11n.pt')
    parser.add_argument('--epochs', type=int, default=100)
    parser.add_argument('--imgsz', type=int, default=640, choices=(640, 960))
    parser.add_argument('--seed', type=int, default=371)
    parser.add_argument('--lr0', type=float, default=0.01)
    parser.add_argument('--batch', type=int, default=8)
    parser.add_argument('--patience', type=int, default=0)
    parser.add_argument('--export-coreml', action='store_true')
    args = parser.parse_args()
    print(json.dumps(run_training(
        args.membership, args.out, weights=args.weights, epochs=args.epochs, imgsz=args.imgsz,
        seed=args.seed, lr0=args.lr0, batch=args.batch, patience=args.patience, export_coreml=args.export_coreml,
    ), indent=2))


if __name__ == '__main__':
    main()
