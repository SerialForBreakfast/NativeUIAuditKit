"""T44: count eligible related groups and labeled control observations in pinned native focus manifests.

Compare the counts with a pinned quota file. Role ancestry comes from scene.semantic_inventory parent chains.
Each quota entry has a status. A 'frozen' run refuses a selected dimension that has a non-frozen entry.
A 'proposed' run is diagnostic only. No capture, no training, and no model change. No model is accepted.

Units:
- observations: 1 expected control in 1 captured frame, labeled focused or unfocused. This is the pair unit
  of focus_ring_readiness and DeliveryDecisions item 7.
- groups: distinct related groups (plan group / case group). Factor captures of the same case group count once.

A hard negative uses the readiness rule: the frame has known focus and no focused element.
'theme' is the Fixture system theme (scene recipe). The plan case theme is the background luminance; it is
reported as the 'background' slice and does not count toward theme quotas.
"""
from collections import Counter, defaultdict

import research_queue as q
from template_inputs398 import checked
from template_adapters395 import document, resolve_inputs

OUT = None
QUOTA_SETS = ('frozen', 'proposed')
ELIGIBILITY = ('admitted', 'any')
DIMENSIONS = ('scene', 'sceneTheme', 'hardNegative', 'total', 'family', 'familyTheme')
STATUSES = ('frozen', 'proposed')
SELECTORS = ('scene', 'theme', 'family', 'class', 'label', 'hardNegative')
# Fixture component kinds (FixtureComposition.Kind) mapped to the corpus strata of FOCUS-CORPUS-03.
FAMILY = {'poster': 'artwork', 'thumbnail': 'artwork', 'artwork': 'artwork', 'button': 'buttons',
          'row': 'rows', 'tab': 'tabs', 'text': 'other'}
ROLE = {'train': 'training'}
MAX_DEPTH = 16
MANIFEST_LIMIT = 64


def parameters(value):
    """Return (quota set, eligibility, dimensions) or raise."""
    q.require(isinstance(value, dict) and set(value) == {'quotaSet', 'eligibility', 'dimensions'}, 'quota_parameters')
    q.require(value['quotaSet'] in QUOTA_SETS, 'quota_set')
    q.require(value['eligibility'] in ELIGIBILITY, 'quota_eligibility')
    dims = value['dimensions']
    q.require(isinstance(dims, list) and dims and len(dims) == len(set(dims)) and set(dims) <= set(DIMENSIONS),
              'quota_dimensions')
    return value['quotaSet'], value['eligibility'], tuple(dims)


def camel(text):
    head, *rest = str(text).split('_')
    return head + ''.join(p[:1].upper() + p[1:] for p in rest)


def quotas(doc, quota_set, dims):
    """Return the selected entries. Refuse a frozen run that needs a non-frozen entry."""
    q.require(doc.get('version') == 'focus-coverage-quotas-v1', 'quota_version')
    entries = doc['quotas']
    q.require(isinstance(entries, list) and len({e['id'] for e in entries}) == len(entries), 'quota_ids')
    for e in entries:
        q.require(set(e) <= {'id', 'dimension', 'unit', 'roles', 'select', 'kind', 'value', 'base', 'status', 'source'}
                  and {'id', 'dimension', 'unit', 'roles', 'select', 'kind', 'value', 'status', 'source'} <= set(e),
                  'quota_fields:' + str(e.get('id')))
        q.require(e['dimension'] in DIMENSIONS and e['status'] in STATUSES and e['unit'] in ('observations', 'groups'),
                  'quota_entry:' + e['id'])
        q.require(e['kind'] in ('minimum', 'share') and type(e['value']) in (int, float) and e['value'] > 0,
                  'quota_value:' + e['id'])
        q.require(('base' in e) == (e['kind'] == 'share'), 'quota_base:' + e['id'])
        q.require(isinstance(e['source'], str) and len(e['source']) >= 12, 'quota_source:' + e['id'])
        for sel in [e['select']] + ([e['base']] if 'base' in e else []):
            q.require(isinstance(sel, dict) and set(sel) <= set(SELECTORS), 'quota_selector:' + e['id'])
    selected = [e for e in entries if e['dimension'] in dims]
    for dim in dims:
        q.require(any(e['dimension'] == dim for e in selected), 'quota_dimension_empty:' + dim)
        if quota_set == 'frozen':
            q.require(all(e['status'] == 'frozen' for e in selected if e['dimension'] == dim), 'quota_unfrozen:' + dim)
    return selected


