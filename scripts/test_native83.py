import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image
import human_annotation_review as h
import intake_native76 as intake


class CollectionTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(dir=h.ROOT/'.build',prefix='native83-')
        self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)
        for group in range(4):
            base=self.root/f'group-{group}'/'export-0';base.mkdir(parents=True)
            cases=[];accounts={};files={}
            for i in range(9):
                n=group*9+i;ident=f'case-{n}'
                bundle=base/'splits/validation'/ident;bundle.mkdir(parents=True)
                names=['sample_focused.png','sample_unfocused.png'] if n<24 else ['before.png','after.png']
                for j,name in enumerate(names):Image.new('RGB',(4,4),(n,j,0)).save(bundle/name)
                if n>=24:h.write(bundle/'transition-case.json',dict(endpoints=[dict(image=name) for name in names]))
                members=[dict(path=p.name,bytes=p.stat().st_size,sha256=h.sha(p)) for p in sorted(bundle.iterdir())]
                cases.append(dict(case_id=ident,split_group='validation',independence_group='fixture_procedural_renderer_v1',recipe=dict(recipe_hash=str(n))))
                accounts[ident]=dict(case_id=ident,state='completed',recipe_hash=str(n),files=members);files[ident]=members
            h.write(base/'campaign-manifest.json',dict(campaign_id=f'group-{group}',cases=cases))
            path=base/'campaign-manifest.json'
            h.write(base/'campaign-receipt.json',dict(schema_version=1,outcome='completed',campaign_id=f'group-{group}',
                cases_count=9,input_manifest_bytes=path.stat().st_size,input_manifest_sha256=h.sha(path),case_accounting=accounts,files=files))

    def test_actual_entrypoint_accounts_for_rejected_semantics(self):
        with patch.object(intake,'validate_bundle',side_effect=ValueError('unsupported-test-only')), \
             patch.object(intake,'validate_case',side_effect=ValueError('unsupported-test-only')):
            intake.run_collection(self.root,self.root/'output')
        report=h.read(self.root/'output/intake.json')
        self.assertEqual(report['pairs'],36);self.assertEqual(report['uniqueDecodedImages'],72)
        self.assertEqual(report['consumerStates'],{'blocked':36})
        self.assertFalse(report['trainingEligible']);self.assertFalse(report['independentEvaluationEligible'])
        with self.assertRaises(ValueError):intake.run_collection(self.root,self.root/'output')

    def test_wrong_source_roles_and_missing_case_fail(self):
        path=self.root/'group-0/export-0/campaign-manifest.json';doc=h.read(path)
        doc['cases'][0]['split_group']='train';path.write_text(json.dumps(doc))
        with self.assertRaisesRegex(ValueError,'source_role'):intake.collection_selection(self.root)
        doc['cases'].pop();path.write_text(json.dumps(doc))
        with self.assertRaisesRegex(ValueError,'receipt_accounting'):intake.collection_selection(self.root)

    def test_corrupt_source_stops_before_publication(self):
        path=self.root/'group-0/export-0/splits/validation/case-0/sample_focused.png'
        path.write_bytes(b'corrupt')
        with self.assertRaisesRegex(ValueError,'member_integrity'):intake.run_collection(self.root,self.root/'output')
        self.assertFalse((self.root/'output').exists())


if __name__=='__main__':unittest.main()
