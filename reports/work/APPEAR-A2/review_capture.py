"""Diagnostic-only overlays and production crops; does not approve data."""
import base64
import hashlib
import json
from pathlib import Path
import sys
from PIL import Image, ImageDraw
ROOT=Path(__file__).resolve().parents[3]; HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'scripts'))
from direct_tvos_capture import validate_capture
from direct_focus_manifest import pairs_from_capture
from focus_runtime import invoke, identity
from focus_dataset_contract import digest
raw=ROOT/'dataset/tvos_captures/appearance-a2-pilot'
doc=json.loads((raw/'direct-capture.json').read_text())
assert validate_capture(doc,raw)==76
out=HERE/'review'; out.mkdir(exist_ok=False)
runtime=identity(); pairs=pairs_from_capture(doc); records=[]; edges=[]
for p in pairs:
    items=[{'id':p['pair_id']+':'+role,'path':str(raw/p['frames'][role]['path']),
            'sha256':p['frames'][role]['sha256'],'bounds':p['frames'][role]['bounds']}
           for role in ('focused','unfocused')]
    results=invoke(items)['results']
    assert [r['id'] for r in results]==[r['id'] for r in items]
    row={'id':p['pair_id'],'recipe':p['recipe'],'element':p['elementID'],'control':p['element_type']}
    for role,r in zip(('focused','unfocused'),results,strict=True):
        name=p['pair_id']+'-'+role+'.png'; (out/name).write_bytes(base64.b64decode(r['png'],validate=True))
        with Image.open(out/name) as im:
            assert im.size==(256,256)
            sha=hashlib.sha256(str(im.size).encode()+b'\0'+im.convert('RGB').tobytes()).hexdigest()
        row[role]={'path':str((out/name).relative_to(ROOT)),'pixelSHA256':sha}
    records.append(row)
for family in ('media_shelf','grid_matrix','action_dialog','hero_carousel'):
    selected=[(i,r) for i,r in enumerate(doc['recipes']) if r['recipe']['archetype']==family]
    sheet=Image.new('RGB',(1200,250*len(selected)),'#202020'); draw=ImageDraw.Draw(sheet)
    for row,(index,r) in enumerate(selected):
        for col,frame in enumerate((r['frames'][0],r['frames'][1],r['frames'][-1])):
            with Image.open(raw/frame['path']) as source: im=source.convert('RGB')
            paint=ImageDraw.Draw(im)
            for e in frame['before']['scene']['elements']:
                x,y,w,h=e['pixel_bounds']; paint.rectangle((x,y,x+w,y+h),outline='lime' if e['is_focused'] else 'orange',width=4)
            im.thumbnail((400,225)); sheet.paste(im,(400*col,250*row+25))
            draw.text((400*col,250*row),f"{index} {r['recipe']['theme']} {r['recipe']['density']} {frame['observedFocusID'] or 'reference'}",fill='white')
    sheet.save(out/(family+'-scenes.png'))
    subset=[r for r in records if r['recipe']['archetype']==family]
    sheet=Image.new('RGB',(1024,145*((len(subset)+3)//4)),'#202020'); draw=ImageDraw.Draw(sheet)
    for i,r in enumerate(subset):
        x,y=(i%4)*256,(i//4)*145
        for j,role in enumerate(('focused','unfocused')):
            with Image.open(ROOT/r[role]['path']) as im:
                im.thumbnail((128,128)); sheet.paste(im,(x+j*128,y))
        draw.text((x,y+128),r['element']+' + / -',fill='white')
    sheet.save(out/(family+'-pairs.png'))
for r in doc['recipes']:
    for frame in r['frames']:
        s=frame['before']['scene']
        for e in s['elements']:
            x,y,w,h=e['pixel_bounds']
            if min(x,y)<=0 or x+w>=s['scene_width'] or y+h>=s['scene_height']:
                edges.append({'path':frame['path'],'element':e['element_id'],'bounds':e['pixel_bounds']})
assert identity()==runtime and validate_capture(doc,raw)==76
result={'captureSHA256':digest(doc),'runtime':runtime,'pairs':records,'edges':edges,
        'purpose':'diagnostic-review-only','trainingEligible':False}
(out/'index.json').write_text(json.dumps(result,indent=2))
print(json.dumps({'pairs':len(records),'edgeOccurrences':len(edges),'captureSHA256':digest(doc)}))
