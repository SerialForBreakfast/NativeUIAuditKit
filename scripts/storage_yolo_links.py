"""Inventory and explicitly rebind existing local image links to verified SSD copies."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import artifact_storage as s
from corpus_retention import digest, sha256


def links():
    for relative in ('NativeUITrainer', 'dataset', 'reports', '.build/debug-output'):
        for parent, dirs, files in os.walk(s.ROOT / relative, followlinks=False):
            for name in dirs + files:
                path = Path(parent) / name
                if path.is_symlink():
                    yield path


def plan(sources):
    sources = [s.clean(p) for p in sources]
    s.require(all(p.is_relative_to(s.ROOT / 'NativeUITrainer/reconstructed_corpora')
                  and p.is_dir() for p in sources), 'invalid_corpus_root')
    tracked = set(subprocess.check_output(['git', 'ls-files', '-z'], cwd=s.ROOT).decode().split('\0'))
    rows = []
    for link in links():
        target = link.resolve()
        roots = [p for p in sources if target.is_relative_to(p)]
        if not roots:
            continue
        s.require(len(roots) == 1 and target.is_file() and link.suffix == '.png', 'unsupported_link')
        name = str(link.relative_to(s.ROOT))
        s.require(name not in tracked, 'tracked_link')
        s.clean(link.parent)
        rows.append(dict(path=name, old=os.readlink(link), source=str(target.relative_to(s.ROOT)),
                         sha256=sha256(target)))
    doc = dict(version='storage-yolo-links-v1', sources=[str(p.relative_to(s.ROOT)) for p in sources],
               rows=sorted(rows, key=lambda r:r['path']))
    doc['seal'] = digest(doc)
    return doc


def verify(doc, rebound=False):
    s.require(doc.get('version') == 'storage-yolo-links-v1' and
              doc.get('seal') == digest({k:v for k,v in doc.items() if k != 'seal'}), 'link_inventory_changed')
    roots = [s.clean(s.ROOT / p) for p in doc['sources']]
    s.require(roots and all(p.is_relative_to(s.ROOT / 'NativeUITrainer/reconstructed_corpora')
                           for p in roots), 'invalid_corpus_root')
    names = set()
    checked = []
    for row in doc['rows']:
        name = Path(row['path']); source = Path(row['source'])
        s.require(not name.is_absolute() and '..' not in name.parts and
                  not source.is_absolute() and '..' not in source.parts and str(name) not in names,
                  'unsafe_link_member')
        names.add(str(name))
        link = s.ROOT / name; s.clean(link.parent)
        s.require(name.suffix == '.png' and name.parts[0] in ('NativeUITrainer','dataset','reports','.build'),
                  'unsupported_link')
        logical = s.clean(s.ROOT / source)
        s.require(any(logical.is_relative_to(p) for p in roots), 'source_not_in_inventory')
        target = s.resolve_input(logical)
        s.require(target != logical and target.is_file(), 'source_not_migrated')
        s.require(link.is_symlink() and os.readlink(link) == (str(target) if rebound else row['old']),
                  'link_changed')
        s.require(sha256(target) == row['sha256'], 'destination_changed')
        if not rebound:
            s.require(link.resolve() == logical and sha256(logical) == row['sha256'], 'source_changed')
        checked.append((link, target, row))
    return checked


def rebind(doc):
    rows = verify(doc)
    tracked = set(subprocess.check_output(['git','ls-files','-z'], cwd=s.ROOT).decode().split('\0'))
    s.require(not any(r['path'] in tracked for _,_,r in rows), 'tracked_link')
    for link, target, row in rows:
        # Existing links only, never a directory alias. A partial run remains inspectable.
        s.require(os.readlink(link) == row['old'], 'link_changed_during_rebind')
        s.resolve_input(s.ROOT / row['source'])
        link.unlink()
        link.symlink_to(target)
    verify(doc, rebound=True)
    return len(rows)


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('mode',choices=['plan','rebind','verify'])
    p.add_argument('--inventory',required=True,type=Path)
    p.add_argument('--source',action='append',type=Path)
    a=p.parse_args()
    if a.mode=='plan':
        output=s.local_output(a.inventory)
        s.require(not output.exists() and a.source, 'new_inventory_and_sources_required')
        doc=plan(a.source);output.parent.mkdir(parents=True,exist_ok=True)
        with output.open('x') as f:json.dump(doc,f,indent=2)
        print('inventoried',len(doc['rows']))
    else:
        doc=json.loads(a.inventory.read_text())
        print('verified',rebind(doc) if a.mode=='rebind' else len(verify(doc,True)))
