"""RESET604 T2.1: generate varied TTR Fixture recipes for local capture.

Two sources of variation:
1. Plain archetypes (no `appearance`): archetype, element count, theme, density, seed. Counts stay small, because controls that overflow the screen fail `sceneNotSettled`.
2. Proven canvas recipes from earlier NUIAK captures (FOCUS556, CAPTURE553, FOCUS-REPRESENTATIVE-01, FOCUS-GAP-CORPUS-01), mutated inside the Fixture's valid ranges:
   seed, theme, background color, spacing, inset, labels, element count and custom focus style. The structure of each source recipe stays unchanged.
Each recipe gets a `family` for the data split. Held-out families are never training data. Capture decides validity: a recipe that fails is recorded and skipped.
Usage: fixture_recipes604.py --out NEW_DIR [--plain 150] [--canvas 190] [--seed 604]
"""
import argparse
import copy
import glob
import hashlib
import json
import random
from pathlib import Path
import research_queue as q

PLAIN = {'media_shelf': (2, 7), 'grid_matrix': (3, 12), 'settings_list': (2, 4), 'action_dialog': (2, 5), 'hero_carousel': (2, 7), 'focus_maze': (4, 9)}
THEMES, DENSITIES = ('dark', 'light', 'system', 'high_contrast'), ('compact', 'regular', 'spacious')
# Joe, 2026-11-25: "Yes, train on posters" (H2). `composition:poster_grid` left the hold-out; see reports/work/user-approvals/train666-h2-poster-holdout-20261125.json.
HELD_OUT = {'plain:hero_carousel', 'canvas:nested_tabs_v1', 'canvas:photos_like:cards'}
WORDS = ('Home', 'Movies', 'Shows', 'Sports', 'Kids', 'Library', 'Search', 'Settings', 'Live', 'News', 'Music', 'Store', 'Resume', 'Play', 'Trailer',
         'Add to List', 'Details', 'Next Episode', 'Restart', 'Sign In', 'Profiles', 'Downloads', 'Favorites', 'Browse', 'Featured', 'New Releases',
         'Continue Watching', 'Top Picks', 'Comedy', 'Drama', 'Documentaries', 'Audio', 'Subtitles', 'Close', 'Cancel', 'Done', 'More', 'Share', 'Rate', 'Info')
SOURCES = ('reports/work/FOCUS556/recipes/*.json', 'reports/work/CAPTURE553/recipes*/*.json',
           'reports/work/FOCUS-REPRESENTATIVE-01/recipes*/*.json', 'reports/work/FOCUS-REPRESENTATIVE-01/*/recipes*/*.json',
           'reports/work/FOCUS-GAP-CORPUS-01/recipes*/*.json', 'reports/work/FOCUS-GAP-CORPUS-01/*/recipes*/*.json')


def family(recipe):
    a = recipe.get('appearance')
    if not a:
        return 'plain:' + recipe['archetype']
    comp = a.get('composition')
    if isinstance(comp, dict) and comp:
        regs = [r.get('id', 'r') for r in (comp.get('regions') or [])[:3]]
        return 'composition:' + ('+'.join(regs) if regs else str(recipe.get('archetype', 'screen')))
    canvas = a.get('canvas') or {}
    presentation = canvas.get('presentation') or 'cards'
    return 'canvas:' + (a.get('preset', 'artwork') + ':cards' if presentation == 'cards' and a.get('preset') == 'photos_like' else presentation)


def color(rng, light):
    lo, hi = (200, 250) if light else (8, 60)
    return (rng.randint(lo, hi) << 16) | (rng.randint(lo, hi) << 8) | rng.randint(lo, hi)


def mutate(source, rng, seed):
    r = copy.deepcopy(source); r['seed'] = seed; r.pop('recipe_hash', None)
    light = rng.random() < .35; r['theme'] = 'light' if light else 'dark'
    a = r['appearance']; canvas = a.get('canvas')
    if canvas:
        canvas['backgroundRGB'] = color(rng, light)
        canvas['spacing'] = rng.choice((16, 24, 32, 40, 48, 64)); canvas['inset'] = rng.choice((40, 60, 80, 100, 120))
        labels = canvas.get('labels')
        if labels and canvas.get('presentation') in ('buttons', 'tabs', 'settings_rows') and 'tabCount' not in canvas:
            count = rng.randint(2, 6) if canvas['presentation'] == 'settings_rows' else rng.randint(2, min(8, canvas.get('columns', 8)))
            canvas['labels'] = rng.sample(WORDS, count); r['element_count'] = count
            if 'selectedIndex' in canvas:
                canvas['selectedIndex'] = rng.randrange(count)
        elif labels:
            canvas['labels'] = rng.sample(WORDS, len(labels))
    custom = (a.get('focus') or {}).get('custom')
    if custom:
        custom.update(scale=round(rng.uniform(1.0, 1.15), 2), borderWidth=rng.choice((0, 2, 4, 6)), shadowOpacity=round(rng.uniform(0, .8), 2),
                      cornerRadius=rng.choice((0, 8, 16, 24)), borderRGB=color(rng, True))
    return r


