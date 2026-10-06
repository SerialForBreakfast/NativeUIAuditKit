"""Read-only follow-up: source geometry and support for the frozen ROI195 proposal."""
import collections
import statistics
from PIL import Image
import roi195 as r


def bounds_state(box, width, height):
    x,y,w,h=box
    r.h.require(w>0 and h>0,'invalid_bounds')
    return 'outside' if x<0 or y<0 or x+w>width or y+h>height else 'contained'


def run():
    out=r.OUT/'geometry.json'
    r.h.require(not out.exists(),'output_collision')
    proposal=r.p.sealed(r.OUT/'coverage-proposal.json')
    diagnosis=r.p.sealed(r.OUT/'diagnosis.json')
    rows=[]
    for row in proposal['rows']:
        annotation=r.h.read(r.h.checked(r.h.ROOT,row['annotation']))
        with Image.open(r.h.checked(r.h.ROOT,row['image'])) as image:
            width,height=image.size
        for element in annotation['elements']:
            if element['elementType']!='pageControl' or element.get('excluded',False):continue
            b=element['boundsPixels'];box=[b[k] for k in ('x','y','width','height')]
            rows.append(dict(id=row['id'],family=row['sourceFamily'],group=row.get('group',row['id']),
                box=box,frame=[width,height],bounds=bounds_state(box,width,height),
                occluded=element.get('occluded'),knownIssues=element.get('knownIssues',[])))
    families={}
    for family in sorted({v['family'] for v in rows}):
        subset=[v for v in rows if v['family']==family]
        families[family]=dict(instances=len(subset),groups=len({v['group'] for v in subset}),
            heights=[min(v['box'][3] for v in subset),statistics.median(v['box'][3] for v in subset),max(v['box'][3] for v in subset)],
            bounds=dict(collections.Counter(v['bounds'] for v in subset)),occluded=sum(v['occluded'] is True for v in subset))
    evaluation={}
    for kind in ('fit','page','combined'):
        for family in sorted({v['family'] for v in diagnosis['rows'] if v['kind']==kind}):
            subset=[v for v in diagnosis['rows'] if v['kind']==kind and v['family']==family and v['changed'] and 'before' in v]
            if subset:evaluation[kind+'/'+family]=dict(changed=len(subset),
                truthPixelHeights=[min(v['truthHeight'] for v in subset),statistics.median(v['truthHeight'] for v in subset),max(v['truthHeight'] for v in subset)],
                operatingDispositions=dict(collections.Counter(v['disposition'] for v in subset if v['operating'])))
    r.h.write(out,dict(rows=rows,families=families,evaluation=evaluation,
        inputs=[r.h.ref(r.OUT/'diagnosis.json'),r.h.ref(r.OUT/'coverage-proposal.json'),r.h.ref(__file__)],
        limitations=['Bounds containment is not visual occlusion verification.','Crop clipping must be checked during all-class materialization.',
            'Unmatched evaluation source metadata remains unknown; no inference from filenames.'],
        productionEligible=False),sealed=True)
    print(families)


if __name__=='__main__':run()
