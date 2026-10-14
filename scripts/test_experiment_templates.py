"""Contract and real-queue tests. Test data never establishes model accuracy."""
import copy
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch

import experiment_templates as t
import experiment_steps393 as steps
import research_approval as approval


class ContractTests(unittest.TestCase):
    def test_all_contracts_positive_and_missing_inputs(self):
        self.assertEqual(len(t.catalog()),14)
        for contract in t.catalog():
            with self.subTest(template=contract['id']):
                inputs={key: {'testOnly':True} for key in contract['requiredInputs']}
                self.assertEqual(t.validate_contract(contract['id'],inputs)['id'],contract['id'])
                with self.assertRaisesRegex(ValueError,'template_input_fields'):
                    t.validate_contract(contract['id'],{})
                with self.assertRaisesRegex(ValueError,'template_version'):
                    t.validate_contract(contract['id'],inputs,99)

    def test_unknown_template(self):
        with self.assertRaisesRegex(ValueError,'template_unknown'): t.validate_contract('T99',{})


class QueueTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(dir=t.q.ROOT/'.build',prefix='templates393-')
        self.root=Path(self.temp.name); self.queue=self.root/'queue'
        from PIL import Image
        Image.new('RGB',(256,256),(40,30,20)).save(self.root/'image.png')
        (self.root/'model.pt').write_bytes(b'test identity only; preparation does not load weights')
        manifest=dict(version='prepared-crop-membership-v1',preprocessing='production-crops-rgb256-v1',
            rows=[dict(id='test-only',group='test',role='development',profile='hcf',label=1,image=t.pin(self.root/'image.png'))])
        t.q.save(self.root/'membership.json',manifest)
        self.doc=dict(version=t.VERSION,id='template-test',owner='test-NUIAK',question='Does preparation retain the test pixels?',
            decision='Require identical pixels and predictable failures. No scientific claim.',
            manifest=t.pin(self.root/'membership.json'),model=t.pin(self.root/'model.pt'),batchSize=1)

    def tearDown(self): self.temp.cleanup()

    def test_registration_repeat_and_conflict(self):
        first=t.register(self.doc,self.queue); second=t.register(self.doc,self.queue)
        self.assertEqual([r['sha256'] for r in first],[r['sha256'] for r in second])
        self.assertTrue(all(r['state']=='already_submitted' for r in second))
        changed=dict(self.doc,batchSize=2)
        with self.assertRaisesRegex(ValueError,'registration_conflict'):t.register(changed,self.queue)
        self.assertFalse((self.queue/'approved-additions.json').exists())

    def test_interrupted_registration(self):
        original=t.q.submit; calls=[]
        def interrupt(*a,**kw):
            calls.append(1)
            if len(calls)==2:raise OSError('test interrupted registration')
            return original(*a,**kw)
        with patch.object(t.q,'submit',side_effect=interrupt),self.assertRaises(OSError):t.register(self.doc,self.queue)
        result=t.register(self.doc,self.queue)
        self.assertEqual(len(result),3)
        self.assertEqual(result[0]['state'],'already_submitted')

    def test_missing_and_changed_input(self):
        (self.root/'model.pt').write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError,'input_changed'):t.build(self.doc)
        (self.root/'model.pt').unlink()
        with self.assertRaisesRegex(ValueError,'input_missing'):t.build(self.doc)

    def test_invalid_description(self):
        for change in ({'batchSize':0},{'version':'wrong'},{'command':'rm anything'}):
            with self.subTest(change=change),self.assertRaises(ValueError):t.build(dict(self.doc,**change))

    def test_queue_prepare_positive_and_runtime_failure(self):
        t.register(self.doc,self.queue)
        for ident in ('template-test-prepare','template-test-score'):
            approval.approve(self.queue,ident,'test','Software qualification with isolated test inputs.')
        result=t.q.run(self.queue,max_jobs=2,lock=self.root/'test.lock',
                       job_ids=['template-test-prepare','template-test-score'])
        self.assertEqual(result,[('template-test-prepare','complete'),('template-test-score','failed')])
        failure=t.q.load(self.queue/'jobs/template-test-score/attempts/1/out/template-result.json')
        self.assertEqual(failure['execution'],'failed')
        self.assertFalse(failure['modelAccepted'])
        result=t.q.run(self.queue,max_jobs=2,lock=self.root/'test.lock',job_ids=['template-test-prepare','template-test-score'])
        self.assertEqual(result,[])

    def test_report_rejects_nonfinite(self):
        path=self.root/'predictions.json'
        t.q.save(path,dict(version='template-predictions-v1',rows=[dict(id='x',score=2,label=1)]))
        with self.assertRaisesRegex(ValueError,'invalid_scores'):steps.report_at(path,self.root)

    def test_rgba_preserves_production_rgb_conversion(self):
        from PIL import Image
        import numpy as np
        Image.new('RGBA',(256,256),(40,30,20,128)).save(self.root/'image.png')
        manifest=t.q.load(self.root/'membership.json')
        manifest['rows'][0]['image']=t.pin(self.root/'image.png')
        t.q.save(self.root/'membership.json',manifest,replace=True)
        config=dict(self.doc,manifest=t.pin(self.root/'membership.json'))
        steps.prepare_at(config,self.root)
        pixels=np.load(self.root/'tensors.npy',allow_pickle=False)
        self.assertEqual(pixels.shape,(1,256,256,3))
        self.assertEqual(pixels[0,0,0].tolist(),[40,30,20])


if __name__=='__main__':unittest.main()