def ancestry(elements, start):
    """Follow parent links from 1 control to its layout_region. Return the region ID or None."""
    seen, node = set(), elements.get(start)
    while node is not None and len(seen) <= MAX_DEPTH:
        if node.get('role') == 'layout_region':
            return node['id']
        if node['id'] in seen:
            return None
        seen.add(node['id'])
        node = elements.get(node.get('parent_id') or node.get('declared_parent_id'))
    return None


def recipe_items(recipe):
    """Map item ID to (region ID, component kind) from the declared composition."""
    comp = recipe.get('appearance', {}).get('composition', {})
    kinds = {name: d.get('kind') for name, d in comp.get('definitions', {}).items()}
    return {item['id']: (region['id'], kinds.get(item.get('component'), item.get('component')))
            for region in comp.get('regions', []) for item in region.get('items', [])}


def observations(entry, rows, ledger):
    """Add 1 row per expected control per frame. Record ancestry and identity checks in the ledger."""
    plan_doc = document(entry['artifact'])
    plan = plan_doc['plan']
    capture = document(entry['capture'])
    q.require(capture.get('version') == plan.get('version') and capture.get('group') == plan.get('group'),
              'manifest_plan_mismatch:' + entry['capture']['path'])
    cases = {c['id']: c for c in plan['cases']}
    admitted = plan.get('trainingEligible') is True
    for frame in capture['frames']:
        case = cases.get(frame['case'])
        q.require(case is not None, 'manifest_case_unknown:' + str(frame['case']))
        scene = frame['after']['scene']
        recipe, inv = scene['recipe'], scene.get('semantic_inventory')
        q.require(recipe.get('theme') and case.get('theme'), 'manifest_theme_missing:' + frame['id'])
        ledger['frames'] += 1
        if not inv or inv.get('truncated') or inv.get('coverage') != 'complete_declared_composition':
            ledger['framesWithoutInventory'] += 1
            continue
        elements = {e['id']: e for e in inv['elements']}
        items = recipe_items(recipe)
        no_focus = inv.get('focus_known') is True and inv.get('focused_id') is None
        group = plan['group'] + '/' + case['group']
        for control in inv['expected_control_ids']:
            region = ancestry(elements, control)
            declared = items.get(control)
            if region is None or declared is None or declared[0] != region:
                ledger['ancestryUnresolved'] += 1
                ledger['ineligibleGroups'].add(group)
                continue
            ledger['ancestryResolved'] += 1
            rows.append(dict(group=group, role=ROLE.get(case['role'], case['role']), admitted=admitted,
                             scene=camel(recipe.get('archetype')), theme=camel(recipe.get('theme')),
                             family=FAMILY.get(declared[1], 'unmapped:' + str(declared[1])),
                             layout=case.get('family'), background=camel(case['theme']),
                             **{'class': elements[control].get('declared_taxonomy')},
                             label=int(inv.get('focus_known') is True and inv.get('focused_id') == control),
                             hardNegative=no_focus))
    return dict(artifact=entry['artifact'], capture=entry['capture'], version=plan.get('version'),
                role=plan.get('role'), trainingEligible=plan.get('trainingEligible'), frames=len(capture['frames']))


def matches(row, select):
    for key, want in select.items():
        if (row[key] not in want) if isinstance(want, list) else (row[key] != want):
            return False
    return True


def measure(rows, entry, select):
    hit = [r for r in rows if r['role'] in entry['roles'] and matches(r, select)]
    return len(hit) if entry['unit'] == 'observations' else len({r['group'] for r in hit})


def compare(rows, entry):
    observed = measure(rows, entry, entry['select'])
    value = dict(id=entry['id'], dimension=entry['dimension'], status=entry['status'], unit=entry['unit'],
                 roles=entry['roles'], select=entry['select'], kind=entry['kind'], observed=observed,
                 source=entry['source'])
    if entry['kind'] == 'minimum':
        required = entry['value']
    else:
        base = measure(rows, entry, entry['base'])
        required = entry['value'] * base
        value.update(base=base, share=entry['value'])
    deficit = max(0, required - observed)
    value.update(required=required, deficit=deficit,
                 decision='vacuous' if entry['kind'] == 'share' and value['base'] == 0
                 else ('met' if deficit == 0 else 'deficit'))
    return value


