"""Member-bound approval and trainer refusal; retained integration runs separately."""
import copy
import importlib.util
import json
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path
from focus_dataset_contract import ROOT, digest
from focus_training_preflight import preflight

spec=importlib.util.spec_from_file_location('control32',ROOT/'reports/work/FOCUS-CONTROL32-ADMIT-01/assemble.py')
module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)


class AdmissionTests(unittest.TestCase):
    def setUp(self):
        temporary=tempfile.TemporaryDirectory(dir=ROOT/'.build/debug-output',prefix='control32-unit-')
        self.addCleanup(temporary.cleanup)
        path=Path(temporary.name)/'proposal.json'
        self.proposal=dict(proposedPairs=32,members=[dict(corpusID='unit-source',pairID=str(i),
            recommendation='propose-training-addition' if i<32 else 'hold-for-geometry-comparison',
            crops=[dict(sha256='1'*64)]) for i in range(96)])
        self.proposal['proposalSHA256']=digest(self.proposal)
        path.write_text(json.dumps(self.proposal))
        for name,value in (('PROPOSAL',path),('SEAL',self.proposal['proposalSHA256'])):
            p=patch.object(module,name,value);p.start();self.addCleanup(p.stop)
        self.approval=dict(version='focus-control32-approval-v1',proposal=module.o.ref(module.PROPOSAL),
            proposalSHA256=module.SEAL,members=[m for m in self.proposal['members'] if m['recommendation']=='propose-training-addition'],
            approved=True,scope='training-candidate-data-only',
            authority='User: Approved; exact 32-pair proposal, current conversation',trainingExecutionApproved=False)

    def test_exact_approval(self):
        self.assertEqual(len(module.members(self.proposal,self.approval)),32)

    def test_changed_proposal_rejected(self):
        for field,value in [('proposedPairs',31),('proposalSHA256','0'*64)]:
            p=copy.deepcopy(self.proposal);p[field]=value
            with self.assertRaises(ValueError):module.members(p,self.approval)

    def test_approval_cannot_expand_scope_or_change_members(self):
        variants=[]
        a=copy.deepcopy(self.approval);a['members'].pop();variants.append(a)
        a=copy.deepcopy(self.approval);a['members'].append(self.proposal['members'][-1]);variants.append(a)
        a=copy.deepcopy(self.approval);a['trainingExecutionApproved']=True;variants.append(a)
        a=copy.deepcopy(self.approval);a['approved']=False;variants.append(a)
        a=copy.deepcopy(self.approval);a['members'][0]['crops'][0]['sha256']='0'*64;variants.append(a)
        for a in variants:
            with self.assertRaises(ValueError):module.members(self.proposal,a)

    def test_actual_trainer_preflight_refuses_data_assembly(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'.build/debug-output',prefix='control32-') as folder:
            Path(folder,'focus_dataset_manifest.json').write_text(json.dumps({'version':'focus-control32-data-assembly-v1'}))
            result=preflight(Path(folder),'control32-preflight-only')
            self.assertFalse(result['launchEligible'])
            self.assertIn('data_admission_is_not_training_execution_approval',str(result))


if __name__=='__main__':unittest.main()
