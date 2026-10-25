"""Consume predecessor evidence before any campaign dispatch."""
import unittest
from pathlib import Path
from unittest.mock import patch
import research_queue as q
import ttr_campaign_queue493 as adapter

class DependencyTests(unittest.TestCase):
    def invoke(self, cleanup):
        values=[{'capture':{'plan':{'path':'config','sha256':'0'*64}}},{},
                [{'outputs':[{'path':'receipt','sha256':'0'*64}]}],
                {'cleanup':cleanup,'modelAccepted':False}]
        with patch.object(adapter,'OUT',Path('/unused/job/attempts/1/out')), \
             patch.object(q,'load',side_effect=values) as read, \
             patch.object(adapter,'checked',side_effect=lambda x:Path(x['path'])), \
             patch.object(adapter,'Client'),patch.object(adapter,'execute') as execute:
            if cleanup:
                adapter.run();execute.assert_called_once();self.assertEqual(read.call_count,4)
            else:
                with self.assertRaisesRegex(ValueError,'campaign_dependency_cleanup'):adapter.run()
                execute.assert_not_called()
    def test_valid_receipt_is_read_before_dispatch(self):self.invoke(True)
    def test_failed_cleanup_prevents_dispatch(self):self.invoke(False)

if __name__=='__main__':unittest.main()
