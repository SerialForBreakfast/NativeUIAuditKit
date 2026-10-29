import copy
import unittest
from pathlib import Path
import research_queue as q
from experiment_templates import pin
from test_sdk_episode529 import EpisodeTests
import sdk_episode_crops530 as m

class CropLabelsTests(EpisodeTests):
    def config(self,r):
        p=self.root/(r['id']+'-request.json');q.save(p,r)
        tool=q.ROOT/'.build/standard392-swift/arm64-apple-macosx/debug/FocusRingTool'
        return dict(version='sdk-episode-crops-v1',id=r['id'],episodes=pin(p),tool=pin(tool))
    def test_binary_labels_need_no_detector_class(self):
        data=m.normalize(self.config(self.request()))
        self.assertEqual(len(data['frames']),2)
        self.assertEqual(data['frames'][0]['focusID'],'button')
        self.assertFalse(data['trainingEligible'])
        self.assertEqual(data['frames'][0]['profile'],'unknown')
    def test_production_crops_through_two_isolated_jobs(self):
        import research_approval as approval
        queue=self.root/'crop-queue'
        for ident in ('crop-first','crop-second'):
            r=self.request(ident)
            self.edit(r,1,lambda e:[e[s].update(focusID=None) for s in ('before','after')])
            cfg=self.config(r);path=self.root/(ident+'-crop.json');q.save(path,cfg)
            spec=m.build(path);sp=self.root/(ident+'-spec.json');q.save(sp,spec)
            q.submit(sp,queue);approval.approve(queue,ident,'test','Qualified software production crop test')
        q.run(queue=queue,max_jobs=2,python=str(q.ROOT/'.venv-yolo/bin/python'),lock=self.root/'crops.lock')
        for ident in ('crop-first','crop-second'):
            job=queue/'jobs'/ident
            self.assertEqual(q.state(job)[0],'complete',str(q.load(job/'attempts/1/result.json'))+' '+(job/'attempts/1/stderr.log').read_text() if (job/'attempts/1/stderr.log').exists() else str(list((job/'attempts/1').iterdir())))
            result=q.load(job/'attempts/1/out/crops.json')
            self.assertEqual([r['label'] for r in result['rows']],[1,0])
            self.assertFalse(result['trainingEligible'])
            self.assertTrue(all(r['profile']=='unknown' for r in result['rows']))

    def test_unknown_frame_is_not_negative(self):
        r=self.request();self.edit(r,0,lambda e:e['after'].update(focusKnown=False))
        data=m.normalize(self.config(r));self.assertEqual(len(data['excluded']),1);self.assertEqual(len(data['frames']),1)
    def test_empty_frame_is_not_a_background_crop(self):
        r=self.request()
        self.edit(r,0,lambda e:[e[s].update(elements=[],focusID=None) for s in ('before','after')])
        data=m.normalize(self.config(r));self.assertEqual(len(data['emptyFrames']),1);self.assertEqual(len(data['frames']),1)
    def test_conflicting_labels_on_identical_pixels_fail(self):
        r=self.request();a,b=r['episodes'][0]['frames']
        b['image']=copy.deepcopy(a['image'])
        def change(e):
            e['imageSHA256']=a['image']['sha256']
            for side in ('before','after'):e[side]['focusID']=None
        self.edit(r,1,change)
        with self.assertRaisesRegex(ValueError,'conflicting_pixels'):m.normalize(self.config(r))
    def test_missing_geometry_excludes_frame(self):
        r=self.request();self.edit(r,0,lambda e:e['issues'].append('registered_geometry_not_stable'))
        data=m.normalize(self.config(r));self.assertEqual(len(data['excluded']),1)

    def test_profile_or_taxonomy_cannot_admit_training(self):
        r=self.request();r['episodes'][0]['role']='train'
        with self.assertRaisesRegex(ValueError,'episode_crops_role'):m.normalize(self.config(r))
    def test_missing_history_does_not_block_static_labels(self):
        r=self.request();self.edit(r,0,lambda e:e['before'].pop('timeline'))
        self.assertEqual(len(m.normalize(self.config(r))['frames']),2)

if __name__=='__main__':unittest.main()
