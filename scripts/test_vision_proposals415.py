"""T50 Vision rectangle proposals: parameter checks and isolated-queue qualification on the 46 reviewed tvOS frames."""
from pathlib import Path
import shutil
import tempfile
import unittest
import research_queue as q
import experiment_batch402 as batches
from vision_proposals415 import parameters

LABELS = 'reports/work/REAL-MODEL-SCORECARD-36/production/inputs.json'
BASELINE = 'reports/work/REAL-MODEL-SCORECARD-36/scorecard-final/scorecard.json'
TOOL = '.build/vision-probe/vision_annotation_probe'


class UnitTests(unittest.TestCase):
    def test_parameters(self):
        self.assertEqual(parameters(dict(proposals='rectangles', slice='class')), ('rectangles', 'class'))
        for value, error in [(dict(proposals='saliency', slice='class'), 'proposal_source'),
                             (dict(proposals='none', slice='geometry'), 'proposal_slice'),
                             (dict(proposals='none'), 'proposal_parameters')]:
            with self.assertRaisesRegex(ValueError, error): parameters(value)


@unittest.skipUnless((q.ROOT / TOOL).is_file(), 'compile scripts/vision_annotation_probe.swift to ' + TOOL)
class QueueTests(unittest.TestCase):
    """Control, rectangle, and changed-tool paths through the actual queue."""

    def test_actual_queue(self):
        with tempfile.TemporaryDirectory(dir=q.ROOT / '.build', prefix='vision415-') as folder:
            root = Path(folder); queue = root / 'queue'
            changed = root / 'probe'
            shutil.copyfile(q.ROOT / TOOL, changed)

            def desc(ident, source, tool=TOOL):
                return dict(version='hcf-template-description-v1', id=ident, owner='test-NUIAK', template='T50',
                            question='How many missed tvOS controls do Vision rectangles recover?',
                            decision='Keep rectangles only if they recover controls at a low unmatched cost.',
                            inputs=dict(labels=dict(file=LABELS), baseline=dict(file=BASELINE), tool=dict(file=tool)),
                            parameters=dict(proposals=source, slice='class'), dependencies=[])
            docs = [desc('vision-control', 'none'), desc('vision-rectangles', 'rectangles'),
                    desc('vision-changed', 'rectangles', q.relative(changed))]
            batches.register_batch(dict(version='experiment-batch-v1', jobs=docs), queue, [d['id'] for d in docs], approver='test')
            # Negative: the tool changes after registration. The pin check fails before any probe call.
            changed.write_bytes(changed.read_bytes() + b'\0')
            for ident in ('vision-control', 'vision-rectangles'):
                self.assertEqual(q.run(queue, max_jobs=1, lock=root / 'lock', job_ids=[ident]), [(ident, 'complete')])
            control, added = [q.load(queue / 'jobs' / i / 'attempts/1/out/benchmark_summary.json')
                              for i in ('vision-control', 'vision-rectangles')]
            # The control reproduces the stored scorecard: 346 of 583 controls located at IoU 0.5.
            self.assertEqual(control['totals']['candidate']['detected'], 346)
            self.assertEqual((control['gains'], control['lostPriorSuccesses'], control['addedProposals']), ([], [], 0))
            self.assertGreater(added['addedProposals'], 0)
            self.assertEqual(added['lostPriorSuccesses'], []); self.assertFalse(added['modelAccepted'])
            self.assertEqual(q.run(queue, max_jobs=1, lock=root / 'lock', job_ids=['vision-changed']), [('vision-changed', 'failed')])
            attempt = queue / 'jobs/vision-changed/attempts/1'
            self.assertFalse((attempt / 'out/benchmark_summary.json').exists())
            # The queue checks input pins before it starts the process, so the reason is in result.json.
            self.assertIn('input_changed', q.load(attempt / 'result.json')['reason'])


if __name__ == '__main__':
    unittest.main()
