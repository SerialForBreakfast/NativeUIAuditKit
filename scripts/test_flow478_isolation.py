"""Exercise independent graphs through the real isolated queue."""
import copy
import unittest
import research_queue as q
import model_decision_batch434 as compiler
from test_model_decision434 import DecisionTests


class IsolationTests(DecisionTests):
    def test_failed_branch_does_not_stop_other_campaign_or_duplicate_it(self):
        blocked = copy.deepcopy(self.plan)
        blocked['id'] = 'blocked478'
        independent = copy.deepcopy(self.plan)
        independent['id'] = 'independent478'
        self.add_pair('failed-native', False)
        blocked['pairs'] = [self.pairs[-1]]
        self.reinventory('failed-native-candidate', 'failed')
        first = self.compile(blocked)
        second = self.compile(independent)
        for manifest in (first, second):
            compiler.register(manifest, self.queue, approve=True)
        jobs = [r['job'] for m in (first, second) for r in m['jobs']]
        for _ in range(5):
            q.run(self.queue, max_jobs=10, job_ids=jobs, lock=self.root / 'runner.lock')
        output = self.queue / 'jobs/independent478-followup/attempts/1/out/followup.json'
        details = {}
        for job in jobs:
            attempts = q.attempts_of(self.queue / 'jobs' / job)
            details[job] = ((attempts[-1] / 'stderr.log').read_text()[-2000:]
                            if attempts and q.state(self.queue / 'jobs' / job)[0] != 'complete'
                            else q.state(self.queue / 'jobs' / job)[0])
        self.assertTrue(output.is_file(), details)
        self.assertFalse(q.load(output)['newTrainingAuthorized'])
        self.assertNotEqual(q.state(self.queue / 'jobs/blocked478-decision')[0], 'complete')
        before = {j: len(q.attempts_of(self.queue / 'jobs' / j)) for j in jobs}
        q.run(self.queue, max_jobs=10, job_ids=jobs, lock=self.root / 'runner.lock')
        self.assertEqual(before, {j: len(q.attempts_of(self.queue / 'jobs' / j)) for j in jobs})


if __name__ == '__main__':
    unittest.main()