def mutate_composition(source, rng, seed):
    """Mutate appearance, theme, gradients, copy strings, and custom focus styles on a qualified v5 composition recipe.

    Preserves composition region geometry, component definitions, element IDs, and target selection so pre-capture expectations remain valid.
    """
    r = copy.deepcopy(source)
    r['seed'] = seed
    r.pop('recipe_hash', None)
    # TTR `FixtureComposition.validateRecipe` requires theme `dark` (style is composition-owned); comp-capture-v1 lost 56 / 56 `light` mutations at validation.
    light = r.get('theme') == 'light'
    comp = (r.get('appearance') or {}).get('composition') or {}
    bg = comp.get('background')
    if isinstance(bg, dict) and isinstance(bg.get('colors'), list) and len(bg['colors']) >= 2:
        bg['colors'] = [color(rng, light) for _ in bg['colors']]
    contents = comp.get('contents') or {}
    for val in contents.values():
        if isinstance(val, dict):
            if 'seed' in val:
                val['seed'] = rng.randint(1, 99999)
            if 'title' in val:
                val['title'] = rng.choice(WORDS)
    for st in (comp.get('styles') or {}).values():
        if not isinstance(st, dict):
            continue
        foc = st.get('focus') or {}
        custom = foc.get('custom')
        if isinstance(custom, dict):
            custom.update(
                scale=round(rng.uniform(1.02, 1.12), 2),
                borderWidth=rng.choice((2, 3, 4)),
                shadowOpacity=round(rng.uniform(0.3, 0.75), 2),
                borderRGB=color(rng, True),
            )
    return r


POSTER_SHAPES = {'tall': (1.5, (200, 300)), 'wide': (0.5625, (300, 460)), 'square': (1.0, (220, 340))}


def poster_variant(source, rng, seed, targets=6):
    """H2: vary the qualified `grid-uniform-poster` geometry: card shape and size, columns, rows, gap and grid position.

    Every card stays inside the 1920 x 1080 screen with a 60 px margin, because the capture audit needs fully visible cards.
    The focused targets are sampled from the cards. The capture audit checks each frame against these expectations.
    """
    r = copy.deepcopy(source)
    comp = r['appearance']['composition']
    region = comp['regions'][0]; item = region['items'][0]; card = comp['definitions'][item['component']]
    ratio, (lo, hi) = POSTER_SHAPES[rng.choice(sorted(POSTER_SHAPES))]
    pad, gap = rng.choice((10, 20, 30)), rng.choice((24, 32, 40, 56))
    left, top = rng.choice((60, 80, 120)), rng.choice((80, 120, 200, 300))
    for _ in range(50):
        w = rng.randrange(lo, hi + 1, 10); h = int(round(w * ratio / 10) * 10)
        cols_max = (1920 - 60 - left - 2 * pad + gap) // (w + gap); rows_max = (1080 - 60 - top - 2 * pad + gap) // (h + gap)
        if cols_max >= 2 and rows_max >= 1:
            break
    else:
        raise ValueError('poster_variant_no_fit')
    cols = rng.randint(max(2, min(7, cols_max) - 1), min(7, cols_max)); rows = rng.randint(1, min(3, rows_max))  # Media rows fill the width.
    card.update(width=w, height=h)
    region.update(columns=cols, gap=gap, content_insets=[pad, pad, pad, pad],
                  frame=[left, top, cols * w + (cols - 1) * gap + 2 * pad, rows * h + (rows - 1) * gap + 2 * pad])
    template = comp['contents'][item['content']]
    region['items'] = [dict(item, id=f'poster-{i}', content=f'poster-{i}', selected=False) for i in range(cols * rows)]
    comp['contents'] = {f'poster-{i}': dict(template) for i in range(cols * rows)}
    r['element_count'] = cols * rows
    chosen = rng.sample([f'poster-{i}' for i in range(cols * rows)], min(targets, cols * rows))
    r['capture_selection'] = dict(version=1, target_element_ids=chosen, max_targets=len(chosen))
    return mutate_composition(r, rng, seed)


def _has_scroll(node):
    """Return True when any nested `scroll` flag is true; such recipes lack scroll-offset ground truth."""
    if isinstance(node, dict):
        return node.get('scroll') is True or any(_has_scroll(v) for v in node.values())
    if isinstance(node, list):
        return any(_has_scroll(v) for v in node)
    return False


