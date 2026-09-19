#!/usr/bin/env python3
import json, shutil, tempfile, unittest
from pathlib import Path
from regression_selector import SelectorError, build
ROOT=Path(__file__).resolve().parent.parent
class Tests(unittest.TestCase):
 def setUp(self):
  (ROOT/'.build/debug-output').mkdir(parents=True,exist_ok=True); self.d=Path(tempfile.mkdtemp(dir=ROOT/'.build/debug-output'))
  self.rows=[]
  for i in range(4):
   im=self.d/f'{i}.png'; la=self.d/f'{i}.txt'; im.write_bytes(f'image{i}'.encode()); la.write_text(str(i))
   self.rows.append({'id':f'i{i}','image':str(im),'label':str(la),'sourceSplit':'test','platform':'iOS','family':f'f{i}','width':100+i,'height':100,'classes':[i],'smallElement':i==0})
 def tearDown(self): shutil.rmtree(self.d)
 def test_repeatable_and_explicit_coverage(self):
  a=build(self.rows,[],2); self.assertEqual(a,build(self.rows,[],2)); self.assertEqual(len(a['members']),2); self.assertEqual(len(a['coverageExceptions']['uncoveredClasses']),2)
 def test_missing_and_leakage_reject(self):
  Path(self.rows[0]['image']).unlink()
  with self.assertRaisesRegex(SelectorError,'missing'): build(self.rows,[])
  self.setUp()
  with self.assertRaisesRegex(SelectorError,'leakage'): build(self.rows,[{'id':'other','family':'f1'}])
if __name__=='__main__': unittest.main()
