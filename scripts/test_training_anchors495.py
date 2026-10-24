"""Run anchor preparation through an isolated queue, including rejected membership."""
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path
import research_queue as q
import research_approval as approval
import hcf_templates395 as templates
from experiment_templates import pin


class AnchorQueueTests(unittest.TestCase):
    def setUp(self):
        # The runtime adapter is independent of the pending authoring-catalog activation.
        self.contract = patch.dict(templates.CONTRACTS, {
            'T93': ({'membership', 'original', 'suite'}, set(), 'training_anchors495.run', 'artifact', 'diagnostic')})
        self.contract.start()

    def tearDown(self): self.contract.stop()

    def test_two_requests_and_rejected_evaluation_group(self):
        with tempfile.TemporaryDirectory(dir=q.ROOT/'.build', prefix='anchors495-') as folder:
            root = Path(folder); queue = root/'queue'
            image = root/'pixels'; image.write_bytes(b'software-only-pixels')
            rows = [dict(id=str(i), role='train', label=i, group='train', profile='standard',
                         path=str(image), sha256=q.digest(image)) for i in (0, 1)]
            original=root/'original.json'; q.save(original,dict(rows=rows))
            membership=root/'membership.json'; q.save(membership,dict(rows=[dict(r,id='copy-'+r['id'],sourceID=r['id']) for r in rows]))
            suite=root/'suite.json';q.save(suite,dict(excludedGroups=['evaluation']))
            bad=root/'bad.json';q.save(bad,dict(excludedGroups=['train']))
            for ident, ref in [('anchors-one',suite),('anchors-two',suite),('anchors-z-invalid',bad)]:
                spec=templates.build(dict(version='hcf-template-description-v1',id=ident,template='T93',
                    owner='Maximum-mini-NUIAK',inputs=dict(membership=pin(membership),original=pin(original),suite=pin(ref)),
                    parameters={},dependencies=[],question='Does exact source matching exclude evaluation rows from teacher anchors?',
                    decision='Reject altered membership or evaluation ancestry. Software evidence only.'))
                path=root/(ident+'.json');q.save(path,spec);q.submit(path,queue)
                approval.approve(queue,ident,'test','Isolated anchor software qualification.')
            q.run(queue,max_jobs=3,lock=root/'lock')
            self.assertEqual(q.state(queue/'jobs/anchors-one')[0],'complete')
            self.assertEqual(q.state(queue/'jobs/anchors-two')[0],'complete')
            failure=q.load(queue/'jobs/anchors-z-invalid/attempts/1/result.json')
            self.assertNotEqual(failure['status'],'complete')
            error=(queue/'jobs/anchors-z-invalid/attempts/1/stderr.log')
            self.assertIn('anchor_evaluation_overlap',error.read_text())


if __name__ == '__main__': unittest.main()
