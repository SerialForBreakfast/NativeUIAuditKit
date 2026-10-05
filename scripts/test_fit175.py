import copy
import unittest
from unittest.mock import patch
import fit175 as f


class FitTests(unittest.TestCase):
    def metadata(self):
        return {f'{g}-{p}':dict(group=str(g),tint='blue',placement=p)
            for g in range(72) for p in ('leading','center','trailing')}

    def test_exact_triads_stable_with_incomplete_extras(self):
        data=self.metadata();wanted=f.select(data)
        data['extra']=dict(group='extra',tint='blue',placement='leading')
        self.assertEqual(wanted,f.select(dict(reversed(list(data.items())))))
        self.assertEqual(len(wanted),216)

    def test_duplicate_missing_unknown_rejected(self):
        for kind in ('duplicate','missing','unknown'):
            data=self.metadata()
            if kind=='duplicate':data['dup']=data['0-leading']
            elif kind=='missing':data.pop('0-leading')
            else:data['0-leading']['placement']='mystery'
            with self.subTest(kind=kind),self.assertRaises(Exception):f.select(data)

    def test_prepare_collision_precedes_inputs(self):
        with patch.object(f,'OUT',f.h.ROOT),patch.object(f.d,'inputs') as read:
            with self.assertRaisesRegex(Exception,'output_collision'):f.prepare()
            read.assert_not_called()

    def test_terminal_requires_fixed_settings_epochs_finiteness(self):
        args=dict(f.p.control.full_frame_finetune_kwargs(),epochs=20,imgsz=640,batch=8,workers=0,
            device='mps',resume=False,seed=42,optimizer='AdamW',cos_lr=True,name=f.RUN.name,
            data=str(f.OUT/'dataset/dataset.yaml'))
        rows=[{'epoch':str(i),'loss':'0.5'} for i in range(1,21)];f.check_terminal(args,rows)
        for kind in ('settings','epochs','nan'):
            a=copy.deepcopy(args);r=copy.deepcopy(rows)
            if kind=='settings':a['translate']=.1
            elif kind=='epochs':r.pop()
            else:r[0]['loss']='nan'
            with self.subTest(kind=kind),self.assertRaises(Exception):f.check_terminal(a,r)


if __name__=='__main__':unittest.main()
