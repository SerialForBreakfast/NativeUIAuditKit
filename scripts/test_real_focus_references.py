import unittest
from prepare_real_focus_references import intersections


class ReferenceTests(unittest.TestCase):
    def test_neighbor_overlap_is_not_target_growth(self):
        controls=[dict(id='target',state='focused',bounds=[5,5,50,50]),
                  dict(id='neighbor',state='unfocused',bounds=[50,10,50,50])]
        rows=intersections([0,0,60,60],controls,'target')
        self.assertEqual([r['id'] for r in rows],['neighbor'])
        self.assertEqual(rows[0]['area'],500)

    def test_touching_edge_is_not_overlap(self):
        self.assertEqual(intersections([0,0,60,60],[dict(id='n',state='focused',bounds=[60,0,10,10])],'t'),[])

if __name__=='__main__':unittest.main()
