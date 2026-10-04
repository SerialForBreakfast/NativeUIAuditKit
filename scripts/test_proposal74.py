import copy
import unittest
import tempfile
from pathlib import Path
import json
import focus_direct_transition as d
from prepare_proposal74 import targets,unique_frames,validate_response,load_inputs


class CandidateBankTests(unittest.TestCase):
    def test_retained_calibration_bank_never_becomes_training(self):
        root=d.h.ROOT/'reports/work/NATIVE-PROPOSALS-78/bank-host'
        if not root.exists():self.skipTest('retained calibration batch absent')
        report=d.h.sealed(root/'report.json','native78-proposals-v1')
        inputs=d.h.sealed(root/'inputs.json','calibration-proposals-v1')
        self.assertFalse(inputs['trainingEligible']);self.assertFalse(report['trainingLaunched'])
        self.assertEqual(len(inputs['frames']),24)
        self.assertTrue(all(set(c)=={'id','bounds'} for f in inputs['frames'] for c in f['candidates']))
        request=d.h.read(root/'request.json');raw=d.h.read(root/'raw.json')
        self.assertEqual(len(validate_response(request,raw)),24)
        self.assertTrue(all(set(f)=={'id','path','sha256'} for f in request['frames']))
        with self.assertRaises(ValueError):load_inputs(root/'inputs.json')

    def test_label_free_consumer_rejects_injected_truth_and_corrupt_source(self):
        with tempfile.TemporaryDirectory(dir=d.h.ROOT/'.build',prefix='proposal74-test-') as td:
            root=Path(td);image=root/'bytes.png';image.write_bytes(b'test source bytes')
            doc=dict(version='transition-candidate-inputs-v1',frames=[dict(id=d.h.ref(image)['sha256'],image=d.h.ref(image),
                size=[10,10],split='train',source='test',candidates=[dict(id='a',bounds=[0,0,5,5])])])
            path=root/'inputs.json';d.h.write(path,doc,sealed=True);self.assertEqual(len(load_inputs(path)['frames']),1)
            doc.pop('seal');doc['frames'][0]['candidates'][0]['state']='focused';doc['seal']=d.h.digest(doc);path.write_text(json.dumps(doc))
            with self.assertRaisesRegex(ValueError,'truth_leak'):load_inputs(path)
            doc.pop('seal');doc['frames'][0]['candidates'][0].pop('state');doc['seal']=d.h.digest(doc);path.write_text(json.dumps(doc))
            image.write_bytes(b'changed')
            with self.assertRaisesRegex(ValueError,'changed_hash'):load_inputs(path)
    def test_missing_multiple_positive_and_negative_support(self):
        self.assertTrue(targets([], [0,0,10,10])['missingPositive'])
        pool=[dict(id='a',bounds=[0,0,10,10]),dict(id='b',bounds=[1,0,10,10]),dict(id='c',bounds=[50,0,10,10])]
        before=copy.deepcopy(pool);result=targets(pool,[0,0,10,10])
        self.assertEqual(result['positiveIDs'],['a','b']);self.assertEqual(result['negativeIDs'],['c'])
        self.assertTrue(result['ambiguousPositive']);self.assertEqual(pool,before)

    def test_deduplication_preserves_roles_and_dimensions(self):
        rows=[dict(images=[dict(sha256='x',path='a')]*2,size=[100,100],split='train')]*2
        self.assertEqual(len(unique_frames(rows)),1)
        other=copy.deepcopy(rows[0]);other['split']='development'
        with self.assertRaisesRegex(ValueError,'split_or_size'):unique_frames(rows+[other])
        other['split']='train';other['size']=[50,50]
        with self.assertRaisesRegex(ValueError,'split_or_size'):unique_frames(rows+[other])

    def test_native_membership_hash_errors_and_ocr(self):
        request=dict(frames=[dict(id='a',sha256='x')])
        raw=dict(version=1,os='test',results=[dict(id='a',sha256='x',errors=[],text=[])])
        self.assertEqual(len(validate_response(request,raw)),1)
        for mutate in (lambda r:r['results'][0].update(id='wrong'),lambda r:r['results'][0].update(sha256='wrong'),
            lambda r:r['results'][0].update(errors=['failed']),lambda r:r['results'][0].update(text=[{}]),
            lambda r:r.update(results=[])):
            bad=copy.deepcopy(raw);mutate(bad)
            with self.assertRaises(ValueError):validate_response(request,bad)


if __name__=='__main__':unittest.main()
