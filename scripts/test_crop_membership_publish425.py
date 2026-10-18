"""Exercise retained membership publication through the real isolated queue."""
import copy
import tempfile
import unittest
from pathlib import Path
import research_queue as q
import research_approval as approval
from template_inputs398 import pin


class PublicationTests(unittest.TestCase):
    def test_queue_positive_and_duplicate_rejection(self):
        source = q.ROOT / 'reports/work/PROFILE424/standard-crops.json'
        original = q.load(source)
        with tempfile.TemporaryDirectory(dir=q.ROOT / '.build', prefix='publish425-') as folder:
            root = Path(folder)
            queue = root / 'queue'
            # Use distinct retained pixels in each role for this software check.
            rows = []
            seen = set()
            for role in ('train', 'development'):
                row = next(r for r in original['rows'] if r['role'] == role and r['sha256'] not in seen)
                rows.append(row); seen.add(row['sha256'])
            for name in ('valid', 'duplicate', 'changed-hash', 'missing-development'):
                bad = name != 'valid'
                doc = copy.deepcopy(original); doc['rows'] = copy.deepcopy(rows)
                if name == 'duplicate':doc['rows'].append(copy.deepcopy(rows[0]))
                if name == 'changed-hash':doc['rows'][0]['sha256'] = '0' * 64
                if name == 'missing-development':doc['rows'] = doc['rows'][:1]
                member = root / (name + '.json'); q.save(member, doc)
                spec = q.load(q.ROOT / 'reports/work/CONTINUATION425/producer-spec.json')
                spec['id'] = 'test-publish-' + name
                ref = pin(member)
                spec['inputs'] = [pin(q.MODULES / 'crop_membership_publish425.py'), ref]
                spec['stage'] = [{'from': ref, 'to': 'membership.json'}]
                spec['evidence']['reads'] = [ref['path']]
                path = root / (name + '-spec.json'); q.save(path, spec)
                q.submit(path, queue)
                approval.approve(queue, spec['id'], 'test', 'Isolated positive and negative publication checks.')
                result = q.run(queue, max_jobs=1, lock=root / 'lock', job_ids=[spec['id']])
                out = queue / 'jobs' / spec['id'] / 'attempts/1/out'
                self.assertEqual(result, [(spec['id'], 'failed' if bad else 'complete')],
                                 (out.parent / 'result.json').read_text() + (out.parent / 'stderr.log').read_text())
                if not bad:self.assertEqual(q.digest(out / 'crops.json'), q.digest(member))
                else:self.assertFalse((out / 'crops.json').exists())


if __name__ == '__main__':
    unittest.main()
