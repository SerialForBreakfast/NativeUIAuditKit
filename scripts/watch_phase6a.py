#!/usr/bin/env python3
"""
watch_phase6a.py — Keep Run 007 training until Ultralytics exits successfully.

After a power cut, last.pt is only valid at epoch boundaries (BP-30). This
loop resumes from last.pt (or last.prev.pt) whenever train_ios_model.py is
not running, and exits 0 when training has actually finished (100 epochs,
early-stop, or the TRAINING_COMPLETE marker).

Usage (from package root, machine-awake):
  caffeinate -dims .venv-yolo/bin/python -u scripts/watch_phase6a.py
"""

from __future__ import annotations

import csv
import fcntl
import os
import subprocess
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RUN_DIR = PROJECT_ROOT / "NativeUITrainer" / "yolo_runs" / "phase6a_r007"
WEIGHTS = RUN_DIR / "weights"
RESULTS = RUN_DIR / "results.csv"
DONE = RUN_DIR / "TRAINING_COMPLETE"
LOG = PROJECT_ROOT / "NativeUITrainer" / "training_6a.log"
WATCH_LOG = PROJECT_ROOT / "NativeUITrainer" / "watch_phase6a.log"
PYTHON = PROJECT_ROOT / ".venv-yolo" / "bin" / "python"
TRAIN = PROJECT_ROOT / "scripts" / "train_ios_model.py"
PIDFILE = PROJECT_ROOT / "NativeUITrainer" / "phase6a_r007.pid"
LOCKFILE = PROJECT_ROOT / "NativeUITrainer" / "watch_phase6a.lock"
EPOCHS_TARGET = 100
RETRY_SEC = 30
POLL_SEC = 60


def log(msg: str) -> None:
    line = time.strftime("%Y-%m-%d %H:%M:%S") + " " + msg
    print(line, flush=True)


def csv_epochs() -> int:
    if not RESULTS.exists():
        return 0
    with RESULTS.open() as fh:
        rows = list(csv.DictReader(fh))
    if not rows:
        return 0
    return int(float(rows[-1]["epoch"]))


def log_says_complete() -> bool:
    if not LOG.exists():
        return False
    tail = LOG.read_text(errors="replace")[-80_000:]
    return "Training complete. best.pt" in tail


def is_complete() -> bool:
    if DONE.exists():
        return True
    n = csv_epochs()
    if n >= EPOCHS_TARGET:
        return True
    if log_says_complete() and n >= 2 and not train_pids():
        return True
    return False


def mark_done() -> None:
    DONE.write_text(
        f"completed {time.strftime('%Y-%m-%d %H:%M:%S')} csv_epochs={csv_epochs()}\n"
    )
    log(f"TRAINING_COMPLETE written (csv epochs={csv_epochs()})")


def train_pids() -> list[int]:
    try:
        out = subprocess.check_output(["pgrep", "-f", "scripts/train_ios_model.py"], text=True)
    except subprocess.CalledProcessError:
        return []
    pids = []
    for line in out.split():
        try:
            pids.append(int(line))
        except ValueError:
            continue
    # Exclude this watcher if the pattern ever matches us (it should not).
    me = os.getpid()
    return [p for p in pids if p != me]


def ckpt_loadable(path: Path) -> bool:
    if not path.exists() or path.stat().st_size < 1_000_000:
        return False
    env = os.environ.copy()
    env["YOLO_CONFIG_DIR"] = str(PROJECT_ROOT / "NativeUITrainer" / ".ultralytics")
    env["TMPDIR"] = str(PROJECT_ROOT / "NativeUITrainer" / ".tmp")
    code = (
        "import torch,sys; "
        "c=torch.load(sys.argv[1], map_location='cpu', weights_only=False); "
        "print(c.get('epoch','?')); "
    )
    try:
        subprocess.check_output(
            [str(PYTHON), "-c", code, str(path)],
            env=env,
            cwd=str(PROJECT_ROOT),
            stderr=subprocess.STDOUT,
            timeout=120,
        )
        return True
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return False


def pick_ckpt() -> Path | None:
    for name in ("last.pt", "last.prev.pt", "best.pt"):
        p = WEIGHTS / name
        if ckpt_loadable(p):
            return p
    return None


def start_train(ckpt: Path) -> subprocess.Popen:
    env = os.environ.copy()
    tmp = PROJECT_ROOT / "NativeUITrainer" / ".tmp"
    tmp.mkdir(parents=True, exist_ok=True)
    env["TMPDIR"] = str(tmp)
    env["TMP"] = str(tmp)
    env["YOLO_CONFIG_DIR"] = str(PROJECT_ROOT / "NativeUITrainer" / ".ultralytics")
    env["PYTHONUNBUFFERED"] = "1"
    env["PYTHONFAULTHANDLER"] = "1"
    with LOG.open("a") as fh:
        fh.write(
            f"\n\n===== WATCH RESUME {time.strftime('%Y-%m-%d %H:%M:%S')} "
            f"ckpt={ckpt} csv_epochs={csv_epochs()} =====\n"
        )
        fh.flush()
        proc = subprocess.Popen(
            [
                str(PYTHON),
                "-u",
                str(TRAIN),
                "--name",
                "phase6a_r007",
                "--batch",
                "4",
                "--resume",
                str(ckpt),
            ],
            stdout=fh,
            stderr=subprocess.STDOUT,
            stdin=subprocess.DEVNULL,
            cwd=str(PROJECT_ROOT),
            env=env,
        )
    PIDFILE.write_text(str(proc.pid) + "\n")
    log(f"started train_ios_model pid={proc.pid} resume={ckpt}")
    return proc


def main() -> int:
    os.chdir(PROJECT_ROOT)
    (PROJECT_ROOT / "NativeUITrainer" / ".tmp").mkdir(parents=True, exist_ok=True)
    lock_fh = LOCKFILE.open("a+")
    try:
        fcntl.flock(lock_fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        log("another watch_phase6a.py already holds the lock; exiting")
        return 0
    log(f"watch_phase6a start csv_epochs={csv_epochs()} done={DONE.exists()}")
    if is_complete():
        mark_done()
        return 0

    running = train_pids()
    if running:
        log(f"trainer already running pids={running}; waiting")
        while train_pids():
            if is_complete():
                mark_done()
                return 0
            time.sleep(POLL_SEC)
        log("existing trainer exited; checking completion")
        if is_complete():
            mark_done()
            return 0

    while True:
        if is_complete():
            mark_done()
            return 0
        live = train_pids()
        if live:
            log(f"trainer already running pids={live}; waiting instead of launching another")
            time.sleep(POLL_SEC)
            continue
        ckpt = pick_ckpt()
        if ckpt is None:
            log("ERROR: no loadable last.pt / last.prev.pt / best.pt")
            return 1
        proc = start_train(ckpt)
        rc = proc.wait()
        log(f"train_ios_model pid={proc.pid} exited rc={rc} csv_epochs={csv_epochs()}")
        if rc == 0 and is_complete():
            mark_done()
            return 0
        if rc == 0:
            # Ultralytics can exit 0 after early-stop; treat as done if csv grew
            # and the process is gone.
            if csv_epochs() >= 2 and log_says_complete():
                mark_done()
                return 0
            log("exit 0 but not marked complete; retrying")
        else:
            log(f"non-zero exit; retry in {RETRY_SEC}s")
        time.sleep(RETRY_SEC)


if __name__ == "__main__":
    sys.exit(main())