def _load_qualified_compositions(manifest_paths):
    """Collect unique qualified composition source recipes from passing qualification report(s)."""
    pool = {}
    for mpath in manifest_paths:
        mpath = Path(mpath)
        rpt = json.loads(mpath.read_text())
        passed_recipes = {row['recipe'] for row in rpt.get('rows', []) if row.get('passed')}
        failed_recipes = {row['recipe'] for row in rpt.get('rows', []) if not row.get('passed')}
        clean_names = passed_recipes - failed_recipes
        recipes_dir = mpath.parent / 'recipes'
        for rname in sorted(clean_names):
            rfile = recipes_dir / rname
            if not rfile.is_file():
                continue
            doc = json.loads(rfile.read_text())
            if isinstance(doc, dict) and isinstance((doc.get('appearance') or {}).get('composition'), dict):
                if _has_scroll(doc):
                    continue  # scroll=true drifts/culls cards without scrollOffset export (comp-qual-offscreen)
                key = json.dumps({k: v for k, v in doc.items() if k != 'seed'}, sort_keys=True)
                pool.setdefault(key, (str(rfile), doc))
    return list(pool.values())


def build(out, plain, canvas, seed, composition=0, composition_manifests=(), poster=0):
    rng = random.Random(seed); out = Path(out); out.mkdir(parents=True, exist_ok=False); rows = []; seen = set()
    def add(recipe, origin):
        key = hashlib.sha256(json.dumps(recipe, sort_keys=True).encode()).hexdigest()
        if key in seen:
            return
        seen.add(key); name = f'r604-{len(rows):04}'; fam = family(recipe)
        q.save(out/(name + '.json'), recipe)
        rows.append(dict(recipe=name + '.json', family=fam, role='held-out' if fam in HELD_OUT else 'training', origin=origin, sha256=q.digest(out/(name + '.json'))))
    archetypes = list(PLAIN)
    for i in range(plain):
        arch = archetypes[i % len(archetypes)]; lo, hi = PLAIN[arch]
        add(dict(schema_version=1, archetype=arch, element_count=rng.randint(lo, hi), theme=rng.choice(THEMES), density=rng.choice(DENSITIES), seed=seed*1000 + i), 'plain')
    pool = {}
    for pattern in SOURCES:
        for path in sorted(glob.glob(str(q.ROOT/pattern))):
            doc = json.loads(Path(path).read_text())
            if isinstance(doc, dict) and doc.get('appearance') and set(doc['appearance']) <= {'version', 'preset', 'layout', 'canvas', 'focus'}:
                pool.setdefault(json.dumps({k: v for k, v in doc.items() if k != 'seed'}, sort_keys=True), (str(Path(path).relative_to(q.ROOT)), doc))
    sources = list(pool.values()); q.require(sources, 'fixture_recipes604_no_sources')
    for i in range(canvas):
        origin, doc = sources[i % len(sources)]
        add(mutate(doc, rng, seed*1000 + 500 + i), origin)
    if composition > 0:
        comp_sources = _load_qualified_compositions(composition_manifests)
        q.require(comp_sources, 'fixture_recipes604_no_qualified_compositions')
        for i in range(composition):
            origin, doc = comp_sources[i % len(comp_sources)]
            add(mutate_composition(doc, rng, seed * 1000 + 5000 + i), origin)
    if poster > 0:
        sources = [x for x in _load_qualified_compositions(composition_manifests) if x[0].endswith('grid-uniform-poster.json')]
        q.require(sources, 'fixture_recipes604_no_qualified_poster')
        for i in range(poster):
            add(poster_variant(sources[0][1], rng, seed * 1000 + 8000 + i), sources[0][0])
    index = dict(version='fixture-recipes604-v1', seed=seed, recipes=len(rows), heldOutFamilies=sorted(HELD_OUT), rows=rows)
    q.save(out/'index.json', index)
    return index


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--out', type=Path, required=True); parser.add_argument('--plain', type=int, default=150)
    parser.add_argument('--canvas', type=int, default=190); parser.add_argument('--seed', type=int, default=604)
    parser.add_argument('--composition', type=int, default=0)
    parser.add_argument('--composition-manifest', action='append', default=[])
    parser.add_argument('--poster', type=int, default=0, help='H2: varied poster-grid recipes from the qualified grid-uniform-poster source')
    args = parser.parse_args()
    index = build(args.out, args.plain, args.canvas, args.seed, composition=args.composition, composition_manifests=args.composition_manifest, poster=args.poster)
    families = {}
    for r in index['rows']:
        families[r['family']] = families.get(r['family'], 0) + 1
    print(dict(recipes=index['recipes'], families=families))


if __name__ == '__main__':
    main()
