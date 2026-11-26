"""TRAIN666 B405-298: propose independent-layout IDs for captured AX drafts. The result is a proposal for Joe's review.

Rule (Research/ModelImprovementLoop/SKILL.md): frames of 1 screen (scroll, focus and repeat states) count once.
- 1 capture (1 screenID, all its sweep frames) is 1 screen.
- 2 screens of 1 app are 1 layout when their box geometry matches (similarity >= --same). Live content changes do not make a new layout.
- A layout that matches a screen already in the benchmark (--reference) is familiar and gives no new credit.
- Pairs with similarity in [--borderline, --same) need a human decision. The check does not merge or split them.
Similarity of 2 frames: boxes are normalized to the frame size; class is ignored (sources use different class sets).
Boxes match greedily at IoU >= 0.5; similarity = 2 * matches / (boxes in A + boxes in B). Screen similarity = best frame pair.
App data roles come from C1 (Tasks.md). Training apps get no benchmark credit unless Joe changes their role.
Usage: layout_independence666.py --drafts GLOB ... --reference GLOB_OR_MANIFEST ... --exclude CASE_ID ... --out NEW_DIR
"""
import argparse
import glob
import json
from collections import defaultdict
from pathlib import Path
import research_queue as q

ROLES = {  # C1 inventory, reports/work/TRAIN666/development-rescore/tranche.md (2026-11). Joe owns changes.
    'com.jordankoch.NewsTV': 'training',
    'com.geoffmyers.PhotoGuessingGame': 'training',
    'com.example.apple-samplecode.TVCatalog': 'training',
    'org.jellyfin.swiftfin': 'benchmark-candidate',
    'com.thatcube.Plozz': 'benchmark-candidate',
    'org.nuiak.rc561.strimr': 'benchmark-candidate',
}


def norm_boxes(objects, width, height):
    return [(o['box'][0]/width, o['box'][1]/height, o['box'][2]/width, o['box'][3]/height) for o in objects]


def iou(a, b):
    w = min(a[0]+a[2], b[0]+b[2]) - max(a[0], b[0]); h = min(a[1]+a[3], b[1]+b[3]) - max(a[1], b[1])
    if w <= 0 or h <= 0:
        return 0.0
    inter = w*h
    return inter / (a[2]*a[3] + b[2]*b[3] - inter)


def similarity(a, b):
    """Class-agnostic box agreement of 2 frames, 0..1."""
    if not a or not b:
        return 0.0
    pairs = sorted(((iou(x, y), i, j) for i, x in enumerate(a) for j, y in enumerate(b)), reverse=True)
    used_a, used_b, matches = set(), set(), 0
    for v, i, j in pairs:
        if v < 0.5:
            break
        if i not in used_a and j not in used_b:
            used_a.add(i); used_b.add(j); matches += 1
    return 2*matches / (len(a) + len(b))


def load_drafts(patterns, exclude):
    """Group draft frames by (app, screenID). Return screens and the frames left out with a reason."""
    screens, skipped = defaultdict(list), []
    for path in sorted({p for pattern in patterns for p in glob.glob(pattern, recursive=True)}):
        d = q.load(path); case = Path(path).name.removesuffix('.draft.json')
        if case in exclude or screen_key(d['screenID']) in exclude:
            skipped.append(dict(case=case, reason='excluded_by_capture_report')); continue
        if not d['objects']:
            skipped.append(dict(case=case, reason='no_objects')); continue
        frame = dict(case=case, path=path, sha256=d['imageSHA256'], focus=d['focus'].get('state'), objects=len(d['objects']),
                     boxes=norm_boxes(d['objects'], d['width'], d['height']))
        screens[(d['bundleIdentifier'], screen_key(d['screenID']))].append(frame)
    return screens, skipped


def screen_key(screen_id):
    """Drop the frame suffix (`-00`, `-01-down`): all frames of 1 capture are 1 screen."""
    parts = screen_id.split('-')
    while parts and (parts[-1].isdigit() and len(parts[-1]) == 2 or parts[-1] in ('down', 'up', 'left', 'right')):
        parts.pop()
    return '-'.join(parts)


