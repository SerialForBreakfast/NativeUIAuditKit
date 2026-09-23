import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'scripts'))
import direct_tvos_capture as d
HERE=Path(__file__).resolve().parent
target='9026ECA9-77DB-4AE6-8FE6-BB239E9571FA'
binding=d.bind_target(target,'http://127.0.0.1:8080')
snap=d.Fixture(binding['endpoint']).snapshot()
d.write_json(HERE/'preflight.json',{'binding':binding,'snapshot':snap})
scene=snap['scene']
size=(scene['scene_width'],scene['scene_height'])
conflicts=[]
for element in scene['elements']:
    x,y,w,h=element['pixel_bounds']
    actual=[x/size[0],y/size[1],(x+w)/size[0],(y+h)/size[1]]
    if any(abs(a-b)>1e-6 for a,b in zip(actual,element['normalized_bounds'])): conflicts.append(element['element_id'])
print(json.dumps({'binding':binding,'size':size,'conflicts':conflicts,
                  'headerPublished':any(e['element_id']=='header_shelf' for e in scene['elements']),
                  'layoutExclusions':scene.get('layout_exclusions'),
                  'diagnostics':scene.get('observation_diagnostics')},indent=2))
assert not conflicts
assert binding['binaries']['TVTestRigFixture.debug.dylib']=='46011bb0a95cb007325a64baaab643ad913e0bf46c250a7198caab7b9f31a095'
