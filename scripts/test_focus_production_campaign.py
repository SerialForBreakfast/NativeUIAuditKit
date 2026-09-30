import copy
import unittest
from focus_production_campaign import inventory, schedule, reserve, QUOTAS, COUNTS
from harvest_sidecar_v2 import recipe_hash


def pair(key,scene='gridMatrix',split='train'):
    return [dict(id=f'{key}:{label}',sourceID='source',pairID=key,label=label,split=split,
                 scene=scene,style='light',control='collectionItem',relatedGroup='family',
                 frame={'pixelSHA256':f'frame-{key}-{label}'},
                 crop={'pixelSHA256':f'crop-{key}-{label}'}) for label in (0,1)]


class CampaignTests(unittest.TestCase):
    def test_exact_quotas_and_no_native_settings_reclassification(self):
        value=inventory(pair('a')+pair('b','settings/general')+pair('c','settingsList','validation'))
        self.assertEqual(value['canonicalAdditionalPairs'],5999)
        self.assertEqual(value['nonQuotaTrainingPairs'],1)
        self.assertEqual(value['sceneQuota']['settingsList']['remaining'],1000)

    def test_schedule_deterministic_bounded_and_hashable(self):
        coverage=inventory(pair('a'));jobs=schedule(coverage)
        self.assertEqual(jobs,schedule(coverage))
        self.assertEqual(len({j['id'] for j in jobs}),len(jobs))
        for scene in QUOTAS:
            subset=[j for j in jobs if j['scene']==scene]
            self.assertEqual(sum(j['collectionTarget'] for j in subset),coverage['sceneQuota'][scene]['remaining'])
            self.assertEqual({j['recipe']['theme'] for j in subset},{'dark','light','high_contrast'})
            for j in subset:
                self.assertIn(j['requestedElements'],COUNTS[scene])
                self.assertLessEqual(j['collectionTarget'],j['requestedElements'])
                self.assertEqual(j['recipeSHA256'],recipe_hash(j['recipe']))
                self.assertEqual(j['admittedPairs'],0)

    def test_full_quota_no_jobs(self):
        self.assertEqual(schedule({'sceneQuota':{s:{'remaining':0} for s in QUOTAS}}),[])

    def test_incomplete_duplicate_conflicting_pair_rejected(self):
        p=pair('a')
        for rows in (p[:1],p+p):
            with self.assertRaises(ValueError):inventory(rows)
        q=copy.deepcopy(p);q[0]['split']='test'
        with self.assertRaises(ValueError):inventory(q)
        q=copy.deepcopy(p);q[0]['crop']=q[1]['crop']
        with self.assertRaises(ValueError):inventory(q)

    def test_cross_role_pixel_leakage_rejected(self):
        p=pair('a');q=pair('b',split='test');q[0]['frame']=p[0]['frame']
        with self.assertRaises(ValueError):inventory(p+q)

    def test_roles_and_challenge_never_reassigned(self):
        r=[dict(role='protected-challenge',groups=['family'],members=['image'])]
        self.assertEqual(reserve(r)['members']['image'],'protected-challenge')
        for extra in [dict(role='train-candidate',groups=['family'],members=['another']),
                      dict(role='train-candidate',groups=['other'],members=['image'])]:
            with self.assertRaises(ValueError):reserve(r+[extra])


if __name__=='__main__':unittest.main()
