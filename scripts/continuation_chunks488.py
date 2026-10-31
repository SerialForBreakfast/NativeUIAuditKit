"""RECOVERY488: derive bounded continuation chunks from 1 reviewed base specification.

Chunk 1 resumes the exhausted checkpoint and stops at `stop`. Chunk 2 resumes chunk 1's `last.pt` to epoch 30.
Both use the restore adapter and a passed 2-step chain parity proof. This tool writes definitions only.
It does not register, approve, or start a job.
"""
import argparse
import copy
import json
from pathlib import Path

import research_queue as q
import research_continuations as c
from checkpoint_restore404 import CHAIN


def pin(path):
    path = Path(path)
    return dict(path=q.relative(path), sha256=q.digest(path))


def replace_pin(pins, old, new):
    """Replace 1 pinned input by path. Other pins keep their order."""
    out = [p for p in pins if p['path'] != old['path']]
    q.require(len(out) == len(pins) - 1, 'chunk_pin_missing:' + old['path'])
    return out + [new]


def qualification(destination, checkpoint, adapter, budget, parent_result, proof, scope):
    doc = dict(version='resume-qualification-v1', passed=True, checkpoint=checkpoint, adapter=adapter,
               preservesControls=True, budget=budget, parentResult=parent_result,
               mechanismQualification=pin(proof), scope=scope)
    if destination.exists():
        q.require(q.load(destination) == doc, 'chunk_qualification_changed')
    else:
        q.save(destination, doc)
    return pin(destination)


def build(base, ids, stop, proof, folder, budget, reason, queue=q.QUEUE, timeout=None):
    """Return [(spec, record)] for 2 chunks. `base` is the reviewed revoked successor or an equivalent spec."""
    q.require(base['training']['resume'] == 'checkpoint-v1' and base['adapter']['steps'] == ['checkpoint_restore404.run'],
              'chunk_base_not_restore')
    restoration = q.load(proof)
    q.require(restoration.get('passed') is True and restoration.get('scopeVersion') == CHAIN, 'chunk_chain_unqualified')
    old_proof = base['resumeInputs']['qualification']
    parent_checkpoint = base['resumeInputs']['checkpoint']
    record = c.records(queue)[base['id']]
    parent, attempt, parent_result = record['parent'], record['parentAttempt'], record['parentResult']
    old_record_proof = record['qualification']
    out = []
    for index, ident in enumerate(ids):
        spec = copy.deepcopy(base)
        spec['id'] = ident
        # The trust check requires every dependency output to be read. The restore adapter reads only the
        # previous chunk's checkpoint, so other gates (for example a completed negative test) stay out.
        spec['dependencies'] = []
        if timeout is not None:
            q.require(type(timeout) is int and 0 < timeout <= budget['maxChunkSeconds'], 'chunk_timeout')
            spec['limits'] = dict(spec['limits'], timeoutSeconds=timeout)
        # The chunks use the current restore adapter, which adds stop epochs and dependency checkpoints.
        adapter = q.ROOT/'scripts/checkpoint_restore404.py'
        spec['inputs'] = [pin(adapter) if p['path'] == q.relative(adapter) else p for p in spec['inputs']]
        spec['resumeInputs']['qualification'] = pin(proof)
        spec['inputs'] = replace_pin(spec['inputs'], old_proof, pin(proof))
        reads = [r for r in spec['evidence']['reads'] if r != old_proof['path']] + [pin(proof)['path']]
        if index == 0:
            checkpoint = parent_checkpoint
            spec['resumeStopEpoch'] = stop
        else:
            previous = out[0][0]
            checkpoint = dict(job=previous['id'], output='last.pt')
            spec.pop('resumeStopEpoch', None)
            spec['resumeInputs']['checkpoint'] = checkpoint
            spec['inputs'] = [p for p in spec['inputs'] if p['path'] != parent_checkpoint['path']]
            reads = [r for r in reads if r != parent_checkpoint['path']]
            spec['dependencies'] = [dict(job=previous['id'], specSHA256=q.text_digest(previous), outputs=['last.pt'])]
        spec['evidence']['reads'] = reads
        scope = (f'Chunk {index + 1} of 2. The chain parity proof stops at the same epochs. '
                 'Repeat-9 subset parity only; native accuracy is not qualified.')
        proof_pin = qualification(folder/(ident + '-qualification.json'), checkpoint, spec['adapter'], budget,
                                  parent_result, proof, scope)
        spec['inputs'] = replace_pin(spec['inputs'], old_record_proof, proof_pin)
        q.validate(spec)
        entry = dict(version=c.VERSION if index == 0 else c.CHAIN_VERSION, job=ident, specSHA256=q.text_digest(spec),
                     parent=parent, parentAttempt=attempt, parentResult=parent_result, checkpoint=checkpoint,
                     qualification=proof_pin, reason=reason, budget=budget)
        if index:
            entry['previous'] = ids[0]
        out.append((spec, entry))
    return out


