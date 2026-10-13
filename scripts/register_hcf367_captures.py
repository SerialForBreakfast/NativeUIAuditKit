"""Queue fresh native pilots after verified recovery. Preserve old attempts."""
import copy
import research_queue as q
import dataset351
from research_campaign340 import pin
import hcf_capture362 as h
from generation352 import MARKER


def fit_regions(plan):
    composition=plan['recipe']['appearance']['composition']
    for region in composition['regions']:
        q.require(len(region['items'])==1, 'pilot_region_count')
        definition=composition['definitions'][region['items'][0]['component']]
        region['frame'][2]=max(region['frame'][2],definition['width'])
        region['frame'][3]=max(region['frame'][3],definition['height'])
        x,y,w,h=region['frame']
        q.require(x+w<=1920 and y+h<=1080, 'pilot_outside_screen')


def register(prefix='hcf368', recovery_id='hcf368-recover'):
    recovery=q.QUEUE/('jobs/'+recovery_id+'/attempts/1/out')
    q.require(q.load(recovery/'recovery.json')['complete'], 'recovery_missing')
    q.require(not MARKER.exists(), 'capture_guard_present')
    qualification=recovery/'qualification/qualification.json'
    q.require(q.load(qualification)['complete'], 'qualification_missing')
    original=dataset351.run(None)
    q.require(q.ID.fullmatch(prefix) is not None, 'capture_prefix')
    folder=q.ROOT/'Research/ResearchSpecs'/prefix.upper()
    folder.mkdir(exist_ok=True)
    additions=[]
    for name in ('small-dark','large-dark','small-light'):
        old=q.ROOT/'Research/ResearchSpecs/HCF362'
        plan=q.load(old/(name+'-plan.json'))
        fit_regions(plan)
        plan['normalizeSettings']=True
        plan['binding']=original['binding']
        plan['helperSHA256']=q.digest(h.CLI.resolve())
        plan['qualification']['evidence']=pin(qualification)
        # These replacements retain the original development group and exclusions.
        h.validate_plan(plan)
        pp=folder/(name+'-plan.json');q.save(pp,plan)
        spec=q.load(old/('hcf362-'+name+'-capture.json'))
        spec['id']=prefix+'-'+name+'-capture';spec['task']='HCF367'
        spec['inputs']=[pin(q.ROOT/ref['path']) for ref in spec['inputs']
                        if ref['path'].startswith('scripts/')]+[pin(qualification),pin(recovery/'recovery.json'),
                        pin(q.ROOT/'scripts/hcf_settings368.py')]
        spec['capture']['plan']=pin(pp)
        path=folder/(spec['id']+'.json');q.save(path,spec);q.submit(path)
        additions.append(dict(id=spec['id'],sha256=q.text_digest(spec)))
        compare=copy.deepcopy(spec);compare.pop('capture')
        compare.update(id=prefix+'-'+name+'-compare',authority='diagnostic',
            hypothesis='Measure native Standard/HCF differences against repeated capture noise: '+name,
            decisionRule='Report visible native cues separately from switching success. Do not admit training data.',
            dependencies=[dict(job=spec['id'],specSHA256=q.text_digest(spec),outputs=['capture/capture.json'])],
            adapter=dict(type='python-callable',steps=['hcf_capture362.compare'],outputAttributes=['hcf_capture362.OUT']))
        path=folder/(compare['id']+'.json');q.save(path,compare);q.submit(path)
        additions.append(dict(id=compare['id'],sha256=q.text_digest(compare)))
    q.save(folder/'capture-additions.json',additions)
    print('Registered 3 native pilots and 3 matched comparisons.')


if __name__=='__main__':register()
