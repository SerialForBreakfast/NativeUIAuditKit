import unittest
from study_storage import reservation


class StorageTests(unittest.TestCase):
    def test_capacity(self):
        self.assertTrue(reservation(1000,500,10,100,50,300)['ready'])

    def test_quota(self):
        self.assertIn('study_quota',reservation(1000,500,250,51,0,300)['blockers'])

    def test_extraction_reserve(self):
        self.assertIn('volume_free_reserve',reservation(1000,400,0,100,101)['blockers'])

    def test_invalid(self):
        with self.assertRaises(ValueError):reservation(100,101,0,0,0)


if __name__=='__main__':unittest.main()