def load_reference(patterns):
    """Prior benchmark frames by app: AX drafts (`*.draft.json`) or TVBench manifests with label files."""
    ref = defaultdict(list)
    for pattern in patterns:
        for path in sorted(glob.glob(pattern, recursive=True)):
            d = q.load(path)
            if 'cases' in d and 'version' in d and str(d['version']).startswith('tvbench'):
                for c in d['cases']:
                    labels = q.load(q.ROOT/c['labels']['path'])
                    ref[c['app']].append(dict(id=c['id'], source=path, boxes=norm_boxes(labels['objects'], c['width'], c['height'])))
            elif 'objects' in d and 'bundleIdentifier' in d:
                ref[d['bundleIdentifier']].append(dict(id=Path(path).name.removesuffix('.draft.json'), source=path,
                                                       boxes=norm_boxes(d['objects'], d['width'], d['height'])))
    return ref


def screen_similarity(a, b):
    return max(((similarity(x['boxes'], y['boxes']), x['case'], y.get('case', y.get('id'))) for x in a for y in b), default=(0.0, None, None))


def propose(screens, reference, same=0.6, borderline=0.4):
    by_app = defaultdict(list)
    for (app, key), frames in screens.items():
        by_app[app].append((key, frames))
    layouts, borderline_pairs = [], []
    for app, items in sorted(by_app.items()):
        parent = list(range(len(items)))

        def find(i):
            while parent[i] != i:
                parent[i] = parent[parent[i]]; i = parent[i]
            return i
        for i in range(len(items)):
            for j in range(i+1, len(items)):
                s, fa, fb = screen_similarity(items[i][1], items[j][1])
                if s >= same:
                    parent[find(i)] = find(j)
                elif s >= borderline:
                    borderline_pairs.append(dict(app=app, a=items[i][0], b=items[j][0], similarity=round(s, 3), frames=[fa, fb]))
        groups = defaultdict(list)
        for i, item in enumerate(items):
            groups[find(i)].append(item)
        for members in groups.values():
            members.sort(key=lambda m: m[0])
            frames = [f for _, fs in members for f in fs]
            rep = max(frames, key=lambda f: (f['focus'] == 'focused', f['case'].endswith('-00'), f['objects']))
            prior = max(((similarity(f['boxes'], r['boxes']), r['id'], r['source']) for f in frames for r in reference.get(app, [])),
                        default=(0.0, None, None))
            familiar = prior[0] >= same
            role = ROLES.get(app, 'unassigned')
            layouts.append(dict(
                layoutId=f"{app.rsplit('.', 1)[-1].lower()}:{members[0][0]}", app=app, role=role,
                screens=[m[0] for m in members], frames=[f['case'] for f in frames], representative=rep['case'],
                representativeFocus=rep['focus'], priorMatch=dict(similarity=round(prior[0], 3), id=prior[1], source=prior[2]),
                familiar=familiar, priorBorderline=borderline <= prior[0] < same,
                credit='none_familiar' if familiar else ('benchmark_candidate' if role == 'benchmark-candidate' else f'none_{role}')))
    return layouts, borderline_pairs


def summarize(layouts, borderline_pairs):
    """Counts for the TRAIN666 rule: at least 30 credited layouts in at least 5 apps."""
    new = [l for l in layouts if not l['familiar']]
    credit = [l for l in new if l['credit'] == 'benchmark_candidate']
    apps = defaultdict(lambda: dict(layouts=0, new=0, credit=0))
    for l in layouts:
        a = apps[l['app']]; a['layouts'] += 1; a['new'] += not l['familiar']; a['credit'] += l['credit'] == 'benchmark_candidate'
    return dict(layouts=len(layouts), newLayouts=len(new), creditCandidates=len(credit),
                appsWithCredit=sum(v['credit'] > 0 for v in apps.values()), byApp=dict(apps), borderlinePairs=len(borderline_pairs), priorBorderline=sum(l['priorBorderline'] for l in layouts),
                thisRoundAloneMeets30In5Apps=len(credit) >= 30 and sum(v['credit'] > 0 for v in apps.values()) >= 5,
                note='Proposal only. Joe reviews layout groups, borderline pairs and app roles before any benchmark credit.')


