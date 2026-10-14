"""Compare pinned cached predictions in one bounded, resumable worker.

This adapter reuses standard390.compare. It does not run model inference.
"""
import argparse
from collections import OrderedDict
import fcntl
import hashlib
import json
from pathlib import Path
import resource
import sys
import time

import research_queue as q
import standard390

OUT = None
VERSION = 'cached-comparison-suite391-v1'


class Documents:
    """Bound the serialized JSON cache and verify bytes before decoding."""
    def __init__(self, root, maximum=32_000_000):
        self.root, self.maximum = root, maximum
        self.cache = OrderedDict()
        self.size = self.reads = self.hits = 0
        self.seconds = 0.0

    def get(self, ref):
        q.check_pin(ref)
        key = (ref['path'], ref['sha256'])
        if key in self.cache:
            self.hits += 1
            self.cache.move_to_end(key)
            return self.cache[key][1]
        start = time.monotonic()
        path = q.local_path(self.root, ref['path'])
        q.require(path.stat().st_size <= self.maximum, 'input_size_limit')
        raw = path.read_bytes()
        q.require(hashlib.sha256(raw).hexdigest() == ref['sha256'], 'input_changed')
        doc = json.loads(raw)
        while self.cache and self.size + len(raw) > self.maximum:
            _, (size, _) = self.cache.popitem(last=False)
            self.size -= size
        self.cache[key] = (len(raw), doc)
        self.size += len(raw)
        self.reads += 1
        self.seconds += time.monotonic() - start
        return doc


def validate(manifest):
    q.require(manifest.get('version') == VERSION, 'suite_version')
    items = manifest.get('slices')
    q.require(isinstance(items, list) and 1 <= len(items) <= 56, 'slice_count')
    seen, pairs = set(), set()
    for item in items:
        ident = item['id']
        q.require(q.ID.fullmatch(ident) and ident not in seen, 'duplicate_or_invalid_slice')
        seen.add(ident)
        for name in ('control', 'candidate', 'expected'):
            q.check_pin(item[name])
        pair = (item['control']['sha256'], item['candidate']['sha256'])
        q.require(pair not in pairs, 'duplicate_comparison')
        pairs.add(pair)
        q.require(type(item['cases']) is int and item['cases'] > 0, 'zero_support')
    q.require(isinstance(manifest.get('evidence'), list) and 1 <= len(manifest['evidence']) <= 512, 'missing_evidence')
    for ref in manifest['evidence']:
        q.check_pin(ref)


def references(manifest, items):
    refs = list(manifest['evidence'])
    for item in items:
        refs.extend(item[k] for k in ('control', 'candidate', 'expected'))
    by_path = {}
    for ref in refs:
        old = by_path.setdefault(ref['path'], ref)
        q.require(old == ref, 'conflicting_input_identity')
    return list(by_path.values())


def check_roles(doc):
    roles = {}
    for part in doc['sets'].values():
        for row in part['rows']:
            q.require(row['role'] in ('train', 'development', 'retained-evaluation', 'calibration'), 'unknown_or_audit_role')
            key = (row['sourceDomain'], row['group'])
            previous = roles.setdefault(key, row['role'])
            q.require(previous == row['role'], 'cross_role_group')


def execute(manifest, output, root=q.ROOT, only=None, maximum=100_000_000, timeout=800):
    validate(manifest)
    root, output = Path(root), Path(output)
    output = q.local_path(root, str(output.relative_to(root)))
    q.require(output != root, 'output_is_root')
    q.require(only is None or only in {s['id'] for s in manifest['slices']}, 'unknown_slice')
    items = [s for s in manifest['slices'] if only is None or s['id'] == only]
    refs = references(manifest, items)
    # Verify inputs again on resume, even when all slice outputs exist.
    for ref in refs:
        q.require(q.digest(q.local_path(root, ref['path'])) == ref['sha256'], 'input_changed')
    output.mkdir(parents=True, exist_ok=True)
    lock_path = q.local_path(output, 'suite.lock')
    with lock_path.open('a') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise ValueError('suite_busy') from error
        return _locked(manifest, items, refs, output, root, maximum, timeout)


