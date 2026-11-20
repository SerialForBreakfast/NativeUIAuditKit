"""REALAPP554 RA554-08: blinded human label review on a local page.

The page shows captured frames and SDK draft boxes only. It never reads replay results or model predictions.
Commands:
  prepare --sessions SESSION_JSON ... --out NEW_DIR
  prepare-ax --drafts SCREEN.draft.json ... --out NEW_DIR  (10 contract classes)
  serve --dir DIR [--port 8770]          (review page at /, recheck page at /recheck)
  recheck-prepare --dir DIR              (targeted questions about the first review)
  recheck-apply --dir DIR --out NEW_DIR  (label version 2; first labels stay unchanged)
Saved labels use the `real_app_benchmark543.validate_labels` format. Each save keeps the earlier version.
"""
import argparse
import json
import re
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import research_queue as q

MANIFEST = q.ROOT/'NativeUIAuditKitModels/Sources/NativeUIAuditKitModels/Resources/model_manifest_tvos_v1.json'
CLASSES = [m['label'] for m in q.load(MANIFEST)['tensorChannelMapping'] if m['type'] == 'taxonomyClass']
VISIBILITY = ('visible', 'clipped', 'occluded', 'unknown')
FOCUS = ('focused', 'no_focus', 'unknown')
DRAFT_CLASS = {'article': 'collectionItem', 'category': 'secondaryButton', 'main-tab': 'secondaryButton'}  # Fixture tab labels use secondaryButton.
EXPLICIT_CLASS_MAP = {
    'button': 'secondaryButton',
    'primaryButton': 'primaryButton',
    'secondaryButton': 'secondaryButton',
    'destructiveButton': 'destructiveButton',
    'cancelAction': 'cancelAction',
    'menuButton': 'menuButton',
    'link': 'link',
    'disclosureGroup': 'disclosureGroup',
    'cell': 'collectionItem',
    'collectionItem': 'collectionItem',
    'listRow': 'listRow',
    'bar': 'tabBar',
    'tabBar': 'tabBar',
    'navigationBar': 'navigationBar',
    'toolbar': 'toolbar',
    'sidebar': 'sidebar',
    'textField': 'textField',
    'searchField': 'searchField',
    'toggle': 'toggle',
    'adjustable': 'slider',
    'slider': 'slider',
    'segmentedControl': 'segmentedControl',
    'pageControl': 'pageControl',
    'picture': 'imageView',
    'imageView': 'imageView',
    'dialog': 'sheet',
    'sheet': 'sheet',
    'alert': 'alert',
    'indicator': 'progressView',
}
AX_TRAIT_BUTTON = 1 << 0
AX_TRAIT_STATIC_TEXT = 1 << 6
AX_TRAIT_SEARCH_FIELD = 1 << 10
PAGE = Path(__file__).with_name('real_app_review554.html')


def sdk_to_pixel_box(bounds, capture_geometry, img_w, img_h):
    """Convert SDK window/screen bounds to clipped top-left image pixels via captureGeometry."""
    b = json.loads(bounds) if isinstance(bounds, str) else bounds
    if isinstance(b, (list, tuple)) and len(b) == 4:
        x, y, w, h = [float(v) for v in b]
    else:
        x, y, w, h = float(b['x']), float(b['y']), float(b['width']), float(b['height'])

    if capture_geometry:
        sb = capture_geometry.get('screenBounds') or {}
        pts_w = float(sb.get('width') or 0.0)
        pts_h = float(sb.get('height') or 0.0)
        mat = capture_geometry.get('toScreenPoints')
        if isinstance(mat, (list, tuple)) and len(mat) == 6:
            a, b_m, c, d, tx, ty = [float(v) for v in mat]
            corners = [(x, y), (x + w, y), (x, y + h), (x + w, y + h)]
            xs = [a * cx + c * cy + tx for cx, cy in corners]
            ys = [b_m * cx + d * cy + ty for cx, cy in corners]
            x, y, w, h = min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys)
        sx = (img_w / pts_w) if pts_w > 0 else float(capture_geometry.get('displayScale') or (img_w / 1920.0))
        sy = (img_h / pts_h) if pts_h > 0 else float(capture_geometry.get('displayScale') or (img_h / 1080.0))
    else:
        sx = img_w / 1920.0
        sy = img_h / 1080.0

    px1 = max(0.0, x * sx)
    py1 = max(0.0, y * sy)
    px2 = min(float(img_w), (x + w) * sx)
    py2 = min(float(img_h), (y + h) * sy)
    if px2 - px1 <= 0.5 or py2 - py1 <= 0.5:
        return None
    return [round(px1, 1), round(py1, 1), round(px2 - px1, 1), round(py2 - py1, 1)]


