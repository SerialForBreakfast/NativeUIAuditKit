import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from PIL import Image, ImageDraw
from validate_ios_artwork_probe import validate


class ProbeTests(unittest.TestCase):
    def setUp(self):
        parent = Path(__file__).resolve().parents[1]/'.build/debug-output'
        parent.mkdir(parents=True, exist_ok=True)
        self.tmp = tempfile.TemporaryDirectory(dir=parent)
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.data = self.root/'data'; self.data.mkdir()
        self.catalog = self.root/'catalog.json'
        self.catalog.write_text(json.dumps({'assets': [{'id':'a','sha256':'a'*64,'width':20,'height':20,'ancestryGroup':'g'}]}))
        elems = []
        for i in range(4):
            b = dict(x=30+i*90,y=30,width=60,height=60)
            elems.append(dict(id=f'imageView_thumb_{i}',boundsPixels=b,
                              boundsPoints={k:v/3 for k,v in b.items()}))
        self.frames=[]
        for name in ['default','fit','fill']:
            im=Image.new('RGB',(1179,2556))
            bindings=[]
            if name!='default':
                draw=ImageDraw.Draw(im)
                for e in elems:
                    p=e['boundsPixels'];draw.rectangle((p['x'],p['y'],p['x']+59,p['y']+59),fill='white')
                    v=e['boundsPoints'];box=[v[k] for k in ('x','y','width','height')]
                    bindings.append(dict(elementID=e['id'],assetID='a',sha256='a'*64,
                        ancestryGroup='g',viewportPoints=box,contentExtentPoints=box,placement=name))
            im.save(self.data/(name+'.png'))
            digest=hashlib.sha256((self.data/(name+'.png')).read_bytes()).hexdigest()
            (self.data/(name+'.json')).write_text(json.dumps(dict(imageSHA256=digest,elements=elems,image={'colorScheme':'light'})))
            self.frames.append(dict(file=name+'.png',sha256=digest,dataRole='development',bindings=bindings))
        self.receipt=dict(schemaVersion='ios-artwork-probe-v1',complete=True,frames=self.frames,
                          catalogSHA256=hashlib.sha256(self.catalog.read_bytes()).hexdigest())
        self.save()

    def save(self):
        (self.data/'receipt.json').write_text(json.dumps(self.receipt))

    def test_valid(self):
        self.assertEqual(validate(self.data,self.catalog)['bindings'],8)

    def test_partial_or_wrong_members(self):
        self.receipt['complete']=False;self.save()
        with self.assertRaisesRegex(ValueError,'incomplete'):validate(self.data,self.catalog)

    def test_changed_hash(self):
        self.frames[1]['sha256']='f'*64;self.save()
        with self.assertRaisesRegex(ValueError,'image_hash'):validate(self.data,self.catalog)

    def test_wrong_theme(self):
        p = self.data/'fill.json'
        a = json.loads(p.read_text()); a['image']['colorScheme'] = 'dark'
        p.write_text(json.dumps(a))
        with self.assertRaisesRegex(ValueError,'probe_theme'):validate(self.data,self.catalog)

    def test_wrong_geometry(self):
        self.frames[1]['bindings'][0]['contentExtentPoints'][0]=500;self.save()
        with self.assertRaisesRegex(ValueError,'viewport|content_geometry'):validate(self.data,self.catalog)

    def test_outside_change_even_with_matching_hashes(self):
        p=self.data/'fit.png'
        with Image.open(p) as original: im=original.copy()
        im.putpixel((0,0),(255,255,255));im.save(p)
        digest=hashlib.sha256(p.read_bytes()).hexdigest()
        self.frames[1]['sha256']=digest;self.save()
        a=json.loads(p.with_suffix('.json').read_text());a['imageSHA256']=digest
        p.with_suffix('.json').write_text(json.dumps(a))
        with self.assertRaisesRegex(ValueError,'outside_viewport'):validate(self.data,self.catalog)


if __name__=='__main__':unittest.main()
