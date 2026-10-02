import unittest
import subprocess
import sys
import tempfile
from pathlib import Path
import numpy as np
from PIL import Image
import settings_context_probe as p


class ContextTests(unittest.TestCase):
    def test_mask_tracks_translation_and_clipping(self):
        a=p.body_mask([200,200,160,60],[200,200,160,60],(640,480))
        b=p.body_mask([200,100,160,60],[200,100,160,60],(640,480))
        np.testing.assert_array_equal(a,b)
        self.assertFalse(a[0].any());self.assertTrue(a[128,128])
        c=p.body_mask([0,200,160,60],[0,200,160,60],(640,480))
        self.assertGreater(c.sum(),a.sum())

    def test_neighbor_rejected_by_full_but_not_body(self):
        a=Image.new('RGB',(256,256),(80,)*3);array=np.asarray(a).copy();array[:20]=255
        b=Image.fromarray(array);mask=np.zeros((256,256),bool);mask[32:224,32:224]=True
        pred=dict(tracking=dict(status='matched'),decision='unknown',illuminationWarning=False)
        r=p.proposals(pred,[a,b],mask)
        self.assertEqual(r['decisions'],dict(full='unknown',body='unchanged'))
        self.assertGreater(r['outside']['mean'],0);self.assertEqual(r['body']['maximum'],0)

    def test_internal_change_does_not_become_stable(self):
        a=Image.new('RGB',(256,256),(80,)*3);array=np.asarray(a).copy();array[70:140,70:140]=255
        mask=np.zeros((256,256),bool);mask[32:224,32:224]=True
        pred=dict(tracking=dict(status='matched'),decision='unknown',illuminationWarning=False)
        r=p.proposals(pred,[a,Image.fromarray(array)],mask)
        self.assertEqual(r['decisions']['body'],'unknown')

    def test_rejects_empty_mask_and_nonfinite_bounds(self):
        with self.assertRaisesRegex(ValueError,'support'):
            p.metrics(Image.new('RGB',(256,256)),Image.new('RGB',(256,256)),np.zeros((256,256),bool))
        with self.assertRaisesRegex(ValueError,'bounds'):
            p.body_mask([float('nan'),0,100,100],[0,0,100,100],(640,480))

    def test_outline_counterexample_is_explicit(self):
        a=Image.new('RGB',(256,256),(80,)*3);array=np.asarray(a).copy()
        array[29:31,29:226]=255
        mask=np.zeros((256,256),bool);mask[32:224,32:224]=True
        prediction=dict(tracking=dict(status='matched'),decision='unknown',illuminationWarning=False)
        result=p.proposals(prediction,[a,Image.fromarray(array)],mask)
        # The experiment intentionally exposes why this candidate cannot be promoted.
        self.assertEqual(result['decisions'],dict(full='unknown',body='unchanged'))

    def test_cli_invalid_source_preserves_existing_destination(self):
        root=p.h.ROOT/'.build/debug-output';root.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(dir=root,prefix='context24-') as tmp:
            marker=Path(tmp)/'keep';marker.write_text('preserved')
            r=subprocess.run([sys.executable,str(p.h.ROOT/'scripts/settings_context_probe.py'),
                '--previous','missing.json','--output',tmp],capture_output=True,text=True,timeout=30)
            self.assertNotEqual(r.returncode,0);self.assertEqual(marker.read_text(),'preserved')


if __name__=='__main__':unittest.main()
