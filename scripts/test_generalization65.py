import unittest
from PIL import Image
from focus_pair_translation import translate,transform
from diagnose_generalization65 import conditions,counterfactual_summary


class GeneralizationTests(unittest.TestCase):
    def test_proposal_reader_checks_its_own_schema(self):
        from unittest.mock import patch
        from admit_negatives65 import read_proposal
        import human_annotation_review as h
        rows=[dict(id=str(i),sourceRole='calibration',requestedRole='train',changed=False,
            group='fixture-procedural-renderer-v1',condition='boundary_unchanged' if i<4 else 'content_only') for i in range(8)]
        doc=dict(version='focus-negative-role-proposal-v1',approved=False,executionEligible=False,reviewer=None,members=rows)
        doc['seal']=h.digest(doc)
        with patch.object(h,'read',return_value=doc):self.assertEqual(read_proposal('unused'),doc)
        doc['members'][0]['changed']=True
        with patch.object(h,'read',return_value=doc):
            with self.assertRaisesRegex(ValueError,'seal_changed'):read_proposal('unused')

    def test_exact_role_amendment(self):
        import copy
        import focus_direct_transition as d
        from admit_negatives65 import build_admission
        old_rows=[dict(id=str(i),group='train' if i<24 else 'dev',
            decodedPixelHashes=[str(i)],images=[dict(sha256=str(i))]) for i in range(29)]
        old=dict(records=old_rows,excluded=[],corpusSHA256='old')
        previous=dict(version='focus-direct-admission-v1',approved=True,reviewer='test',decisionReference='test',
            corpusSHA256='old',assignments={str(i):'train' if i<24 else 'development' for i in range(29)})
        new=[dict(id='negative'+str(i),group='fixture-procedural-renderer-v1',sourceRole='calibration',
            requestedRole='train',changed=False,condition='boundary_unchanged' if i<4 else 'content_only',
            decodedPixelHashes=['n'+str(i)],images=[dict(sha256='n'+str(i))]) for i in range(8)]
        proposal=dict(version='focus-negative-role-proposal-v1',approved=False,executionEligible=False,reviewer=None,
            members=new,memberSHA256=d.digest(new),source=dict(sha256='source'))
        corpus=dict(records=old_rows+[dict({k:v for k,v in r.items() if k!='requestedRole'},id='source:'+r['id']) for r in new],
            excluded=[],corpusSHA256='new')
        decision=dict(version='focus-negative-role-decision-v1',approved=True,reviewer='maintainer',
            decisionReference='explicit test decision',memberSHA256=proposal['memberSHA256'])
        result=build_admission(old,corpus,previous,proposal,decision)
        self.assertEqual(list(result['assignments'].values()).count('train'),32)
        for mutate in (lambda c:c['records'][0].update(group='changed'),lambda c:c['records'].pop()):
            bad=copy.deepcopy(corpus);mutate(bad)
            with self.assertRaises(ValueError):build_admission(old,bad,previous,proposal,decision)
        for bad in (dict(decision,approved=False),dict(decision,memberSHA256='other')):
            with self.assertRaises(ValueError):build_admission(old,corpus,previous,proposal,bad)

    def test_proposal_cannot_be_an_approval(self):
        from propose_negative_admission65 import validate_proposal
        rows=[dict(id=str(i),sourceRole='calibration',requestedRole='train',changed=False,
            group='fixture-procedural-renderer-v1',condition='boundary_unchanged' if i<4 else 'content_only') for i in range(8)]
        doc=dict(version='focus-negative-role-proposal-v1',approved=False,executionEligible=False,reviewer=None,members=rows)
        validate_proposal(doc);doc['approved']=True
        with self.assertRaisesRegex(ValueError,'not_approval'):validate_proposal(doc)

    def test_conditions_and_geometry(self):
        self.assertEqual(len(conditions()),13);self.assertEqual(len({c[0] for c in conditions()}),13)
        images=[Image.new('RGB',(100,100),'red')]*2;boxes=[[10,10,20,20]]*2
        pair,truth=translate(images,boxes,2,-6)
        self.assertEqual(truth,[[12,4,20,20]]*2)
        self.assertEqual(pair[0].getpixel((0,0)),(0,0,0))
        self.assertEqual(transform(images,boxes,'right')[1],translate(images,boxes,4,0)[1])
        self.assertEqual(translate(images,boxes,-20,0),(None,None))
        for dx in (True,float('nan'),.2):
            with self.assertRaises(ValueError):translate(images,boxes,dx,0)
        with self.assertRaises(ValueError):translate(images,[[float('nan'),1,2,3]]*2,0,0)

    def test_zero_difference_is_not_semantic_accuracy(self):
        row=dict(prediction=dict(decision='changed',changeProbability=.9),predictedBoxOverlap=0.)
        report=counterfactual_summary([row]);self.assertIsNone(report['semanticAccuracy'])
        self.assertEqual(report['rawChangePredictions'],1)


if __name__=='__main__':unittest.main()
