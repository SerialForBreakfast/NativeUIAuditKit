import unittest
from unittest.mock import patch
import crossover189 as c

class Tests(unittest.TestCase):
    def test_complete_case_matching(self):
        old=[dict(id='a',disposition='miss'),dict(id='b',disposition='hit')]
        new=[dict(id='b',disposition='hit'),dict(id='a',disposition='hit')]
        self.assertEqual(c.transitions(old,new)[1],dict(id='a',before='miss',after='hit'))
        for rows in [new[:1],[new[0],new[0]],[dict(id='c',disposition='hit'),new[0]]]:
            with self.assertRaises(Exception):c.transitions(old,rows)
    def test_collision_before_inputs(self):
        with patch.object(c,'OUT',c.h.ROOT),patch.object(c.g,'admission') as admission:
            with self.assertRaisesRegex(Exception,'output_collision'):c.prepare()
            admission.assert_not_called()
    def test_changed_settings(self):
        for doc in [dict(newArms=[],settings=c.SETTINGS),dict(newArms=[['022',1280],['024',640]],settings={})]:
            with patch.object(c.p,'sealed',return_value=doc),self.assertRaisesRegex(Exception,'changed_experiment'):c.inputs()

if __name__=='__main__':unittest.main()
