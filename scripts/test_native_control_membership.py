"""Matched sample exposure tests. These tests do not establish model accuracy."""
from collections import Counter
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from PIL import Image
import native_control_membership as m
import research_queue as q


class ExposureTests(unittest.TestCase):
    def members(self):
        def row(label, family):
            return dict(id=f'{family}-{label}',family=family,label=label,role='train',group=family)
        return dict(artwork={i:[row(i,'poster')] for i in (0,1)},
                    native={i:[row(i,f) for f in ('button','row','tab')] for i in (0,1)})

    def test_same_exposure_and_development(self):
        dev=[dict(id='dev',role='development')]
        arms=[m.select(self.members(),dev,48,12,a) for a in ('control','mixed')]
        for rows in arms:
            self.assertEqual(len(rows),97)
            self.assertEqual(Counter(r['label'] for r in rows[:-1]),{0:48,1:48})
            self.assertEqual(rows[-1],dev[0])
            self.assertEqual(len({r['id'] for r in rows}),97)
        self.assertEqual(Counter(r['family'] for r in arms[1][:-1]),dict(poster=72,button=8,row=8,tab=8))

    def test_limits(self):
        for args in [(47,12,'control'),(48,13,'mixed'),(48,48,'mixed'),(48,12,'other')]:
            with self.assertRaises(ValueError):m.select(self.members(),[],*args)
        members=self.members();members['native'][0]=[]
        with self.assertRaisesRegex(ValueError,'membership_insufficient_exposure'):
            m.select(members,[],48,12,'mixed')

    def test_missing_changed_and_duplicate_pixels(self):
        with tempfile.TemporaryDirectory(dir=q.ROOT/'.build',prefix='native-membership-') as directory:
            path=Path(directory)/'crop.png';Image.new('RGB',(256,256),(11,22,33)).save(path)
            row=dict(id='a',path=str(path),sha256=q.digest(path),role='train',label=1,group='g',family='button')
            self.assertEqual(len(m.validate_rows([row,dict(row,id='b')])['native'][1]),1)
            for change,reason in [(dict(role='development',group='d'),'membership_pixel_leak'),
                                  (dict(label=0),'membership_label_conflict'),
                                  (dict(sha256='0'*64),'membership_crop_changed')]:
                with self.assertRaisesRegex(ValueError,reason):m.validate_rows([row,dict(row,**change)])
            with self.assertRaises(FileNotFoundError):m.validate_rows([dict(row,path=str(path)+'missing')])

    def test_two_descriptions_through_isolated_queue(self):
        import hcf_templates395 as templates
        import research_approval as approval
        from experiment_templates import pin
        with tempfile.TemporaryDirectory(dir=q.ROOT/'.build',prefix='native-exposure-') as directory:
            root=Path(directory);queue=root/'queue';rows=[]
            for role in ('train','development'):
                for family in ('poster','button','row','tab'):
                    for label in (0,1):
                        index=len(rows);path=root/f'crop-{index}.png'
                        Image.new('RGB',(256,256),(index*10,12,34)).save(path)
                        rows.append(dict(id=f'crop-{index}',path=str(path),sha256=q.digest(path),role=role,
                            family=family,label=label,group=role+'-'+family,profile='standard'))
            for kind in ('artwork','native'):
                selected=[r for r in rows if (r['family']=='poster')==(kind=='artwork')]
                q.save(root/(kind+'.json'),dict(rows=selected,frames=[],runtime={'test':True},preprocessing={'test':True}))
            contract=({'configuration','artwork','native'},set(),'native_control_membership.run','artifact','diagnostic')
            with patch.dict(templates.CONTRACTS,T54=contract):
                for arm in ('control','mixed'):
                    q.save(root/(arm+'.json'),dict(version=m.VERSION,arm=arm,perLabel=48,nativePerLabel=12))
                    ident='native-exposure-'+arm
                    doc=dict(version='hcf-template-description-v1',id=ident,owner='test-NUIAK',template='T54',
                        question='Does membership preserve equal exposure and fixed development?',decision='Require exact counts and no overlap.',
                        inputs=dict(configuration=pin(root/(arm+'.json')),artwork=pin(root/'artwork.json'),native=pin(root/'native.json')),
                        parameters={},dependencies=[])
                    templates.register(doc,queue);approval.approve(queue,ident,'test','Software membership qualification only.')
                    self.assertEqual(q.run(queue,max_jobs=1,lock=root/'lock',job_ids=[ident]),[(ident,'complete')])
                    output=q.load(queue/'jobs'/ident/'attempts/1/out/crops.json')
                    expected=m.select(m.validate_rows(rows),[r for r in rows if r['role']=='development'],48,12,arm)
                    # Input concatenation determines development order, not labels or membership.
                    self.assertEqual(output['rows'][:96],expected[:96])
                    self.assertEqual({r['id'] for r in output['rows'][96:]},{r['id'] for r in expected[96:]})


if __name__=='__main__':unittest.main()
