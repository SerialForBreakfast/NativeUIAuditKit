"""Incremental preparation without simulator, model inference or role admission."""
import base64
import copy
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
from PIL import Image
import focus_candidate_ranker as r


class DerivativeTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(dir=r.d.h.ROOT/'.build',prefix='batch79-test-')
        self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)
        self.cache=self.root/'cache'

    def frame(self,name,color):
        path=self.root/(name+'.png');Image.new('RGB',(80,60),color).save(path)
        ref=r.d.h.ref(path)
        return dict(id=ref['sha256'],image=ref,size=[80,60],split='train',source='test-only',
            candidates=[dict(id='one',bounds=[2,3,40,20]),dict(id='two',bounds=[8,8,20,20])])

    @staticmethod
    def fake(items,**kwargs):
        results=[]
        for item in items:
            out=io.BytesIO()
            Image.new('RGB',(256,256),(int(item['bounds'][0]),20,30)).save(out,format='PNG')
            results.append(dict(id=item['id'],png=base64.b64encode(out.getvalue()).decode()))
        return dict(results=results)

    def test_cold_warm_append_roles_and_model_only_changes(self):
        a=self.frame('a','red');b=self.frame('b','blue')
        with patch.object(r.runtime,'invoke',side_effect=self.fake) as invoke:
            cold=r.encode_frames([a],self.cache);self.assertEqual(invoke.call_count,1)
            warm=r.encode_frames([a],self.cache);self.assertEqual(invoke.call_count,1)
            changed=copy.deepcopy(a);changed['split']='calibration'
            with patch.dict(r.CONFIG,lr=.02):role=r.encode_frames([changed],self.cache)
            self.assertEqual(invoke.call_count,1)
            extended=r.encode_frames([a,b],self.cache);self.assertEqual(invoke.call_count,2)
            self.assertEqual(extended[3],dict(cacheHits=1,cacheMisses=1,invocations=1))
            np.testing.assert_array_equal(cold[0],warm[0]);np.testing.assert_array_equal(cold[0],role[0])
            np.testing.assert_array_equal(cold[0],extended[0][:2])
            reordered=r.encode_frames([b,a],self.cache);self.assertEqual(invoke.call_count,2)
            np.testing.assert_array_equal(reordered[0],np.concatenate((extended[0][2:],extended[0][:2])))

    def test_geometry_and_dependency_invalidation(self):
        frame=self.frame('a','red')
        with patch.object(r.runtime,'invoke',side_effect=self.fake) as invoke:
            r.encode_frames([frame],self.cache)
            changed=copy.deepcopy(frame);changed['candidates'][0]['bounds'][0]=5
            r.encode_frames([changed],self.cache);self.assertEqual(invoke.call_count,2)
            identity=r.derivative_identity();identity['dependencies']['pillow']='test-changed'
            with patch.object(r,'derivative_identity',return_value=identity):r.encode_frames([frame],self.cache)
            self.assertEqual(invoke.call_count,3)

    def test_corrupt_partial_and_changed_source_fail_closed(self):
        frame=self.frame('a','red')
        with patch.object(r.runtime,'invoke',side_effect=self.fake) as invoke:
            result=r.encode_frames([frame],self.cache)
            manifest=r.d.h.read(r.d.h.checked(r.d.h.ROOT,result[4][0]))
            tensor=r.d.h.checked(r.d.h.ROOT,manifest['tensor']);tensor.write_bytes(b'corrupt')
            with self.assertRaisesRegex(ValueError,'changed_hash'):r.encode_frames([frame],self.cache)
            self.assertEqual(invoke.call_count,1)
            other=self.frame('b','blue')
            with patch.object(r.runtime,'invoke',side_effect=ValueError('test-interruption')):
                with self.assertRaisesRegex(ValueError,'test-interruption'):r.encode_frames([other],self.cache)
            with self.assertRaises(FileNotFoundError):r.encode_frames([other],self.cache)
            Image.new('RGB',(80,60),'green').save(self.root/'a.png')
            with self.assertRaisesRegex(ValueError,'changed_hash'):r.encode_frames([frame],self.cache)

    def test_schema_bounds_reply_and_runtime_guards(self):
        frame=self.frame('a','red')
        bad=copy.deepcopy(frame);bad['candidates'][0]['truth']=True
        with self.assertRaisesRegex(ValueError,'derivative_candidates'):r.encode_frames([bad],self.cache)
        bad=copy.deepcopy(frame);bad['size']=[80,61]
        with self.assertRaisesRegex(ValueError,'actual_size'):r.encode_frames([bad],self.cache)
        bad=copy.deepcopy(frame);bad['candidates'][0]['bounds']=[79,0,10,10]
        with self.assertRaisesRegex(ValueError,'bounds'):r.encode_frames([bad],self.cache)
        with self.assertRaisesRegex(ValueError,'frame_identity'):r.encode_frames([frame,frame],self.cache)
        with patch.object(r.runtime,'invoke',return_value=dict(results=[])):
            with self.assertRaisesRegex(ValueError,'reply_order'):r.encode_frames([frame],None)
        identity=r.derivative_identity()
        with patch.object(r.runtime,'invoke',side_effect=self.fake),patch.object(r,'derivative_identity',side_effect=[identity,dict(changed=True)]):
            with self.assertRaisesRegex(ValueError,'runtime_changed'):r.encode_frames([frame],None)

    def test_inspection_entrypoint_no_approval_or_role_upgrade(self):
        frame=self.frame('a','red');frame.pop('split');frame.pop('source')
        path=self.root/'inputs.json'
        r.d.h.write(path,dict(version='calibration-proposals-v1',trainingEligible=False,frames=[frame]),sealed=True)
        with patch.object(r.runtime,'invoke',side_effect=self.fake) as invoke:
            report=r.prepare_derivatives(self.root/'inspection',path,self.cache)
            again=r.prepare_derivatives(self.root/'warm',path,self.cache)
            self.assertEqual(invoke.call_count,1);self.assertEqual(again['statistics']['invocations'],0)
        self.assertFalse(report['trainingEligible']);self.assertFalse(report['executionEligible'])
        self.assertEqual({p.name for p in (self.root/'inspection').iterdir()},{'derivatives.json','encodings.npy'})
        with self.assertRaisesRegex(ValueError,'output_collision'):r.prepare_derivatives(self.root/'inspection',path,self.cache)
        with self.assertRaises(ValueError):r.bank(self.root/'inspection/derivatives.json')

    def test_real_helper_cold_warm_and_uncached_parity(self):
        frame=self.frame('a','red')
        cold=r.encode_frames([frame],self.cache)
        uncached=r.encode_frames([frame])
        with patch.object(r.runtime,'invoke',side_effect=AssertionError('warm must not crop')):
            warm=r.encode_frames([frame],self.cache)
        np.testing.assert_array_equal(cold[0],uncached[0]);np.testing.assert_array_equal(cold[0],warm[0])
        self.assertEqual(cold[2],uncached[2]);self.assertEqual(cold[2],warm[2])


if __name__=='__main__':unittest.main()
