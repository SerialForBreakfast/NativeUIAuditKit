#!/usr/bin/env python3
"""Unit tests for OHEM helpers — no GPU, no Ultralytics required."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from ohem_callback import (
    OHEMCallback,
    oversample_files,
    select_hard_indices,
    sync_dataset_lists,
)


class SelectHardIndicesTests(unittest.TestCase):
    def test_top_fraction_is_highest_loss(self):
        losses = {f"img_{i}": float(i) for i in range(10)}
        hard = select_hard_indices(losses, fraction=0.2)
        self.assertEqual(hard, ["img_9", "img_8"])

    def test_empty_losses(self):
        self.assertEqual(select_hard_indices({}, 0.2), [])

    def test_at_least_one(self):
        hard = select_hard_indices({"a": 1.0}, fraction=0.2)
        self.assertEqual(hard, ["a"])


class OversampleFilesTests(unittest.TestCase):
    def test_factor_two_replaces_easy_slots_same_length(self):
        original = ["a", "b", "c", "d"]
        hard = ["b", "d"]
        out = oversample_files(original, hard, factor=2.0)
        self.assertEqual(len(out), len(original))
        self.assertEqual(out.count("b"), 2)
        self.assertEqual(out.count("d"), 2)
        self.assertEqual(out.count("a") + out.count("c"), 0)

    def test_does_not_mutate_original(self):
        original = ["a", "b"]
        snapshot = list(original)
        oversample_files(original, ["a"], factor=2.0)
        self.assertEqual(original, snapshot)

    def test_reset_then_oversample_does_not_compound(self):
        original = ["a", "b", "c", "d", "e"]
        epoch1 = oversample_files(original, ["a"], factor=2.0)
        epoch2 = oversample_files(original, ["c"], factor=2.0)
        self.assertEqual(epoch1.count("a"), 2)
        self.assertEqual(epoch1.count("c"), 1)
        self.assertEqual(epoch2.count("c"), 2)
        self.assertLessEqual(epoch2.count("a"), 1)
        self.assertEqual(len(epoch1), len(original))
        self.assertEqual(len(epoch2), len(original))


class SyncDatasetListsTests(unittest.TestCase):
    def test_resizes_image_cache_to_file_list(self):
        class DS:
            pass

        ds = DS()
        files = ["a.jpg", "b.jpg"]
        labels = [{"i": 0}, {"i": 1}]
        sync_dataset_lists(ds, files, labels)
        self.assertEqual(ds.ni, 2)
        self.assertEqual(len(ds.ims), 2)
        self.assertEqual(len(ds.npy_files), 2)
        self.assertEqual(ds.im_files, files)


class OHEMCallbackDatasetTests(unittest.TestCase):
    def test_epoch_end_keeps_len_and_ims_in_sync(self):
        class DS:
            def __init__(self):
                self.im_files = [f"img_{i}.jpg" for i in range(10)]
                self.labels = [{"i": i} for i in range(10)]
                self.ni = 10
                self.ims = [None] * 10
                self.im_hw0 = [None] * 10
                self.im_hw = [None] * 10
                self.npy_files = [Path(f).with_suffix(".npy") for f in self.im_files]

        class Loader:
            def __init__(self, ds):
                self.dataset = ds
                self.reset_calls = 0

            def reset(self):
                """Match Ultralytics InfiniteDataLoader.reset()."""
                self.reset_calls += 1

        class Trainer:
            def __init__(self, ds):
                self.train_loader = Loader(ds)
                self.preprocess_batch = lambda b: b

        ds = DS()
        trainer = Trainer(ds)
        cb = OHEMCallback(fraction=0.2, factor=2.0)
        cb.on_pretrain_routine_end(trainer)
        for i, f in enumerate(ds.im_files):
            cb._epoch_loss[f].append(float(i))
        cb.on_train_epoch_end(trainer)
        self.assertEqual(len(ds.im_files), 10)
        self.assertEqual(len(ds.ims), 10)
        self.assertEqual(ds.ni, 10)
        self.assertEqual(ds.im_files.count("img_9.jpg"), 2)
        self.assertEqual(trainer.train_loader.reset_calls, 1)


if __name__ == "__main__":
    unittest.main()
