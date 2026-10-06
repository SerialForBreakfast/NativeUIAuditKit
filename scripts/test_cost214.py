import unittest
from cost214 import workload

class CostTests(unittest.TestCase):
    def test_zero_and_duplicate_windows(self):
        base=[dict(imageID='a',width=100,height=100),dict(imageID='b',width=100,height=100)]
        ref=[dict(imageID='a',proposals=[dict(window=[0,0,20,20])]),dict(imageID='b',proposals=[])]
        extra=[dict(imageID='a',cropID='c',window=[0,0,20,20]),dict(imageID='b',cropID=None)]
        d=workload(base,ref,extra)
        self.assertEqual(d['cropCalls'],2);self.assertEqual(d['maxCrops'],2)
        self.assertEqual(d['sameFrameDuplicateWindows'],1)
        self.assertEqual(d['decodedRGBBytes'],2400)
        self.assertEqual(d['distribution'],{2:1,0:1})

    def test_missing_and_invalid_geometry(self):
        base=[dict(imageID='a',width=100,height=100)]
        extra=[dict(imageID='a',cropID=None)]
        for ref in ([],[dict(imageID='b',proposals=[])],
                    [dict(imageID='a',proposals=[dict(window=[0,0,101,2])])]):
            with self.assertRaises(ValueError):workload(base,ref,extra)

if __name__=='__main__':unittest.main()
