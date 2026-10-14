import unittest
from unittest.mock import patch
from pathlib import Path
import duration358 as d


class DurationTests(unittest.TestCase):
    def test_fixed_epochs_and_restoration(self):
        seen=[]
        def fit(net,x,y,settings,progress,**kwargs):
            seen.append(settings['epochs']);return net,[]
        def training():
            d.p.a.b.trainer.fit(None,None,None,{'epochs':10},None)
        with patch.object(d.p.a.b.trainer,'fit',fit),patch.object(d.p,'training',training):
            d.training()
            self.assertIs(d.p.a.b.trainer.fit,fit)
        self.assertEqual(seen,[30])

    def test_failure_restores_hooks(self):
        fit=d.p.a.b.trainer.fit;emit=d.p.m.emit
        with patch.object(d.p,'training',side_effect=ValueError('failed')):
            with self.assertRaises(ValueError):d.training()
        self.assertIs(d.p.a.b.trainer.fit,fit)
        self.assertIs(d.p.m.emit,emit)

    def test_acceptance_requires_complete_comparisons_and_no_losses(self):
        for count,lost,expected in ((23,0,False),(24,1,False),(24,0,True)):
            rows=[dict(job=f'focus358-control-{i}-movement',counts={'lost':lost if i==0 else 0,'gained':1}) for i in range(count)]
            with patch.object(d.p,'collect'),patch.object(d.p.q,'load',return_value={'summaryRows':rows}),patch.object(d.p.q,'save') as save:
                d.OUT=Path('unused')
                d.collect()
                decisions=save.call_args.args[1]['decisions']
                self.assertEqual(decisions['control']['passesDevelopmentRule'],expected)
                self.assertFalse(decisions['position']['passesDevelopmentRule'])


if __name__=='__main__':unittest.main()
