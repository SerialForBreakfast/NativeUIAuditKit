"""Test the restore contract without loading checkpoint objects."""
import copy
import unittest
from unittest.mock import patch
import checkpoint_restore404 as restore


class AdmissionTests(unittest.TestCase):
    def setUp(self):
        self.refs={name:{'path':name,'sha256':'a'*64} for name in
                   ('checkpoint','qualification','membership','initialization')}
        self.spec={'resumeInputs':self.refs,'inputs':list(self.refs.values()),
                   'training':{'initialization':self.refs['initialization'],
                               'membership':[self.refs['membership']],'epochs':30},
                   'limits':{'timeoutSeconds':800}}
        self.proof={'version':'hcf-crop-restoration-v1','passed':True,
                    'sources':{k:self.refs[k] for k in ('membership','initialization')}}

    def check(self):
        with patch.object(restore,'checked',return_value='proof'), patch.object(restore.q,'load',return_value=self.proof):
            return restore.validate_inputs(self.spec)

    def test_valid_contract(self):
        self.assertEqual(self.check(),self.refs)

    def test_unpinned_input(self):
        self.spec['inputs']=self.spec['inputs'][1:]
        with self.assertRaisesRegex(ValueError,'restore_input_not_pinned'):self.check()

    def test_failed_qualification(self):
        self.proof['passed']=False
        with self.assertRaisesRegex(ValueError,'restore_unqualified'):self.check()

    def test_changed_membership(self):
        self.proof=copy.deepcopy(self.proof)
        self.proof['sources']['membership']['sha256']='b'*64
        with self.assertRaisesRegex(ValueError,'restore_configuration_not_qualified'):self.check()

    def test_changed_epoch_limit(self):
        self.spec['training']['epochs']=31
        with self.assertRaisesRegex(ValueError,'restore_limits'):self.check()

    def test_missing_inputs(self):
        self.spec['resumeInputs']={}
        with self.assertRaisesRegex(ValueError,'restore_inputs'):self.check()

    def test_subset_preserves_all_settings_and_membership(self):
        actual={'resumeContract':{'rows':[{'id':'a'},{'id':'b'}],'repeat':9,'trainer':'fixed'}}
        tested={'resumeContract':{'rows':[{'id':'a'}],'repeat':9,'trainer':'fixed'}}
        self.assertEqual(restore.validate_contract(actual,tested,True),9)
        tested['resumeContract']['repeat']=1
        with self.assertRaisesRegex(ValueError,'contract_not_qualified'):
            restore.validate_contract(actual,tested,True)
        tested['resumeContract']['repeat']=9
        tested['resumeContract']['rows']=[{'id':'other'}]
        with self.assertRaisesRegex(ValueError,'not_training_subset'):
            restore.validate_contract(actual,tested,True)

    def test_default_contract_stays_exact(self):
        a={'resumeContract':{'rows':[1,2]}}
        b={'resumeContract':{'rows':[1]}}
        with self.assertRaisesRegex(ValueError,'contract_not_qualified'):
            restore.validate_contract(a,b)


    # RECOVERY488: bounded chunks need a 2-step chain proof.
    def chain(self):
        self.proof['scopeVersion']=restore.CHAIN
        self.proof['sources']={'initialization':self.refs['initialization']}

    def test_stop_epoch_requires_chain_proof(self):
        self.spec['resumeStopEpoch']=23
        with self.assertRaisesRegex(ValueError,'restore_chain_unqualified'):self.check()
        self.chain()
        self.assertEqual(self.check(),self.refs)

    def test_stop_epoch_range(self):
        self.chain()
        for bad in (0,30,23.0):
            self.spec['resumeStopEpoch']=bad
            with self.subTest(bad=bad),self.assertRaisesRegex(ValueError,'restore_stop_epoch'):self.check()

    def test_dependency_checkpoint(self):
        self.chain()
        self.refs['checkpoint']={'job':'chunk-1','output':'last.pt'}
        self.spec['inputs']=[r for k,r in self.refs.items() if k!='checkpoint']
        with self.assertRaisesRegex(ValueError,'restore_checkpoint_dependency'):self.check()
        self.spec['dependencies']=[{'job':'chunk-1','outputs':['last.pt'],'specSHA256':'c'*64}]
        self.assertEqual(self.check()['checkpoint'],{'job':'chunk-1','output':'last.pt'})
        self.refs['checkpoint']={'job':'chunk-1','output':'final.pt'}
        with self.assertRaisesRegex(ValueError,'restore_checkpoint_dependency'):self.check()

    def test_dependency_checkpoint_requires_chain_proof(self):
        self.refs['checkpoint']={'job':'chunk-1','output':'last.pt'}
        self.spec['dependencies']=[{'job':'chunk-1','outputs':['last.pt'],'specSHA256':'c'*64}]
        with self.assertRaisesRegex(ValueError,'restore_chain_unqualified'):self.check()


if __name__=='__main__':unittest.main()
