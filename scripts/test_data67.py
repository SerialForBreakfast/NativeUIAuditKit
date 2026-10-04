import copy
import unittest
from unittest.mock import patch
import focus_direct_transition as d
from prepare_data67 import original_corpus
from evaluate_data67 import group,summarize


class DataTests(unittest.TestCase):
    def test_cli_parity_uses_prepared_membership(self):
        from qualify_context57 import protocol_rows
        protocol=dict(preparedInputs={},corpusSHA256='c',admission={'hash':'a'},sources={})
        with patch.object(d.h,'checked',return_value='unused'),patch.object(d,'collect',side_effect=AssertionError('intake')), \
             patch('prepare_transition_inputs.manifest',return_value=({'admission':protocol['admission']},
                 {'corpusSHA256':'c','sources':{}},['row'])):
            self.assertEqual(protocol_rows(protocol),['row'])
            with self.assertRaisesRegex(ValueError,'parity_prepared_binding'):protocol_rows(dict(protocol,corpusSHA256='changed'))

    def test_original_prefix_is_hash_bound(self):
        rows=[dict(id=str(i),group='g',changed=bool(i%2)) for i in range(29)]
        old=dict(version='focus-direct-corpus-v1',sources={'reference':1,'settings':2},records=rows,
            excluded=[],groups={'g':{'unchanged':15,'changed':14}},trainingEligible=False)
        old['corpusSHA256']=d.digest(old)
        protocol=dict(sources=old['sources'],corpusSHA256=old['corpusSHA256'])
        new=dict(old,records=rows+[dict(id='new',group='g',changed=False)],sources=dict(old['sources'],negatives=3))
        self.assertEqual(original_corpus(new,protocol),old)
        for mutate in (lambda v:v['records'][0].update(changed=True),lambda v:v['records'].reverse(),
                       lambda v:v.update(excluded=['other']),lambda v:v['sources'].update(reference=5)):
            bad=copy.deepcopy(new);mutate(bad)
            with self.assertRaises(ValueError):original_corpus(bad,protocol)

    def test_group_and_abstention(self):
        self.assertEqual(group(dict(id='a',split='train'),['a']),'original24')
        self.assertEqual(group(dict(id='b',split='train'),['a']),'added8')
        self.assertEqual(group(dict(id='b',split='development'),['a']),'development')
        row=dict(prediction=dict(decision='unknown'),expectedChange=False,rawChangeCorrect=False,bothBoxesCorrect=False,baseline=None)
        report=summarize([row]);self.assertEqual(report['decidedFalseChanges'],0)
        self.assertEqual(report['all']['abstained'],1)


if __name__=='__main__':unittest.main()
