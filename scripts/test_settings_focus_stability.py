import copy
import unittest
import subprocess
import sys
import tempfile
from pathlib import Path
import numpy as np
from PIL import Image
import settings_focus_stability as s


class StabilityTests(unittest.TestCase):
    def prediction(self):return dict(tracking=dict(status='matched'),decision='unknown',illuminationWarning=False)

    def test_fixed_noise_passes_while_content_cancellation_fails(self):
        a=np.full((256,256,3),100,dtype=np.uint8)
        for name,b,expected in [('identical',a,'unchanged'),('one_level',a+1,'unchanged'),
            ('brighten',a+30,'unknown'),('balanced_content',np.concatenate((a[:128]+30,a[128:]-30)),'unknown')]:
            with self.subTest(name=name):
                m=s.measure(Image.fromarray(a),Image.fromarray(b))
                self.assertEqual(s.extend(self.prediction(),m,settings_context=True)['decision'],expected)

    def test_gates_and_existing_changes_preserved(self):
        m=dict(mean=0.,p95=0.,changedFraction=0.,maximum=0.)
        p=self.prediction()
        self.assertEqual(s.extend(p,m,settings_context=False)['decision'],'unavailable')
        for decision in ('arrival','departure','unchanged','unavailable'):
            p['decision']=decision
            self.assertEqual(s.extend(p,m,settings_context=True)['decision'],decision)
        p=self.prediction();p['illuminationWarning']=True
        self.assertEqual(s.extend(p,m,settings_context=True)['decision'],'unknown')
        p=self.prediction();p['tracking']['status']='unavailable'
        self.assertEqual(s.extend(p,m,settings_context=True)['decision'],'unavailable')

    def test_bad_metrics_and_dimensions(self):
        with self.assertRaisesRegex(ValueError,'dimensions'):s.measure(Image.new('RGB',(8,8)),Image.new('RGB',(8,8)))
        with self.assertRaisesRegex(ValueError,'metrics'):s.extend(self.prediction(),dict(mean=float('nan')),settings_context=True)

    def test_action_decisions_never_use_truth(self):
        def rows(*ds):return [dict(decision=d,expected='arbitrary') for d in ds]
        self.assertEqual(s.action_outcome(rows('arrival','departure','unchanged'),True),'switch')
        self.assertEqual(s.action_outcome(rows('arrival','arrival'),True),'ambiguous')
        self.assertEqual(s.action_outcome(rows('unchanged','unchanged'),True),'unchanged')
        self.assertEqual(s.action_outcome(rows('unknown'),True),'abstained')
        self.assertEqual(s.action_outcome(rows('unchanged'),False),'incomplete')

    def test_change_guard_requires_all_quadrants(self):
        p=dict(decision='arrival')
        self.assertEqual(s.guard(p,dict(directionalCoverage=dict(arrival=[1,1,1,1])))['decision'],'arrival')
        self.assertEqual(s.guard(p,dict(directionalCoverage=dict(arrival=[1,1,0,1])))['decision'],'unknown')
        self.assertEqual(s.guard(p,None)['decision'],'unknown')
        self.assertEqual(s.guard(dict(decision='unchanged'),None)['decision'],'unchanged')

    def test_real_cli_rejects_colliding_output_before_reading_inputs(self):
        root=s.h.ROOT/'.build/debug-output';root.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(dir=root,prefix='stability-test-') as tmp:
            marker=Path(tmp)/'keep';marker.write_text('preserved')
            r=subprocess.run([sys.executable,str(s.h.ROOT/'scripts/settings_focus_stability.py'),
                '--semantics','missing.json','--output',tmp],capture_output=True,text=True,timeout=30)
            self.assertNotEqual(r.returncode,0);self.assertEqual(marker.read_text(),'preserved')

    def test_prediction_inputs_unchanged(self):
        p=self.prediction();original=copy.deepcopy(p)
        m=s.measure(Image.new('RGB',(256,256)),Image.new('RGB',(256,256)))
        s.guard(s.extend(p,m,settings_context=True),m)
        self.assertEqual(p,original)


if __name__=='__main__':unittest.main()
