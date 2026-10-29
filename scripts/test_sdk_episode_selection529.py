import copy
import unittest
import sdk_episode_selection529 as m

class SelectionTests(unittest.TestCase):
 def setUp(self):
  self.rows=[dict(id=str(i),group='g'+str(i//2),candidate='miss' if i<6 else 'wrong') for i in range(8)]
  self.metadata={'g'+str(i):dict(episodeIDs=['e'+str(i)],controlFamily='button',transition='arrival' if i<3 else 'departure',annotationUnits=6,frameCount=2,role='review_only') for i in range(4)}
 def test_equal_budgets_and_no_repeated_groups(self):
  r=m.select(self.rows,self.metadata,2,529)
  for arm in ('diverse','random'):
   self.assertEqual(len(set(r[arm]['groups'])),2)
   self.assertEqual(r[arm]['annotationUnits'],12)
   self.assertEqual(r[arm]['frameCount'],4)
  self.assertFalse(r['trainingAdmitted']);self.assertFalse(r['modelImprovement'])
 def test_reordering_is_deterministic(self):
  self.assertEqual(m.select(self.rows,self.metadata,2,529),m.select(self.rows[::-1],self.metadata,2,529))
 def test_diversity_uses_transition_and_error(self):
  self.assertIn('g3',m.select(self.rows,self.metadata,2,529)['diverse']['groups'])
 def test_unequal_costs_fail_without_dropping_cases(self):
  self.metadata['g3']['annotationUnits']=8
  with self.assertRaisesRegex(ValueError,'unequal_group_costs'):m.select(self.rows,self.metadata,2,529)
 def test_shared_episode_fails(self):
  self.metadata['g3']['episodeIDs']=['e0']
  with self.assertRaisesRegex(ValueError,'shared_ancestry'):m.select(self.rows,self.metadata,2,529)
 def test_successes_are_not_failure_candidates(self):
  for row in self.rows:row['candidate']='correct'
  with self.assertRaisesRegex(ValueError,'insufficient_groups'):m.select(self.rows,self.metadata,2,529)
 def test_roles_are_preserved(self):
  self.metadata['g3']['role']='evaluation'
  r=m.select(self.rows,self.metadata,4,529)
  self.assertEqual(r['diverse']['roles']['g3'],'evaluation');self.assertFalse(r['trainingAdmitted'])

class SelectionQueueTests(unittest.TestCase):
 def test_two_descriptions_use_verified_comparisons_through_queue(self):
  import test_model_decision434 as fixtures
  import research_queue as q
  import research_approval as approval
  from experiment_templates import pin
  fixture=fixtures.DecisionTests();fixture.setUp();self.addCleanup(fixture.tearDown)
  candidate=fixture.queue/'jobs/native-candidate/attempts/1/out/selection.json'
  report=q.load(candidate)
  for row in report['rows']:
   for arm in row['arms'].values():arm.update(scores=[.1],outcome='miss')
  q.save(candidate,report,replace=True);fixture.reinventory('native-candidate')
  fixture.execute(fixture.compile())
  source=fixture.queue/'jobs/experiment-a-compare-01/attempts/1'
  metadata=fixture.root/'episode-metadata.json'
  q.save(metadata,{'native-group':dict(episodeIDs=['software-episode'],controlFamily='software-button',transition='arrival',annotationUnits=2,frameCount=2,role='review_only')})
  for index in (1,2):
   request=dict(version='sdk-episode-selection-v1',id='episode-selection-'+str(index),comparison=dict(report=pin(source/'out/comparison.json'),result=pin(source/'result.json')),metadata=pin(metadata),count=1,seed=52900+index)
   path=fixture.root/('request-'+str(index)+'.json');q.save(path,request)
   spec=m.build(path);sp=fixture.root/('spec-'+str(index)+'.json');q.save(sp,spec)
   q.submit(sp,fixture.queue);approval.approve(fixture.queue,request['id'],'test','Software-only episode selection')
  q.run(queue=fixture.queue,job_ids=['episode-selection-1','episode-selection-2'],max_jobs=2,python=str(q.ROOT/'.venv-yolo/bin/python'),lock=fixture.root/'isolated.lock')
  for index in (1,2):
   job=fixture.queue/('jobs/episode-selection-'+str(index))
   self.assertEqual(q.state(job)[0],'complete')
   result=q.load(job/'attempts/1/out/benchmark_summary.json')
   self.assertEqual(result['diverse']['annotationUnits'],result['random']['annotationUnits'])
   self.assertFalse(result['trainingAdmitted'])

if __name__=='__main__':unittest.main()
