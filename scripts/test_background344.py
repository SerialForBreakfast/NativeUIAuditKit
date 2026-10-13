import unittest
import numpy as np
from background344 import summary,detail_size

class BackgroundTests(unittest.TestCase):
    def test_counts(self):
        rows=[dict(id='native343-a',condition='movement',changed=1),dict(id='b',condition='content',changed=0)]
        result=summary(rows,[.1,.9],[.9,.1])
        self.assertEqual(result['native/movement']['missedChange'],1)
        self.assertEqual(result['native/movement']['lost'],1)
        self.assertEqual(result['authored/content']['falseChange'],1)
    def test_invalid_score(self):
        with self.assertRaises(ValueError):summary([dict(id='x',condition='a',changed=0)],[float('nan')],[0])
    def test_unknown_size(self):
        with self.assertRaisesRegex(ValueError,'window_width'):detail_size(np.zeros((0,6,128,192)),[],17)

if __name__=='__main__':unittest.main()
