"""Keep selected capture validation pinned without importing unrelated contracts."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import research_queue as q
import research_approval as approval
import research_capture_contracts as contracts


class CaptureContractTests(unittest.TestCase):
    def spec(self,step,authority='capture'):
        return dict(authority=authority,adapter=dict(steps=[step]))
    def test_only_named_capture_adapter_selects_a_contract(self):
        for step,name in contracts.MODULES.items():
            self.assertEqual(contracts.module_for(self.spec(step)),name)
            self.assertEqual(name,step.split('.')[0])
            with patch.object(contracts.importlib,'import_module',return_value='selected') as load:
                self.assertEqual(contracts.selected(self.spec(step)),'selected');load.assert_called_once_with(name)
        for spec in [self.spec('sdk_capture527.run','diagnostic'),self.spec('unapproved.run'),dict(authority='capture',adapter=dict(steps=[]))]:
            self.assertIsNone(contracts.module_for(spec))
            with patch.object(contracts.importlib,'import_module') as load:
                with self.assertRaisesRegex(ValueError,'unknown'):contracts.selected(spec)
                load.assert_not_called()
    def test_registry_cannot_substitute_an_unpinned_module(self):
        with patch.dict(contracts.MODULES,{'sdk_capture527.run':'other_module'}):
            with self.assertRaisesRegex(ValueError,'module_mismatch'):contracts.selected(self.spec('sdk_capture527.run'))
    def test_selected_source_changes_still_change_code_pins(self):
        with tempfile.TemporaryDirectory(dir=q.ROOT/'.build',prefix='capture580-') as temp:
            modules=Path(temp);path=modules/'sdk_capture527.py'
            path.write_text('def run(): return 1\n')
            spec=self.spec('sdk_capture527.run')
            before={r['path']:r['sha256'] for r in approval.code_pins(spec,modules)}
            self.assertEqual(before[q.relative(path)],q.digest(path))
            self.assertIn('scripts/research_capture_contracts.py',before)
            path.write_text('def run(): return 2\n')
            after={r['path']:r['sha256'] for r in approval.code_pins(spec,modules)}
            self.assertNotEqual(before[q.relative(path)],after[q.relative(path)])
    def test_non_capture_closure_excludes_capture_dispatch_and_authoring(self):
        spec=self.spec('template_adapters395.run','diagnostic')
        pins={r['path'] for r in approval.code_pins(spec,q.MODULES)}
        for name in list(contracts.MODULES.values())+['experiment_templates','hcf_templates395','template_analysis397']:
            self.assertNotIn('scripts/'+name+'.py',pins)
        self.assertIn('scripts/research_capture_contracts.py',pins)

if __name__=='__main__':unittest.main()