def _map_sdk_class(role, sdk_id=''):
    if role in CLASSES:
        return role
    if role in EXPLICIT_CLASS_MAP:
        return EXPLICIT_CLASS_MAP[role]
    return DRAFT_CLASS.get((sdk_id or '').split('.')[0])


def prepare(sessions, out):
    """Write 1 case list, rich metadata sidecars, and SDK-only drafts (quarantining transitional frames)."""
    out = Path(out); (out/'drafts').mkdir(parents=True, exist_ok=False); (out/'labels').mkdir(); (out/'metadata').mkdir()
    cases, seen, skipped_transitional = [], {}, []
    for path in sessions:
        session = q.load(path)
        for record in session['cases']:
            if record.get('transitional') or record['status'] == 'transitional':
                skipped_transitional.append(record['id'])
                continue
            if record['status'] != 'captured':
                continue
            if record['sha256'] in seen:
                seen[record['sha256']]['duplicates'].append(record['id']); continue
            from PIL import Image
            with Image.open(record['image']) as image:
                width, height = image.size
            sdk_before = record.get('sdkBefore') or {}
            geom = sdk_before.get('captureGeometry')
            objects = []
            id_to_box = {}
            exceptions = []
            if sdk_before.get('truncated'):
                exceptions.append('truncated_tree')

            rich_els = sdk_before.get('richElements')
            if rich_els:
                for index, el in enumerate(rich_els):
                    if el.get('hidden'):
                        continue
                    eid = el.get('id') or f'sdk-{index:02d}'
                    cls = _map_sdk_class(el.get('declaredTaxonomy') or el.get('role'), eid)
                    if (el.get('declaredTaxonomy') or el.get('role')) in ('label', 'label_view', 'staticText', 'text'):
                        continue
                    raw_bounds = el.get('visibleBounds') or el.get('clippedBounds') or el.get('bounds')
                    if not raw_bounds:
                        continue
                    box = sdk_to_pixel_box(raw_bounds, geom, width, height)
                    if not box:
                        continue
                    id_to_box[eid] = box
                    objects.append({
                        'id': f'sdk-{index:02d}',
                        'class': cls,
                        'box': box,
                        'visibility': 'visible',
                        'provenance': f"sdk-registered:{el.get('role') or 'unknown'}:{eid}",
                    })
            else:
                for index, (sdk_id, bounds, _) in enumerate(sdk_before.get('elements', [])):
                    box = sdk_to_pixel_box(bounds, geom, width, height)
                    if not box:
                        continue
                    id_to_box[sdk_id] = box
                    objects.append({
                        'id': f'sdk-{index:02d}',
                        'class': _map_sdk_class(None, sdk_id),
                        'box': box,
                        'visibility': 'unknown',
                        'provenance': 'sdk-draft:' + sdk_id,
                    })

            ax_page = sdk_before.get('accessibilityDrafts') or {}
            if ax_page.get('truncated'):
                exceptions.append('ax_truncated')
            ax_added = 0
            for ax_idx, ax in enumerate(ax_page.get('elements') or []):
                traits = int(ax.get('traits') or 0)
                if (traits & AX_TRAIT_STATIC_TEXT) and not (traits & (AX_TRAIT_BUTTON | AX_TRAIT_SEARCH_FIELD)):
                    continue
                box = sdk_to_pixel_box(ax['bounds'], geom, width, height)
                if not box:
                    continue
                cls = 'searchField' if (traits & AX_TRAIT_SEARCH_FIELD) else ('secondaryButton' if (traits & AX_TRAIT_BUTTON) else None)
                objects.append({
                    'id': f'ax-{ax_idx:02d}',
                    'class': cls,
                    'box': box,
                    'visibility': 'visible',
                    'provenance': f"sdk-ax-draft:{ax.get('draftID', ax_idx)}",
                })
                ax_added += 1
            if ax_added:
                exceptions.append('unregistered_ax_drafts')

            focus_doc = dict(state='unknown', box=None)
            if record.get('focusKnown') or sdk_before.get('focusKnown'):
                fid = record.get('focusID') or sdk_before.get('focusID')
                if fid and fid in id_to_box:
                    focus_doc = dict(state='focused', box=id_to_box[fid])
                elif fid is None:
                    focus_doc = dict(state='no_focus', box=None)
                else:
                    exceptions.append('focus_outside_registered_box')
            else:
                exceptions.append('unknown_focus')

            q.save(out/'metadata'/f"{record['id']}.json", dict(
                id=record['id'], screenshotSHA256=record['sha256'], generation=sdk_before.get('generation'),
                captureGeometry=geom, focusKnown=bool(record.get('focusKnown') or sdk_before.get('focusKnown')),
                focusID=record.get('focusID') or sdk_before.get('focusID'),
                exceptionReasons=exceptions, richElements=rich_els or [],
            ))
            case = dict(
                id=record['id'], app=session['bundle'], flow=record['flow'], image=record['image'], sha256=record['sha256'],
                width=width, height=height, plannedFocus=None, expectedScreen=record.get('expectedScreen'),
                duplicates=[], exceptionReasons=exceptions, needsReview=bool(exceptions),
            )
            seen[record['sha256']] = case; cases.append(case)
            q.save(out/'drafts'/f"{record['id']}.json", dict(
                imageSHA256=record['sha256'], complete=False, objects=objects,
                focus=focus_doc, review=dict(blinded=True, reviewer='', status='pending'),
            ))
    cases.sort(key=lambda c: (0 if c.get('needsReview') else 1, c['id']))
    q.save(out/'cases.json', dict(
        version='realapp554-review-v2', sessions=[str(p) for p in sessions], classes=CLASSES, cases=cases,
        skippedTransitional=skipped_transitional,
        note='Blinded SDK/AX drafts sorted exceptions-first. No model predictions.',
    ))
    return cases


