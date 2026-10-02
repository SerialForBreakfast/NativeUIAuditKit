import copy
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image
import native_focus_transfer as f


def request():
    return dict(version=1,knownUnfocusedReference=True,sameScreen=True,settled=True,
        nativeEffect=True,correspondenceVerified=True,contextClear=True,unoccluded=True,
        imageAgeSeconds=1,referenceAgeSeconds=2,referenceEvidence='observed-unfocused',
        contextEvidence='test-same-scene',referenceBounds=[100,100,100,80],imageSize=[500,500])


class TransferTests(unittest.TestCase):
    def test_every_unknown_gate_stops_before_model(self):
        r=request();self.assertEqual(f.gate(r)['status'],'eligible')
        for key in list(r):
            if key in ('version','referenceBounds','imageSize'):continue
            with self.subTest(key=key):
                changed=copy.deepcopy(r);changed.pop(key)
                with patch.object(f,'Scorer',side_effect=AssertionError('must not load')):
                    self.assertEqual(f.advisory(changed)['status'],'unavailable')

    def test_stale_nonfinite_and_false_prerequisites(self):
        for value in [float('nan'),float('inf'),-1,6,True,'1']:
            r=request();r['referenceAgeSeconds']=value
            self.assertEqual(f.gate(r)['status'],'unavailable')
        r=request();r['sameScreen']=1;self.assertEqual(f.gate(r)['status'],'unavailable')

    def test_invalid_or_clipped_geometry(self):
        for bounds in [[0,0,100,80],[100,100,0,80],[100,100,float('nan'),80],[100,100,-1,80],[490,100,20,80]]:
            with self.assertRaises(ValueError):f.geometry(bounds,[500,500])

    def test_neutralization_preserves_context_and_scale(self):
        import numpy as np
        image=Image.new('RGB',(256,256),(7,9,11));ref=[100,100,100,80]
        a=np.asarray(f.neutralize(image,ref,ref));b=np.asarray(f.neutralize(image,[90,92,120,96],ref))
        self.assertTrue((a[0,0]==[7,9,11]).all())
        self.assertTrue((a[128,128]==128).all())
        self.assertGreater((b==128).all(2).sum(),(a==128).all(2).sum())

    def test_cli_unavailable_and_collision(self):
        import sys,os
        root=f.n.ROOT/'.build/debug-output/native28-tests';root.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(dir=root) as temp:
            temp=Path(temp);r=request();r['knownUnfocusedReference']=False
            path=temp/'request.json';path.write_text(json.dumps(r));out=temp/'reply.json'
            cmd=[sys.executable,str(f.n.ROOT/'scripts/native_focus_transfer.py'),'advisory','--request',str(path),'--output',str(out)]
            a=subprocess.run(cmd,capture_output=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
            self.assertEqual(a.returncode,0,a.stderr);self.assertEqual(json.loads(out.read_text())['status'],'unavailable')
            old=out.read_bytes();a=subprocess.run(cmd,capture_output=True)
            self.assertNotEqual(a.returncode,0);self.assertEqual(out.read_bytes(),old)

    def test_scored_caller_and_hash_guard(self):
        root=f.n.ROOT/'.build/debug-output/native28-tests';root.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(dir=root) as temp:
            path=Path(temp)/'frame.png';Image.new('RGB',(500,500)).save(path)
            r=request();r['image']=r['referenceImage']=dict(path=str(path),sha256=f.n.sha(path))
            class Fake:
                identity={'test':True}
                def score(self,images):return [.9]
            with patch.object(f,'crop',return_value=Image.new('RGB',(256,256))),patch.object(f.runtime,'identity',return_value={}):
                d=f.advisory(r,Fake);self.assertEqual(d['candidateState'],'focused');self.assertTrue(d['advisoryOnly'])
                r['image']['sha256']='0'*64
                with self.assertRaisesRegex(ValueError,'changed_input'):f.advisory(r,Fake)


if __name__=='__main__':unittest.main()
