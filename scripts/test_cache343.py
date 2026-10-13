import shutil
import unittest
import uuid
import numpy as np
import cache343 as c


class CacheTests(unittest.TestCase):
    def setUp(self):
        self.folder=c.q.ROOT/'.build'/('cache343-test-'+uuid.uuid4().hex);self.folder.mkdir()
    def tearDown(self):shutil.rmtree(self.folder)
    def test_identity_and_roundtrip(self):
        values=np.zeros((2,3),np.float32);key=c.cache_key(values,{'model':'a'})
        self.assertNotEqual(key,c.cache_key(values,{'model':'b'}))
        self.assertNotEqual(key,c.cache_key(values+1,{'model':'a'}))
        c.store(self.folder,key,values);np.testing.assert_array_equal(c.read(self.folder,key),values)
        with self.assertRaises(ValueError):c.store(self.folder,key,values)
        with self.assertRaises(ValueError):c.read(self.folder,'missing')
    def test_partial_not_visible(self):
        (self.folder/'x.partial').write_bytes(b'interrupted')
        with self.assertRaisesRegex(ValueError,'cache_not_complete'):c.read(self.folder,'x')
    def test_corrupt(self):
        np.savez(self.folder/'x.npz',key=np.array('x'),values=np.zeros(2,np.float32),digest=np.array('bad'))
        with self.assertRaisesRegex(ValueError,'cache_corrupt'):c.read(self.folder,'x')


if __name__=='__main__':unittest.main()
