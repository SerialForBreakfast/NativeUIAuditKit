"""Generated source-shaped sidecars, never prior human annotation artifacts."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from PIL import Image
from human_vision_import import load, CONVENTION, INTERPRETATION
from human_annotation_review import ROOT


def document(image):
    with Image.open(image) as im:w,h=im.size
    sha=hashlib.sha256(Path(image).read_bytes()).hexdigest()
    features=dict(ocrRevision=3,rectangleRevision=1,textTruncated=False,
        rectangles=[dict(bounds=dict(x=.7,y=.1,width=.2,height=.3),confidence=.9)],
        text=[dict(bounds=dict(x=.1,y=.8,width=.3,height=.1),confidence=.8,text='Search')])
    return dict(schemaVersion=1,kind='vision_pair_preprocessing',coordinateConvention=CONVENTION,
        interpretation=INTERPRETATION,configuration={'compute':'cpu_supported_stages'},operatingSystem='fixture',
        frames=[dict(role=role,sha256=sha if role=='after' else '0'*64,width=w,height=h,features=copy.deepcopy(features)) for role in ('before','after')])


class ImportTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(dir=ROOT/'.build/debug-output',prefix='vision-import-')
        self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
        self.image=self.root/'frame.png';Image.new('RGB',(100,60)).save(self.image)
        self.path=self.root/'vision.json';self.doc=document(self.image)

    def run_load(self,doc=None,**kwargs):
        self.path.write_text(json.dumps(doc or self.doc));return load(self.path,self.image,**kwargs)

    def test_binding_conversion_separate_ocr_and_duplicate_suppression(self):
        r=self.run_load();self.assertEqual(len(r['regions']),2)
        self.assertAlmostEqual(r['regions'][0]['points'][0][0],70)
        self.assertEqual(r['regions'][1]['text'],'Search')
        self.assertEqual(len(self.run_load(existing=[[[70,6],[90,24]]])['regions']),1)
        self.doc['frames'][1]['features']['rectangles']*=2
        self.assertEqual(len(self.run_load()['regions']),2)

    def test_wrong_hash_dimensions_schema_geometry_and_confidence(self):
        variants=[]
        for key,value in [('sha256','f'*64),('width',101)]:
            d=copy.deepcopy(self.doc);d['frames'][1][key]=value;variants.append(d)
        for key,value in [('schemaVersion',2),('coordinateConvention','bottom-left')]:
            d=copy.deepcopy(self.doc);d[key]=value;variants.append(d)
        for key,value in [('confidence',float('nan')),('confidence',2),('bounds',dict(x=.9,y=0,width=.2,height=.2))]:
            d=copy.deepcopy(self.doc);d['frames'][1]['features']['rectangles'][0][key]=value;variants.append(d)
        for d in variants:
            with self.assertRaises(ValueError):self.run_load(d)

    def test_empty_corrupt_and_ambiguous_equal_images(self):
        self.path.write_text('{')
        with self.assertRaises(ValueError):load(self.path,self.image)
        self.doc['frames'][0]['sha256']=self.doc['frames'][1]['sha256']
        self.doc['frames'][0]['features']['text']=[]
        with self.assertRaises(ValueError):self.run_load()
        for f in self.doc['frames']:f['features'].update(text=[],rectangles=[])
        self.assertEqual(self.run_load()['regions'],[])


if __name__=='__main__':unittest.main()
