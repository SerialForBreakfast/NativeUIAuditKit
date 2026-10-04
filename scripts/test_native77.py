import copy
import unittest
import focus_direct_transition as d
import propose_native77 as p


class NativeAdmissionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Pure contract fixtures: never silently skip when private corpora are absent.
        def row(i,group,role):
            return dict(id=str(i),group=group,sourceRole=role,changed=True,
                decodedPixelHashes=[d.h.digest([i,'pixels',j]) for j in range(2)],
                images=[dict(path=f'test-only/{i}-{j}.png',sha256=d.h.digest([i,'bytes',j])) for j in range(2)])
        old=[row(i,'train-family' if i<32 else 'development-family',
                 'train' if i<32 else 'development') for i in range(37)]
        cls.old=d.corpus_document({},old,[])
        cls.previous=dict(version='focus-direct-admission-v1',approved=True,
            reviewer='unit-test',decisionReference='generated fixture only',
            corpusSHA256=cls.old['corpusSHA256'],assignments={r['id']:r['sourceRole'] for r in old})
        members=[dict(row(i,'fixture-procedural-renderer-v1','calibration'),requestedRole='train') for i in range(37,49)]
        source=dict(path='test-only/source.json',sha256=d.h.digest('generated-source'))
        cls.proposal=dict(version='native77-role-proposal-v1',approved=False,executionEligible=False,
            members=members,memberSHA256=d.h.digest(members),source=source,
            originalCorpusSHA256=cls.old['corpusSHA256'],originalAdmission=cls.previous)
        added=[dict({k:v for k,v in r.items() if k!='requestedRole'},id=source['sha256']+':'+r['id']) for r in members]
        cls.corpus=d.corpus_document({},old+added,[])
        cls.decision=dict(version='native77-role-decision-v1',approved=True,reviewer='unit-test',
            decisionReference='in-memory fixture only',memberSHA256=cls.proposal['memberSHA256'])

    def test_exact_in_memory_decision_preserves_all_original_roles(self):
        result=p.build_admission(self.old,self.corpus,self.previous,self.proposal,self.decision)
        self.assertTrue(all(result['assignments'][k]==v for k,v in self.previous['assignments'].items()))
        self.assertEqual(sum(v=='train' for v in result['assignments'].values()),44)
        self.assertEqual(sum(v=='development' for v in result['assignments'].values()),5)
        self.assertFalse(self.proposal['approved'])

    def test_absent_false_or_wrong_approval(self):
        for decision in ({},dict(self.decision,approved=False),dict(self.decision,memberSHA256='wrong'),dict(self.decision,reviewer=None)):
            with self.assertRaisesRegex(ValueError,'explicit_role_decision'):
                p.build_admission(self.old,self.corpus,self.previous,self.proposal,decision)

    def test_original_roles_and_records_cannot_change(self):
        corpus=copy.deepcopy(self.corpus);corpus['records'][0]['changed']=not corpus['records'][0]['changed']
        with self.assertRaisesRegex(ValueError,'records_changed'):
            p.build_admission(self.old,corpus,self.previous,self.proposal,self.decision)
        previous=copy.deepcopy(self.previous);previous['assignments'][next(iter(previous['assignments']))]='development'
        with self.assertRaises(ValueError):p.build_admission(self.old,self.corpus,previous,self.proposal,self.decision)

    def test_new_membership_and_role_changes_refused(self):
        proposal=copy.deepcopy(self.proposal);proposal['members'][0]['requestedRole']='development'
        proposal['memberSHA256']=d.h.digest(proposal['members'])
        with self.assertRaisesRegex(ValueError,'roles'):
            p.build_admission(self.old,self.corpus,self.previous,proposal,dict(self.decision,memberSHA256=proposal['memberSHA256']))
        proposal=copy.deepcopy(self.proposal);proposal['members'].pop()
        with self.assertRaises(ValueError):p.validate_proposal(proposal)

    def test_cross_split_pixel_leakage_refused_even_with_new_digest(self):
        corpus=copy.deepcopy(self.corpus);proposal=copy.deepcopy(self.proposal)
        dev=next(r for r in self.old['records'] if self.previous['assignments'][r['id']]=='development')
        proposal['members'][0]['decodedPixelHashes'][0]=dev['decodedPixelHashes'][0]
        corpus['records'][37]['decodedPixelHashes'][0]=dev['decodedPixelHashes'][0]
        proposal['memberSHA256']=d.h.digest(proposal['members'])
        with self.assertRaisesRegex(ValueError,'leakage'):
            p.build_admission(self.old,corpus,self.previous,proposal,dict(self.decision,memberSHA256=proposal['memberSHA256']))


if __name__=='__main__':unittest.main()
