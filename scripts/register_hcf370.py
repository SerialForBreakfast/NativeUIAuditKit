"""Queue matched position and artwork tests after native spatial qualification."""
import copy
import research_queue as q
import dataset351
import hcf_capture362 as h
from generation352 import MARKER
from research_campaign340 import pin


def variant(base, name):
    plan = copy.deepcopy(base)
    composition = plan['recipe']['appearance']['composition']
    if name == 'opposite-corners':
        plan['targets'] = ['item-1', 'item-2']
    elif name == 'center':
        for region, origin in zip(composition['regions'], ((550, 250), (1050, 250), (550, 650), (1050, 650))):
            region['frame'][:2] = origin
    elif name == 'artwork-exchange':
        for index, content in enumerate(composition['contents'].values()):
            content['seed'] = 23000+index
            content['title'] = 'Example '+str(23000+index)
    else:
        raise ValueError('unknown_variant')
    # These recipes share the earlier family. They cannot become an independent audit set.
    plan['group'] = base['group']
    h.validate_plan(plan)
    return plan


def register():
    q.require(not MARKER.exists(), 'capture_guard_present')
    for name in ('small-dark', 'large-dark', 'small-light'):
        result = q.QUEUE/('jobs/hcf369-'+name+'-spatial/attempts/1/out/summary.json')
        q.require(q.load(result)['followsFocus'], 'spatial_qualification_missing')
    binding = dataset351.run(None)['binding']
    base_folder = q.ROOT/'Research/ResearchSpecs/HCF368'
    base = q.load(base_folder/'small-dark-plan.json')
    q.require(binding == base['binding'], 'fixture_changed')
    q.require(q.digest(h.CLI.resolve()) == base['helperSHA256'], 'helper_changed')
    folder = q.ROOT/'Research/ResearchSpecs/HCF370'
    folder.mkdir(exist_ok=True)
    additions = []
    for name in ('opposite-corners', 'center', 'artwork-exchange'):
        plan = variant(base, name)
        path = folder/(name+'-plan.json')
        q.save(path, plan)
        spec = q.load(base_folder/'hcf368-small-dark-capture.json')
        spec.update(id='hcf370-'+name+'-capture', task='HCF370',
            hypothesis='Capture matched native OS profiles with '+name+'. Keep all other recipe factors fixed.',
            decisionRule='Require observed native focus and restored state. Use the spatial comparison to decide whether this variation preserves the HCF cue.')
        spec['capture']['plan'] = pin(path)
        spec['inputs'] = [pin(q.ROOT/ref['path']) for ref in spec['inputs']]
        path = folder/(spec['id']+'.json')
        q.save(path, spec); q.submit(path)
        additions.append(dict(id=spec['id'], sha256=q.text_digest(spec)))
        audit = q.load(q.ROOT/'Research/ResearchSpecs/HCF369/hcf369-small-dark-spatial.json')
        audit.update(id='hcf370-'+name+'-spatial', task='HCF370',
            hypothesis='Test whether native HCF differences still follow focus with '+name+'.',
            decisionRule='Compare focused and unfocused controls with fixed windows and repeat noise. Report failures before expanding collection.',
            dependencies=[dict(job=spec['id'], specSHA256=q.text_digest(spec), outputs=['capture/capture.json'])])
        path = folder/(audit['id']+'.json')
        q.save(path, audit); q.submit(path)
        additions.append(dict(id=audit['id'], sha256=q.text_digest(audit)))
    q.save(folder/'additions.json', additions)


if __name__ == '__main__':
    register()
