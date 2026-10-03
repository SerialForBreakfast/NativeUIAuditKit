import unittest
from proposal_recovery import union,ocr_rows,semantic_hint,geometry

class ProposalTests(unittest.TestCase):
    def test_dedup_does_not_suppress_nested_text(self):
        self.assertEqual(len(union([[0,0,100,20]],[[0,0,100,20],[10,5,30,10]])),2)
    def test_ocr_is_support_not_body_geometry(self):
        text=[dict(bounds=[10,5,20,5],confidence=.9,text='Settings')]
        self.assertEqual(ocr_rows([[0,0,100,20],[200,0,100,20]],text),[[0,0,100,20]])
    def test_cancel_hint_is_selective_and_local(self):
        text=[dict(bounds=[1,1,5,5],confidence=.9,text=' Cancel ')]
        self.assertEqual(semantic_hint(text,[0,0,10,10]),'cancelAction')
        self.assertIsNone(semantic_hint(text,[20,20,10,10]))
        text[0]['text']='Save';self.assertIsNone(semantic_hint(text,[0,0,10,10]))
    def test_low_confidence_abstains(self):
        self.assertIsNone(semantic_hint([dict(bounds=[1,1,5,5],confidence=.4,text='Cancel')],[0,0,10,10]))
    def test_focus_recall_separate_from_unreviewed(self):
        f={'controls':[dict(bounds=[0,0,10,10],state='focused')]}
        r=geometry([[0,0,10,10],[20,20,10,10]],f,.5)
        self.assertEqual((r['focusedLocated'],r['unreviewedProposals']),(1,1))

if __name__=='__main__':unittest.main()