def slices(rows):
    out = {}
    for key in ('role', 'scene', 'theme', 'background', 'family', 'layout', 'class'):
        table = defaultdict(lambda: dict(observations=0, groups=set(), focused=0, hardNegatives=0))
        for r in rows:
            cell = table[str(r[key])]
            cell['observations'] += 1
            cell['groups'].add(r['group'])
            cell['focused'] += r['label']
            cell['hardNegatives'] += r['hardNegative']
        out[key] = {k: dict(v, groups=len(v['groups'])) for k, v in sorted(table.items())}
    return out


def summarize(manifests, rows, ledger, selected, settings):
    quota_set, eligibility, dims = settings
    conflicts = defaultdict(set)
    for r in rows:
        conflicts[r['group']].add(r['role'])
    leaked = sorted(g for g, roles in conflicts.items() if len(roles) > 1)
    excluded = ledger['ineligibleGroups'] | set(leaked)
    eligible = [r for r in rows if r['group'] not in excluded and (eligibility == 'any' or r['admitted'])]
    results = [compare(eligible, e) for e in selected]
    deficits = [r for r in results if r['decision'] == 'deficit']
    return dict(version='quota-comparison-v1', quotaSet=quota_set, eligibility=eligibility, dimensions=list(dims),
                diagnosticOnly=quota_set == 'proposed' or eligibility == 'any',
                manifests=manifests, frames=ledger['frames'], framesWithoutInventory=ledger['framesWithoutInventory'],
                ancestry=dict(resolved=ledger['ancestryResolved'], unresolved=ledger['ancestryUnresolved']),
                observations=dict(all=len(rows), eligible=len(eligible),
                                  admitted=sum(r['admitted'] for r in rows)),
                groups=dict(all=len(conflicts), eligible=len({r['group'] for r in eligible}),
                            ancestryExcluded=sorted(ledger['ineligibleGroups']), roleConflicts=leaked),
                decisions=results, deficitCount=len(deficits),
                deficitsByDimension=dict(Counter(r['dimension'] for r in deficits)),
                slices=slices(eligible), gains=[], lostPriorSuccesses=[], modelAccepted=False,
                limitation='Counts pinned capture manifests only. Image count is not coverage. Proposed quota entries '
                           'are not maintainer-frozen; a proposed run is diagnostic only. Hard negatives use the '
                           'readiness no-focus rule. Theme is the system theme; a light background in the dark system theme '
                           'is not a light theme. No pixels are read and no model is evaluated.')


def run():
    cfg = q.load(OUT.parents[2] / 'spec.json')['template']
    settings = parameters(cfg['parameters'])
    refs = resolve_inputs(cfg, OUT)
    selected = quotas(document(refs['quotas']), settings[0], settings[2])
    listing = document(refs['manifests'])
    q.require(listing.get('version') == 'quota-manifests-v1', 'manifests_version')
    entries = listing['manifests']
    q.require(0 < len(entries) <= MANIFEST_LIMIT, 'manifests_count')
    q.require(len({e['capture']['path'] for e in entries}) == len(entries), 'manifests_duplicate')
    rows, info = [], []
    ledger = Counter(frames=0, framesWithoutInventory=0, ancestryResolved=0, ancestryUnresolved=0)
    ledger['ineligibleGroups'] = set()
    for entry in entries:
        q.require(set(entry) == {'artifact', 'capture'}, 'manifest_fields')
        checked(entry['artifact']); checked(entry['capture'])
        info.append(observations(entry, rows, ledger))
    report = summarize(info, rows, ledger, selected, settings)
    report.update(quotaFile=refs['quotas'], manifestList=refs['manifests'])
    q.save(OUT / 'benchmark_summary.json', report)
    q.save(OUT / 'artifact-receipt.json', dict(version='research-artifact-v1', outputs=[
        dict(path='benchmark_summary.json', sha256=q.digest(OUT / 'benchmark_summary.json'))]))
