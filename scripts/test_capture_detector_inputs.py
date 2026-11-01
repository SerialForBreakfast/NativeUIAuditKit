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



W,H=200,100
IDS=['a','b']


def scene(focused,generation=5,run='run',recipe='r1'):
    body=lambda i,x:dict(version=1,role='rendered_control_body',coordinate_space='image_top_left_pixels',element_id=i,
        generation=generation,source='native_body_presentation_layer',availability='measured',
        full_pixel_bounds=[x,10,40,20],visible_pixel_bounds=[x,10,40,20],visible_normalized_bounds=[x/W,.1,(x+40)/W,.3])
    return dict(fixture_run_id=run,recipe=dict(recipe_hash=recipe),scene_width=W,scene_height=H,is_settled=True,
        observation_generation=generation,focused_element_id=focused,timestamp=1.0,
        focus_observation=dict(verified=True,source='uikit_focus_system',generation=generation,plannedFocusIDs=IDS,
                               **({} if focused is None else dict(observedID=focused))),
        observation_diagnostics=dict(nativeFocusResolved=True,reason='ready',sampledGeneration=generation,
            sampleAgeMilliseconds=10,stableMilliseconds=200,nativeProbe=dict(referenceFocused=focused is None)),
        elements=[dict(element_id=i,is_focused=i==focused,taxonomy_class='primaryButton',rendered_body_geometry=body(i,10+60*n))
                  for n,i in enumerate(IDS)])


class FixtureBatchInputTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(dir=adapter.q.ROOT/'.build',prefix='capture-batch-test-')
        self.root=Path(self.tmp.name).resolve();self.out=self.root/'out';self.out.mkdir()
        self.batch=self.root/'batch';self.batch.mkdir()
        self.patch=patch.object(adapter,'BATCH_ROOT',self.root);self.patch.start()

    def tearDown(self):
        self.patch.stop();self.tmp.cleanup()

    def png(self,name,shade):
        path=self.batch/name;adapter.Image.new('RGB',(W,H),(shade,0,0)).save(path);return adapter.q.digest(path)

    def build(self,baseline_focus=None,target='SIM',frame_ns=15):
        base=self.png('u.png',1);rows=[]
        for n,focus in enumerate(IDS):
            sha=self.png(f'f{n}.png',10+n)
            capture=lambda s,f:dict(correlation='validated_capture_bracket',frame_png_sha256=s,frame_width=W,frame_height=H,
                before_scene_received_host_ns=10,frame_received_host_ns=frame_ns,after_scene_received_host_ns=20,
                before_scene=scene(f),after_scene=scene(f))
            prov=lambda s:dict(pngSHA256=s,sourceDeviceID=target,providerID='simctl-screenshot-companion')
            sidecar=dict(focused_element_id=focus,focused_sha256=sha,unfocused_sha256=base,focused_capture=capture(sha,focus),
                         reference_capture=capture(base,baseline_focus),focused_provenance=prov(sha),unfocused_provenance=prov(base))
            adapter.q.save(self.batch/f'm{n}.json',sidecar,replace=True)
            rows.append(dict(id=f'synth-{n}',expectedFocus=focus,sha256=sha,metadata=dict(recipeFile='r.json',recipeHash='r1',
                metadataPath=f'm{n}.json',focusedPath=f'f{n}.png',unfocusedPath='u.png')))
        adapter.q.save(self.batch/'manifest.json',rows,replace=True)
        adapter.q.save(self.batch/'harvest-receipt.json',dict(outcome='completed',rejections=[],acceptedRowCount=len(rows)),replace=True)
        source=self.batch/'manifest.json'
        return dict(version=adapter.FIXTURE_BATCH,path=str(source),sha256=adapter.q.digest(source),
                    plan=dict(trainingEligible=False,target='SIM',cases=[dict(recipe='r.json',role='development',group='g',family='button')]))

    def test_batch_frames_and_shared_baseline(self):
        labels=adapter.prepare(self.build(),self.out)
        self.assertEqual(len(labels['frames']),3)
        self.assertEqual(sum(e['noFocus'] for f in labels['frames'] for e in f['events']),1)
        self.assertEqual(labels['source']['unavailable'],adapter.BATCH_UNAVAILABLE)
        self.assertFalse(labels['trainingEligible'])

    def test_baseline_with_observed_focus_is_labelled_focused(self):
        labels=adapter.prepare(self.build(baseline_focus='a'),self.out)
        baseline=[f for f in labels['frames'] if f['id'].endswith('-baseline')][0]
        self.assertFalse(baseline['events'][0]['noFocus'])
        self.assertEqual([c['id'] for c in baseline['controls'] if c['state']=='focused'],['a'])

    def test_fail_closed(self):
        cases=[('capture_target',dict(target='OTHER')),('batch_frame_outside_bracket',dict(frame_ns=25))]
        for reason,kwargs in cases:
            with self.subTest(reason=reason):
                with self.assertRaisesRegex(ValueError,reason):adapter.prepare(self.build(**kwargs),self.out)

    def test_changed_pixels_and_training_role_fail(self):
        artifact=self.build();self.png('f1.png',99)
        with self.assertRaisesRegex(ValueError,'capture_pixels_changed'):adapter.prepare(artifact,self.out)
        artifact=self.build();artifact['plan']['trainingEligible']=True
        with self.assertRaisesRegex(ValueError,'capture_role'):adapter.prepare(artifact,self.out)

    def test_source_outside_batch_root_fails(self):
        artifact=self.build();artifact['path']=str(adapter.q.ROOT.resolve()/'reports/manifest.json')
        with self.assertRaisesRegex(ValueError,'capture_source_scope'):adapter.prepare(artifact,self.out)


if __name__=='__main__':unittest.main()
