import importlib.util
from pathlib import Path
import numpy as np
spec=importlib.util.spec_from_file_location('pairing',Path(__file__).resolve().with_name('pairing.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
try:
    m.check_frame({'focusState':'no_focus','focusID':123})
    raise AssertionError('A no-focus record cannot name a target')
except ValueError:
    pass
a={'group':'g','role':'train','contentVariant':'v1','focusState':'focused','focusID':'a','controls':[{'id':'a','bounds':[0,0,2,2]},{'id':'b','bounds':[2,0,2,2]}]}
b={**a,'focusID':'b'}
p=np.zeros((3,5,3),dtype=np.uint8); q=p.copy();q[0,0]=1;q[0,2]=1
assert m.assess(a,b,p,q)['eligible']
q[2,4]=1
assert m.assess(a,b,p,q)['reason']=='unmatched_pixels'
assert m.assess(a,{**b,'focusState':'unknown','focusID':None},p,q)['reason']=='missing_focus_observation'
assert m.assess(a,{**b,'focusState':'no_focus','focusID':None},p,q)['reason']=='explicit_no_focus'
assert m.assess(a,{**b,'role':'held-out'},p,q)['reason']=='group_or_role_mismatch'
assert m.assess(a,{**b,'focusID':'a'},p,q)['reason']=='same_focused_control'
assert m.assess(a,{**b,'contentVariant':'v2'},p,q)['reason']=='content_changed'
assert m.assess(a,{**b,'contentVariant':None},p,q)['reason']=='missing_content_identity'
m.check_frame=lambda frame: p
f1={**a,'id':'1','image':{'sha256':'same'}}
f2={**b,'id':'2','image':{'sha256':'other'}}
f3={**a,'id':'3','role':'held-out','image':{'sha256':'same'}}
r=m.build([f1,f2,f3])
assert r['crossRoleImageHashes']==['same']
assert r['pairs'][0]['reason']=='cross_role_duplicate'
f4={**b,'id':'4','image':{'sha256':'same'}}
r=m.build([f1,f2,f4])
assert r['conflictingFocusImageHashes']==['same']
assert all(x['reason']=='conflicting_focus_for_identical_pixels' for x in r['pairs'])
print('Passed 11 pair, content, role, collision, and focus-state checks.')