def prepare_ax(drafts, out):
    """Make a contract-class review pack from passive AX drafts. Keep source drafts unchanged."""
    import framework_projection604 as fp
    from PIL import Image
    out = Path(out)
    classes = fp.tvos_classes()
    rows = []
    for path in map(Path, drafts):
        draft = q.load(path)
        q.require(draft.get('version') == 'tvbench-ax-draft-v1', 'ax_draft_version')
        q.require(draft.get('classes') == classes, 'ax_draft_classes')
        q.require(path.name.endswith('.draft.json'), 'ax_draft_filename')
        image = path.with_name(path.name.removesuffix('.draft.json') + '.png').resolve()
        q.require(q.digest(image) == draft['imageSHA256'], 'image_changed')
        with Image.open(image) as im:
            q.require(list(im.size) == [draft['width'], draft['height']], 'image_dimensions')
        case_id = path.name.removesuffix('.draft.json')
        q.require(re.fullmatch(r'[A-Za-z0-9._-]+', case_id), 'case_id')
        case = dict(id=case_id, app=draft['bundleIdentifier'], flow=draft['screenID'], screenID=draft['screenID'], bundleIdentifier=draft['bundleIdentifier'], image=str(image),
                    sha256=draft['imageSHA256'], width=draft['width'], height=draft['height'],
                    duplicates=[], needsReview=True, exceptionReasons=['ax_draft_requires_review'])
        objects = [dict(id=o['id'], **{'class': o['class']}, box=o['box'], visibility=o['visibility'],
                        provenance='ax-draft:' + str(path.resolve()), roleSource=o.get('roleSource', 'ax_element_type'))
                   for o in draft['objects']]
        focus = draft['focus']
        state = focus['state']
        q.require(state in ('focused', 'known_no_focus', 'unknown'), 'focus_state')
        label = dict(imageSHA256=draft['imageSHA256'], complete=False, objects=objects,
                     focus=dict(state=state, box=focus.get('box') if state == 'focused' else None),
                     review=dict(blinded=True, reviewer='', status='pending'))
        check(label, case, classes, ('focused', 'known_no_focus', 'unknown'))
        rows.append((case, label, draft))
    q.require(len({c['id'] for c, _, _ in rows}) == len(rows), 'duplicate_case_id')
    out.mkdir(parents=True, exist_ok=False)
    for folder in ('drafts', 'labels', 'metadata'):
        (out/folder).mkdir()
    for case, label, draft in rows:
        q.save(out/'drafts'/f"{case['id']}.json", label)
        q.save(out/'metadata'/f"{case['id']}.json", draft)
    q.save(out/'cases.json', dict(version='tvbench-ax-review-v1', labelMode='contract', classes=classes,
                                 focusStates=['focused', 'known_no_focus', 'unknown'], cases=[c for c, _, _ in rows],
                                 note='Passive AX drafts. Human review is required. No model predictions.'))
    return [c for c, _, _ in rows]


