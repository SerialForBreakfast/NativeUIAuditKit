import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import numpy as np
from PIL import Image
import focus_direct_transition as d
import prepare_transition_inputs as p
from focus_translation_training import bank,schedule


class PreparedTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(dir=d.h.ROOT/'.build',prefix='prepared66-test-')
        self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)
        im=self.root/'image.png';Image.new('RGB',(100,100),'red').save(im)
        evidence=self.root/'source.json';d.h.write(evidence,dict(native='test-only'))
        row=dict(id='a',group='g',sourceRole='calibration',images=[d.h.ref(im)]*2,
            evidence=[d.h.ref(evidence)],decodedPixelHashes=['same']*2,size=[100,100],
            boxes=[[10,10,20,20]]*2,changed=False)
        self.corpus=dict(version='focus-direct-corpus-v1',records=[row],excluded=[],
            sources=dict(reference=d.h.ref(evidence)),trainingEligible=False)
        self.corpus['corpusSHA256']=d.digest(self.corpus)
        self.admission=dict(version='focus-direct-admission-v1',approved=True,reviewer='test-only',
            decisionReference='synthetic test, no execution',corpusSHA256=self.corpus['corpusSHA256'],assignments={'a':'train'})
        self.cp=self.root/'corpus.json';self.ap=self.root/'admission.json'
        d.h.write(self.cp,self.corpus);d.h.write(self.ap,self.admission)
        with patch.object(d,'collect',return_value=self.corpus):p.prepare(self.cp,self.ap,self.root/'bank')
        self.mp=self.root/'bank/manifest.json';self.rows=d.admitted(self.corpus,self.admission)

    def test_tensor_schedule_and_real_trainer_boundary(self):
        expected=bank(self.rows)
        with patch.object(d,'pixels',side_effect=AssertionError('unexpected decode')):
            actual=d.training_bank(self.rows,d.h.ref(self.mp))
        np.testing.assert_array_equal(actual[0],expected[0]);np.testing.assert_array_equal(actual[1],expected[1])
        self.assertEqual(actual[2:],expected[2:])
        self.assertEqual(schedule(actual[2],600,42),schedule(expected[2],600,42))

    def test_collision_and_membership(self):
        with self.assertRaisesRegex(ValueError,'output_collision'):p.prepare(self.cp,self.ap,self.root/'bank')
        for mutate in (lambda r:r[0].update(split='development'),lambda r:r[0].update(changed=True)):
            rows=copy.deepcopy(self.rows);mutate(rows)
            with self.assertRaisesRegex(ValueError,'training_rows_changed'):p.load(self.mp,rows)
        with self.assertRaisesRegex(ValueError,'policy_mismatch'):p.load(self.mp,self.rows,'paired-halfwidth-25x15pct-v1')

    def test_legacy_manifest_defaults_only_to_original_policy(self):
        doc=d.h.read(self.mp);doc['version']='prepared-transition-inputs-v1';doc.pop('policy');doc.pop('seal')
        doc['seal']=d.digest(doc);self.mp.write_text(json.dumps(doc))
        self.assertEqual(p.load(self.mp,self.rows)[0].shape,(5,6,64,96))
        doc['policy']='paired-halfwidth-25x15pct-v1';doc.pop('seal');doc['seal']=d.digest(doc)
        self.mp.write_text(json.dumps(doc))
        with self.assertRaisesRegex(ValueError,'prepared_policy'):p.manifest(self.mp)

    def test_source_and_code_invalidation(self):
        with patch.object(d,'pins',return_value={}):
            with self.assertRaisesRegex(ValueError,'code_or_runtime_changed'):p.manifest(self.mp)
        Image.new('RGB',(100,100),'blue').save(self.root/'image.png')
        with self.assertRaisesRegex(ValueError,'changed_hash'):p.load(self.mp,self.rows)

    def test_array_corruption_and_missing(self):
        arr=self.root/'bank/x.npy'
        with arr.open('r+b') as stream:stream.seek(-1,2);stream.write(b'!')
        with self.assertRaisesRegex(ValueError,'changed_hash'):p.load(self.mp,self.rows)
        arr.unlink()
        with self.assertRaises((ValueError,OSError)):p.load(self.mp,self.rows)

    def test_admission_change(self):
        self.admission['approved']=False
        # This simulates external modification, not a second publication.
        self.ap.write_text(__import__('json').dumps(self.admission))
        with self.assertRaisesRegex(ValueError,'changed_hash'):p.manifest(self.mp)

    def test_unsupported_manifest_and_invalid_array_shape(self):
        doc=d.h.read(self.mp);doc['version']='unknown';doc.pop('seal')
        doc['seal']=d.digest(doc);self.mp.write_text(json.dumps(doc))
        with self.assertRaisesRegex(ValueError,'manifest_changed'):p.manifest(self.mp)
        doc['version']=p.VERSION
        np.save(self.root/'bank/x.npy',np.zeros((1,),dtype=np.float32),allow_pickle=False)
        doc['x']=d.h.ref(self.root/'bank/x.npy');doc.pop('seal');doc['seal']=d.digest(doc)
        self.mp.write_text(json.dumps(doc))
        with self.assertRaisesRegex(ValueError,'shape_or_range'):p.load(self.mp,self.rows)

    def test_real_protocol_keeps_execution_gate(self):
        protocol=dict(version=d.VERSION,configuration=d.TRANSLATION_CONFIG,
            implementation=d.h.ref(Path(d.__file__)),pins=d.pins(),sources=self.corpus['sources'],
            corpusSHA256=self.corpus['corpusSHA256'],admission=d.h.ref(self.ap),
            preparedInputs=d.h.ref(self.mp),diagnosticGate={'test':'no real qualification'})
        protocol['protocolSHA256']=d.digest(protocol);path=self.root/'protocol.json';d.h.write(path,protocol)
        with patch.object(d,'collect',side_effect=AssertionError('unexpected intake')), \
             patch('prepare_robustness63.verify_gate') as gate, \
             patch.object(d.old,'fresh_run',return_value=self.root/'unused'):
            result,rows=d.load_protocol(path,d.ARM,'prepared66-test')
        gate.assert_called_once();self.assertFalse(result['launchEligible'])
        self.assertIn('missing_execution_approval',result['blockers']);self.assertEqual(rows,self.rows)


if __name__=='__main__':unittest.main()
