"""Offline compiler checks. These tests do not admit or run queue jobs."""
import copy
from pathlib import Path
import tempfile
import unittest

import hcf_templates395 as compiler
import research_queue as q
from experiment_templates import pin


class PredictionAdmissionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=q.ROOT / '.build', prefix='train666-admission-')
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        weights = root / 'weights.pt'
        weights.write_bytes(b'offline software fixture')
        initial = pin(weights)
        membership = root / 'membership.json'
        q.save(membership, {'rows': []})
        config = root / 'configuration.json'
        q.save(config, {'initialization': initial})
        self.doc = dict(version='hcf-template-description-v1', id='train666-software-test', task='TRAIN666',
                        owner='Maximum-mini-NUIAK', template='T107', question='Does the candidate improve benchmark recall?',
                        decision='Compare both seeds on frozen TVBench development beyond measured noise.',
                        inputs=dict(configuration=pin(config), initialization=initial, membership=pin(membership)),
                        parameters={}, dependencies=[], training=dict(experimentLogRunId='TRAIN666-SOFTWARE',
                        membership=[pin(membership)], initialization=initial, epochs=100,
                        storageBudgetBytes=2 << 30, acceptanceEvidence='Paired frozen TVBench development scores.',
                        resume='restart'))

    def test_new_detector_compilation_requires_prediction(self):
        for template in ('T89', 'T107'):
            for value in (None, '', '   ', 42, {}):
                doc = copy.deepcopy(self.doc)
                doc['template'] = template
                doc['training']['epochs'] = 30 if template == 'T89' else 100
                if value is not None:
                    doc['training']['expectedScoreboardChange'] = value
                with self.subTest(template=template, prediction=value):
                    with self.assertRaisesRegex(ValueError, 'training_expected_scoreboard_change'):
                        compiler.build(doc)

    def test_prediction_survives_compilation_and_historical_validation(self):
        for template in ('T89', 'T107'):
            doc = copy.deepcopy(self.doc)
            doc['template'] = template
            doc['training']['epochs'] = 30 if template == 'T89' else 100
            prediction = 'Localization recall on frozen TVBench development improves beyond seed noise at both seeds.'
            doc['training']['expectedScoreboardChange'] = prediction
            spec = compiler.build(doc)
            self.assertEqual(spec['training']['expectedScoreboardChange'], prediction)
            q.validate(spec)
            legacy = copy.deepcopy(spec)
            del legacy['training']['expectedScoreboardChange']
            frozen = q.text_digest(legacy)
            q.validate(legacy)
            q.validate(legacy)  # Retry validation uses the same immutable specification.
            self.assertEqual(q.text_digest(legacy), frozen)


if __name__ == '__main__':
    unittest.main()
