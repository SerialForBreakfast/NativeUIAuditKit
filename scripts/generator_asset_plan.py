"""Offline asset reuse planning. No transfer, rendering, or training admission."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys

from shared_transfer import document, path_under, require, verified

KINDS = {'artwork', 'mockup', 'native_capture', 'ui_source'}
ROLES = {'train', 'development', 'validation', 'test', 'unassigned'}
STATES = {'verified', 'pending', 'rejected'}
FIELDS = {'id', 'kind', 'sha256', 'bytes', 'source', 'sourceRevision',
          'ancestryGroups', 'dataRole', 'rightsStatus', 'rightsEvidence',
          'reviewStatus', 'reviewEvidence'}
MAX_OBJECT = 64 * 1024 * 1024
MAX_BATCH = 128 * 1024 * 1024


def keys(value, required, optional=()):
    require(type(value) is dict and required <= value.keys() and
            value.keys() <= required | set(optional), 'fields')


def string(value):
    require(type(value) is str and 0 < len(value) <= 4096 and
            not any(ord(c) < 32 for c in value), 'string')
    return value


def sha(value):
    require(type(value) is str and re.fullmatch('[0-9a-f]{64}', value), 'sha256')
    return value


def identity(value):
    string(value)
    require(re.fullmatch('[A-Za-z0-9_.:/-]+', value) is not None, 'identity')
    return value


def records(value):
    require(type(value) is list and len(value) <= 4096, 'record_count')
    return value


def validate_inventory(value):
    keys(value, {'schemaVersion', 'resources'})
    require(value['schemaVersion'] == 'generator-resource-inventory-v1', 'schema')
    seen = set()
    sizes = {}
    assessments = {}
    for r in records(value['resources']):
        keys(r, FIELDS, {'sourceRecord'})
        identity(r['id'])
        require(r['id'] not in seen, 'duplicate_id')
        seen.add(r['id'])
        require(r['kind'] in KINDS and r['dataRole'] in ROLES, 'kind_or_role')
        sha(r['sha256'])
        require(type(r['bytes']) is int and 0 < r['bytes'] <= MAX_OBJECT, 'object_size')
        require(sizes.setdefault(r['sha256'], r['bytes']) == r['bytes'], 'size_conflict')
        for field in ('source', 'sourceRevision'):
            string(r[field])
        groups = records(r['ancestryGroups'])
        require(groups and len(groups) == len(set(map(identity, groups))), 'ancestry')
        for prefix in ('rights', 'review'):
            require(r[prefix + 'Status'] in STATES, 'assessment_status')
            evidence = records(r[prefix + 'Evidence'])
            for item in evidence:
                string(item)
            require(r[prefix + 'Status'] != 'verified' or evidence, 'missing_evidence')
        assessment = (r['rightsStatus'], r['reviewStatus'])
        require(assessments.setdefault(r['sha256'], assessment) == assessment, 'alias_assessment_conflict')
        if 'sourceRecord' in r:
            require(type(r['sourceRecord']) is dict, 'source_record')
    return sorted(value['resources'], key=lambda r: r['id'])


def components(resources):
    """Union via content or ancestry, including unassigned/blocked bridge nodes."""
    parents = {r['id']: r['id'] for r in resources}

    def root(x):
        while parents[x] != x:
            parents[x] = parents[parents[x]]
            x = parents[x]
        return x

    tokens = {}
    for r in resources:
        for token in [('hash', r['sha256'])] + [('group', g) for g in r['ancestryGroups']]:
            other = tokens.setdefault(token, r['id'])
            a, b = root(r['id']), root(other)
            parents[max(a, b)] = min(a, b)
    groups = {}
    for r in resources:
        groups.setdefault(root(r['id']), []).append(r)
    out = []
    for group in groups.values():
        roles = sorted({r['dataRole'] for r in group} - {'unassigned'})
        require(len(roles) <= 1, 'cross_role_ancestry: ' + ','.join(r['id'] for r in group))
        out.append({'ids': sorted(r['id'] for r in group), 'assignedRoles': roles})
    return sorted(out, key=lambda g: g['ids'])


def plan(inventory, cache_index, cache_root):
    resources = validate_inventory(inventory)
    ancestry = components(resources)
    root = Path(os.path.abspath(cache_root))
    require(root.is_dir() and root.resolve() == root, 'cache_root')
    keys(cache_index, {'schemaVersion', 'files'})
    require(cache_index['schemaVersion'] == 'asset-cache-index-v1', 'cache_schema')
    by_hash = {r['sha256']: r for r in resources}
    cached = set()
    for entry in records(cache_index['files']):
        keys(entry, {'sha256', 'path'})
        digest = sha(entry['sha256'])
        require(digest in by_hash and digest not in cached, 'cache_hash_unknown_or_duplicate')
        path = path_under(root, entry['path'])
        verified(path, by_hash[digest])
        cached.add(digest)

    decisions, wanted = [], {}
    for r in resources:
        reasons = []
        if r['kind'] != 'artwork':
            reasons.append({'mockup': 'design_reference_only', 'native_capture':
                            'native_intake_required', 'ui_source': 'source_review_required'}[r['kind']])
        for field in ('rights', 'review'):
            if r[field + 'Status'] != 'verified':
                reasons.append(field + '_' + r[field + 'Status'])
        if r['dataRole'] == 'unassigned':
            reasons.append('role_unassigned')
        available = r['sha256'] in cached
        decisions.append({'id': r['id'], 'sha256': r['sha256'], 'dataRole': r['dataRole'],
                          'bytesVerified': available, 'renderEligible': not reasons and available,
                          'trainingAdmission': 'not_assessed', 'blockers': reasons +
                          ([] if available else ['bytes_missing'])})
        if not reasons and not available:
            item = wanted.setdefault(r['sha256'], {'sha256': r['sha256'], 'bytes': r['bytes'], 'ids': []})
            item['ids'].append(r['id'])
    batches = []
    for digest in sorted(wanted):
        item = wanted[digest]
        if not batches or batches[-1]['bytes'] + item['bytes'] > MAX_BATCH:
            batches.append({'bytes': 0, 'files': []})
        batches[-1]['bytes'] += item['bytes']
        batches[-1]['files'].append(item)
    canonical = json.dumps({'schemaVersion': inventory['schemaVersion'], 'resources': resources},
                           sort_keys=True, separators=(',', ':'), allow_nan=False).encode()
    return {'schemaVersion': 'asset-reuse-plan-v1',
            'inventoryContentSha256': hashlib.sha256(canonical).hexdigest(),
            'resources': decisions, 'connectedGroups': ancestry, 'missingArtworkBatches': batches,
            'summary': {'resources': len(resources), 'verifiedCacheObjects': len(cached),
                        'renderEligible': sum(r['renderEligible'] for r in decisions),
                        'missingEligibleObjects': len(wanted), 'requestedBytes': sum(b['bytes'] for b in batches)},
            'limitations': ['byte verification is not image decoding or native label validation',
                            'assessment evidence is retained, not independently adjudicated',
                            'no training admission, transfer or rendering performed']}


def normalize_image201(value):
    """Explicit producer adapter; never interprets incoming code or cache paths."""
    require(type(value) is dict and type(value.get('schema_version')) is int and
            value['schema_version'] == 1, 'image201_schema')
    out = []
    for r in records(value.get('assets')):
        require(type(r) is dict and r.get('split') ==
                'development_only;all pilot variants excluded from future independent final evaluation',
                'image201_role')
        require(r.get('parent') is None, 'image201_derived_requires_lineage_adapter')
        revisions = r.get('model_revisions')
        require(type(revisions) is dict and revisions, 'model_revisions')
        for key, revision in revisions.items():
            string(key)
            require(type(revision) is str and re.fullmatch('[0-9a-f]{40}', revision), 'model_revision')
        out.append({'id': r['stable_id'], 'kind': 'artwork', 'sha256': r['sha256'],
                    'bytes': r['bytes'], 'source': 'Big Dog LOCAL-IMAGE201 inventory-v1',
                    'sourceRevision': json.dumps(revisions, sort_keys=True),
                    'ancestryGroups': [identity(r['derivative_group'])], 'dataRole': 'development',
                    'rightsStatus': 'pending', 'rightsEvidence': [string(r['licence']), string(r['provenance'])],
                    'reviewStatus': 'pending', 'reviewEvidence': ['Retained producer review in sourceRecord; NUIAK decision pending'],
                    'sourceRecord': r})
    inventory = {'schemaVersion': 'generator-resource-inventory-v1', 'resources': out}
    validate_inventory(inventory)
    return inventory


def output(value, target):
    text = json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n'
    if target is None:
        print(text, end='')
        return
    path = Path(os.path.abspath(target))
    project = Path(__file__).resolve().parents[1]
    require(path.is_relative_to(project) and path.resolve() == path and path.parent.is_dir(), 'output_boundary')
    with path.open('x') as f:
        f.write(text)


def normalize_artwork204(value, review, source_hash):
    """Explicit local review, bound to source bytes; unreviewed siblings stay pending."""
    require(type(value) is dict and value.get('schema') == 'generator-resource-inventory-v1', 'artwork204_schema')
    keys(review, {'schemaVersion', 'sourceSHA256', 'evidence', 'familyRoles', 'reviewedIDs', 'useScope'})
    require(review['schemaVersion']=='artwork204-review-v1' and
            sha(review['sourceSHA256'])==source_hash, 'review_source_mismatch')
    evidence=string(review['evidence']);string(review['useScope'])
    families=review['familyRoles'];require(type(families) is dict and families,'family_roles')
    for family,role in families.items():
        identity(family);require(role in ROLES-{'unassigned'},'family_role')
    selected=records(review['reviewedIDs']);require(len(selected)==len(set(selected)),'duplicate_review')
    for item in selected:identity(item)
    seen=set();found=set();out=[]
    for r in records(value.get('resources')):
        require(type(r) is dict and r.get('dataRole')=='unassigned' and
                r.get('kind') in ('poster','thumbnail','avatar','backdrop'),'producer_role')
        groups=records(r.get('ancestryGroups'));require(groups,'ancestry')
        role_set={families[g] for g in groups if g in families}
        require(len(role_set)<=1,'cross_role_ancestry');found.update(set(groups)&families.keys())
        reviewed=r['id'] in selected;seen.add(r['id'])
        require(not reviewed or role_set,'review_without_role')
        out.append(dict(id=r['id'],kind='artwork',sha256=r['sha256'],bytes=r['bytes'],
            source=r['source'],sourceRevision=r['sourceRevision'],ancestryGroups=groups,
            dataRole=next(iter(role_set),'unassigned'),rightsStatus='verified' if reviewed else 'pending',
            reviewStatus='verified' if reviewed else 'pending',rightsEvidence=[evidence] if reviewed else [],
            reviewEvidence=[evidence] if reviewed else [],sourceRecord=dict(producer=r,
                assessmentScope=review['useScope'],reviewSourceSHA256=source_hash)))
    require(set(selected)<=seen and found==set(families),'unknown_review_member_or_family')
    inventory=dict(schemaVersion='generator-resource-inventory-v1',resources=out)
    validate_inventory(inventory);components(out)
    return inventory


def metadata(path):
    path = Path(os.path.abspath(path))
    require(path.resolve() == path and stat.S_ISREG(path.lstat().st_mode), 'metadata_file_type')
    return document(path)


def inventory_metadata(path, expected_sha256=None, *, max_bytes=4*1024**2, max_nodes=100000):
    """Larger JSON inventory budget, never relax the coordination parser."""
    require(type(max_bytes) is int and 0<max_bytes<=8*1024**2,'inventory_budget')
    require(type(max_nodes) is int and 0<max_nodes<=150000,'inventory_node_budget')
    path=Path(os.path.abspath(path))
    require(path.resolve()==path and stat.S_ISREG(path.lstat().st_mode),'metadata_file_type')
    require(path.stat().st_size<=max_bytes,'inventory_size')
    raw=path.read_bytes();require(len(raw)<=max_bytes,'inventory_size')
    require(expected_sha256 is None or hashlib.sha256(raw).hexdigest()==sha(expected_sha256),'review_source_mismatch')
    def unique(pairs):
        result={}
        for key,value in pairs:
            require(key not in result,'duplicate_key');result[key]=value
        return result
    def invalid(value):raise ValueError('nonfinite_json')
    value=json.loads(raw,object_pairs_hook=unique,parse_constant=invalid)
    stack=[(value,0)];count=0
    while stack:
        item,depth=stack.pop();count+=1
        require(depth<=32 and count<=max_nodes,'inventory_complexity')
        if isinstance(item,dict):stack.extend((v,depth+1) for v in item.values())
        elif isinstance(item,list):stack.extend((v,depth+1) for v in item)
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('plan')
    p.add_argument('--inventory', type=Path, required=True)
    p.add_argument('--cache-index', type=Path, required=True)
    p.add_argument('--cache-root', type=Path, required=True)
    p.add_argument('--output', type=Path)
    n = sub.add_parser('normalize-image201')
    n.add_argument('--inventory', type=Path, required=True)
    n.add_argument('--output', type=Path)
    a = sub.add_parser('normalize-artwork204')
    a.add_argument('--inventory', type=Path, required=True)
    a.add_argument('--review', type=Path, required=True)
    a.add_argument('--output', type=Path)
    args = parser.parse_args()
    try:
        if args.command == 'normalize-artwork204':
            review=metadata(args.review)
            value=inventory_metadata(args.inventory,review['sourceSHA256'])
            result=normalize_artwork204(value,review,review['sourceSHA256'])
        elif args.command == 'normalize-image201':result=normalize_image201(metadata(args.inventory))
        else:result=plan(inventory_metadata(args.inventory), metadata(args.cache_index), args.cache_root)
        output(result, args.output)
        return 0
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print('asset_plan_rejected: ' + str(exc), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
