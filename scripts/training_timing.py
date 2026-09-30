"""Optional host-wall timing; no model imports, device sync or kernel-time claims."""
from collections import defaultdict
from functools import wraps
import json
import warnings
from pathlib import Path
from time import perf_counter
from uuid import uuid4


class TrainingTiming:
    def __init__(self, root, clock=perf_counter):
        self.root = Path(root).resolve()
        self.clock = clock
        self.stats = defaultdict(lambda: {"calls": 0, "seconds": 0.0, "errors": 0})
        self.path = None
        self.epoch_start = self.batch_start = self.previous_end = None

    def measured(self, name, function):
        @wraps(function)
        def wrapped(*args, **kwargs):
            start = self.clock()
            failed = False
            try:
                return function(*args, **kwargs)
            except BaseException:
                failed = True
                raise
            finally:
                self.add(name, self.clock() - start, failed)
        return wrapped

    def add(self, name, seconds, failed=False):
        item = self.stats[name]
        item["calls"] += 1
        item["seconds"] += seconds
        item["errors"] += int(failed)

    def setup(self, trainer):
        directory = Path(trainer.save_dir).resolve()
        if not directory.is_relative_to(self.root):
            raise ValueError("Timing output must stay inside project")
        self.path = directory / f"host-timing-{uuid4().hex}.jsonl"
        with self.path.open("x") as stream:
            stream.write(json.dumps({"schema_version": 1, "kind": "metadata",
                "clock": "perf_counter", "device_sync": False,
                "semantics": "host wall time; nested intervals not additive; gaps are not pure loader time",
                "device": str(trainer.device), "workers": trainer.args.workers,
                "batch_size": trainer.batch_size, "rect": trainer.train_loader.dataset.rect,
                "amp": bool(getattr(trainer, "amp", False)),
                "accumulate_at_setup": getattr(trainer, "accumulate", None)}) + "\n")
        for name in ("preprocess_batch", "optimizer_step", "validate", "save_model"):
            setattr(trainer, name, self.measured(name, getattr(trainer, name)))

    def epoch_begin(self, trainer):
        self.epoch_start = self.clock()
        self.previous_end = self.epoch_start

    def batch_begin(self, trainer):
        now = self.clock()
        if self.previous_end is not None:
            self.add("inter_batch_gap", now - self.previous_end)
        self.batch_start = now

    def batch_end(self, trainer):
        now = self.clock()
        if self.batch_start is not None:
            self.add("batch_interval", now - self.batch_start)
        self.batch_start = None
        self.previous_end = now

    def emit(self, kind, trainer, outcome=None):
        if self.path is None:
            return
        with self.path.open("a") as stream:
            stream.write(json.dumps({"schema_version": 1, "kind": kind,
                "epoch": getattr(trainer, "epoch", None), "intervals": dict(self.stats),
                "outcome": outcome,
                "ohem_replacements": getattr(trainer, "ohem_replacements", None),
                "accumulate_at_record": getattr(trainer, "accumulate", None)}) + "\n")
        self.stats.clear()

    def epoch_end(self, trainer):
        if self.epoch_start is None:  # final_eval also emits on_fit_epoch_end
            return
        self.add("epoch_total", self.clock() - self.epoch_start)
        self.emit("epoch", trainer)
        self.epoch_start = None

    def terminal(self, trainer, outcome="unknown"):
        try:
            if self.epoch_start is not None:
                self.add("unfinished_epoch_elapsed", self.clock() - self.epoch_start)
            self.emit("terminal", trainer, outcome)
        except OSError as error:
            warnings.warn(f"Could not preserve terminal timing: {error}", RuntimeWarning)

    def register(self, model):
        for event, method in {
            "on_pretrain_routine_end": self.setup,
            "on_train_epoch_start": self.epoch_begin,
            "on_train_batch_start": self.batch_begin,
            "on_train_batch_end": self.batch_end,
            "on_fit_epoch_end": self.epoch_end,
        }.items():
            model.add_callback(event, method)
