"""Review native focus without changing capture records or detector reference labels."""
import json
import math
import os
import re
import time
from http.server import ThreadingHTTPServer
from pathlib import Path

import real_app_review554 as core

PAGE = Path(__file__).with_suffix('.html')


def valid_box(b, c):
    return (isinstance(b, list) and len(b) == 4 and
            all(type(v) in (int, float) and math.isfinite(v) for v in b) and
            b[0] >= 0 and b[1] >= 0 and min(b[2:]) > 0 and
            b[0]+b[2] <= c['width'] and b[1]+b[3] <= c['height'])


def observed(root, c, selected):
    missing = dict(box=None, message='TTR did not capture verified focus for this frame.')
    s = [s for s in selected if s['sha256'] == c['sha256']]
    if len(s) != 1 or s[0].get('repeatSHA256') != c['sha256']:
        return missing
    path = (root/s[0]['nativeRecords']).resolve()
    if not path.is_relative_to(root) or not path.is_file():
        return missing
    data = json.loads(path.read_text())
    # SwiftUI global frames identify the rendered control body in this packet.
    # Keep the raw SDK frame available for comparison with its coordinate conversion.
    if all("nativeState" in data.get(phase, {}) for phase in ("before", "middle", "after")):
        states = []
        for phase in ("before", "middle", "after"):
            frame = data[phase]
            if (frame.get("readinessReasons") != [] or frame.get("truncated") is not False
                    or frame.get("nativeFocusKnown") is not True
                    or (frame.get("width"), frame.get("height")) != (c["width"], c["height"])):
                return missing
            owners = frame.get("owners", {})
            nodes = frame.get("nodes", [])
            if frame["nativeState"] == "known_no_focus" and not owners and not nodes:
                states.append(("no_focus", None, None))
                continue
            if frame["nativeState"] != "focused" or len(owners) != 1 or len(nodes) != 1:
                return missing
            name, body = next(iter(owners.items()))
            node = nodes[0]
            if (node.get("focused") is not True or node.get("accessibilityIdentifier") != name
                    or not valid_box(body, c)):
                return missing
            states.append(("focused", name, body))
        if not states[0] == states[1] == states[2]:
            return missing
        state, name, body = states[0]
        if state == "no_focus":
            return dict(state=state, box=None, message="TTR verified no focused control on this screen.")
        return dict(state=state, box=body, message=f"Focused control: {name} · SwiftUI control bounds")
    observations = []
    for phase in ('before', 'middle', 'after'):
        frame = data.get(phase, {})
        if (frame.get('nativeFocusKnown') is not True or
                (frame.get('width'), frame.get('height')) != (c['width'], c['height'])):
            return missing
        nodes = [n for n in frame['nodes'] if n.get('focused') is True]
        if len(nodes) != 1:
            return missing
        n = nodes[0]
        if n.get('hidden') is not False or n.get('alpha', 0) <= 0 or not valid_box(n.get('boundsPx'), c):
            return missing
        observations.append((n.get('index'), n.get('accessibilityIdentifier'), n['boundsPx']))
    if not observations[0] == observations[1] == observations[2]:
        return missing
    return dict(box=observations[0][2], message='TTR focus box · native control bounds')


class Handler(core.Handler):
    def record(self, c):
        p = self.root/'focus-reviews'/c['id']
        files = sorted(p.glob('*.json'))
        return json.loads(files[-1].read_text()) if files else None

    def do_GET(self):
        if self.path == '/':
            return self.send(200, PAGE.read_bytes(), 'text/html; charset=utf-8')
        if self.path != '/api/focus':
            return super().do_GET()
        selected = json.loads((self.root/'selected-captures.json').read_text())['cases']
        rows = []
        for c in self.cases().values():
            rows.append(dict(id=c['id'], app=c['app'], width=c['width'], height=c['height'],
                             sha256=c['sha256'], proposal=observed(self.root,c,selected), decision=self.record(c),
                             previous=self.current(c['id'])['review']['status']))
        self.send(200, rows)

    def do_POST(self):
        m = re.fullmatch(r'/api/focus/([\w.-]+)', self.path)
        if not m or self.headers.get('Origin') != f'http://{self.headers.get("Host")}':
            return self.send(403, dict(error='Unexpected review request'))
        c = self.cases().get(m[1])
        try:
            if c is None or int(self.headers['Content-Length']) > 4096:
                raise ValueError('Invalid case or request size')
            d = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
            if d.get('sha256') != c['sha256']:
                raise ValueError('Frame changed. Reload before saving.')
            proposal = observed(self.root,c,json.loads((self.root/'selected-captures.json').read_text())['cases'])
            action, b = d.get('action'), d.get('box')
            if action == 'validate' and proposal['box'] and b == proposal['box']:
                pass
            elif action == 'correct' and valid_box(b,c):
                pass
            elif action in ('flag','no_focus') and b is None:
                pass
            else:
                raise ValueError('Invalid focus decision')
            out = dict(case=c['id'],sha256=c['sha256'],action=action,box=b,ttrBox=proposal['box'],
                       scope='human-focus-review-only',timestamp=time.time())
            folder = self.root/'focus-reviews'/c['id']
            folder.mkdir(parents=True,exist_ok=True)
            key = str(time.time_ns())
            tmp = folder/(key+'.partial')
            tmp.write_text(json.dumps(out,indent=2))
            os.replace(tmp,folder/(key+'.json'))
            return self.send(200,out)
        except (KeyError, ValueError, TypeError, OSError) as e:
            return self.send(400,dict(error=str(e)))


def serve(root, port):
    Handler.root = root.resolve()
    assert Handler.root.is_relative_to(core.q.ROOT)
    ThreadingHTTPServer(('127.0.0.1',port),Handler).serve_forever()
