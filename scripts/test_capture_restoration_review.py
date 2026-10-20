"""Check exact failure and membership gates without native operations."""
import copy
import unittest
from capture_restoration_review import validate_failure


class FailureTests(unittest.TestCase):
    def setUp(self):
        self.plan = dict(cases=[dict(id='a', targets=['x'])], profiles=['standard','hcf'], expectedFrames=2)
        self.capture = dict(complete=False, cleanup=False, error=None, originalProfile='standard',
            cleanupErrors=['profile_restore:profile-standard:None'],
            frames=[dict(case='a',profile=p,focus='x',repeat=0) for p in self.plan['profiles']])

    def test_complete_frames_with_failed_restoration(self):
        validate_failure(self.capture,self.plan)

    def test_missing_frame(self):
        self.capture['frames'].pop()
        with self.assertRaisesRegex(ValueError,'membership'):validate_failure(self.capture,self.plan)

    def test_duplicate_frame(self):
        self.capture['frames'][1]=copy.deepcopy(self.capture['frames'][0])
        with self.assertRaisesRegex(ValueError,'membership'):validate_failure(self.capture,self.plan)

    def test_capture_error(self):
        self.capture['error']='uncertain'
        with self.assertRaisesRegex(ValueError,'original_state'):validate_failure(self.capture,self.plan)

    def test_other_cleanup_failure(self):
        self.capture['cleanupErrors'].append('disconnect:unknown')
        with self.assertRaisesRegex(ValueError,'failure_scope'):validate_failure(self.capture,self.plan)

    def test_wrong_original_profile(self):
        self.capture['originalProfile']='hcf'
        with self.assertRaisesRegex(ValueError,'original_state'):validate_failure(self.capture,self.plan)

    def test_already_complete(self):
        self.capture['complete']=True
        with self.assertRaisesRegex(ValueError,'failure_state'):validate_failure(self.capture,self.plan)


if __name__ == '__main__': unittest.main()
