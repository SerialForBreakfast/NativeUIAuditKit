"""Compare all 4 matched crop-training cells without changing acceptance gates."""
import research_queue as q
from hcf_crop_review376 import review
OUT=None


def run():
    docs={};refs=[]
    for dependency in q.load(OUT/'dependencies.json'):
        ref,=dependency['outputs'];path=q.local_path(q.ROOT,ref['path'])
        q.require(q.digest(path)==ref['sha256'],'comparison_changed')
        docs[dependency['job']]=q.load(path);refs.append(ref)
    control=docs['hcf376-hcf-repeated-evaluate-v1']
    reports={key:review(control,value,{}) for key,value in docs.items() if key!='hcf376-hcf-repeated-evaluate-v1'}
    q.save(OUT/'factor-comparison.json',dict(version='hcf-factor-comparison-v1',comparisons=reports,
        modelAccepted=False,finalAuditOpened=False,
        nextAction='Review gains and losses before selecting a repeat seed. Do not promote from one seed.',
        limitation='Fixed epochs, not equal update counts. Duplicate removal also changes sample-derived positive loss weighting.'))
    q.save(OUT/'sources.json',refs)
