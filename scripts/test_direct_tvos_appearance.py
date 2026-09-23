"""Offline integration of the closed appearance pilot, without simulator access."""
import copy
import hashlib
import json
import subprocess
import sys
import unittest
from unittest.mock import patch

import direct_tvos_appearance as a
import direct_tvos_capture as d
import direct_tvos_resume as resume
import test_direct_tvos_resume as fixtures
from focus_dataset_contract import ROOT, FocusDataError


class AppearanceTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fixtures.ResumeTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.root = self.fixture.root

    def cli(self, script, *args):
        return subprocess.run([sys.executable, str(ROOT/'scripts'/script), *map(str,args)],
                              capture_output=True, text=True, timeout=180)

    def receipt(self):
        with patch.object(d, 'catalog', a.catalog):
            path = self.fixture.receipt('appearance', 0, 24)
        canonical = path.parent/'direct-capture.json'
        path.rename(canonical)
        return canonical

    def test_catalog_and_actual_plan_cli(self):
        plan = a.catalog()
        self.assertEqual((len(plan['recipes']),plan['expectedPairs'],plan['expectedFrames']), (24,76,100))
        self.assertEqual(len(d.catalog()['recipes']),42)
        self.assertEqual(len(d.catalog(True)['recipes']),1)
        out = self.root/'catalog.json'
        result = self.cli('direct_tvos_capture.py','--plan','--appearance','--output',out)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(json.loads(out.read_text()),plan)
        self.assertEqual(self.cli('direct_tvos_capture.py','--plan','--appearance','--output',out).returncode,2)
        bad=copy.deepcopy(plan); bad['recipes'][0]['seed']=7
        with self.assertRaises(FocusDataError): d.validate_catalog(bad)
        bad=copy.deepcopy(plan); bad['sourceHashes']['extra']='0'*64
        with self.assertRaises(FocusDataError): d.validate_catalog(bad)
        plan['sourceHashes'].clear()
        self.assertTrue(a.catalog()['sourceHashes'])

    def test_offline_preflight_and_pre_mutation_guards(self):
        source=self.root/'source'; source.mkdir(); (source/'file').write_bytes(b'pinned')
        pins={'file':hashlib.sha256(b'pinned').hexdigest()}
        with patch.object(a,'PINS',pins), patch.object(d,'bind_target',side_effect=AssertionError('device I/O')):
            plan=a.catalog()
            args=(plan,self.fixture.target['simulatorUDID'],'http://127.0.0.1:8080',self.root/'capture')
            report=d.offline_preflight(*args,source)
            self.assertTrue(report['configurationValid'])
            for field in ('executionAuthorized','runtimeQualified','trainingEligible'):
                self.assertFalse(report[field])
            self.assertFalse((self.root/'capture').exists())
            for target,endpoint,out in [('booted',args[2],args[3]),(args[1],'http://192.168.1.1:8080',args[3]),
                                        (args[1],args[2],source)]:
                with self.subTest(target=target,endpoint=endpoint,out=out), self.assertRaises(ValueError):
                    d.execute(plan,target,endpoint,out,producer_source=source)
            with self.assertRaisesRegex(FocusDataError,'source_required'): d.execute(*args)
            with self.assertRaisesRegex(FocusDataError,'continuation_unsupported'):
                d.execute(*args,producer_source=source,continuation={})
            (source/'file').write_bytes(b'changed')
            with self.assertRaisesRegex(FocusDataError,'changed_appearance_source'):
                d.execute(*args,producer_source=source)

    def test_complete_receipt_actual_intake_and_no_training_upgrade(self):
        path=self.receipt(); doc=json.loads(path.read_text())
        self.assertEqual(d.validate_capture(doc,path.parent),76)
        result=self.cli('direct_tvos_capture.py','--validate',path)
        self.assertEqual(result.returncode,0,result.stderr)
        crops=self.root/'crops'
        result=self.cli('direct_focus_manifest.py','--capture',path,'--output',crops)
        self.assertEqual(result.returncode,0,result.stderr)
        manifest=json.loads((crops/'focus_dataset_manifest.json').read_text())
        self.assertEqual(len(manifest['pairs']),76)
        self.assertEqual(manifest['evidenceKind'],'test-only')
        from focus_training_preflight import preflight
        self.assertFalse(preflight(crops,'appearance-test')['launchEligible'])
        with self.assertRaisesRegex(FocusDataError,'pilot_catalog_required'): resume.audit_chain([path])

    def test_partial_corrupt_and_false_focus_rejected(self):
        path=self.receipt(); doc=json.loads(path.read_text())
        variants=[]
        bad=copy.deepcopy(doc); bad['recipes'].pop(); variants.append(bad)
        bad=copy.deepcopy(doc); bad['state']='failed'; variants.append(bad)
        bad=copy.deepcopy(doc); bad['recipes'][0]['frames'][0]['before']['scene']['is_settled']=False; variants.append(bad)
        bad=copy.deepcopy(doc); bad['targetPlanSourceHashes']={}; variants.append(bad)
        for bad in variants:
            with self.assertRaises(FocusDataError): d.validate_capture(bad,path.parent)
        frame=doc['recipes'][0]['frames'][0]
        image=path.parent/frame['path']; image.write_bytes(b'corrupt')
        with self.assertRaises(FocusDataError): d.validate_capture(doc,path.parent)

    def test_full_execution_adapter_offline(self):
        owner=self.fixture
        class OfflineFixture:
            deadline=None
            last_snapshot=None
            def __init__(self, endpoint): pass
            def request(self, path, body=None): return copy.deepcopy(owner.device)
        def frame(fixture,target,output,name,expected,recipe):
            return owner.frame(output,recipe,name,expected)
        out=self.root/'executed'
        with patch.object(a,'check_source',return_value=dict(a.PINS)), \
             patch.object(d,'bind_target',return_value=owner.target), \
             patch.object(d,'Fixture',OfflineFixture), patch.object(d,'capture_frame',side_effect=frame):
            doc=d.execute(a.catalog(),owner.target['simulatorUDID'],owner.target['endpoint'],out,
                          producer_source=self.root)
        self.assertEqual(d.validate_capture(doc,out),76)
        self.assertTrue((out/'direct-capture.json').is_file())
        # Temporary mocked runtime evidence is never published or used for training.


if __name__=='__main__': unittest.main()
