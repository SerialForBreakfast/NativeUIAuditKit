"""REALAPP554 RA554-08: blinded human label review on a local page.

The page shows captured frames and SDK draft boxes only. It never reads replay results or model predictions.
Commands:
  prepare --sessions SESSION_JSON ... --out NEW_DIR
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
PAGE = Path(__file__).with_name('real_app_review554.html')


def prepare(sessions, out):
    """Write 1 case list and 1 draft for each distinct captured frame. Drafts come from SDK rectangles only."""
    out = Path(out); (out/'drafts').mkdir(parents=True, exist_ok=False); (out/'labels').mkdir()
    cases, seen = [], {}
    for path in sessions:
        session = q.load(path)
        for record in session['cases']:
            if record['status'] != 'captured':
                continue
            if record['sha256'] in seen:
                seen[record['sha256']]['duplicates'].append(record['id']); continue
            from PIL import Image
            with Image.open(record['image']) as image:
                width, height = image.size
            scale = width/1920
            objects = []
            for index, (sdk_id, bounds, _) in enumerate((record.get('sdkBefore') or {}).get('elements', [])):
                b = json.loads(bounds)
                box = [b['x']*scale, b['y']*scale, b['width']*scale, b['height']*scale]
                box[2] = min(box[2], width-box[0]); box[3] = min(box[3], height-box[1])
                if box[2] <= 0 or box[3] <= 0:
                    continue
                objects.append({'id': f'sdk-{index:02}', 'class': DRAFT_CLASS.get(sdk_id.split('.')[0]), 'box': [round(v, 1) for v in box],
                                'visibility': 'unknown', 'provenance': 'sdk-draft:'+sdk_id})
            case = dict(id=record['id'], app=session['bundle'], flow=record['flow'], image=record['image'], sha256=record['sha256'],
                        width=width, height=height, plannedFocus=None, expectedScreen=record.get('expectedScreen'), duplicates=[])
            seen[record['sha256']] = case; cases.append(case)
            q.save(out/'drafts'/f"{record['id']}.json", dict(imageSHA256=record['sha256'], complete=False, objects=objects,
                   focus=dict(state='unknown', box=None), review=dict(blinded=True, reviewer='', status='pending')))
    q.save(out/'cases.json', dict(version='realapp554-review-v1', sessions=[str(p) for p in sessions], classes=CLASSES, cases=cases,
                                  note='Blinded: no model predictions. SDK drafts can miss controls and can be misaligned.'))
    return cases


def check(label, case):
    """Apply the benchmark label rules. Raise ValueError with a reason."""
    q.require(set(label) == {'imageSHA256', 'complete', 'objects', 'focus', 'review'} and label['imageSHA256'] == case['sha256'], 'label_shape')
    q.require(type(label['complete']) is bool, 'completeness')
    ids = set()
    for obj in label['objects']:
        q.require(set(obj) <= {'id', 'class', 'box', 'visibility', 'provenance', 'flag'} and obj['id'] not in ids, 'object_shape')
        q.require(obj.get('flag') in (None, 'wrong-class', 'wrong-box', 'not-control', 'missing'), 'object_flag')
        ids.add(obj['id'])
        q.require(obj['class'] is None or obj['class'] in CLASSES, 'label_class')
        q.require(obj['visibility'] in VISIBILITY and isinstance(obj['provenance'], str) and obj['provenance'], 'object_fields')
        box(obj['box'], case)
    focus = label['focus']
    q.require(focus['state'] in FOCUS, 'focus_state')
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

    def cases(self):
        return {c['id']: c for c in q.load(self.root/'cases.json')['cases']}

    def current(self, case_id):
        saved = self.root/'labels'/f'{case_id}.json'
        return q.load(saved if saved.exists() else self.root/'drafts'/f'{case_id}.json')

    def do_GET(self):
        cases = self.cases()
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
            rows = [dict(c, image=None, status=self.current(i)['review']['status']) for i, c in cases.items()]
            return self.send(200, dict(classes=CLASSES, visibility=VISIBILITY, cases=rows))
        match = re.fullmatch(r'/(api/case|image)/([A-Za-z0-9._-]+)', self.path)
        if not match or match[2] not in cases:
            return self.send(404, dict(error='not_found'))
        if match[1] == 'image':
            path = Path(cases[match[2]]['image'])
            q.require(q.digest(path) == cases[match[2]]['sha256'], 'image_changed')
            return self.send(200, path.read_bytes(), 'image/png')
        return self.send(200, self.current(match[2]))

    def do_POST(self):
        cases = self.cases()
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
            check(label, cases[match[1]])
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
    s = sub.add_parser('serve'); s.add_argument('--dir', type=Path, required=True); s.add_argument('--port', type=int, default=8770)
    r = sub.add_parser('recheck-prepare'); r.add_argument('--dir', type=Path, required=True)
    a = sub.add_parser('recheck-apply'); a.add_argument('--dir', type=Path, required=True); a.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    if args.command == 'prepare':
        print(len(prepare(args.sessions, args.out)), 'cases')
    elif args.command == 'recheck-prepare':
        items = recheck_items(args.dir); print(len(items), 'items', dict(__import__('collections').Counter(i['kind'] for i in items)))
    elif args.command == 'recheck-apply':
        print(len(apply_recheck(args.dir, args.out)), 'changes')
    else:
        serve(args.dir, args.port)


if __name__ == '__main__':
    main()
