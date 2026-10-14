import unittest
from PIL import Image,ImageDraw
from hcf_rule_review376 import boundary,proposal_rows


class RuleTests(unittest.TestCase):
    def test_dark(self):
        result=boundary(Image.new('RGB',(100,100)),[0,0,100,100])
        self.assertEqual(result['minimumSideSupport'],0)

    def test_outline(self):
        image=Image.new('RGB',(100,100));ImageDraw.Draw(image).rectangle([1,1,98,98],outline='white',width=3)
        result=boundary(image,[0,0,100,100]);self.assertGreater(result['minimumSideSupport'],.95)

    def test_small(self):
        self.assertFalse(boundary(Image.new('RGB',(10,10)),[0,0,3,3])['available'])

    def test_proposal_abstention(self):
        frames={'a':dict(boxes={'f':[0,0,10,10]},focus='f')}
        rules=dict(rows=[dict(id='a',sha256='x',group='g',profile='hcf',outcome='miss',
            prediction=dict(candidates=[[0,0,10,10],[20,0,10,10]]))])
        rows=proposal_rows(rules,frames);self.assertTrue(rows[0]['proposalHit']);self.assertEqual(rows[0]['selectedOutcome'],'miss')


if __name__=='__main__':unittest.main()
