"""Experimental static local+scene+geometry inputs; no model imports or execution.

Consumes a sealed native-body protocol. Missing original geometry is accounted for,
never inferred from labels. Existing production crops are references, not recropped.
"""
import argparse
import math
from pathlib import Path

from PIL import Image, ImageDraw
import human_annotation_review as h

VERSION = 'focus-context-inputs-v1'
SIZE = (768, 432)
MAX_PIXELS = 16_777_216


def transform(size):
    w, ht = size
    h.require(w > 0 and ht > 0 and w*ht <= MAX_PIXELS, 'scene_pixel_limit')
    scale = min(SIZE[0]/w, SIZE[1]/ht)
    rw, rh = max(1, round(w*scale)), max(1, round(ht*scale))
    return dict(sourceSize=list(size), outputSize=list(SIZE), resizedSize=[rw,rh],
                scale=[rw/w,rh/ht], offset=[(SIZE[0]-rw)//2,(SIZE[1]-rh)//2])


def geometry(bounds, tx):
    h.require(isinstance(bounds,(list,tuple)) and len(bounds)==4 and
              all(type(v) in (int,float) and math.isfinite(v) for v in bounds), 'invalid_context_bounds')
    x,y,w,ht = bounds; W,H = tx['sourceSize']
    h.require(w > 0 and ht > 0, 'invalid_context_bounds')
    left,top,right,bottom = max(0,x),max(0,y),min(W,x+w),min(H,y+ht)
    h.require(right > left and bottom > top, 'invisible_context_bounds')
    sx,sy = tx['scale']; ox,oy = tx['offset']
    scene = [ox+left*sx,oy+top*sy,(right-left)*sx,(bottom-top)*sy]
    return dict(normalizedBounds=[x/W,y/H,w/W,ht/H], sceneBounds=scene,
                clipped=[left!=x,top!=y,right!=x+w,bottom!=y+ht])


def scene_image(original, tx):
    canvas = Image.new('RGB', SIZE, (0,0,0))
    canvas.paste(original.convert('RGB').resize(tuple(tx['resizedSize']),Image.Resampling.LANCZOS),
                 tuple(tx['offset']))
    return canvas


def candidate_mask(geo):
    # Half-open pixel-center membership: avoids PIL's inclusive far-edge bias.
    x,y,w,ht = geo['sceneBounds']
    l,t = max(0,math.ceil(x-.5)),max(0,math.ceil(y-.5))
    r,b = min(SIZE[0],math.ceil(x+w-.5)),min(SIZE[1],math.ceil(y+ht-.5))
    mask = Image.new('L',SIZE,0)
    if r>l and b>t: ImageDraw.Draw(mask).rectangle((l,t,r-1,b-1),fill=255)
    return mask


def load_samples(protocol):
    doc = h.read(h.local(protocol),limit=32*1024*1024)
    h.require(doc.get('version') in ('focus-native-body-full-fit-v1','focus-native-body-assembly-v1')
              and doc.get('protocolSHA256') == h.digest({k:v for k,v in doc.items() if k!='protocolSHA256'}),
              'changed_context_protocol')
    rows = doc['samples']
    h.require(rows and len(rows)<=4096 and len({r['id'] for r in rows})==len(rows), 'context_membership')
    # Reject the entire input before opening any image if protected roles occur.
    h.require(all((r.get('split'),r.get('use')) in
                  {('train','train-candidate'),('train','human-static-auxiliary'),
                   ('validation','representative-selection'),('validation','retention-validation')}
                  for r in rows),
              'unsupported_or_protected_context_role')
    return rows


def geometry_index(paths):
    """Recover historical bounds by pair+frame+crop identity, never by label."""
    indexed={}; refs=[]
    for path in paths:
        path=h.local(path);doc=h.read(path,limit=32*1024*1024)
        h.require(doc.get('version')=='1.4','unsupported_geometry_manifest')
        refs.append(h.ref(path))
        for pair in doc['pairs']:
            for state,frame in pair['frames'].items():
                key=(pair['pair_id'],frame['sha256'],pair[state+'_crop_sha256'])
                bounds=frame['bounds']
                h.require(key not in indexed or indexed[key]==bounds,'conflicting_context_geometry')
                indexed[key]=bounds
    return indexed,refs


def build(protocol, output, geometry_manifests=()):
    rows = load_samples(protocol)
    out = h.fresh(output)
    recovered,geometry_refs=geometry_index(geometry_manifests)
    scenes, members, blocked = {}, [], []
    # Validate all supplied references/bounds first. Missing attributes are explicit
    # blocked members; corrupt supplied evidence aborts rather than hiding in counts.
    prepared = []
    for row in sorted(rows,key=lambda r:r['id']):
        row = dict(row,frame=row.get('frame',row.get('image')))
        if not row.get('bounds') and row.get('frame'):
            key=(row.get('pairID'),row['frame']['sha256'],row['crop']['sha256'])
            if key in recovered:row['bounds']=recovered[key]
        missing = [k for k in ('frame','bounds') if not row.get(k)]
        if missing:
            blocked.append(dict(id=row['id'],reason='missing_'+ '_and_'.join(missing))); continue
        frame = h.checked(h.ROOT,row['frame'])
        crop = h.checked(h.ROOT,row['crop'])
        with Image.open(crop) as im:
            h.require(im.size == (256,256), 'local_crop_dimensions')
            im.verify()
        with Image.open(frame) as im:
            tx = transform(im.size)
            geo = geometry(row['bounds'],tx)
            im.verify()
        prepared.append((row,frame,tx,geo))
    out.mkdir(parents=True)
    for row,frame,tx,geo in prepared:
        key = row['frame']['sha256']
        if key not in scenes:
            path = out/(key+'-scene.png')
            with Image.open(frame) as im: scene_image(im,tx).save(path)
            scenes[key] = dict(original=row['frame'],scene=h.ref(path),transform=tx)
        path = out/(h.digest(row['id'])+'-mask.png')
        candidate_mask(geo).save(path)
        # Whitelist model inputs: no native state, label, expected focus or reference
        # unfocused geometry can enter this record. Labels remain in source protocol.
        members.append(dict(id=row['id'],localCrop=row['crop'],sceneKey=key,
                            mask=h.ref(path),geometry=geo))
    result = dict(version=VERSION,diagnosticOnly=True,trainingEligible=False,
                  protocol=h.ref(h.local(protocol)),sceneSize=list(SIZE),
                  geometryManifests=geometry_refs,
                  scenes=scenes,members=members,blocked=blocked,
                  counts=dict(input=len(rows),prepared=len(members),blocked=len(blocked),scenes=len(scenes)))
    h.write(out/'manifest.json',result)
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--protocol',required=True);p.add_argument('--output',required=True)
    p.add_argument('--geometry-manifest',action='append',default=[],
                   help='Historical v1.4 crop manifest for exact identity-bound missing geometry')
    args=p.parse_args()
    try:
        print(build(args.protocol,args.output,args.geometry_manifest)['counts']);return 0
    except (ValueError,OSError,KeyError,TypeError) as error:
        print('Context preparation rejected: '+str(error));return 2


if __name__=='__main__':raise SystemExit(main())
