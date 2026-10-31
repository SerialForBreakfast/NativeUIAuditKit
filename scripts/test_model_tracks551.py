import unittest
from model_tracks551 import report,START,END
class TracksTests(unittest.TestCase):
    def text(self):return START+'\n| Track | Task | Prefix | Question | Inputs | State | Owner | Action |\n|---|---|---|---|---|---|---|---|\n| iOS | IOS | ios551- | Retain? | Pinned data | implementation | Maximum-mini-NUIAK | Prepare fit. |\n'+END
    def test_preparation_is_not_ready(self):
        t=report(self.text(),[])['tracks'][0];self.assertEqual(t['readyJobs'],0);self.assertEqual(t['state'],'implementation')
    def test_only_ready_and_same_kind_duration_count(self):
        rows=[dict(job='ios551-a',state='pending',displayState='ready',task='IOS',jobKind='training'),
              dict(job='old',state='complete',task='IOS',jobKind='training',wallSeconds=100),
              dict(job='fast',state='complete',task='IOS',jobKind='artifact',wallSeconds=1),
              dict(job='ios551-b',state='blocked',displayState='unselected',task='IOS',jobKind='training')]
        t=report(self.text(),rows)['tracks'][0];self.assertEqual(t['readySeconds'],100);self.assertEqual(t['readyJobs'],1);self.assertEqual(t['actionableBlockers'],[])
    def test_unknown_duration_not_ceiling(self):
        t=report(self.text(),[dict(job='ios551-a',state='pending',displayState='ready',task='IOS',jobKind='training')])['tracks'][0]
        self.assertEqual(t['readyUnknown'],1);self.assertEqual(t['readySeconds'],0)
    def test_invalid_definition_fails_without_queue_mutation(self):
        with self.assertRaisesRegex(ValueError,'definition'):report(self.text().replace('implementation','imagined'),[])
    def test_missing_is_explicit(self):self.assertTrue(report('',[])['error'])
if __name__=='__main__':unittest.main()
