#!/usr/bin/env python3
"""
ohem_callback.py — Online Hard Example Mining for Ultralytics YOLO (Phase 6a).

Ultralytics' DataLoader sampler has no `.oversample()` API. This callback:

1. Records per-image training loss during the epoch (`on_train_batch_end`).
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

from collections import defaultdict


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
    ds.im_files = list(files)
    ds.labels = list(labels)
    ds.ni = n
    ds.ims = [None] * n
    ds.im_hw0 = [None] * n
    ds.im_hw = [None] * n
    ds.npy_files = [Path(f).with_suffix(".npy") for f in files]


class OHEMCallback:
    """Ultralytics callback bundle. Register with `model.add_callback(...)`."""

    def __init__(self, fraction: float = 0.2, factor: float = 2.0):
        self.fraction = fraction
        self.factor = factor
        self._orig_im_files: list[str] | None = None
        self._orig_labels: list | None = None
        self._epoch_loss: dict[str, list[float]] = defaultdict(list)
        self.last_hard: list[str] = []

    def on_pretrain_routine_end(self, trainer) -> None:
        ds = trainer.train_loader.dataset
        self._orig_im_files = list(ds.im_files)
        self._orig_labels = list(ds.labels)
        # Ultralytics 8.4 does not assign trainer.batch; stash it from preprocess.
        if not getattr(trainer, "_ohem_preprocess_wrapped", False):
            orig = trainer.preprocess_batch

            def _stash(batch, _orig=orig, _trainer=trainer):
                _trainer.batch = batch
                return _orig(batch)

            trainer.preprocess_batch = _stash
            trainer._ohem_preprocess_wrapped = True

    def on_train_batch_end(self, trainer) -> None:
        loss_t = getattr(trainer, "loss", None)
        loss = float(loss_t.detach().cpu()) if loss_t is not None else 0.0
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
        mean_loss = {p: sum(v) / len(v) for p, v in self._epoch_loss.items() if v}
        self.last_hard = select_hard_indices(mean_loss, self.fraction)
        self._epoch_loss.clear()

        ds = trainer.train_loader.dataset
        label_by_file = {f: lab for f, lab in zip(self._orig_im_files, self._orig_labels)}
        new_files = oversample_files(self._orig_im_files, self.last_hard, self.factor)
        if any(f not in label_by_file for f in new_files):
            return
        new_labels = [label_by_file[f] for f in new_files]
        sync_dataset_lists(ds, new_files, new_labels)
        loader = trainer.train_loader
        reset = getattr(loader, "reset", None)
        if callable(reset):
            reset()
        replaced = sum(1 for a, b in zip(self._orig_im_files, new_files) if a != b)
        print(
            f"OHEM: oversampled {len(self.last_hard)} hard images "
            f"(fraction={self.fraction}, factor={self.factor}); "
            f"replaced {replaced}/{len(self._orig_im_files)} easy slots "
            f"(len stays {len(new_files)})"
        )

    # Ultralytics 8.4 also emits on_batch_end.
    on_batch_end = on_train_batch_end


# Aliases for the names train_ios_model.py / tests use.
select_hard_indices = select_hard_indices
OHEMCallback = OHEMCallback
OHEMCallback.on_pretrain_routine_end = OHEMCallback.on_pretrain_routine_end
OHEMCallback.on_train_epoch_end = OHEMCallback.on_train_epoch_end