def from_parent(parent_id, ident, proof, folder, budget, reason, timeout, max_bytes, trainer=None, queue=q.QUEUE):
    """QUEUE548: build 1 continuation that resumes an exhausted T06 fit to epoch 30. Return (spec, record).

    Only the adapter, resume inputs, limits, and resume mode change. The job declares no unread dependency.
    """
    parent = q.load(queue/'jobs'/parent_id/'spec.json')
    q.require(parent['authority'] == 'training' and parent['training']['resume'] == 'restart' and
              parent['template']['id'] == 'T06', 'chunk_parent_not_t06')
    attempts = q.attempts_of(queue/'jobs'/parent_id)
    result_path = attempts[-1]/'result.json'
    result = q.load(result_path)
    q.require(result.get('status') == 'failed' and result.get('reason') == 'timeout', 'chunk_parent_not_timeout')
    checkpoint = pin(attempts[-1]/'out/last.pt')
    restoration = q.load(proof)
    q.require(restoration.get('passed') is True and restoration.get('trainer') == trainer, 'chunk_parity_trainer')
    spec = copy.deepcopy(parent)
    spec['id'] = ident
    spec['adapter'] = dict(type='python-callable', steps=['checkpoint_restore404.run'],
                           outputAttributes=['checkpoint_restore404.OUT'])
    spec['dependencies'] = []
    spec['limits'] = dict(maxAttempts=1, timeoutSeconds=timeout, maxOutputBytes=max_bytes)
    spec['training'] = dict(spec['training'], resume='checkpoint-v1')
    membership, initialization = spec['training']['membership'][0], spec['training']['initialization']
    parent_result = pin(result_path)
    proof_pin = qualification(folder/(ident + '-qualification.json'), checkpoint, spec['adapter'], budget,
                              parent_result, proof, 'Single chunk to epoch 30. Subset parity with the same trainer and '
                              'deduplication setting. Native accuracy is not qualified.')
    spec['resumeInputs'] = dict(checkpoint=checkpoint, qualification=pin(proof), membership=membership,
                                initialization=initialization)
    if trainer is not None:
        spec['restoreTrainer'] = trainer
    extra = [checkpoint, pin(proof), proof_pin, pin(q.ROOT/'scripts/checkpoint_restore404.py')]
    if trainer is not None:
        extra.append(pin(q.ROOT/('scripts/train_focus_ring_detector_' + trainer + '.py')))
    kept = []
    for p in spec['inputs']:
        current = q.ROOT/p['path']
        if current.is_file() and q.digest(current) == p['sha256']:
            kept.append(p)
        else:
            # The parent's own adapter code may change after the fit. Any other stale input stops the build.
            q.require(p['path'].startswith('scripts/'), 'chunk_parent_input_changed:' + p['path'])
    spec['inputs'] = kept + [p for p in extra if p not in kept]
    spec['evidence'] = dict(spec['evidence'], reads=[membership['path'], initialization['path'],
                                                     pin(proof)['path'], checkpoint['path']])
    q.validate(spec)
    record = dict(version=c.VERSION, job=ident, specSHA256=q.text_digest(spec), parent=parent_id,
                  parentAttempt=int(attempts[-1].name), parentResult=parent_result, checkpoint=checkpoint,
                  qualification=proof_pin, reason=reason, budget=budget)
    return spec, record


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('base', help='job ID of the reviewed base successor')
    parser.add_argument('--ids', nargs=2, required=True)
    parser.add_argument('--stop', type=int, required=True)
    parser.add_argument('--proof', type=Path, required=True)
    parser.add_argument('--folder', type=Path, required=True)
    parser.add_argument('--reason', required=True)
    parser.add_argument('--timeout', type=int)
    args = parser.parse_args()
    base = q.load(q.QUEUE/'jobs'/args.base/'spec.json')
    budget = c.records(q.QUEUE)[args.base]['budget']
    args.folder.mkdir(parents=True, exist_ok=True)
    for spec, entry in build(base, args.ids, args.stop, args.proof, args.folder, budget, args.reason,
                             timeout=args.timeout):
        q.save(args.folder/(spec['id'] + '-spec.json'), spec)
        q.save(args.folder/(spec['id'] + '-record.json'), entry)
        print(spec['id'], q.text_digest(spec))
