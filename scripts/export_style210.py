"""Export admitted style210 members through the existing all-class exporter."""
import subprocess
import sys
from admit_style210 import ROOT,h,p
from export_coco import load_category_map,CATEGORY_MAP
from page_regeneration41 import checked_export_labels


def main():
    admission=ROOT/'admission01.json';doc=p.sealed(admission)
    h.require(doc['eligible'] and doc['role']=='train' and len(doc['rows'])==96,'admission')
    out=ROOT/'export01';h.require(not out.exists(),'output_collision')
    source=out/'source/train';source.mkdir(parents=True)
    for row in doc['rows']:
        h.require(row['split']=='train','role')
        for key in ('image','annotation'):
            path=h.checked(h.ROOT,row[key]);(source/path.name).symlink_to(path)
    destination=out/'dataset'
    command=[sys.executable,str(h.ROOT/'scripts/export_coco.py'),'--dataset',str(source.parent),'--output',str(destination)]
    with (out/'export.log').open('x') as log:
        completed=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,timeout=120)
    h.require(completed.returncode==0,'export_failure')
    names,_=load_category_map(CATEGORY_MAP);rows=[]
    h.require({f.stem for f in (destination/'train/labels').iterdir()}=={r['id'] for r in doc['rows']},'export_membership')
    for split in ('val','test'):
        h.require(not list((destination/split/'images').iterdir()) and not list((destination/split/'labels').iterdir()),'role_drift')
    for row in doc['rows']:
        image=destination/'train/images'/(row['id']+'.png');label=destination/'train/labels'/(row['id']+'.txt')
        h.require(h.sha(image)==row['image']['sha256'],'changed_pixels')
        checked_export_labels(h.read(h.checked(h.ROOT,row['annotation'])),label.read_text(),names)
        rows.append(dict(row,label=h.ref(label)))
    h.write(out/'membership.json',dict(admission=h.ref(admission),rows=rows,source=h.ref(__file__),
        exporter=h.ref(h.ROOT/'scripts/export_coco.py'),classMap=h.ref(CATEGORY_MAP),role='train',modelGatePassed=False),sealed=True)
    print('Exported96images/480labels with unchanged41class mapping; no validation/test members')


if __name__=='__main__':main()
