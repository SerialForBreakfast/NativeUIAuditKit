"""Explicit appearance-assembly runtime replay; never changes reported runtime identity.

Source-specific validators still replay crops and validate raw labels. This scope
only admits the declared previous runtime after a complete, input-bound pixel proof.
"""
from contextlib import contextmanager
from contextvars import ContextVar
import json

from focus_dataset_contract import FocusDataError, digest
from focus_runtime import identity

_scope = ContextVar("appearance_runtime_replay", default=None)


def require(ok, reason):
    if not ok: raise FocusDataError(reason)


def matches(recorded, actual=None):
    actual = identity() if actual is None else actual
    if recorded == actual: return True
    scope = _scope.get()
    return bool(scope and scope["runtime"] == actual and recorded in scope["oldRuntimes"])


@contextmanager
def replay_scope(spec):
    require(isinstance(spec, dict), "unsupported_appearance_input")
    ref = spec.get("runtimeReplay")
    if ref is None:
        yield None
        return
    from focus_mixed_assembly import checked
    proof = json.loads(checked(ref).read_text())
    require(proof.get("version") == "candidate-runtime-replay-v1"
            and proof.get("runtime") == identity(), "changed_replay_runtime")
    old = json.loads(checked(proof["source"]).read_text())
    require(old.get("version") == "focus-appearance-experiment-v1" and bool(old.get("samples"))
            and old.get("protocolSHA256") == digest({k: v for k, v in old.items() if k != "protocolSHA256"}),
            "changed_replay_source")
    require({k: v for k, v in spec.items() if k != "runtimeReplay"} == old["inputs"], "replay_input_drift")
    expected = [{"id": r["id"], "pixelSHA256": r["crop"]["pixelSHA256"], "matchesRetainedCrop": True}
                for r in old["samples"]]
    require(proof.get("samples") == expected and proof.get("matches") == len(expected)
            and proof.get("selectionValidated") is True, "incomplete_replay_pixels")
    old_runtimes = list({digest(r["runtime"]): r["runtime"] for r in old["samples"] if "runtime" in r}.values())
    require(proof.get("oldRuntimes") == old_runtimes and bool(old_runtimes), "unbound_replay_runtime")
    token = _scope.set(proof)
    try:
        yield old
        checked(ref); checked(proof["source"])
        require(proof["runtime"] == identity(), "changed_replay_runtime")
    finally:
        _scope.reset(token)