def check(label, case, classes=None, focus_states=None):
    """Apply the benchmark label rules. Raise ValueError with a reason."""
    q.require(set(label) == {'imageSHA256', 'complete', 'objects', 'focus', 'review'} and label['imageSHA256'] == case['sha256'], 'label_shape')
    q.require(type(label['complete']) is bool, 'completeness')
    classes = CLASSES if classes is None else classes
    focus_states = FOCUS if focus_states is None else focus_states
    ids = set()
    for obj in label['objects']:
        q.require(set(obj) <= {'id', 'class', 'box', 'visibility', 'provenance', 'flag', 'roleSource'} and obj['id'] not in ids, 'object_shape')
        q.require(obj.get('flag') in (None, 'wrong-class', 'wrong-box', 'not-control', 'missing'), 'object_flag')
        ids.add(obj['id'])
        q.require(obj['class'] is None or obj['class'] in classes, 'label_class')
        q.require(obj['visibility'] in VISIBILITY and isinstance(obj['provenance'], str) and obj['provenance'], 'object_fields')
        box(obj['box'], case)
    focus = label['focus']
    q.require(focus['state'] in focus_states, 'focus_state')
    if focus['state'] == 'focused':
        box(focus['box'], case)
    else:
        q.require(focus.get('box') is None, 'focus_box')
    review = label['review']
    q.require(review['blinded'] is True and review['status'] in ('pending', 'accepted'), 'review_fields')
    if review['status'] == 'accepted':
        q.require(isinstance(review['reviewer'], str) and review['reviewer'].strip(), 'reviewer')


def box(value, case):
    q.require(isinstance(value, list) and len(value) == 4 and all(isinstance(v, (int, float)) for v in value), 'invalid_box')
    x, y, w, h = value
    q.require(x >= 0 and y >= 0 and w > 0 and h > 0 and x+w <= case['width']+0.01 and y+h <= case['height']+0.01, 'box_out_of_frame')


RECHECK_PAGE = Path(__file__).with_name('real_app_recheck554.html')
EDGE = 8  # Pixels. A box this close to a frame edge can be clipped.
ANSWERS = {'complete': ('complete', 'missing'), 'clip': ('done',), 'nofocus': ('no_focus', 'unknown', 'focused'),
           'focusbox': ('correct', 'unknown', 'replace', 'no_focus'), 'extra': ('keep', 'remove')}


