"""Validation entrypoints must not require training or pixel-analysis packages."""
import os
from pathlib import Path
import subprocess
import unittest


class ImportBoundaryTests(unittest.TestCase):
    def test_real_review_interpreter_without_analysis_dependencies(self):
        root=Path(__file__).resolve().parent.parent
        python=root/'.venv-review/bin/python'
        if not python.is_file():self.skipTest('resident review interpreter unavailable')
        code='''
import sys, importlib.abc
class Block(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split('.')[0] in ('cv2','torch','ultralytics','coremltools'):
            raise RuntimeError('annotation validation loaded analysis dependency: '+fullname)
sys.meta_path.insert(0,Block())
sys.path.insert(0,'scripts')
import fixture_batch_review, reference_delivery
from test_fixture_reference import reference_scene
from harvest_sidecar_v2 import scene_check
assert scene_check(reference_scene(),(64,48),'ref-0')==4
print('validation-only reference import passed')
'''
        result=subprocess.run([str(python),'-c',code],cwd=root,text=True,capture_output=True,
                              timeout=30,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertIn('passed',result.stdout)


if __name__=='__main__':unittest.main()
