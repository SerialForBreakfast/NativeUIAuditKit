#!/usr/bin/env python3
"""
ohem_callback.py — Online Hard Example Mining for Ultralytics YOLO (Phase 6a).

Ultralytics' DataLoader sampler has no `.oversample()` API. This callback:

1. Records a batch-loss proxy for each image (`on_train_batch_end`).
2. At epoch end, selects the top-K (default 20%) highest-loss images.
3. Restores the dataset to its original file list, then overwrites easy slots
   with extra copies of each hard image (factor=2.0) so they appear ~2× next
   epoch without changing dataset length (BP-29).

Compounding is avoided by always resetting to the snapshot taken at
`on_pretrain_routine_end`.

Helpers `select_hard_indices` and `oversample_files` are pure and unit-tested
in `scripts/test_ohem_callback.py` (no GPU required).
"""

from __future__ import annotations

from collections import defaultdict, deque
from copy import deepcopy
import math


def rectangular_keys(ds, count):
    """Validate rectangular slot geometry without importing the training runtime."""
    if not getattr(ds, "rect", False):
        return [None] * count
    batch = list(ds.batch)
    shapes = list(ds.batch_shapes)
    if len(batch) != count or int(ds.batch_size) != ds.batch_size or ds.batch_size <= 0:
        raise ValueError("OHEM invalid rectangular batch metadata")
    keys = []
    for i, index in enumerate(batch):
        if index != i // ds.batch_size or not 0 <= index < len(shapes):
            raise ValueError("OHEM invalid rectangular batch index")
        shape = tuple(shapes[int(index)])
        if len(shape) != 2 or any(not math.isfinite(float(v)) or v <= 0 or int(v) != v for v in shape):
            raise ValueError("OHEM invalid rectangular shape")
        keys.append(shape)
    return keys


def compatible_oversample(files, hard, keys, factor):
    """Replace only equal-output-shape slots; return explicit shortfall counts."""
    result = list(files)
    by_file = dict(zip(files, keys))
    if any(f not in by_file for f in hard):
        raise ValueError("OHEM score references unknown image")
    slots = defaultdict(deque)
    hard_set = set(hard)
    for i, f in enumerate(files):
        if f not in hard_set:
            slots[keys[i]].append(i)
    requested = replaced = 0
    for _ in range(max(0, int(round(factor)) - 1)):
        for f in hard:
            requested += 1
            if slots[by_file[f]]:
                result[slots[by_file[f]].popleft()] = f
                replaced += 1
    return result, {"requested": requested, "replaced": replaced, "unfulfilled": requested - replaced}


def select_hard_indices(losses: dict[str, float], fraction: float = 0.2) -> list[str]:
    """Return the `fraction` of keys with the highest loss, sorted descending."""
    if not losses or fraction <= 0:
        return []
    ranked = sorted(losses.items(), key=lambda kv: kv[1], reverse=True)
    k = max(1, int(len(ranked) * fraction))
    return [path for path, _ in ranked[:k]]


def oversample_files(
    original_files: list[str],
    hard_files: list[str],
    factor: float = 2.0,
) -> list[str]:
    """
    Return a same-length list: extra copies of `hard_files` overwrite easy slots.

    factor=2.0 → each hard file appears twice; an equal number of non-hard
    files are replaced. Length always equals `len(original_files)` so YOLO's
    `ims` / `npy_files` / `ni` / `nb` stay valid (BP-29).
    """
    extra_copies = max(0, int(round(factor)) - 1)
    files = list(original_files)
    if extra_copies == 0 or not hard_files:
        return files
    hard_set = set(hard_files)
    slots = [i for i, f in enumerate(files) if f not in hard_set]
    extras: list[str] = []
    for _ in range(extra_copies):
        extras.extend(hard_files)
    for i, src in zip(slots, extras):
        files[i] = src
    return files


def sync_dataset_lists(ds, files: list[str], labels: list) -> None:
    """Write file/label lists and reset YOLO image-cache arrays to the same length."""
    from pathlib import Path

    n = len(files)
    if len(labels) != n:
        raise ValueError("OHEM file/label length mismatch")
    ds.im_files = list(files)
    ds.labels = list(labels)
    ds.ni = n
    ds.ims = [None] * n
    ds.im_hw0 = [None] * n
    ds.im_hw = [None] * n
    ds.npy_files = [Path(f).with_suffix(".npy") for f in files]
    if hasattr(ds, "buffer"):
        ds.buffer = []