def recheck_items(root):
    """Targeted questions for the first review. Each item shows reviewed boxes only, never model output."""
    root = Path(root); items = []
    q.require(q.load(root/'cases.json').get('labelMode') != 'contract', 'contract_recheck_unsupported')
    for case in q.load(root/'cases.json')['cases']:
        label = q.load(root/'labels'/f"{case['id']}.json")
        newstv = case['app'].endswith('NewsTV')
        add = lambda kind, prompt, **extra: items.append(dict(id=f"{case['id']}--{kind}", case=case['id'], kind=kind, prompt=prompt, **extra))
        if newstv:
            add('complete', 'Does every visible control have a box? Count tabs, buttons, cards, and rows. Ignore plain text.')
            edge = [o['id'] for o in label['objects'] if o['box'][0] <= EDGE or o['box'][1] <= EDGE or
                    o['box'][0]+o['box'][2] >= case['width']-EDGE or o['box'][1]+o['box'][3] >= case['height']-EDGE]
            if edge:
                add('clip', 'Click each highlighted box whose control is cut off by the screen edge or by other content.', objects=edge)
        focus = label['focus']['state']
        if focus == 'focused':
            add('focusbox', 'Is the green box exactly the control that shows the focus effect?')
        else:
            add('nofocus', f"First review: {focus.replace('_', ' ')}. Does any control show a visible focus effect (lift, glow, scale, or highlight)?")
        for o in label['objects']:
            if o.get('flag') == 'missing' and (label['focus']['box'] is None or o['box'] != label['focus']['box']):
                add('extra', f"You drew this extra box as {o['class'] or 'unclassified'}. Is it a real control with a correct box?", objects=[o['id']])
    (root/'recheck').mkdir(exist_ok=True)
    q.save(root/'recheck/items.json', dict(version='realapp554-recheck-v1', items=items), replace=True)
    return items


def check_answer(item, answer, case):
    q.require(set(answer) <= {'result', 'boxes', 'clipped', 'box', 'reviewer'} and answer.get('result') in ANSWERS[item['kind']], 'answer_shape')
    q.require(isinstance(answer.get('reviewer'), str) and answer['reviewer'].strip(), 'reviewer')
    for added in answer.get('boxes', []):
        q.require(set(added) == {'class', 'box'} and (added['class'] is None or added['class'] in CLASSES), 'added_box')
        box(added['box'], case)
    q.require(set(answer.get('clipped', [])) <= set(item.get('objects', [])), 'clipped_objects')
    if answer['result'] in ('replace', 'focused'):
        box(answer.get('box'), case)


def apply_recheck(root, out):
    """Write a second label version from the first labels and the recheck answers. The first labels stay unchanged."""
    root, out = Path(root), Path(out); out.mkdir(parents=True, exist_ok=False)
    items = q.load(root/'recheck/items.json')['items']
    answers = {i['id']: q.load(root/'recheck/answers'/f"{i['id']}.json") for i in items if (root/'recheck/answers'/f"{i['id']}.json").exists()}
    missing = [i['id'] for i in items if i['id'] not in answers]
    q.require(not missing, 'recheck_unanswered:'+','.join(missing[:5]))
    changes = []
    for case in q.load(root/'cases.json')['cases']:
        label = q.load(root/'labels'/f"{case['id']}.json")
        for item in (i for i in items if i['case'] == case['id']):
            a = answers[item['id']]; kind = item['kind']
            if kind == 'complete':
                label['complete'] = a['result'] == 'complete'
                for n, added in enumerate(a.get('boxes', [])):
                    label['objects'].append({'id': f'recheck-{n:02}', 'class': added['class'], 'box': added['box'], 'visibility': 'visible',
                                             'provenance': 'reviewer:recheck-missing', 'flag': 'missing'})
            elif kind == 'clip':
                for o in label['objects']:
                    if o['id'] in a.get('clipped', []):
                        o['visibility'] = 'clipped'
                    elif o['id'] in item['objects'] and not o.get('flag'):
                        o['visibility'] = 'visible'
            elif kind in ('focusbox', 'nofocus'):
                if a['result'] in ('replace', 'focused'):
                    label['focus'] = dict(state='focused', box=a['box'])
                elif a['result'] in ('unknown', 'no_focus'):
                    label['focus'] = dict(state=a['result'], box=None)
            elif kind == 'extra' and a['result'] == 'remove':
                label['objects'] = [o for o in label['objects'] if o['id'] not in item['objects']]
            changes.append(dict(item=item['id'], result=a['result']))
        label['review'] = dict(label['review'], recheck='realapp554-recheck-v1')
        check(label, case)
        q.save(out/f"{case['id']}.json", label)
    q.save(out/'recheck-receipt.json', dict(version='realapp554-recheck-apply-v1', items=len(items), changes=changes,
                                            source=str(root/'labels'), note='First labels are unchanged. This folder is label version 2.'))
    return changes


