import unittest
from native_selection404 import outcome


class SelectionTests(unittest.TestCase):
    def test_no_focus(self):
        self.assertEqual(outcome([],[],None),'correct-abstention')
        self.assertEqual(outcome([.9],[[0,0,10,10]],None),'false-selection')
        self.assertEqual(outcome([.9,.9],[[0,0,10,10]]*2,None),'correct-abstention')

    def test_focus_and_localization(self):
        self.assertEqual(outcome([.9],[[0,0,10,10]],[0,0,10,10]),'correct')
        self.assertEqual(outcome([.9],[[20,20,10,10]],[0,0,10,10]),'wrong')
        self.assertEqual(outcome([.8],[[0,0,10,10]],[0,0,10,10]),'miss')


if __name__=='__main__':unittest.main()
