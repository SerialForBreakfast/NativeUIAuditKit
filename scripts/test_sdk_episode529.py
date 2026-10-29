import copy
import tempfile
import unittest
from pathlib import Path
from PIL import Image
import research_queue as q
import research_approval as approval
from experiment_templates import pin
from test_sdk_packet502 import sample
import sdk_episode529 as m

class EpisodeTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(dir=q.ROOT/'.build');self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)
    def event(self,seq):return dict(schemaVersion=1,processID='test-process',runID='test-run',sequence=seq,monotonicNanoseconds=19000+seq*100,
                                  source='nativeCallback',name='ui.focus',fields={'known':'true'},kind='focus')
    def request(self,ident='episode-a'):
        folder=self.root/ident;folder.mkdir();refs=[]
        for i in range(2):
            image=folder/f'{i}.png';Image.new('RGB',(1,1),(i,0,0)).save(image);e=sample(image)
            start=10000+i*1000;e.update(captureID=f'{ident}-{i}',captureStartNS=start,captureEndNS=start+1,observationEndNS=start+5)
            for j,side in enumerate(('before','after')):
                host=start-10 if j==0 else start+3;high=i*2+j+1
                e[side]['timeline']=dict(schemaVersion=1,processID='test-process',runID='test-run',highestSequence=high,producerDroppedEvents=0,
                    omittedEvents=0,events=[self.event(n) for n in range(1,high+1)],
                    clockBracket=dict(hostRequestStartNS=host,hostResponseEndNS=host+1,producerSampleNS=host+10000))
            p=folder/f'{i}.json';q.save(p,e);refs.append(dict(image=pin(image),evidence=pin(p)))
        return dict(version='sdk-episode-request-v1',id=ident,episodes=[dict(id=ident,scenario='unchanged-focus',group=ident,role='review_only',frames=refs)])
    def edit(self,r,index,fn):
        ref=r['episodes'][0]['frames'][index]['evidence'];p=q.ROOT/ref['path'];e=q.load(p);fn(e);q.save(p,e,replace=True);ref.update(pin(p))
    def test_full_episode_has_independent_eligibility(self):
        row=m.intake(self.request())['episodes'][0]
        self.assertTrue(row['eligibility']['temporalReview']);self.assertFalse(row['eligibility']['detectorTraining'])
        self.assertEqual([e['sequence'] for e in row['events']],[2,3,4]);self.assertEqual(row['transitions'][0]['observed'],'unchanged')
    def test_transition_frame_is_evidence_not_a_stable_image_label(self):
        r=self.request()
        self.edit(r,0,lambda e:e['issues'].append('registered_geometry_not_stable'))
        row=m.intake(r)['episodes'][0]
        self.assertTrue(row['eligibility']['temporalReview'])
        self.assertFalse(row['eligibility']['allFramesAligned'])
        self.assertFalse(row['frames'][0]['frameReviewable'])
        self.assertFalse(row['eligibility']['focusTraining'])
    def test_missing_history_keeps_static_work(self):
        r=self.request();self.edit(r,0,lambda e:e['before'].pop('timeline'))
        row=m.intake(r)['episodes'][0];self.assertTrue(row['eligibility']['staticDiagnostics']);self.assertFalse(row['eligibility']['temporalReview'])
    def test_event_gap_and_loss_remain_explicit(self):
        r=self.request()
        def drop(e):
            for side in ('before','after'):e[side]['timeline']['events']=[v for v in e[side]['timeline']['events'] if v['sequence']!=3]
        self.edit(r,1,drop);self.assertIn('episode_event_gap',m.intake(r)['episodes'][0]['reasons'])
    def test_old_queue_gap_does_not_invalidate_complete_new_window(self):
        r=self.request()
        for index in (0,1):
            self.edit(r,index,lambda e:[e[side]['timeline'].update(producerQueueGap=True) for side in ('before','after')])
        row=m.intake(r)['episodes'][0]
        self.assertTrue(row['eligibility']['temporalReview'])
        self.assertTrue(row['history']['historicalQueueGap'])
    def test_gap_inside_episode_disqualifies_temporal_only(self):
        r=self.request()
        def change(e):
            for side in ('before','after'):
                for event in e[side]['timeline']['events']:
                    if event['sequence']==3:event['name']='ui.queue.gap'
        self.edit(r,1,change)
        row=m.intake(r)['episodes'][0]
        self.assertIn('producer_event_loss',row['reasons'])
        self.assertTrue(row['eligibility']['staticDiagnostics'])

    def test_reordered_events_and_conflicts_fail(self):
        r=self.request();self.edit(r,1,lambda e:e['after']['timeline']['events'].reverse())
        with self.assertRaisesRegex(ValueError,'event_order'):m.intake(r)
    def test_group_split_rejects_adjacent_frame_leakage(self):
        r=self.request();other=copy.deepcopy(r['episodes'][0]);other.update(id='other',role='train');r['episodes'].append(other)
        with self.assertRaisesRegex(ValueError,'group_split'):m.intake(r)
    def test_real_queue_two_configuration_only_campaigns(self):
        queue=self.root/'queue'
        for ident in ('queue-episode-a','queue-episode-b'):
            r=self.request(ident);p=self.root/(ident+'.json');q.save(p,r);s=m.build(p);sp=self.root/(ident+'-spec.json');q.save(sp,s)
            q.submit(sp,queue);approval.approve(queue,ident,'test','Software-only positive episode queue qualification')
        result=q.run(queue=queue,max_jobs=2,python=str(q.ROOT/'.venv-yolo/bin/python'),lock=self.root/'isolated.lock')
        for ident in ('queue-episode-a','queue-episode-b'):
            self.assertEqual(q.state(queue/'jobs'/ident)[0],'complete')

if __name__=='__main__':unittest.main()