class Handler(BaseHTTPRequestHandler):
    root = None

    def log_message(self, *args):
        pass

    def send(self, code, body, kind='application/json'):
        data = body if isinstance(body, bytes) else json.dumps(body).encode()
        self.send_response(code); self.send_header('Content-Type', kind); self.send_header('Cache-Control', 'no-store')
        self.send_header('Content-Length', str(len(data))); self.end_headers(); self.wfile.write(data)

    def policy(self):
        doc = q.load(self.root/'cases.json')
        if doc.get('labelMode') == 'contract':
            import framework_projection604 as fp
            q.require(doc.get('classes') == fp.tvos_classes(), 'review_contract_classes')
            return doc['classes'], ('focused', 'known_no_focus', 'unknown')
        return CLASSES, FOCUS

    def cases(self):
        return {c['id']: c for c in q.load(self.root/'cases.json')['cases']}

    def current(self, case_id):
        saved = self.root/'labels'/f'{case_id}.json'
        return q.load(saved if saved.exists() else self.root/'drafts'/f'{case_id}.json')

    def hints(self, case_id):
        hint_path = self.root/'hints'/f'{case_id}.json'
        return q.load(hint_path) if hint_path.is_file() else dict(focusCandidates=[])

    def do_GET(self):
        cases = self.cases()
        classes, focus_states = self.policy()
        if self.path == '/':
            return self.send(200, PAGE.read_bytes(), 'text/html; charset=utf-8')
        if self.path == '/recheck':
            return self.send(200, RECHECK_PAGE.read_bytes(), 'text/html; charset=utf-8')
        if self.path == '/api/recheck':
            items = q.load(self.root/'recheck/items.json')['items']
            answers = self.root/'recheck/answers'
            return self.send(200, dict(classes=CLASSES, items=[dict(i, answered=(answers/f"{i['id']}.json").exists(),
                answer=q.load(answers/f"{i['id']}.json") if (answers/f"{i['id']}.json").exists() else None) for i in items],
                cases={k: dict(v, image=None) for k, v in cases.items()}))
        if self.path == '/api/cases':
            rows = []
            for i, c in cases.items():
                cur = self.current(i)
                rows.append(dict(c, image=None, status=cur['review']['status'],
                                 draftCount=len(cur.get('objects', [])),
                                 focusState=cur.get('focus', {}).get('state', 'unknown')))
            return self.send(200, dict(classes=classes, focusStates=focus_states, visibility=VISIBILITY, cases=rows))
        match = re.fullmatch(r'/(api/case|api/hints|image)/([A-Za-z0-9._-]+)', self.path)
        if not match or match[2] not in cases:
            return self.send(404, dict(error='not_found'))
        if match[1] == 'image':
            path = Path(cases[match[2]]['image'])
            q.require(q.digest(path) == cases[match[2]]['sha256'], 'image_changed')
            return self.send(200, path.read_bytes(), 'image/png')
        if match[1] == 'api/hints':
            return self.send(200, self.hints(match[2]))
        source_path = self.root/'metadata'/f'{match[2]}.json'
        source = q.load(source_path) if source_path.is_file() and 'known_no_focus' in focus_states else None
        return self.send(200, dict(self.current(match[2]), hints=self.hints(match[2]), source=source))

    def do_POST(self):
        cases = self.cases()
        classes, focus_states = self.policy()
        if self.headers.get('Origin') not in (None, *(f'http://{h}:{self.server.server_port}' for h in ('127.0.0.1', 'localhost'))):
            return self.send(404, dict(error='not_found'))
        recheck = re.fullmatch(r'/api/recheck/([A-Za-z0-9._-]+)', self.path)
        if recheck:
            items = {i['id']: i for i in q.load(self.root/'recheck/items.json')['items']}
            if recheck[1] not in items:
                return self.send(404, dict(error='not_found'))
            item = items[recheck[1]]
            try:
                answer = json.loads(self.rfile.read(min(int(self.headers.get('Content-Length', 0)), 200_000)))
                check_answer(item, answer, cases[item['case']])
            except (ValueError, KeyError, TypeError) as error:
                return self.send(400, dict(error=str(error)))
            target = self.root/'recheck/answers'/f'{recheck[1]}.json'; target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists():  # Keep every earlier answer.
                target.rename(target.with_name(f'{recheck[1]}.{time.monotonic_ns()}.old'))
            q.save(target, dict(answer, answeredAt=time.time()))
            return self.send(200, dict(saved=True))
        match = re.fullmatch(r'/api/case/([A-Za-z0-9._-]+)', self.path)
        if not match or match[1] not in cases:
            return self.send(404, dict(error='not_found'))
        try:
            label = json.loads(self.rfile.read(min(int(self.headers.get('Content-Length', 0)), 2_000_000)))
            check(label, cases[match[1]], classes, focus_states)
        except (ValueError, KeyError, TypeError) as error:
            return self.send(400, dict(error=str(error)))
        target = self.root/'labels'/f'{match[1]}.json'
        if target.exists():  # Keep every earlier version.
            target.rename(target.with_name(f'{match[1]}.{time.strftime("%Y%m%dT%H%M%S")}.{time.monotonic_ns()}.json'))
        q.save(target, label)
        return self.send(200, dict(saved=True, status=label['review']['status']))


