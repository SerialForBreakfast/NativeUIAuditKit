import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import human_annotation_review as h
from harvest_sidecar_v2 import recipe_hash, appearance_digest_source
from focus_corrected_transition_audit import validate_case
from synth05_receive import receive


class Native76Tests(unittest.TestCase):
    def setUp(self):
        self.root=h.ROOT/'reports/work/NATIVE-INTAKE-76/received/ttr-native-table-directional12-20261003-r1/recovered-directional-export'
        if not self.root.exists():self.skipTest('retained producer corpus absent')
        doc=h.read(self.root/'campaign-manifest.json')
        self.case=doc['cases'][0]
        self.evidence=self.root/'splits/validation'/self.case['case_id']/'transition-case.json'

    def test_source_recipe_hash_and_reject_unsupported_shapes(self):
        recipe=self.case['recipe']
        self.assertEqual(recipe_hash(recipe),recipe['recipe_hash'])
        for fields in ({'version':2},{'width':True},{'width':1401},{'x':401},{'rowHeight':79},{'richContent':True}):
            bad=copy.deepcopy(recipe);bad['appearance']['canvas']['nativeTable'].update(fields)
            with self.assertRaises(ValueError):appearance_digest_source(bad)
        for fields in ({'presentation':'buttons'},{'selectedIndex':0},{'columns':2},{'fillViewport':True}):
            bad=copy.deepcopy(recipe);bad['appearance']['canvas'].update(fields)
            with self.assertRaises(ValueError):appearance_digest_source(bad)

    def test_real_directional_acceptance_does_not_assert_stationary(self):
        raw,b,a=validate_case(self.root,self.evidence,self.case,directional=True)
        self.assertNotEqual(b['focus'],a['focus'])
        with self.assertRaisesRegex(ValueError,'stationary_.*offset'):
            validate_case(self.root,self.evidence,self.case,stationary=True)
        original=h.read
        for mutation in (dict(cleanup='unknown'),dict(action_receipt=None)):
            bad=copy.deepcopy(raw);bad.update(mutation)
            def read(path):return bad if Path(path)==self.evidence else original(path)
            with patch.object(h,'read',side_effect=read):
                with self.assertRaises((ValueError,TypeError)):
                    validate_case(self.root,self.evidence,self.case,directional=True)

    def test_parameterized_transfer_rejects_paths_before_writes(self):
        with tempfile.TemporaryDirectory(dir=h.ROOT/'.build',prefix='native76-test-') as td:
            root=Path(td)/'absent'
            for entry in (('../bad.tar.gz',1,'0'*64),('bad.zip',1,'0'*64),('bad.tar.gz',0,'0'*64)):
                with self.assertRaises(ValueError):receive(Path(td),root,[entry])
                self.assertFalse(root.exists())


class NativeV3RetainedTests(unittest.TestCase):
    def test_v3_directional_preserves_cleanup_and_focus_checks(self):
        root=h.ROOT/'reports/work/RESIDUAL-160/artifacts/native24-r1/extracted/ttr-native-table-appearance24-20261005-r1'
        if not root.exists():self.skipTest('retained native v3 corpus absent')
        count=0
        for folder in ('pilot','remaining'):
            for case in h.read(root/folder/'campaign-manifest.json')['cases']:
                if case['transition']['condition']!='focus_moved':continue
                evidence=root/folder/'splits/validation'/case['case_id']/'transition-case.json'
                raw,b,a=validate_case(root,evidence,case,directional=True)
                self.assertNotEqual(b['focus'],a['focus']);count+=1
                original=h.read
                for field,value in [('cleanup','unknown'),('mutation_receipt',{})]:
                    bad=copy.deepcopy(raw);bad[field]=value
                    def read(path):return bad if Path(path)==evidence else original(path)
                    with patch.object(h,'read',side_effect=read):
                        with self.assertRaisesRegex(ValueError,'directional_action_cleanup'):
                            validate_case(root,evidence,case,directional=True)
        self.assertEqual(count,8)


if __name__=='__main__':unittest.main()
