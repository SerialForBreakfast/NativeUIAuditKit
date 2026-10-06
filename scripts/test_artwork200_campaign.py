import json
from pathlib import Path
import shutil
import tempfile
import unittest
import subprocess
import sys
from PIL import Image, ImageDraw
import artwork200_campaign as c


class CampaignTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        parent=Path(__file__).resolve().parents[1]/'.build/debug-output'
        parent.mkdir(parents=True,exist_ok=True)
        cls.tmp=tempfile.TemporaryDirectory(dir=parent)
        cls.base=Path(cls.tmp.name);source=cls.base/'source';source.mkdir()
        for name,color in [('thumbnail-03','white'),('thumbnail-04','gray')]:
            Image.new('RGB',(1216,832),color).save(source/(name+'.png'))
        cls.inputs=cls.base/'inputs';c.prepare(source,cls.inputs,
            reviewed={p.stem:c.sha(p) for p in source.iterdir()})
        cls.frames=cls.base/'frames';cls.frames.mkdir()
        plan=json.loads((cls.inputs/'campaign.json').read_text())
        assets={a['id']:a for a in json.loads((cls.inputs/'catalog.json').read_text())['assets']}
        records=[]
        for r in c.recipes():
            count=(4 if r['density']=='low' else 6) if r['layout']=='grid' else 1
            elements=[];bindings=[];im=Image.new('RGB',(1179,2556));draw=ImageDraw.Draw(im)
            for i in range(count):
                b=dict(x=30+i*90,y=30,width=60,height=60)
                ident=f'imageView_thumb_{i}' if r['layout']=='grid' else 'imageView_hero'
                v={k:n/3 for k,n in b.items()};elements.append(dict(id=ident,boundsPixels=b,boundsPoints=v))
                if r['condition']!='procedural':
                    asset=assets[plan['lowAsset'] if r['condition']=='low' else plan['busyAsset']]
                    draw.rectangle((b['x'],30,b['x']+59,89),fill='gray' if r['condition']=='low' else 'white')
                    aw=20*1216/832
                    bindings.append(dict(elementID=ident,assetID=asset['id'],sha256=asset['sha256'],
                        ancestryGroup=asset['ancestryGroup'],placement='fill',viewportPoints=list(v.values()),
                        contentExtentPoints=[v['x']+(20-aw)/2,10,aw,20]))
            png=cls.frames/(r['id']+'.png');im.save(png)
            ann=cls.frames/(r['id']+'.json')
            c.write(ann,dict(imageSHA256=c.sha(png),image=dict(colorScheme=r['theme']),elements=elements))
            record=dict(recipe=r,planSHA256=c.sha(cls.inputs/'campaign.json'),imageSHA256=c.sha(png),
                sidecarSHA256=c.sha(ann),dataRole='development',bindings=bindings)
            c.write(cls.frames/(r['id']+'.record.json'),record);records.append(record)
        for s in (0,1):
            c.write(cls.frames/f'shard-{s}.json',dict(schemaVersion='ios-artwork-shard-v1',complete=True,shard=s,
                planSHA256=c.sha(cls.inputs/'campaign.json'),frames=records[s*48:(s+1)*48],seconds=1))

    @classmethod
    def tearDownClass(cls):cls.tmp.cleanup()

    def setUp(self):
        self.tmpcase=tempfile.TemporaryDirectory(dir=self.base);self.addCleanup(self.tmpcase.cleanup)
        self.root=Path(self.tmpcase.name)/'frames';shutil.copytree(self.frames,self.root)

    def test_full_accounting(self):
        result=c.validate(self.root,self.inputs)
        self.assertEqual(result['frames'],96);self.assertTrue(result['duplicateGroups'])

    def test_partial_rejected(self):
        (self.root/'shard-1.json').unlink()
        with self.assertRaisesRegex(ValueError,'membership'):c.validate(self.root,self.inputs)

    def test_changed_sidecar(self):
        p=self.root/(c.recipes()[0]['id']+'.json');p.write_text('{}')
        with self.assertRaisesRegex(ValueError,'hash'):c.validate(self.root,self.inputs)

    def test_collision(self):
        with self.assertRaisesRegex(ValueError,'collision'):c.prepare(self.base/'source',self.inputs)

    def test_link_rejected(self):
        p=self.root/(c.recipes()[0]['id']+'.png');p.unlink();p.symlink_to(self.frames/p.name)
        with self.assertRaisesRegex(ValueError,'file_type'):c.validate(self.root,self.inputs)

    def test_plan_cardinality(self):
        self.assertEqual(len(c.recipes()),96)
        self.assertEqual(len({r['id'].rsplit('-',1)[0] for r in c.recipes()}),32)

    def test_resealed_outside_change_rejected(self):
        key=c.recipes()[1]['id'];png=self.root/(key+'.png');ann=self.root/(key+'.json')
        with Image.open(png) as original:im=original.copy()
        im.putpixel((0,0),(255,0,0));im.save(png)
        a=json.loads(ann.read_text());a['imageSHA256']=c.sha(png);ann.write_text(json.dumps(a))
        seal=self.root/(key+'.record.json');r=json.loads(seal.read_text())
        r['imageSHA256']=c.sha(png);r['sidecarSHA256']=c.sha(ann);seal.write_text(json.dumps(r))
        shard=self.root/'shard-0.json';d=json.loads(shard.read_text());d['frames'][1]=r;shard.write_text(json.dumps(d))
        with self.assertRaisesRegex(ValueError,'outside_artwork_change'):c.validate(self.root,self.inputs)

    def test_wrong_target_plan_rejected(self):
        inputs=Path(self.tmpcase.name)/'inputs';shutil.copytree(self.inputs,inputs)
        path=inputs/'campaign.json';d=json.loads(path.read_text());d['target']='booted';path.write_text(json.dumps(d))
        with self.assertRaisesRegex(ValueError,'plan'):c.validate(self.root,inputs)

    def test_unreviewed_same_named_image_rejected(self):
        with self.assertRaisesRegex(ValueError,'unreviewed_bytes'):
            c.prepare(self.base/'source',Path(self.tmpcase.name)/'unreviewed')

    def test_real_cli_validation(self):
        out=Path(self.tmpcase.name)/'validation.json'
        result=subprocess.run([sys.executable,c.__file__,'validate',str(self.root),str(self.inputs),str(out)],
                              capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(json.loads(out.read_text())['frames'],96)
        again=subprocess.run([sys.executable,c.__file__,'validate',str(self.root),str(self.inputs),str(out)],
                             capture_output=True,text=True)
        self.assertNotEqual(again.returncode,0)


if __name__=='__main__':unittest.main()
