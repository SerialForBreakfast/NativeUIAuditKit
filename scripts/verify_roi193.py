"""Read back prepared inputs and render six boundary examples; never train."""
import collections
import time
from PIL import Image,ImageDraw
import roi193 as r


def run():
    start=time.monotonic();h,p,e=r.h,r.p,r.e
    doc=p.sealed(r.OUT/'proposal.json')
    for source in doc['sources']:h.checked(h.ROOT,source,256*1024**2)
    train=e.load_request(h.checked(h.ROOT,doc['membership']),41)
    parent=r.c.inputs();requests={k:e.load_request(h.checked(h.ROOT,v),41) for k,v in parent['manifests'].items()}
    parents={im.image_id:im for im in requests['fit'].images}
    generated={im.image_id:im for im in train.images};seen=set();counts=collections.Counter()
    for row in doc['rows']:
        im=generated[row['id']];source=parents[row['parent']]
        digest,labels=r.signature(source,row['window'])
        h.require(digest==row['pixelSHA256'] and digest not in seen,'pixel_identity_or_duplicate');seen.add(digest)
        h.require(tuple(sorted(im.label_path.read_text().splitlines()))==labels,'label_identity')
        counts.update(a['disposition'] for a in row['dispositions'])
    by_id={row['id']:row for row in doc['rows']}
    for row in doc['duplicateAliases']:
        digest,labels=r.signature(parents[row['parent']],row['window'])
        canonical=by_id[row['canonical']]
        h.require(digest==canonical['pixelSHA256'] and labels==tuple(sorted(generated[row['canonical']].label_path.read_text().splitlines())),'alias_identity')
    coverage={}
    for kind,plan in doc['evaluation'].items():
        req=e.load_request(h.checked(h.ROOT,plan['manifest']),41)
        h.require({x['imageID'] for x in plan['records']}=={im.image_id for im in requests[kind].images},'missing_original')
        h.require({x['id'] for row in plan['records'] for x in row['proposals']}=={im.image_id for im in req.images},'proposal_accounting')
        coverage[kind]=dict(originals=len(plan['records']),crops=len(req.images),noProposal=plan['noProposal'])
    sheet=Image.new('RGB',(900,600),'#222222');draw=ImageDraw.Draw(sheet)
    selected=[doc['rows'][i] for i in (0,100,250,400,600,801)]
    for index,row in enumerate(selected):
        im=generated[row['id']]
        with Image.open(im.image_path) as opened:tile=opened.convert('RGB').resize((280,280))
        td=ImageDraw.Draw(tile)
        for line in im.label_path.read_text().splitlines():
            cid,cx,cy,w,ht=map(float,line.split());box=[(cx-w/2)*280,(cy-ht/2)*280,(cx+w/2)*280,(cy+ht/2)*280]
            td.rectangle(box,outline='lime' if int(cid)==18 else 'orange',width=2)
        x,y=index%3*300,index//3*300;sheet.paste(tile,(x,y+20));draw.text((x,y),row['id'],fill='white')
    sheet.save(r.OUT/'boundary-review.png')
    report=dict(version='roi193-verification-v1',proposal=h.ref(r.OUT/'proposal.json'),trainingCrops=len(train.images),
        aliases=len(doc['duplicateAliases']),sourceImages=len({x['parent'] for x in doc['rows']+doc['duplicateAliases']}),
        dispositions=dict(counts),evaluation=coverage,seconds=time.monotonic()-start,trainingLaunched=False,
        boundaryExamples=[x['id'] for x in selected],softwareTestsSeparate=True)
    h.write(r.OUT/'verification.json',report,sealed=True);print(report)


if __name__=='__main__':run()
