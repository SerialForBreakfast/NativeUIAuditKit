"""Qualify the retained native corpus audit without new capture."""
import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import research_queue as q
import sdk_dataset505 as a


class CorpusTests(unittest.TestCase):
    path=q.ROOT/'reports/work/SDK504/extracted/packet/manifest.json'

    def test_real_delivery_preserves_roles_and_reports_missing_evidence(self):
        r=a.audit(self.path)
        self.assertEqual(r['counts']['frames'],2);self.assertEqual(r['counts']['focused'],2)
        self.assertEqual(r['counts']['classNames'],0);self.assertEqual(r['ancestryGroups'],1)
        self.assertEqual({c['split'] for c in r['cases']},{'test'})
        self.assertEqual({f['role'] for c in r['cases'] for f in c['frames']},{'single'})
        self.assertFalse(r['trainingEligible']);self.assertEqual(r['verifiedNavigationPairs'],0)
        self.assertEqual({x['id'] for x in r['requirements']},{'observed-no-focus','action-linked-transitions','detector-label-coverage'})

    def test_changed_members_duplicate_cases_and_role_changes_fail(self):
        original=q.load;manifest=original(self.path)
        for kind,reason in [('bytes','sdk_dataset_member_changed'),('duplicate','sdk_dataset_duplicate_case'),
                            ('admission','sdk_dataset_frame_admission')]:
            doc=copy.deepcopy(manifest)
            if kind=='bytes':doc['members'][0]['bytes']+=1
            elif kind=='duplicate':doc['cases'].append(copy.deepcopy(doc['cases'][0]))
            else:doc['cases'][0]['frames'][0]['labelAdmission']='training'
            def load(path):return doc if Path(path)==self.path else original(path)
            with self.subTest(kind=kind),patch.object(q,'load',side_effect=load),self.assertRaisesRegex(ValueError,reason):
                a.audit(self.path)
