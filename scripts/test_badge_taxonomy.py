import json,unittest
from pathlib import Path
R=Path(__file__).resolve().parent.parent
class T(unittest.TestCase):
 def test_append_only(self):
  old=json.loads((R/'Research/schemas/category_map.json').read_text())['categories']; new=json.loads((R/'Research/schemas/category_map.v1.1.json').read_text())
  self.assertEqual(len(old),41); self.assertEqual(new['append'],[{'id':41,'name':'badge','supercategory':'indicators'}])
if __name__=='__main__': unittest.main()
