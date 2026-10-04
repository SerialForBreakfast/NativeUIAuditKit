"""Source-pinned collection extensions; no live captures or data admission."""
import json
import unittest
from unittest.mock import patch
import human_annotation_review as h
import intake_native76 as intake
from harvest_sidecar_v2 import appearance_digest_source, recipe_hash
from test_native84 import recipe
from test_native83 import CollectionTests


class Canvas101Tests(unittest.TestCase):
    def test_context_identity_and_old_null_stability(self):
        r=recipe(True);old=recipe_hash(r)
        r['appearance']['canvas']['collectionContext']=None
        self.assertEqual(old,recipe_hash(r))
        hashes=set()
        for style in ('mixed_items','sectioned','small_controls'):
            r['appearance']['canvas'].update(collectionStyle=style,contrastNeighbors=True)
            self.assertIn(':contrast=true',appearance_digest_source(r));hashes.add(recipe_hash(r))
        for context in ('city','orbit','collage','checkerboard'):
            r['appearance']['canvas'].update(collectionStyle='sectioned',contrastNeighbors=None,collectionContext=context)
            self.assertIn(':collection=sectioned:collectionContext='+context,appearance_digest_source(r))
            hashes.add(recipe_hash(r))
        self.assertEqual(len(hashes),7)

    def test_conflicting_or_unknown_fields_fail(self):
        for changes in (dict(collectionContext='unknown'),dict(collectionContext='city'),
                        dict(contrastNeighbors=False),dict(collectionStyle='sectioned',collectionContext='city',contrastNeighbors=True),
                        dict(collectionStyle='sectioned',contrastNeighbors=1)):
            r=recipe(True);r['appearance']['canvas'].update(changes)
            with self.assertRaises(ValueError):appearance_digest_source(r)


class PartialReceiptTests(CollectionTests):
    def test_partial_campaign_is_never_silently_completed(self):
        selection=intake.collection_selection(self.root)
        p=self.root/'group-0/export-0/campaign-receipt.json';d=h.read(p)
        d['outcome']='completed_with_failures';p.write_text(json.dumps(d))
        with self.assertRaisesRegex(ValueError,'source_receipt'):
            intake.verify_selection(self.root,selection,expected_pairs=36)
        # Explicit case-level inspection still requires completed, byte-bound cases.
        self.assertEqual(len(intake.verify_selection(self.root,selection,expected_pairs=36,allow_completed_cases=True)),36)
        d['case_accounting']['case-0']['state']='failed';p.write_text(json.dumps(d))
        with self.assertRaisesRegex(ValueError,'source_case_receipt'):
            intake.verify_selection(self.root,selection,expected_pairs=36,allow_completed_cases=True)

    def test_transition_condition_dispatch(self):
        with patch.object(intake,'validate_bundle'),patch.object(intake,'validate_case') as transition:
            intake.run_collection(self.root,self.root/'dispatch')
        self.assertEqual(transition.call_count,12)
        self.assertTrue(all(call.kwargs=={'directional':False} for call in transition.call_args_list))


if __name__=='__main__':unittest.main()
