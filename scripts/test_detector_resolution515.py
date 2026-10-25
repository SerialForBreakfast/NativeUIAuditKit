import unittest
import copy
from unittest.mock import patch
from pathlib import Path
import research_queue as q
from experiment_templates import pin
import detector_resolution515 as d

class Tests(unittest.TestCase):
    def refs(self):
        root=q.QUEUE/'jobs'
        a=pin(root/'coverage498-focus-button/attempts/1/out/benchmark_summary.json')
        b=pin(root/'tvos511-focus-button/attempts/1/out/benchmark_summary.json')
        cards=[q.load(q.ROOT/x['path'])['inputs']['scorecard'] for x in (a,b)]
        return *cards,q.load(q.ROOT/cards[0]['path'])['inputs']

    def test_retained_matched_comparison(self):
        result=d.compare(*self.refs());self.assertFalse(result['modelAccepted']);self.assertEqual(result['comparison'],'matched-resolution')

    def test_changed_weights_rejected(self):
        a,b,labels=self.refs();docs=[q.load(q.ROOT/x['path']) for x in (a,b,labels)];docs[1]['identity']['detector']['weightsSHA256']='0'*64
        with patch.object(d.q,'load',side_effect=docs):
            with self.assertRaisesRegex(ValueError,'matched_weights'):d.compare(a,b,labels)

    def test_changed_settings_rejected(self):
        a,b,labels=self.refs();docs=[q.load(q.ROOT/x['path']) for x in (a,b,labels)];docs[1]['settings']['confidence']=.1
        with patch.object(d.q,'load',side_effect=docs):
            with self.assertRaisesRegex(ValueError,'resolution515_settings'):d.compare(a,b,labels)

    def test_two_campaigns_through_queue(self):
        import tempfile
        import research_approval as approval
        a,b,labels=self.refs()
        candidate=b['path'].split('/jobs/')[1].split('/')[0]
        parent=q.load(q.QUEUE/'jobs'/candidate/'spec.json')
        with tempfile.TemporaryDirectory(dir=q.ROOT/'.build',prefix='resolution515-') as folder:
            root=Path(folder);queue=root/'queue'
            # Reuse the verified producer by copying its immutable records into this isolated queue.
            import shutil
            shutil.copytree(q.QUEUE/'jobs'/candidate,queue/'jobs'/candidate)
            for i in range(2):
                plan=root/f'plan-{i}.json';q.save(plan,dict(version='detector-resolution-plan-v1',pairs=[dict(baseline=a,preservation=a,labels=labels,candidate=candidate)]))
                spec=d.make_spec(f'resolution515-test-{i}',plan,[dict(job=candidate,specSHA256=q.text_digest(parent),outputs=['scorecard.json'])],0)
                path=root/f'spec-{i}.json';q.save(path,spec);q.submit(path,queue)
                approval.approve(queue,spec['id'],'test','Isolated retained comparison.')
                self.assertEqual(q.run(queue,job_ids=[spec['id']],max_jobs=1,lock=root/'lock'),[(spec['id'],'complete')])

    def test_role_rejected(self):
        a,b,labels=self.refs();docs=[q.load(q.ROOT/x['path']) for x in (a,b,labels)];docs[2]['trainingEligible']=True
        with patch.object(d.q,'load',side_effect=docs):
            with self.assertRaisesRegex(ValueError,'resolution515_role'):d.compare(a,b,labels)

if __name__=='__main__':unittest.main()
