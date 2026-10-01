import unittest
import json
from focus_retained_next import disposition, inventory, prepare_review, experiment_proposal, h
import test_human_recording_review as recording_tests


class RetainedSelectionTests(unittest.TestCase):
    def test_reviewed_pixels_take_precedence(self):
        self.assertEqual(disposition('postInputSettled','a',{'a'},{'a'}),'already-reviewed')

    def test_duplicate_is_not_new_support(self):
        self.assertEqual(disposition('postInputUnverified','a',set(),{'a'}),'duplicate-observation')

    def test_transition_never_becomes_review_candidate(self):
        for role in ('transition','unknown'):
            self.assertEqual(disposition(role,'a',set(),set()),'transition-excluded')

    def test_unverified_is_diagnostic_not_settled(self):
        self.assertEqual(disposition('postInputUnverified','a',set(),set()),'unreviewed-candidate')


class InventoryTests(unittest.TestCase):
    def setUp(self):
        self.fixture=recording_tests.RecordingTests(); self.fixture.setUp()
        self.source=self.fixture.source; self.root=self.fixture.f.root
        path=self.source/'events.jsonl'
        rows=[json.loads(s) for s in path.read_text().splitlines()]
        for row in rows: row['frame']['_0']['dimensions']=dict(width=100,height=60)
        path.write_text('\n'.join(json.dumps(r) for r in rows))

    def tearDown(self): self.fixture.tearDown()

    def test_all_accounted_and_preserved(self):
        before=h.sha(self.source/'events.jsonl')
        doc=inventory(self.source,set(),self.root/'report')
        self.assertEqual(doc['counts'],{'unreviewed-candidate':2})
        self.assertEqual(h.sha(self.source/'events.jsonl'),before)
        self.assertFalse(doc['trainingEligible'])

    def test_corrupt_and_missing_are_blocked_not_dropped(self):
        paths=list((self.source/'images').glob('*.png'))
        paths[0].write_bytes(b'bad'); paths[1].unlink()
        doc=inventory(self.source,set(),self.root/'report')
        self.assertEqual(doc['counts'],{'blocked':2})

    def test_wrong_target(self):
        p=self.source/'manifest.json'; doc=json.loads(p.read_text());doc['targetDeviceID']='wrong'
        p.write_text(json.dumps(doc))
        self.assertEqual(inventory(self.source,set(),self.root/'report')['counts'],{'blocked':2})

    def test_duplicate_sequence_rejected(self):
        p=self.source/'events.jsonl';p.write_text(p.read_text()+'\n'+p.read_text().splitlines()[0])
        with self.assertRaises(ValueError):inventory(self.source,set(),self.root/'report')

    def test_real_import_proposals_and_blocked_experiment(self):
        batch=self.fixture.prepare()
        result=prepare_review(batch,self.root/'proposals')
        self.assertFalse(result['trainingEligible'])
        self.assertTrue(all(not r['humanConfirmed'] for r in result['frames']))
        audit=self.root/'audit.json'
        h.write(audit,dict(protocol={'path':'baseline'},trainingIDs=['old'],validationIDs=['reserved'],configuration={},selection={}))
        proposal=experiment_proposal(audit,self.root/'proposals/selection.json',self.root/'proposal.json')
        self.assertFalse(proposal['launchEligible']);self.assertIsNone(proposal['newControlIDs'])
        self.assertEqual(proposal['validationIDs'],['reserved'])
        for p in (batch.parent/'editor').glob('*.json'):
            self.assertFalse(any(h.read(p)['flags'].values()))
        changed=h.read(self.root/'proposals/selection.json');changed['frames'].reverse()
        (self.root/'proposals/selection.json').write_text(json.dumps(changed))
        with self.assertRaises(ValueError):experiment_proposal(audit,self.root/'proposals/selection.json',self.root/'no.json')


if __name__=='__main__': unittest.main()
