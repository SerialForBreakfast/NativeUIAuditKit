#!/usr/bin/env python3
import json, shutil, subprocess, sys, tempfile, unittest
from pathlib import Path
from training_preflight import PreflightError, validate
ROOT=Path(__file__).resolve().parent.parent
class Tests(unittest.TestCase):
 def setUp(self):
  (ROOT/'.build/debug-output').mkdir(parents=True,exist_ok=True); self.d=Path(tempfile.mkdtemp(dir=ROOT/'.build/debug-output'))
  self.ds=self.d/'ds'; (self.ds/'images').mkdir(parents=True); (self.ds/'labels').mkdir()
  for s in ('train','val','test'):
   (self.ds/'images'/s).mkdir(); (self.ds/'labels'/s).mkdir(); (self.ds/'images'/s/'a.png').write_bytes(b'x'); (self.ds/'labels'/s/'a.txt').write_text('')
  (self.ds/'dataset.yaml').write_text('names: []\n'); self.w=self.d/'best.pt'; self.w.write_bytes(b'w'); self.tax=self.d/'map.json'; self.tax.write_text('{}')
 def tearDown(self): shutil.rmtree(self.d)
 def test_valid_is_not_launch_eligible(self):
  r=validate(self.ds,self.w,None,self.d/'out',self.tax); self.assertTrue(r['configurationValid']); self.assertFalse(r['launchEligible']); self.assertEqual(r['epochs'],150)
 def test_conflict_missing_pixels_and_collision_fail(self):
  with self.assertRaisesRegex(PreflightError,'conflict'): validate(self.ds,self.w,self.w,self.d/'out',self.tax)
  (self.ds/'images'/'test'/'a.png').unlink()
  with self.assertRaisesRegex(PreflightError,'ineligible_corpus'): validate(self.ds,self.w,None,self.d/'out',self.tax)
  self.setUp(); (self.d/'out').mkdir()
  with self.assertRaisesRegex(PreflightError,'output_collision'): validate(self.ds,self.w,None,self.d/'out',self.tax)
 def test_cli_is_side_effect_free_and_separates_modes(self):
  before={p.relative_to(ROOT) for p in (ROOT/'NativeUITrainer').glob('.ultralytics/**') if p.is_file()} if (ROOT/'NativeUITrainer').exists() else set()
  command=[sys.executable,str(ROOT/'scripts/train_ios_model.py'),'--validate-only','--dataset',str(self.ds),'--initial-weights',str(self.w),'--output-dir',str(self.d/'runs')]
  result=subprocess.run(command,capture_output=True,text=True)
  self.assertEqual(result.returncode,0,result.stderr); self.assertIn('"configurationValid": true',result.stdout); self.assertIn('"launchEligible": false',result.stdout)
  after={p.relative_to(ROOT) for p in (ROOT/'NativeUITrainer').glob('.ultralytics/**') if p.is_file()} if (ROOT/'NativeUITrainer').exists() else set()
  self.assertEqual(before,after)
  conflict=subprocess.run(command+['--resume',str(self.w)],capture_output=True,text=True)
  self.assertNotEqual(conflict.returncode,0); self.assertIn('initial_weights_and_resume_conflict',conflict.stdout)
if __name__=='__main__': unittest.main()
