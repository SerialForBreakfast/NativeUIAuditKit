"""Check duplicate events and fail-closed capture admission."""
import copy
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path
import capture_detector_inputs as adapter


class CaptureInputsTests(unittest.TestCase):
    def test_prepared_review_value_matches_consumer_contract(self):
        scene=dict(scene_width=100,scene_height=80,elements=[],focus_observation=dict(plannedFocusIDs=[]))
        frame=dict(id='a',case='case',focus=None,sha256='a',path='frame.png',profile='standard',
                   before=dict(scene=scene),after=dict(scene=scene))
        artifact=dict(path='/Volumes/training-drive/data/NUIAK/HCF371/test.json',sha256='a',
                      plan=dict(trainingEligible=False,cases=[dict(id='case',role='development',group='g',family='no-focus')]))
        with tempfile.TemporaryDirectory(dir=adapter.q.ROOT/'.build',prefix='capture-input-test-') as folder:
            with patch.object(adapter.q,'digest',return_value='a'), patch.object(adapter.q,'load',return_value=dict(complete=True,cleanup=True,frames=[frame])), \
                 patch.object(adapter.native343,'signature'), patch.object(adapter.shutil,'copyfile'), \
                 patch.object(adapter,'pin',return_value=dict(path='test',sha256='a')), patch.object(adapter.Image,'open') as opened:
                opened.return_value.__enter__.return_value.size=(100,80)
                labels=adapter.prepare(artifact,Path(folder))
            self.assertEqual(labels['labelReview'],'unknown')
            self.assertEqual(labels['labelSource'],'native-observation')
            self.assertFalse(labels['labelsComplete'])

    def row(self):
        return dict(sha256='a'*64,group='g',controls=[dict(id='a',state='unfocused')],events=[dict(id='first',noFocus=True)])

    def test_duplicate_events_preserved(self):
        first=self.row(); second=copy.deepcopy(first); second['events'][0]['id']='second'
        result=adapter.unique_rows([first,second])
        self.assertEqual(len(result),1)
        self.assertEqual(len(result[0]['events']),2)

    def test_conflicting_group_or_truth_fails(self):
        for field,value in [('group','other'),('controls',[dict(id='a',state='focused')])]:
            first=self.row(); second=copy.deepcopy(first); second[field]=value
            with self.assertRaisesRegex(ValueError,'capture_duplicate_conflict'):
                adapter.unique_rows([first,second])

    def test_empty_fails(self):
        with self.assertRaisesRegex(ValueError,'capture_frame_count'):adapter.unique_rows([])

    def test_training_role_and_changed_source_fail(self):
        artifact=dict(path='/Volumes/training-drive/data/NUIAK/HCF371/test.json',sha256='a',
                      plan=dict(trainingEligible=True,cases=[]))
        with patch.object(adapter.q,'digest',return_value='a'):
            with self.assertRaisesRegex(ValueError,'capture_role'):adapter.prepare(artifact,Path('.'))
        with patch.object(adapter.q,'digest',return_value='b'):
            with self.assertRaisesRegex(ValueError,'capture_changed'):adapter.prepare(artifact,Path('.'))


if __name__=='__main__':unittest.main()
