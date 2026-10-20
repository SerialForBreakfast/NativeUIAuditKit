"""Run approved capture steps with lossless retention between closed sessions."""
import research_queue as q
from experiment_templates import checked, pin
import ttr_evidence_compaction458 as storage

OUT = None


def compact_after(step):
    """Never retry capture when retention fails. Preserve its receipt."""
    step()
    folder = OUT/'retention'
    folder.mkdir()
    storage.local_compact(folder)


def recovery():
    import native_capture_recovery as worker
    worker.OUT = OUT
    compact_after(worker.run)


def capture():
    import template_bridge395 as worker
    worker.OUT = OUT
    compact_after(worker.capture)


def serial_children(children):
    """Each successor waits for verified retention after the previous capture."""
    previous = None
    for child in children:
        child['retention'] = 'verified-png-hardlinks-v1'
        child['inputs'] += [pin(q.ROOT/'scripts/native_storage458.py'),
                            pin(q.ROOT/'scripts/ttr_evidence_compaction458.py'),
                            pin(q.ROOT/'scripts/hcf_capture362.py')]
        if previous:
            child['dependencies'].append(dict(job=previous['id'], specSHA256=q.text_digest(previous),
                                              outputs=['retention/compaction.json']))
        q.validate(child)
        previous = child
    return children


def admit():
    import recovery_capture_gate437 as gate
    spec = q.load(OUT.parents[2]/'spec.json')
    queue = OUT.parents[4]
    plan = q.load(checked(spec['admissionPlan']))
    children, recovered = gate.prepare(spec, queue, plan, OUT)
    gate.preflight(recovered)
    rows = gate.admit(serial_children(children), queue, OUT)
    gate.retain(OUT/'admission.json', dict(version='native-storage-admission-v1', jobs=rows,
        executionStarted=False, modelAccepted=False, trainingEligible=False))
    gate.retain(OUT/'artifact-receipt.json', dict(version='research-artifact-v1', outputs=[
        dict(path=p.name, sha256=q.digest(p)) for p in sorted(OUT.iterdir())
        if p.is_file() and p.name != 'artifact-receipt.json']))
