import copy
import itertools
import unittest
import json
import hashlib
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch
from PIL import Image
from audit_style210 import audit
from page_style210 import ROOT
from admit_style210 import choose
from page_style210 import catalog,validate,AXES


class StyleCoverageTests(unittest.TestCase):
    def test_admission_dedup_and_conflicts(self):
        a=dict(id='a',pixelSHA256='p',group='g',annotationIdentity=['box'])
        b=dict(a,id='b')
        kept,aliases=choose([b,a],set())
        self.assertEqual([r['id'] for r in kept],['a'])
        self.assertEqual(aliases[0]['retainedID'],'a')
        for bad in (dict(b,group='other'),dict(b,annotationIdentity=['different'])):
            with self.assertRaises(Exception):choose([a,bad],set())
        with self.assertRaises(Exception):choose([a],{'p'})

    def test_audit_rejects_changed_pixels_and_geometry(self):
        root=Path(tempfile.mkdtemp(dir=ROOT/'.build/debug-output',prefix='style210-test-'))
        self.addCleanup(shutil.rmtree,root)
        recipe=catalog('F3EF9DB8-0B0F-4757-B653-D1628269F6FF')['members'][0]
        doc=dict(target='target',members=[recipe]);raw=json.dumps(doc).encode()
        path=root/'catalog.json';path.write_bytes(raw);key=recipe['id']
        Image.new('RGB',(3,3)).save(root/(key+'.png'))
        hidden=Image.new('RGB',(3,3));hidden.paste('white',(0,0,2,2));hidden.save(root/(key+'-hidden.png'))
        row=dict(id=key,group=recipe['group'],interaction=False,requestedBackgroundStyle='automatic',resolvedBackgroundStyle=0,
                 body=[0,0,2,2],sha256=hashlib.sha256((root/(key+'.png')).read_bytes()).hexdigest(),
                 hiddenSHA256=hashlib.sha256((root/(key+'-hidden.png')).read_bytes()).hexdigest())
        ann=dict(elements=[dict(elementType='pageControl',boundsPoints=dict(x=0,y=0,width=2,height=2),boundsPixels=dict(x=0,y=0,width=2,height=2))])
        (root/(key+'.json')).write_text(json.dumps(ann));(root/(key+'-evidence.json')).write_text(json.dumps(row))
        (root/'receipt.json').write_text(json.dumps(dict(target='target',catalogSHA256=hashlib.sha256(raw).hexdigest(),rows=[row])))
        with patch('audit_style210.validate',return_value=doc):
            self.assertFalse(audit(root,path)['trainingEligible'])
            ann['elements'][0]['boundsPixels']['width']=9
            (root/(key+'.json')).write_text(json.dumps(ann))
            with self.assertRaisesRegex(ValueError,'geometry'):audit(root,path)
            (root/(key+'.png')).write_bytes(b'corrupt')
            with self.assertRaisesRegex(ValueError,'image_hash'):audit(root,path)

    def test_complete_independent_axes(self):
        d=catalog('F3EF9DB8-0B0F-4757-B653-D1628269F6FF');validate(d)
        keys=('family','theme','backgroundStyle','interaction','pages','position')
        self.assertEqual({tuple(r[k] for k in keys) for r in d['members']},set(itertools.product(*AXES)))
        self.assertEqual(len(d['members']),144)
        self.assertEqual(len({r['group'] for r in d['members']}),18)
        self.assertFalse(d['trainingEligible'])

    def test_changed_role_duplicate_or_axis_rejected(self):
        d=catalog('F3EF9DB8-0B0F-4757-B653-D1628269F6FF')
        for change in (lambda v:v.update(trainingEligible=True),
                       lambda v:v['members'].append(v['members'][0]),
                       lambda v:v['members'][0].update(backgroundStyle='invented')):
            bad=copy.deepcopy(d);change(bad)
            with self.assertRaises(ValueError):validate(bad)
        with self.assertRaises(ValueError):catalog('booted')
