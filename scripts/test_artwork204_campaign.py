import json
from pathlib import Path
import tempfile
import unittest
from PIL import Image, ImageDraw
import artwork204_campaign as c
import artwork200_campaign as consumer


class SplitCampaignTests(unittest.TestCase):
    def setUp(self):
        parent=Path(__file__).resolve().parents[1]/'.build/debug-output'
        parent.mkdir(parents=True,exist_ok=True)
        self.tmp=tempfile.TemporaryDirectory(dir=parent);self.addCleanup(self.tmp.cleanup)
        self.base=Path(self.tmp.name);self.source=self.base/'source';self.source.mkdir()
        self.inventory=self.base/'inventory.json';self.out=self.base/'input'
        rows=[]
        for index,r in enumerate({r['assetID']:r for r in c.recipes() if 'assetID' in r}.values()):
            p=self.source/(r['assetID']+'.png');Image.new('RGB',(1216,832),(index,20,30)).save(p)
            rows.append(dict(id=r['assetID'],sha256=c.sha(p),bytes=p.stat().st_size,
                ancestryGroups=[r['family']],dataRole=r['dataRole'],reviewStatus='verified',rightsStatus='verified',
                rightsEvidence=['test'],reviewEvidence=['test']))
        self.rows=rows;c.write(self.inventory,dict(resources=rows))

    def test_frozen_roles_and_preparation(self):
        report=c.prepare(self.inventory,self.source,self.out)
        self.assertEqual(report['roles'],{'train':60,'validation':24,'test':12})
        self.assertEqual(len(list(self.out.iterdir())),18)
        self.assertEqual(len({r['id'] for r in c.recipes()}),96)
        self.assertEqual({r['layout'] for r in c.recipes()},{'grid'})
        with self.assertRaisesRegex(ValueError,'collision'):c.prepare(self.inventory,self.source,self.out)

    def test_reject_missing_unreviewed_or_role_change_before_output(self):
        for field,value in [('dataRole','train'),('reviewStatus','pending'),('ancestryGroups',['wrong'])]:
            rows=json.loads(json.dumps(self.rows));rows[-1][field]=value
            self.inventory.write_text(json.dumps(dict(resources=rows)))
            with self.assertRaises(ValueError):c.prepare(self.inventory,self.source,self.out)
            self.assertFalse(self.out.exists())

    def test_hash_target_and_partial_plan(self):
        c.prepare(self.inventory,self.source,self.out)
        plan=c.document(self.out/'campaign.json');catalog=c.document(self.out/'catalog.json')
        for field,value in [('target','booted'),('recipes',plan['recipes'][:-1]),('schemaVersion','future'),('catalogSHA256','bad')]:
            changed=dict(plan);changed[field]=value
            with self.assertRaisesRegex(ValueError,'split_plan'):c.check(changed,catalog,self.out)
        asset=self.out/catalog['assets'][0]['path'];asset.write_bytes(b'corrupt')
        with self.assertRaisesRegex(ValueError,'asset_bytes'):c.check(plan,catalog,self.out)

    def test_split_intake_entrypoint_and_leakage(self):
        c.prepare(self.inventory,self.source,self.out)
        frames=self.base/'frames';frames.mkdir();records=[]
        assets={a['id']:a for a in c.document(self.out/'catalog.json')['assets']}
        for r in c.recipes():
            im=Image.new('RGB',(1179,2556),(r['seed']-20400,0,0));draw=ImageDraw.Draw(im)
            elements=[];bindings=[]
            for i in range(4 if r['density']=='low' else 6):
                v=[10+i*30,10,20,20];b=dict(x=v[0]*3,y=30,width=60,height=60)
                ident=f'imageView_thumb_{i}'
                elements.append(dict(id=ident,boundsPixels=b,boundsPoints=dict(zip(('x','y','width','height'),v))))
                if 'assetID' in r:
                    a=assets[r['assetID']];aw=20*1216/832
                    draw.rectangle((b['x'],30,b['x']+59,89),fill='gray' if r['condition']=='t1' else 'white')
                    bindings.append(dict(elementID=ident,assetID=a['id'],sha256=a['sha256'],
                        ancestryGroup=a['ancestryGroup'],placement='fill',viewportPoints=v,
                        contentExtentPoints=[v[0]+(20-aw)/2,10,aw,20]))
            png=frames/(r['id']+'.png');im.save(png);ann=frames/(r['id']+'.json')
            c.write(ann,dict(imageSHA256=c.sha(png),image=dict(colorScheme=r['theme']),elements=elements))
            rec=dict(recipe=r,dataRole=r['dataRole'],planSHA256=c.sha(self.out/'campaign.json'),
                imageSHA256=c.sha(png),sidecarSHA256=c.sha(ann),bindings=bindings)
            c.write(frames/(r['id']+'.record.json'),rec);records.append(rec)
        for shard in (0,1):
            c.write(frames/f'shard-{shard}.json',dict(schemaVersion='ios-artwork-shard-v2',complete=True,
                shard=shard,planSHA256=c.sha(self.out/'campaign.json'),frames=records[shard*48:(shard+1)*48],seconds=1))
        result=consumer.validate(frames,self.out)
        self.assertEqual(result['frames'],96);self.assertEqual(result['dataRole'],'recipe_bound')
        log=self.base/'shard-0.log';log.write_text("Test Case '-[GenerateDatasetTests testArtworkCampaign]' passed\n")
        c.write(self.base/'shard-0-result.json',dict(exitCode=0,logSHA256=c.sha(log)))
        c.completed_shard(self.base,frames,self.out,0)
        # A migrated container with the same sealed files is valid; a tampered
        # completion record is not permission to recapture automatically.
        receipt0=frames/'shard-0.json';saved=receipt0.read_text();d=json.loads(saved);d['complete']=False
        receipt0.write_text(json.dumps(d))
        with self.assertRaisesRegex(ValueError,'prior_shard_partial'):c.completed_shard(self.base,frames,self.out,0)
        receipt0.write_text(saved)
        with self.assertRaises(ValueError):c.qualify(frames,self.out,self.base/'qualification.json')
        self.assertFalse((self.base/'qualification.json').exists())  # Toy sidecars are not native annotations.
        # Reseal one validation procedural frame with training pixels: hashes alone
        # cannot establish split isolation. The validator must reject it.
        train=c.recipes()[0];val=c.recipes()[60]
        import shutil
        png=frames/(val['id']+'.png');shutil.copyfile(frames/(train['id']+'.png'),png)
        ann=frames/(val['id']+'.json');a=c.document(ann);a['imageSHA256']=c.sha(png);ann.write_text(json.dumps(a))
        seal=frames/(val['id']+'.record.json');rec=c.document(seal)
        rec['imageSHA256']=c.sha(png);rec['sidecarSHA256']=c.sha(ann);seal.write_text(json.dumps(rec))
        receipt=frames/'shard-1.json';d=c.document(receipt);d['frames'][12]=rec;receipt.write_text(json.dumps(d))
        # It rejects even earlier because the paired treatments no longer match
        # their baseline outside the artwork. Never silently accepts cross-role pixels.
        with self.assertRaisesRegex(ValueError,'outside_artwork_change|cross_role_pixels'):
            consumer.validate(frames,self.out)


if __name__=='__main__':unittest.main()
