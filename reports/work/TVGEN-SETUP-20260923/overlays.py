"""Diagnostic contact sheets from immutable capture evidence, not training images."""
import json
from pathlib import Path
import sys
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'scripts'))
import direct_tvos_capture as d
from direct_tvos_resume import audit_chain
HERE=Path(__file__).resolve().parent
paths=[ROOT/p for p in ('dataset/tvos_captures/direct-pilot-20260922-2152/failed.json',
                       'dataset/tvos_captures/direct-media-boundary-20260923-0044/segment.json',
                       'dataset/tvos_captures/direct-pilot-rest-20260923/failed.json')]
entries,recipe_count,pair_count=audit_chain(paths)
records=[(entry['path'].parent,result) for entry in entries for result in entry['doc']['recipes']]
output=HERE/'overlays'
output.mkdir(exist_ok=False)
anomalies=[]
for family in d.COUNTS:
    if not any(result['recipe']['archetype']==family for _,result in records): continue
    sheet=Image.new('RGB',(1920,3*395),'#202020')
    draw=ImageDraw.Draw(sheet)
    for row,theme in enumerate(('light','dark','high_contrast')):
        raw,result=next((raw,r) for raw,r in records if r['recipe']['archetype']==family
                       and r['recipe']['theme']==theme and r['recipe']['seed']==7)
        selected=[result['frames'][0],result['frames'][1],result['frames'][-1]]
        for col,frame in enumerate(selected):
            with Image.open(raw/frame['path']) as original:
                im=original.convert('RGB')
            painter=ImageDraw.Draw(im)
            for element in frame['before']['scene']['elements']:
                x,y,w,h=element['pixel_bounds']
                painter.rectangle((x,y,x+w,y+h),outline='#00ff00' if element['is_focused'] else '#ffc000',width=3)
            im.thumbnail((640,360))
            sheet.paste(im,(col*640,row*395+30))
            draw.text((col*640+5,row*395+5),f"{family} / {theme} / {frame['observedFocusID'] or 'reference'}",fill='white')
    sheet.save(output/(family+'.png'))
for raw,result in records:
    for frame in result['frames']:
        scene=frame['before']['scene']
        for e in scene['elements']:
            x,y,w,h=e['pixel_bounds']
            if min(x,y)<=0 or x+w>=scene['scene_width'] or y+h>=scene['scene_height']:
                anomalies.append({'path':str((raw/frame['path']).relative_to(ROOT)),'element':e['element_id'],'bounds':e['pixel_bounds'],
                                  'reason':'touches_image_edge','focused':e['is_focused']})
d.write_json(HERE/'overlay-index.json',{'retainedPairs':pair_count,'retainedRecipes':recipe_count,
                                      'diagnosticOnly':True,'admittedPairs':0,
                                      'sheets':[p.name for p in output.glob('*.png')],'edgeCases':anomalies})
print(json.dumps({'recipes':recipe_count,'pairs':pair_count,'edgeCases':len(anomalies),'admittedPairs':0}))