class OHEMCallback:
    """Ultralytics callback bundle. Register with `model.add_callback(...)`."""

    def __init__(self, fraction: float = 0.2, factor: float = 2.0):
        if not math.isfinite(fraction) or not 0 <= fraction <= 1 or not math.isfinite(factor) or factor < 1:
            raise ValueError("OHEM invalid fraction/factor")
        self.fraction = fraction
        self.factor = factor
        self._orig_im_files: list[str] | None = None
        self._orig_labels: list | None = None
        self._epoch_loss: dict[str, list[float]] = defaultdict(list)
        self.last_hard: list[str] = []
        self.last_replacements = {}

    def on_pretrain_routine_end(self, trainer) -> None:
        ds = trainer.train_loader.dataset
        if len(ds.im_files) != len(ds.labels) or len(set(ds.im_files)) != len(ds.im_files):
            raise ValueError("OHEM requires aligned, unique original images")
        self._dataset = ds
        self._keys = rectangular_keys(ds, len(ds.im_files))
        self._orig_im_files = list(ds.im_files)
        self._expected_files = list(ds.im_files)
        self._orig_labels = deepcopy(ds.labels)
        # Ultralytics 8.4 does not assign trainer.batch; stash it from preprocess.
        if not getattr(trainer, "_ohem_preprocess_wrapped", False):
            orig = trainer.preprocess_batch

            def _stash(batch, _orig=orig, _trainer=trainer):
                if _trainer.train_loader.dataset is not self._dataset:
                    raise ValueError("OHEM dataset rebuilt; restart with explicit batch size")
                _trainer.batch = batch
                return _orig(batch)

            trainer.preprocess_batch = _stash
            trainer._ohem_preprocess_wrapped = True

    def on_train_batch_end(self, trainer) -> None:
        loss_t = getattr(trainer, "loss", None)
        if loss_t is None:
            return
        loss = float(loss_t.detach().cpu())
        if not math.isfinite(loss):
            raise ValueError("OHEM nonfinite batch loss")
        batch = getattr(trainer, "batch", None) or {}
        files = batch.get("im_file") or batch.get("im_files") or []
        if isinstance(files, (str, bytes)):
            files = [files]
        if not files:
            return
        per = loss / max(len(files), 1)
        for f in files:
            self._epoch_loss[str(f)].append(per)

    def on_train_epoch_end(self, trainer) -> None:
        if self._orig_im_files is None:
            return
        ds = trainer.train_loader.dataset
        if (ds is not self._dataset or list(ds.im_files) != self._expected_files
                or len(ds.labels) != len(self._orig_im_files)
                or any(lab.get("im_file", f) != f for f, lab in zip(ds.im_files, ds.labels))
                or rectangular_keys(ds, len(self._orig_im_files)) != self._keys):
            raise ValueError("OHEM dataset/batch geometry changed; rebuild callback snapshot")
        reset = getattr(trainer.train_loader, "reset", None)
        if not callable(reset):
            raise ValueError("OHEM requires loader reset after membership change")
        mean_loss = {p: sum(v) / len(v) for p, v in self._epoch_loss.items() if v}
        self.last_hard = select_hard_indices(mean_loss, self.fraction)
        self._epoch_loss.clear()

        label_by_file = {f: lab for f, lab in zip(self._orig_im_files, self._orig_labels)}
        new_files, self.last_replacements = compatible_oversample(
            self._orig_im_files, self.last_hard, self._keys, self.factor)
        new_labels = [deepcopy(label_by_file[f]) for f in new_files]
        sync_dataset_lists(ds, new_files, new_labels)
        self._expected_files = list(new_files)
        reset()
        trainer.ohem_replacements = dict(self.last_replacements)
        replaced = sum(1 for a, b in zip(self._orig_im_files, new_files) if a != b)
        print(
            f"OHEM: oversampled {len(self.last_hard)} hard images "
            f"(fraction={self.fraction}, factor={self.factor}); "
            f"replaced {replaced}/{len(self._orig_im_files)} easy slots "
            f"(len stays {len(new_files)}; unfulfilled={self.last_replacements['unfulfilled']})"
        )

    # Ultralytics 8.4 also emits on_batch_end.
    on_batch_end = on_train_batch_end


# Aliases for the names train_ios_model.py / tests use.
select_hard_indices = select_hard_indices
OHEMCallback = OHEMCallback
OHEMCallback.on_pretrain_routine_end = OHEMCallback.on_pretrain_routine_end
OHEMCallback.on_train_epoch_end = OHEMCallback.on_train_epoch_end