def _locked(manifest, items, refs, output, root, maximum, timeout):
    start = time.monotonic()
    contract = dict(manifest=manifest, selected=[s['id'] for s in items])
    identity = q.text_digest(contract)
    state = q.local_path(output, 'contract.json')
    if state.exists():
        q.require(q.load(state) == contract, 'resume_contract_changed')
    else:
        q.save(state, contract)
    cache = Documents(root)
    records, computed, resumed = [], 0, 0
    compare_seconds = 0.0

    def save(name, doc, replace=False):
        encoded = len(json.dumps(doc, sort_keys=True, indent=2, allow_nan=False).encode()) + 1
        q.require(q.live_output_bytes(output) + encoded <= maximum, 'output_size_limit')
        q.save(q.local_path(output, name), doc, replace=replace)

    for index, item in enumerate(items):
        q.require(time.monotonic() - start < timeout, 'suite_timeout')
        name = item['id'] + '.json'
        path = q.local_path(output, name)
        receipt = q.local_path(output, item['id'] + '.receipt.json')
        save('progress.json', dict(step='compare ' + item['id'], completed=index, total=len(items),
            elapsedSeconds=time.monotonic()-start, eta=None), replace=True)
        if receipt.exists():
            record = q.load(receipt)
            q.require(record['contractSHA256'] == identity and record['path'] == name, 'resume_receipt_changed')
            q.require(q.digest(path) == record['sha256'], 'resume_output_changed')
            q.require(record['cases'] == item['cases'], 'resume_count_changed')
            resumed += 1
        else:
            control, candidate = (cache.get(item[k]) for k in ('control', 'candidate'))
            check_roles(control)
            check_roles(candidate)
            tick = time.monotonic()
            comparison = standard390.compare(control, candidate)
            compare_seconds += time.monotonic() - tick
            q.require(len(comparison['cases']) == item['cases'], 'support_changed')
            expected = cache.get(item['expected'])
            matches = [r for r in expected['comparisons'] if r['controlJob'] == item['controlJob']
                       and r['candidateJob'] == item['candidateJob']]
            q.require(len(matches) == 1, 'expected_slice_missing')
            old = {k: v for k, v in matches[0].items() if k not in ('controlJob', 'candidateJob')}
            q.require(old == comparison, 'comparison_parity_failed')
            # A crash can leave an output without its receipt. Verify it before adopting it.
            if path.exists():
                q.require(q.load(path) == comparison, 'orphan_output_changed')
            else:
                save(name, comparison)
            record = dict(path=name, sha256=q.digest(path), cases=len(comparison['cases']), contractSHA256=identity)
            save(receipt.name, record)
            computed += 1
        records.append(record)
    for ref in refs:
        q.require(q.digest(q.local_path(root, ref['path'])) == ref['sha256'], 'input_changed_during_run')
    result = dict(version=VERSION, contractSHA256=identity, complete=len(items) == len(manifest['slices']),
        slices=records, computed=computed, resumed=resumed, jsonReads=cache.reads, cacheHits=cache.hits,
        loadSeconds=cache.seconds, compareSeconds=compare_seconds, seconds=time.monotonic()-start,
        parity='exact', modelAccepted=False, inferenceExecuted=False, sources=refs)
    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    result['peakResidentBytes'] = peak if sys.platform == 'darwin' else peak * 1024
    final = q.local_path(output, 'suite.json')
    if final.exists():
        previous = q.load(final)
        q.require(previous['contractSHA256'] == identity and previous['slices'] == records, 'completed_suite_changed')
    else:
        save('suite.json', result)
    save('progress.json', dict(step='complete', completed=len(items), total=len(items),
        elapsedSeconds=time.monotonic()-start, eta=None), replace=True)
    return result


def run():
    """Queue callable. Existing runner controls time, process, and output limits."""
    manifest = q.load(OUT / 'config.json')
    result = execute(manifest, OUT / 'suite', root=q.ROOT)
    q.save(OUT / 'sources.json', result['sources'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--slice')
    args = parser.parse_args()
    print(json.dumps(execute(q.load(args.manifest), args.output.absolute(), only=args.slice), sort_keys=True))


if __name__ == '__main__':
    main()
