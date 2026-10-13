import unittest
from compare_duration358 import compare


class ComparisonTests(unittest.TestCase):
    def report(self,complete=True,lost=0):
        return {'decisions':{k:dict(complete=complete,comparisons=24,lostPrevious=lost,
            gainedNativeMovement=0,passesDevelopmentRule=False) for k in ('control','position')}}

    def test_deltas(self):
        d=compare(self.report(lost=20),self.report(lost=5))
        self.assertEqual(d['durationComparison']['position']['lostPreviousDelta'],-15)
        self.assertFalse(d['modelAccepted'])

    def test_incomplete(self):
        with self.assertRaises(ValueError):compare(self.report(),self.report(False))
