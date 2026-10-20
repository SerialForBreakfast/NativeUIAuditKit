import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import research_queue as q
from dispatch_candidates479 import unstarted


class DispatchTests(unittest.TestCase):
    def test_only_unstarted_jobs_reach_full_readiness(self):
        with tempfile.TemporaryDirectory(dir=q.ROOT/'.build') as directory:
            root=Path(directory)
            for name in ('complete','failed','running','interrupted'):
                (root/'jobs'/name/'attempts/1').mkdir(parents=True)
            selected={name:'hash' for name in ('complete','failed','running','interrupted','pending','blocked')}
            with patch.object(q,'outputs_intact',side_effect=AssertionError('must not hash historical outputs')):
                self.assertEqual(list(unstarted(selected,root)),[('pending','hash'),('blocked','hash')])

    def test_new_successor_is_not_hidden_by_old_attempt(self):
        with tempfile.TemporaryDirectory(dir=q.ROOT/'.build') as directory:
            root=Path(directory);(root/'jobs/old/attempts/1').mkdir(parents=True)
            self.assertEqual(list(unstarted({'old':'a','successor':'b'},root)),[('successor','b')])

    def test_invalid_job_id_fails(self):
        with self.assertRaisesRegex(ValueError,'dispatch_job_id'):
            list(unstarted({'../outside':'hash'},q.QUEUE))


if __name__=='__main__':unittest.main()
