import copy
import tempfile
from pathlib import Path
from unittest.mock import patch
import unittest
import prepare_collection103 as p


class AdmissionTests(unittest.TestCase):
    def setUp(self):
        h=p.h
        rows=[dict(id=str(i),group='fixture-procedural-renderer-v1' if i<68 else 'settings',
            sourceRole='train' if i<68 else 'development',changed=True,
            images=[dict(sha256=h.digest(['old',i,j])) for j in range(2)],
            decodedPixelHashes=[h.digest(['old-pixels',i,j]) for j in range(2)]) for i in range(73)]
        self.old=p.r.d.corpus_document({},rows,[])
        self.previous=dict(version='focus-direct-admission-v1',approved=True,reviewer='test-only',
            decisionReference='synthetic unit test',corpusSHA256=self.old['corpusSHA256'],
            assignments={v['id']:v['sourceRole'] for v in rows})
        members=[dict(id='new-'+str(i),group='fixture-procedural-renderer-v1',sourceRole='calibration',requestedRole='train',
            condition='focus_moved' if i<16 else 'boundary_unchanged' if i<28 else 'content_only',changed=i<16,
            images=[dict(sha256=h.digest(['new',i,j])) for j in range(2)],
            decodedPixelHashes=[h.digest(['new-pixels',i,j]) for j in range(2)]) for i in range(40)]
        self.proposal=dict(version=p.c.VERSION,**h.FLAGS,approved=False,executionEligible=False,
            members=members,memberSHA256=h.digest(members))
        self.source=dict(path='test-only',sha256=h.digest('test-only'))
        self.decision=dict(version='collection103-role-decision-v1',approved=True,reviewer='test-only',
            decisionReference='synthetic in-memory test, not real data',memberSHA256=self.proposal['memberSHA256'])

    def corpus(self):
        added=[dict({k:v for k,v in row.items() if k!='requestedRole'},id=self.source['sha256']+':'+row['id'])
               for row in self.proposal['members']]
        return p.r.d.corpus_document(dict(nativeCollection=self.source),self.old['records']+added,[])

    def test_preserves_all_original_assignments(self):
        result=p.build_admission(self.old,self.previous,self.proposal,self.decision,self.source,self.corpus())
        self.assertEqual(sum(v=='train' for v in result['assignments'].values()),108)
        self.assertTrue(all(result['assignments'][k]==v for k,v in self.previous['assignments'].items()))

    def test_requires_explicit_matching_approval(self):
        for decision in ({},dict(self.decision,approved=False),dict(self.decision,memberSHA256='wrong'),
                         dict(self.decision,reviewer=None),dict(self.decision,decisionReference=None)):
            with self.assertRaisesRegex(ValueError,'explicit_role_decision'):
                p.build_admission(self.old,self.previous,self.proposal,decision,self.source,self.corpus())

    def test_old_mutation_and_new_development_leak_fail(self):
        corpus=copy.deepcopy(self.corpus());corpus['records'][0]['changed']=False
        with self.assertRaisesRegex(ValueError,'preserve_records'):
            p.build_admission(self.old,self.previous,self.proposal,self.decision,self.source,corpus)
        self.proposal['members'][0]['decodedPixelHashes'][0]=self.old['records'][-1]['decodedPixelHashes'][0]
        self.proposal['memberSHA256']=p.h.digest(self.proposal['members']);self.decision['memberSHA256']=self.proposal['memberSHA256']
        with self.assertRaisesRegex(ValueError,'leakage'):
            p.build_admission(self.old,self.previous,self.proposal,self.decision,self.source,self.corpus())

    def test_actual_admit_entry_rejects_before_source_work_or_output(self):
        with tempfile.TemporaryDirectory(dir=p.h.ROOT/'.build',prefix='collection103-') as td:
            root=Path(td);p.h.write(root/'proposal.json',self.proposal,sealed=True)
            p.h.write(root/'decision.json',dict(self.decision,approved=False))
            with patch.object(p.r.d,'collect',side_effect=AssertionError('must not inspect sources without decision')):
                with self.assertRaisesRegex(ValueError,'explicit_role_decision'):
                    p.admit(root/'proposal.json',root/'decision.json',root/'output')
            self.assertFalse((root/'output').exists())
            (root/'output').mkdir()
            with self.assertRaises(ValueError):p.admit(root/'proposal.json',root/'decision.json',root/'output')


if __name__=='__main__':unittest.main()
