"""Generated receipt regressions; no retained dataset or runtime required."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
import human_annotation_review as h
from intake_native76 import verify_selection


class ReceiptTests(unittest.TestCase):
    def replace_receipt(self, receipt):
        # Mutate only this test's temporary fixture; production writers stay exclusive.
        (self.root/'export.json').write_text(json.dumps(receipt))

    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(dir=h.ROOT/'.build',prefix='intake82-')
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.selection=dict(version=1,pairs=24,endpoint_images=48,source_role='calibration',
            ancestry='fixture_procedural_renderer_v1',cases=[])
        cases=[];accounts={};files={}
        for i in range(24):
            ident=f'case-{i}';folder=self.root/ident;folder.mkdir()
            h.write(folder/'test-only.json',dict(testOnly=True,index=i))
            path=folder/'test-only.json'
            members=[dict(path=path.name,bytes=path.stat().st_size,sha256=h.sha(path))]
            recipe=h.digest(['recipe',i])
            cases.append(dict(case_id=ident,recipe=dict(recipe_hash=recipe)))
            self.selection['cases'].append(dict(case_id=ident,campaign_id='test-campaign',
                bundle=ident,source_receipt='export.json',members=members))
            accounts[ident]=dict(case_id=ident,state='completed',recipe_hash=recipe,files=members)
            files[ident]=members
        h.write(self.root/'campaign-manifest.json',dict(campaign_id='test-campaign',cases=cases))
        manifest=self.root/'campaign-manifest.json'
        self.receipt=dict(schema_version=1,outcome='completed',campaign_id='test-campaign',
            input_manifest_bytes=manifest.stat().st_size,input_manifest_sha256=h.sha(manifest),
            manifest_sha256='semantic-not-byte-hash',case_accounting=accounts,files=files)
        h.write(self.root/'export.json',self.receipt)

    def test_completed_batch_and_semantic_hash_separation(self):
        self.assertEqual(len(verify_selection(self.root,self.selection)),24)
        for count in (True,0,129,36):
            with self.assertRaises(ValueError):verify_selection(self.root,self.selection,expected_pairs=count)

    def test_missing_or_partial_receipt(self):
        selection=copy.deepcopy(self.selection);selection['cases'][0]['source_receipt']='absent.json'
        with self.assertRaises((ValueError,OSError)):verify_selection(self.root,selection)
        for fields in (dict(outcome='partial'),dict(schema_version=2),dict(campaign_id='wrong')):
            self.replace_receipt(dict(self.receipt,**fields))
            with self.assertRaisesRegex(ValueError,'source_receipt'):verify_selection(self.root,self.selection)

    def test_manifest_and_case_binding(self):
        for fields in (dict(input_manifest_sha256='wrong'),dict(input_manifest_bytes=True)):
            self.replace_receipt(dict(self.receipt,**fields))
            with self.assertRaisesRegex(ValueError,'manifest_bytes'):verify_selection(self.root,self.selection)
        for field,value in (('state','failed'),('case_id','wrong'),('recipe_hash','wrong'),('files',[])):
            receipt=copy.deepcopy(self.receipt);receipt['case_accounting']['case-0'][field]=value
            self.replace_receipt(receipt)
            with self.assertRaisesRegex(ValueError,'case_receipt'):verify_selection(self.root,self.selection)

    def test_member_bytes_inventory_and_path_safety(self):
        for mutation in ('changed-hash','duplicate','traversal'):
            selection=copy.deepcopy(self.selection);case=selection['cases'][0]
            if mutation=='changed-hash':case['members'][0]['sha256']='0'*64
            elif mutation=='duplicate':case['members'].append(case['members'][0])
            else:case['bundle']='../outside'
            with self.assertRaises(ValueError):verify_selection(self.root,selection)
        h.write(self.root/'case-0/extra.json',{})
        with self.assertRaisesRegex(ValueError,'unlisted_member'):verify_selection(self.root,self.selection)


if __name__=='__main__':unittest.main()
