"""ARTPARITY595: ingest TTR Programme-edition captures (Scripts/qualify-editorial-gallery.rb --field-atlas|--cinema-program).

Each run captures 3 native focus positions. At each position the driver observes all 3 controls and the decorative illustration
before the snapshot and the focused control after it. This ingest requires the `verified_reopened` summary, exactly 1 focused control
per frame (the expected one, before and after), and unfocused siblings and illustration.
Roles (13-role map, rule B): artwork actions `programme.control.0/1` = cell, text action `programme.control.2` = button, illustration = picture.
Images are resized to 1920 x 1080 (Lanczos) for the detector; the original snapshot is kept. Frames are in points; scale = image width / 1920.
Data role is fixed by asset lineage: edition C and the Matchday Replay series are test-only (Research/Plans/ArtParity595.md).
Usage: artparity595_ingest.py --run RUN_DIR --layout atlas|cinema --edition A|B|C [--series] --out dataset/tvos_captures/artparity595/programme
"""
import argparse
import hashlib
import json
import shutil
from pathlib import Path
from PIL import Image
import research_queue as q

ROLE = {'programme.control.0': 'cell', 'programme.control.1': 'cell', 'programme.control.2': 'button', 'programme.illustration': 'picture'}


def observation(run, label):
    raw = json.loads((run/f'{label}.json').read_text())
    q.require(raw.get('success') is True, 'artparity595_observation_failed:' + label)
    value = next(iter(raw['data'].values()))['_0']['uiObservation']
    q.require(value['matchCount'] == 1 and value['foregroundBefore'] and value['foregroundAfter'], 'artparity595_observation_scope:' + label)
    return value


def data_role(layout, edition, series):
    return 'test' if edition == 'C' or (series and layout == 'cinema') else 'train'


def screen_name(layout, edition, series):
    base = {'atlas': 'field-school' if series else 'field-atlas', 'cinema': 'matchday-replay' if series else 'cinema-programme'}[layout]
    return f'{base}-{edition.lower()}'


def ingest(run, layout, edition, series, out):
    summary = json.loads((run/'summary.json').read_text())
    q.require(summary.get('outcome') == 'verified_reopened', 'artparity595_run_unverified')
    screen = screen_name(layout, edition, series); role = data_role(layout, edition, series)
    folder = Path(out)/screen; folder.mkdir(parents=True, exist_ok=True)
    frames = []
    for i in range(3):
        focus = f'programme.control.{i}'
        before, after = observation(run, f'position-{i}-before'), observation(run, f'position-{i}-after')
        q.require(before['elementID'] == focus and after['elementID'] == focus and before['hasFocus'] and after['hasFocus'], 'artparity595_focus:' + focus)
        elements = []
        for field, label in [(f'programme.control.{j}', f'position-{i}-control-{j}') for j in range(3)] + [('programme.illustration', f'position-{i}-decor')]:
            o = observation(run, label)
            q.require(o['elementID'] == field and o['hasFocus'] == (field == focus), 'artparity595_sibling:' + label)
            elements.append(dict(id=field, role=ROLE[field], focused=field == focus, framePoints=o['frame']))
        source = run/f'position-{i}.png'
        with Image.open(source) as image:
            width, height = image.size
            scale = width / 1920
            q.require(abs(height / scale - 1080) < 1, 'artparity595_aspect')
            original = folder/f'position-{i}-native.png'; shutil.copyfile(source, original)
            target = folder/f'position-{i}.png'
            (image.convert('RGB') if scale == 1 else image.convert('RGB').resize((1920, 1080), Image.LANCZOS)).save(target)
        for e in elements:
            x, y, w, h = e['framePoints']
            e['boundsPixels'] = dict(x=x, y=y, width=w, height=h)  # Points equal 1080p pixels.
        sidecar = dict(version='artparity595-programme-v1', screen=screen, layout=layout, edition=edition, series=series, dataRole=role,
                       group=f'programme-{screen}', position=i, focusedID=focus, focusKind='text' if focus.endswith('.2') else 'artwork',
                       imageSHA256=q.digest(target), nativeImageSHA256=q.digest(original), nativeSize=[width, height], scale=scale,
                       elements=elements, run=dict(path=str(run), movieSHA256=summary.get('sha256'), session=summary.get('session')),
                       limitation='Native focus from bracketed ui-observe. Frames are SwiftUI layout frames in points; the focus scale effect is not in the frame.')
        q.save(folder/f'position-{i}.json', sidecar, replace=True)
        frames.append(dict(image=str(target.relative_to(q.ROOT)), sha256=sidecar['imageSHA256'], focus=focus, role=role))
    return dict(screen=screen, role=role, frames=frames)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--run', type=Path, required=True); parser.add_argument('--layout', choices=('atlas', 'cinema'), required=True)
    parser.add_argument('--edition', choices=('A', 'B', 'C'), required=True); parser.add_argument('--series', action='store_true')
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(ingest(args.run.resolve(), args.layout, args.edition, args.series, args.out.resolve())))


if __name__ == '__main__':
    main()
