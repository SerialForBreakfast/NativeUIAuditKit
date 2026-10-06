"""Training-only coverage proposal from admitted173; no training or transfer."""
import argparse
from collections import Counter
import hashlib
from pathlib import Path
import replay184 as source
from artwork200_campaign import write, sha
from shared_transfer import require
from PIL import Image

ROOT=source.h.ROOT
MEMBERSHIP=ROOT/'reports/work/IOS-PLACEMENT-173/artifacts/membership.json'
PIN='b687565bd5d0f91aca10dde0d5a3e8b3cb89b6f57e09e4bd983cfa7422ed1b65'


def select(rows,target=16,cap=512):
    """Rare classes first; stable hash choice, unique source groups."""
    require(len({r['id'] for r in rows})==len(rows),'duplicate_id')
    support={c:{r['group'] for r in rows if c in r['classes']} for c in {c for r in rows for c in r['classes']}}
    order=sorted(support,key=lambda c:(len(support[c]),c))
    ranked=sorted(rows,key=lambda r:(hashlib.sha256(r['id'].encode()).hexdigest(),r['id']))
    counts=Counter();chosen=[];groups=set()
    for c in order:
        for row in ranked:
            if counts[c]>=target or len(chosen)>=cap:break
            if c not in row['classes'] or row['group'] in groups:continue
            chosen.append(row);groups.add(row['group']);counts.update(row['classes'])
    return chosen,{c:max(0,target-counts[c]) for c in order}


def run(out):
    out=out.absolute();require(out.is_relative_to(ROOT) and out.resolve()==out and not out.exists(),'output_collision_boundary')
    require(sha(MEMBERSHIP)==PIN,'membership_changed')
    doc=source.p.sealed(MEMBERSHIP);rows=doc['rows']
    reserved=[r for r in rows if r['split']!='train']
    forbidden_pixels={r['pixelSHA256'] for r in reserved}
    forbidden_groups={r.get('group',Path(r['id']).stem) for r in reserved}
    pool=[];images=Counter();instances=Counter();groups={};original={r['id']:r for r in rows}
    require(len(original)==len(rows),'duplicate_source_id')
    for row in rows:
        if row['split']!='train':continue
        label=source.h.checked(ROOT,row['label'])
        counts=Counter(int(line.split()[0]) for line in label.read_text().splitlines() if line.strip())
        require(all(0<=c<41 for c in counts),'taxonomy')
        group=row.get('group',Path(row['id']).stem)
        require(group not in forbidden_groups and row['pixelSHA256'] not in forbidden_pixels,'reserved_overlap')
        images.update(counts.keys());instances.update(counts)
        for c in counts:groups.setdefault(c,set()).add(group)
        pool.append(dict(id=row['id'],group=group,classes=sorted(counts)))
    chosen,gaps=select(pool);selected=[];pixels=set()
    for item in chosen:
        row=original[item['id']]
        paths={k:source.h.checked(ROOT,row[k]) for k in ('image','annotation','label')}
        with Image.open(paths['image']) as im:
            im.load();rgb=im.convert('RGB')
            digest=hashlib.sha256(str(rgb.size).encode()+rgb.tobytes()).hexdigest()
        # Admission's original pixel encoding is retained; file hashes separately verified.
        require(digest==row['pixelSHA256'],'selected_pixel_binding')
        require(digest not in pixels and digest not in forbidden_pixels,'selected_duplicate_or_reserved_pixels');pixels.add(digest)
        selected.append(row)
    names=source.r.e.load_names()
    report=dict(sourceMembershipSHA256=PIN,sourceSHA256=sha(Path(__file__)),trainingPool=len(pool),
        targetGroupsPerSupportedClass=16,cap=512,selectedCount=len(selected),rows=selected,
        perClass=[dict(className=name,trainingImages=images[c],instances=instances[c],groups=len(groups.get(c,())),
                      selectedGroups=sum(c in r['classes'] for r in chosen),remainingGroups=gaps.get(c,16)) for c,name in enumerate(names)],
        role='Existing train only; proposal not a model launch',trainingLaunched=False,modelGatePassed=False,
        selectedOriginalBytesVerified=True,reservedAncestry='Preserved sealed173 roles and pixel identities; no new split')
    write(out,report)
    return dict(trainingPool=len(pool),selected=len(selected),unsupported=[names[c] for c in range(41) if not images[c]],
                unmetSupported={names[c]:n for c,n in gaps.items() if n})


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('out',type=Path)
    print(run(parser.parse_args().out))
