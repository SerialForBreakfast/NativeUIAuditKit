"""Use the existing compiled-tree contract for experimental observer delivery."""
import hashlib
import math
from pathlib import Path


def compiled_digest(root):
    root = Path(root)
    if root.is_symlink() or not root.is_dir():
        raise ValueError('compiled_root')
    entries = list(root.rglob('*'))
    if len(entries) > 1024:
        raise ValueError('compiled_entry_limit')
    records = []; total = 0
    for path in entries:
        if path.is_symlink() or not (path.is_file() or path.is_dir()):
            raise ValueError('compiled_special_file')
        if path.is_dir():
            continue
        name = path.relative_to(root).as_posix()
        try:
            name.encode('ascii')
        except UnicodeEncodeError:
            raise ValueError('compiled_path_ascii')
        size = path.stat().st_size; total += size
        if size > 64 * 1024**2 or total > 128 * 1024**2:
            raise ValueError('compiled_size_limit')
        records.append((name, size, hashlib.sha256(path.read_bytes()).hexdigest()))
    if not records:
        raise ValueError('compiled_empty')
    digest = hashlib.sha256(b'compiled-tree-sha256-v1\n')
    for name, size, sha in sorted(records):
        digest.update((name+'\0'+str(size)+'\0'+sha+'\n').encode('ascii'))
    return digest.hexdigest()


def verify_receipt(receipt, expected):
    """Verify a scored observer receipt without granting navigation authority."""
    def require(condition, code):
        if not condition: raise ValueError(code)
    require(receipt.get('version') == 'ttr-crop-observer-v2', 'observer_version')
    require(receipt.get('navigationAuthority') is False, 'observer_authority')
    require(receipt.get('backend') == 'Vision', 'observer_backend')
    require(receipt.get('bundleSHA256') == expected['bundleSHA256'], 'observer_bundle')
    require(receipt.get('compiledDigestAlgorithm') == 'compiled-tree-sha256-v1', 'observer_digest_algorithm')
    before=receipt.get('compiledBeforeSHA256', '')
    require(len(before)==64 and all(c in '0123456789abcdef' for c in before), 'observer_digest')
    require(before==receipt.get('compiledAfterSHA256'), 'observer_loaded_bytes_changed')
    require(all(isinstance(receipt.get(k),str) and receipt[k] for k in
                ('osVersion','architecture','compilerVersion','sourceRevision')), 'observer_host')
    actual=receipt.get('results',[]); reference=expected['results']
    require(reference and [r['id'] for r in actual]==[r['id'] for r in reference], 'observer_membership')
    require(len({r['id'] for r in actual})==len(actual), 'observer_duplicates')
    for row, ref in zip(actual,reference):
        require(all(row.get(k)==ref[k] for k in
                    ('parentSHA256','candidateID','bounds','modelInputRGBSHA256')), 'observer_lineage')
        require(row.get('state')=='scored', 'observer_not_scored')
        score=row.get('score')
        require(type(score) in (int,float) and math.isfinite(score) and 0<=score<=1, 'observer_score')
        require(abs(score-ref['score'])<=.01, 'observer_score_parity')
        require(all((score>=t)==(ref['score']>=t) for t in (.5,.7,.85)), 'observer_decision_parity')
    return dict(verifiedFrames=len(actual),modelAccepted=False,navigationAuthority=False,
                limitation='Sender authentication and deployable proposal quality require separate evidence.')
