"""Unknown native episode frames remain diagnostics, not image labels."""
import copy
import tempfile
import unittest
from pathlib import Path
from PIL import Image
import research_queue as q
from experiment_templates import pin
from test_sdk_packet502 import sample
import sdk_endpoint_focus520 as m

class EpisodeScoringTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(dir=q.ROOT/'.build');self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        dummy=self.root/'model';dummy.write_bytes(b'contract-only')
        self.request=dict(version='sdk-endpoint-episode-v1',id='test-episode-score',episodes=[],
                          models=dict(baseline=pin(dummy),candidate=pin(dummy)),tool=pin(dummy))
        frames=[]
        for i in range(3):
            image=self.root/f'{i}.png';Image.new('RGB',(1,1),(i,0,0)).save(image)
            e=sample(image);e['captureID']=f'capture-{i}'
            for side in ('before','after'):
                if i==0:e[side]['focusID']=None
                if i==2:
                    e[side]['elements'][0]['enabled']=False
                    e[side]['elements'][0]['observedState']['enabled']=False
            path=self.root/f'{i}.json';q.save(path,e)
            frames.append(dict(image=pin(image),evidence=pin(path)))
        self.episode=dict(version='sdk-episode-request-v1',id='test-episode',episodes=[dict(
            id='test-episode',scenario='disabled-focus',group='test-group',role='review_only',frames=frames)])
        self.save_episode()
    def save_episode(self):
        p=self.root/'episode.json';q.save(p,self.episode,replace=p.exists());self.request['episodes']=[pin(p)]
    def test_disabled_frame_scores_without_becoming_negative(self):
        frames=m.prepare(self.request)
        self.assertEqual([f['truthKnown'] for f in frames],[True,True,False])
        self.assertEqual([len(f['controls']) for f in frames],[1,1,1])
        self.assertEqual(frames[-1]['nativeFocusState'],'focused')
        self.assertFalse(frames[-1]['controls'][0]['enabled'])
        boxes=[[0,0,1,1]]
        self.assertEqual(m.frame_outcome([.9],boxes,frames[0]),'false-selection')
        self.assertEqual(m.frame_outcome([.9],boxes,frames[1]),'correct')
        self.assertEqual(m.frame_outcome([.9],boxes,frames[2]),'unknown')
        self.assertEqual(m.frame_outcome([.0],boxes,frames[2]),'unknown')
    def test_all_frame_inputs_pinned(self):
        p=self.root/'request.json';q.save(p,self.request);s=m.build(p);q.validate(s);q.verify_pins(s)
        for f in self.episode['episodes'][0]['frames']:
            for ref in f.values():self.assertIn(ref,s['inputs']);self.assertIn(ref['path'],s['evidence']['reads'])
    def test_changed_evidence_rejected(self):
        ref=self.episode['episodes'][0]['frames'][0]['evidence'];(q.ROOT/ref['path']).write_text('{}')
        with self.assertRaises(ValueError):m.prepare(self.request)
    def test_duplicate_episode_rejected(self):
        self.request['episodes']*=2
        with self.assertRaisesRegex(ValueError,'endpoint_episode_membership'):m.prepare(self.request)
    def test_hidden_controls_not_cropped(self):
        ref=self.episode['episodes'][0]['frames'][2]['evidence'];p=q.ROOT/ref['path'];e=q.load(p)
        for side in ('before','after'):e[side]['elements'][0]['hidden']=True
        q.save(p,e,replace=True);ref.update(pin(p));self.save_episode()
        self.assertEqual(m.prepare(self.request)[-1]['controls'],[])
    def test_no_focus_does_not_require_boxes(self):
        ref=self.episode['episodes'][0]['frames'][0]['evidence'];p=q.ROOT/ref['path'];e=q.load(p)
        for side in ('before','after'):e[side]['elements']=[]
        q.save(p,e,replace=True);ref.update(pin(p));self.save_episode()
        f=m.prepare(self.request)[0];self.assertEqual(m.frame_outcome([],[],f),'correct-abstention')

if __name__=='__main__':unittest.main()