def write_page(out):
    """Static decision page (layout-review.html) next to layouts.json. Images are linked by relative path; nothing is scored."""
    import html
    import os
    doc = q.load(out/'layouts.json'); frames = {}
    for pattern in doc['drafts']:
        for path in glob.glob(pattern, recursive=True):
            frames[Path(path).name.removesuffix('.draft.json')] = Path(path).with_name(Path(path).name.removesuffix('.draft.json') + '.png')

    def img(case, label=''):
        rel = os.path.relpath(frames[case].resolve(), out.resolve())
        return f'<figure><img loading="lazy" src="{html.escape(rel)}" alt=""><figcaption>{html.escape(label or case)}</figcaption></figure>'
    s = doc['summary']; rows = []
    for l in doc['layouts']:
        flag = ' <b>check prior match</b>' if l.get('priorBorderline') else ''
        rows.append(f"<section id='{html.escape(l['layoutId'])}'><h3>{html.escape(l['layoutId'])}</h3>"
                    f"<p>{html.escape(l['role'])} · credit: {html.escape(l['credit'])} · prior similarity {l['priorMatch']['similarity']}"
                    f" ({html.escape(str(l['priorMatch']['id']))}){flag} · {len(l['screens'])} screens, {len(l['frames'])} frames</p>"
                    f"<div class='row'>{''.join(img(f) for f in l['frames'])}</div></section>")
    pairs = [f"<section><h3>{html.escape(p['app'])} · similarity {p['similarity']}</h3><p>Same layout or different?</p>"
             f"<div class='row'>{img(p['frames'][0], p['a'])}{img(p['frames'][1], p['b'])}</div></section>" for p in doc['borderlinePairs']]
    page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Layout independence review</title><style>
:root{{--bg:#fff;--fg:#1d1d1f;--muted:#6e6e73;--line:#d2d2d7}}
@media (prefers-color-scheme: dark){{:root{{--bg:#1c1c1e;--fg:#f5f5f7;--muted:#a1a1a6;--line:#3a3a3c}}}}
body{{background:var(--bg);color:var(--fg);font:15px/1.45 -apple-system,system-ui,sans-serif;margin:0 auto;max-width:1400px;padding:16px}}
p,figcaption{{color:var(--muted)}} section{{border-top:1px solid var(--line);padding:8px 0}}
.row{{display:flex;gap:8px;overflow-x:auto}} figure{{margin:0;flex:0 0 320px}} img{{width:320px;border:1px solid var(--line)}}
figcaption{{font-size:12px;word-break:break-all}}</style></head><body>
<h1>Layout independence review — proposal</h1>
<p>{s['layouts']} layouts, {s['newLayouts']} not in the benchmark, {s['creditCandidates']} credit candidates in {s['appsWithCredit']} apps.
{s['borderlinePairs']} borderline pairs. Nothing here gives credit until Joe decides. Thresholds: same ≥ {doc['thresholds']['same']}, borderline ≥ {doc['thresholds']['borderline']}.</p>
<h2>Decisions</h2><ol><li>Confirm or change each layout group below (frames in 1 group count once).</li>
<li>Decide each borderline pair.</li><li>App roles: NewsTV, TVCatalog and Photo Guessing Game are training apps (no credit). WeatherStar has no role.</li></ol>
<h2>Layout groups</h2>{''.join(rows)}<h2>Borderline pairs</h2>{''.join(pairs)}</body></html>"""
    (out/'layout-review.html').write_text(page)
    return out/'layout-review.html'


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--drafts', nargs='+', required=True); parser.add_argument('--reference', nargs='*', default=[])
    parser.add_argument('--exclude', nargs='*', default=[]); parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--same', type=float, default=0.6); parser.add_argument('--borderline', type=float, default=0.4)
    parser.add_argument('--page', action='store_true', help='Only write layout-review.html for an existing --out')
    args = parser.parse_args()
    if args.page:
        print(write_page(args.out)); return
    q.require(not args.out.exists(), 'layout_out_exists')
    screens, skipped = load_drafts(args.drafts, set(args.exclude))
    layouts, pairs = propose(screens, load_reference(args.reference), args.same, args.borderline)
    summary = summarize(layouts, pairs)
    args.out.mkdir(parents=True)
    q.save(args.out/'layouts.json', dict(version='layout-independence666-v1', thresholds=dict(same=args.same, borderline=args.borderline),
                                         drafts=args.drafts, reference=args.reference, exclude=args.exclude, summary=summary,
                                         layouts=layouts, borderlinePairs=pairs, skipped=skipped))
    q.save(args.out/'layout-ids.proposed.json', {f: l['layoutId'] for l in layouts for f in l['frames']})
    write_page(args.out)
    print(json.dumps(summary, indent=1))


if __name__ == '__main__':
    main()
