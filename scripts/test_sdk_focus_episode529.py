import copy
import unittest
import sdk_focus_episode529 as m


def control(name='old', box=None, life='life'):
 return dict(identity=dict(id=name,lifetime=life,revision=0),pixelBounds=box or [0,0,10,10],geometryAvailable=True,
             observedState=dict(hidden=False,effectiveAlpha=1.,enabled=True))

def frame(index,focus='old',controls=None):
 return dict(image=dict(path=f'{index}.png',sha256=str(index)*64),controls=[control()] if controls is None else controls,
             focusID=focus,frameFocusState='focused' if focus else 'no_focus',frameReviewable=True,producerIntervalNS=[index*1000000000,index*1000000000+1000000])

def episode(frames):
 return dict(id='episode',group='group',scenario='modal-close',role='development',frames=frames,eligibility=dict(temporalReview=True),reasons=[])

def predictions(frames, baseline=None, candidate=None):
 out={}
 for f in frames:
  i=int(f['image']['path'].split('.')[0]);models={}
  for name,values in [('baseline',baseline),('candidate',candidate)]:
   box=(values or {}).get(i,[0,0,10,10]);models[name]=dict(boxes=[] if box is None else [box],scores=[] if box is None else [.95])
  out[f['image']['sha256']]=dict(models=models)
 return out

class EpisodeFocusTests(unittest.TestCase):
 def test_departure_persistent_stale_and_no_focus(self):
  fs=[frame(0),frame(1,None,[]),frame(2,None,[])]
  r=m.analyze(episode(fs),predictions(fs,candidate={1:None,2:None}))
  self.assertEqual(r['gains'],[1,2]);self.assertEqual(r['losses'],[])
  self.assertTrue(all(r['rows'][i]['models']['baseline']['staleLocationSelection'] for i in (1,2)))
  self.assertEqual(r['counts']['candidate']['correct-abstention'],2)
 def test_return_reacquisition_has_bounded_sample_time(self):
  fs=[frame(0,None,[]),frame(1),frame(2)]
  r=m.analyze(episode(fs),predictions(fs,baseline={0:None},candidate={0:None,1:None}))
  self.assertEqual(r['losses'],[1]);self.assertTrue(r['rows'][1]['models']['candidate']['falseNoFocus'])
  recovery=r['sampledReacquisition']['candidate'][0]
  self.assertEqual(recovery['frame'],2);self.assertEqual(recovery['earliestMS'],999);self.assertEqual(recovery['latestMS'],1001)
 def test_reused_location_is_not_claimed_stale_identity(self):
  fs=[frame(0),frame(1,'new',[control('new',life='next')])]
  r=m.analyze(episode(fs),predictions(fs))
  self.assertFalse(r['rows'][1]['models']['candidate']['staleLocationSelection'])
 def test_missing_history_preserves_static_results(self):
  fs=[frame(0),frame(1,None,[])];e=episode(fs);e['eligibility']['temporalReview']=False;e['reasons']=['episode_event_gap']
  r=m.analyze(e,predictions(fs,candidate={1:None}))
  self.assertEqual(r['gains'],[1]);self.assertFalse(r['temporalQualified']);self.assertEqual(r['sampledReacquisition']['candidate'],[])
 def test_unaligned_frames_do_not_become_ground_truth(self):
  fs=[frame(0)];fs[0]['frameReviewable']=False
  r=m.analyze(episode(fs),predictions(fs))
  self.assertEqual(r['counts']['candidate'],{'unknown':1});self.assertFalse(r['rows'][0]['truthKnown'])
 def test_missing_scores_and_invalid_scores_fail(self):
  fs=[frame(0)]
  with self.assertRaisesRegex(ValueError,'missing_prediction'):m.analyze(episode(fs),{})
  p=predictions(fs);p[fs[0]['image']['sha256']]['models']['candidate']['scores']=[float('nan')]
  with self.assertRaisesRegex(ValueError,'focus_score'):m.analyze(episode(fs),p)
 def test_new_wrong_and_multiple_high_scores(self):
  fs=[frame(0)];p=predictions(fs,candidate={0:[30,0,10,10]})
  self.assertEqual(m.analyze(episode(fs),p)['newWrong'],[0])
  p[fs[0]['image']['sha256']]['models']['candidate']=dict(boxes=[[0,0,10,10],[30,0,10,10]],scores=[.95,.95])
  r=m.analyze(episode(fs),p);self.assertEqual(r['rows'][0]['models']['candidate']['outcome'],'miss')

class EpisodeFocusQueueTests(unittest.TestCase):
 def test_two_configurations_run_and_verify_source_lineage(self):
  import test_sdk_episode529 as fixtures
  import research_queue as q
  import research_approval as approval
  from experiment_templates import pin
  fixture=fixtures.EpisodeTests();fixture.setUp();self.addCleanup(fixture.doCleanups)
  queue=fixture.root/'queue'
  models={}
  for name in ('baseline','candidate','tool'):
   path=fixture.root/(name+'.json');q.save(path,dict(softwareOnly=name));models[name]=pin(path)
  for index in (1,2):
   episode_request=fixture.request('episode-queue-'+str(index));ep=fixture.root/('episodes-'+str(index)+'.json');q.save(ep,episode_request)
   config=fixture.root/('score-config-'+str(index)+'.json');q.save(config,dict(models={k:models[k] for k in ('baseline','candidate')},tool=models['tool']))
   attempt=fixture.root/('source-'+str(index));out=attempt/'out';out.mkdir(parents=True)
   rows=[]
   for ref in episode_request['episodes'][0]['frames']:
    rows.append(dict(image=ref['image'],models={name:dict(boxes=[[0,0,1,1]],scores=[.1 if name=='baseline' else .95]) for name in ('baseline','candidate')}))
   report=out/'scores.json';q.save(report,dict(version='sdk-endpoint-focus-results-v1',request=pin(config),rows=rows))
   receipt=attempt/'result.json';q.save(receipt,dict(status='complete',outputs=[dict(path='scores.json',sha256=q.digest(report))]))
   request=dict(version='sdk-focus-episode-v1',id='focus-episode-'+str(index),episodes=pin(ep),scores=[dict(report=pin(report),result=pin(receipt))])
   path=fixture.root/('request-'+str(index)+'.json');q.save(path,request);spec=m.build(path)
   sp=fixture.root/('spec-'+str(index)+'.json');q.save(sp,spec);q.submit(sp,queue)
   approval.approve(queue,request['id'],'test','Software-only focus episode comparison')
  q.run(queue=queue,max_jobs=2,python=str(q.ROOT/'.venv-yolo/bin/python'),lock=fixture.root/'isolated.lock')
  for index in (1,2):
   job=queue/('jobs/focus-episode-'+str(index));self.assertEqual(q.state(job)[0],'complete')
   result=q.load(job/'attempts/1/out/benchmark_summary.json')
   self.assertEqual(result['episodes'][0]['gains'],[0,1]);self.assertFalse(result['modelAccepted'])
  report.write_text('changed')
  with self.assertRaises(ValueError):m.evaluate(request)

if __name__=='__main__':unittest.main()
