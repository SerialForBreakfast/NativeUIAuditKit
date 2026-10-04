import copy
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from PIL import Image
import propose_native86 as p
import prepare_proposal74 as bank


class Native86Tests(unittest.TestCase):
    def proposal(self, rows):
        members=[dict(r,requestedRole='train') for r in rows]
        return dict(version='native86-role-proposal-v1',approved=False,executionEligible=False,
            members=members,memberSHA256=p.d.h.digest(members))

    def rows(self):
        return [dict(id=str(i),sourceRole='calibration',group='fixture-procedural-renderer-v1',changed=True) for i in range(24)]

    def test_role_and_membership_guards(self):
        proposal=self.proposal(self.rows());p.validate_proposal(proposal)
        for key,value in [('approved',True),('executionEligible',True),('memberSHA256','changed')]:
            bad=copy.deepcopy(proposal);bad[key]=value
            with self.assertRaises(ValueError):p.validate_proposal(bad)

    def test_admission_preserves_old_rows_and_rejects_unapproved_decision(self):
        h=p.d.h
        oldrows=[dict(id=str(i),changed=True,group='old' if i<44 else 'dev',sourceRole='train' if i<44 else 'development',
            images=[dict(sha256=h.digest(['old-image',i,j])) for j in range(2)],
            decodedPixelHashes=[h.digest([i,j]) for j in range(2)]) for i in range(49)]
        old=p.d.corpus_document({},oldrows,[])
        previous=dict(version='focus-direct-admission-v1',approved=True,reviewer='test',decisionReference='in-memory',
            corpusSHA256=old['corpusSHA256'],assignments={r['id']:r['sourceRole'] for r in oldrows})
        rows=[dict(r,images=[dict(sha256=h.digest(['new-image',i,j])) for j in range(2)],
            decodedPixelHashes=[h.digest(['new',i,j]) for j in range(2)]) for i,r in enumerate(self.rows())]
        proposal=self.proposal(rows);source=dict(path='test-only',sha256=h.digest('source'))
        added=[dict(r,id=source['sha256']+':'+r['id']) for r in rows]
        corpus=p.d.corpus_document(dict(nativeActions=source),oldrows+added,[])
        decision=dict(version='native86-role-decision-v1',approved=True,reviewer='test-only',decisionReference='in-memory',memberSHA256=proposal['memberSHA256'])
        result=p.build_admission(old,previous,proposal,decision,source,corpus)
        self.assertEqual(sum(v=='train' for v in result['assignments'].values()),68)
        self.assertTrue(all(result['assignments'][k]==v for k,v in previous['assignments'].items()))
        for bad in ({},dict(decision,approved=False),dict(decision,memberSHA256='wrong')):
            with self.assertRaises(ValueError):p.build_admission(old,previous,proposal,bad,source,corpus)
        changed=copy.deepcopy(corpus);changed['records'][0]['group']='changed'
        with self.assertRaises(ValueError):p.build_admission(old,previous,proposal,decision,source,changed)
        proposal['members'][0]['decodedPixelHashes'][0]=oldrows[-1]['decodedPixelHashes'][0]
        proposal['memberSHA256']=h.digest(proposal['members']);decision['memberSHA256']=proposal['memberSHA256']
        added[0]['decodedPixelHashes'][0]=oldrows[-1]['decodedPixelHashes'][0]
        corpus=p.d.corpus_document(dict(nativeActions=source),oldrows+added,[])
        with self.assertRaisesRegex(ValueError,'leakage'):p.build_admission(old,previous,proposal,decision,source,corpus)
        for mutate in (lambda rows:rows.pop(),lambda rows:rows[0].update(requestedRole='evaluation'),
            lambda rows:rows[0].update(changed=False),lambda rows:rows[0].update(id=rows[1]['id'])):
            bad=copy.deepcopy(proposal);mutate(bad['members']);bad['memberSHA256']=p.d.h.digest(bad['members'])
            with self.assertRaises(ValueError):p.validate_proposal(bad)

    def test_real_inspector_batches_and_keeps_labels_separate(self):
        h=p.d.h
        with tempfile.TemporaryDirectory(dir=h.ROOT/'.build',prefix='native86-test-') as td:
            root=Path(td);rows=self.rows()
            for i,r in enumerate(rows):
                refs=[]
                for j in range(2):
                    image=root/f'{i}-{j}.png';Image.new('RGB',(40,30),(i*2+j,60,120)).save(image);refs.append(h.ref(image))
                r.update(images=refs,size=[40,30],boxes=[[0,0,20,20]]*2)
            proposal=root/'proposal.json';h.write(proposal,self.proposal(rows))
            probe=root/'probe';probe.write_bytes(b'test-only probe, never executed')
            original=h.read
            def read(path,*args,**kwargs):
                if str(path).endswith('PROPOSAL-RANK-74/bank/inputs.json'):
                    return dict(probe=h.ref(probe),probeSource=h.ref(h.ROOT/'scripts/vision_annotation_probe.swift'))
                return original(path,*args,**kwargs)
            calls=[]
            def run(command,**kwargs):
                request=json.loads(kwargs['input']);calls.append(request)
                return SimpleNamespace(returncode=0,stderr='',stdout=json.dumps(dict(version=1,os='test-only',results=[
                    dict(id=f['id'],sha256=f['sha256'],width=40,height=30,errors=[],text=[],rectangleRevision=1,
                        rectangles=[dict(bounds=[0,0,20,20],confidence=.9)]) for f in request['frames']])))
            with patch.object(p,'verified_records',return_value=rows),patch.object(h,'read',side_effect=read),patch.object(bank.subprocess,'run',side_effect=run):
                result=bank.inspect_calibration(proposal,root/'out',probe)
            self.assertEqual([len(c['frames']) for c in calls],[40,8])
            self.assertTrue(all(set(f)=={'id','path','sha256'} for c in calls for f in c['frames']))
            self.assertEqual(result['nativeInvocations'],2);self.assertFalse(result['trainingLaunched'])
            inputs=original(root/'out/inputs.json');self.assertFalse(inputs['trainingEligible'])
            self.assertEqual(len(inputs['rawBatches']),2)
            self.assertTrue(all(set(c)=={'id','bounds'} for f in inputs['frames'] for c in f['candidates']))
            with self.assertRaises(ValueError):bank.load_inputs(root/'out/inputs.json')


if __name__=='__main__':unittest.main()
