import copy
import unittest
import evaluate_collection102 as c


def row():
    return dict(id='case',images=[{'sha256':'a'},{'sha256':'b'}],boxes=[[0,0,10,10]]*2,
        changed=False,condition='boundary_unchanged',recipe=dict(theme='dark',appearance=dict(canvas=dict(collectionStyle='sectioned'))))


class CalibrationTests(unittest.TestCase):
    def test_failure_types_and_abstention(self):
        frames={k:dict(candidates=[dict(id='correct',bounds=[0,0,10,10])]) for k in ('a','b')}
        predictions={k:dict(id='wrong',bounds=[20,20,10,10]) for k in ('a','b')}
        result=c.score_row(row(),.01,predictions,frames)
        self.assertEqual(result['endpointFailure'],['ranking_or_geometry']*2)
        self.assertTrue(result['rawChangeCorrect']);self.assertFalse(result['joint'])
        frames['a']['candidates']=[];predictions['a']=None
        result=c.score_row(row(),.5,predictions,frames)
        self.assertEqual(result['endpointFailure'][0],'proposal_miss');self.assertTrue(result['abstained'])
        self.assertFalse(result['confidentFalseChange'])
        self.assertTrue(c.score_row(row(),.95,predictions,frames)['confidentFalseChange'])
        with self.assertRaisesRegex(ValueError,'probability'):c.score_row(row(),float('nan'),predictions,frames)

    def test_noop_correctness_requires_both_boxes_and_confidence(self):
        candidates=[dict(id='correct',bounds=[0,0,10,10])]
        frames={k:dict(candidates=candidates) for k in ('a','b')};predictions={k:candidates[0] for k in frames}
        result=c.score_row(row(),.1,predictions,frames)
        self.assertTrue(result['joint']);self.assertEqual(c.summarize([result])['correctEndpoints'],2)
        self.assertFalse(c.score_row(row(),.2,predictions,frames)['joint'])

    def test_role_proposal_is_never_approval(self):
        members=[dict(id=str(i),sourceRole='calibration',requestedRole='train',group='fixture-procedural-renderer-v1',
                      condition='focus_moved' if i<16 else 'boundary_unchanged' if i<28 else 'content_only',changed=i<16)
                 for i in range(40)]
        doc=dict(version=c.VERSION,approved=False,executionEligible=False,members=members,memberSHA256=c.h.digest(members))
        c.validate_proposal(doc)
        for field in ('approved','executionEligible'):
            bad=copy.deepcopy(doc);bad[field]=True
            with self.assertRaises(ValueError):c.validate_proposal(bad)
        bad=copy.deepcopy(doc);bad['members'][0]['changed']=False;bad['memberSHA256']=c.h.digest(bad['members'])
        with self.assertRaises(ValueError):c.validate_proposal(bad)
        bad=copy.deepcopy(doc);bad['members'].pop()
        with self.assertRaises(ValueError):c.validate_proposal(bad)


if __name__=='__main__':unittest.main()