def serve(root, port):
    Handler.root = Path(root).resolve()
    q.require(Handler.root.is_relative_to(q.ROOT), 'review_scope')
    server = ThreadingHTTPServer(('127.0.0.1', port), Handler)
    print(f'Review page: http://127.0.0.1:{port}/', flush=True)
    server.serve_forever()


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('prepare'); p.add_argument('--sessions', type=Path, nargs='+', required=True); p.add_argument('--out', type=Path, required=True)
    ax = sub.add_parser('prepare-ax'); ax.add_argument('--drafts', type=Path, nargs='+', required=True); ax.add_argument('--out', type=Path, required=True)
    s = sub.add_parser('serve'); s.add_argument('--dir', type=Path, required=True); s.add_argument('--port', type=int, default=8770)
    r = sub.add_parser('recheck-prepare'); r.add_argument('--dir', type=Path, required=True)
    a = sub.add_parser('recheck-apply'); a.add_argument('--dir', type=Path, required=True); a.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    if args.command == 'prepare':
        print(len(prepare(args.sessions, args.out)), 'cases')
    elif args.command == 'prepare-ax':
        print(len(prepare_ax(args.drafts, args.out)), 'cases')
    elif args.command == 'recheck-prepare':
        items = recheck_items(args.dir); print(len(items), 'items', dict(__import__('collections').Counter(i['kind'] for i in items)))
    elif args.command == 'recheck-apply':
        print(len(apply_recheck(args.dir, args.out)), 'changes')
    else:
        serve(args.dir, args.port)


if __name__ == '__main__':
    main()
