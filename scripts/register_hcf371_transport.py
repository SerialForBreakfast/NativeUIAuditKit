"""Preserve the failed USB capture and register successors with worker-owned writes."""
import copy
from research_campaign340 import pin
import research_queue as q
import research_graph


def register():
    from generation352 import MARKER
    q.require(not MARKER.exists(), 'capture_recovery_pending')
    old=q.ROOT/'Research/ResearchSpecs/HCF371'
    folder=q.ROOT/'Research/ResearchSpecs/HCF371-r4'
    q.require(not folder.exists(),'successor_exists');folder.mkdir()
    design=q.load(old/'design.json')
    for case in design['cases']:
        case['theme']=case['recipe']['theme'];case['recipe']['theme']='dark'
    q.save(folder/'design.json',design)
    graph=q.load(old/'graph.json'); specs={};nodes=[];additions=[]
    for node in graph['nodes']:
        original=q.load(q.QUEUE/'jobs'/node['job']/'spec.json')
        state,_=q.state(q.QUEUE/'jobs'/node['job'])
        if node['job'] in ('hcf371-00-retained','hcf371-01-retained-rules'):
            q.require(state=='complete','retained_result_missing')
            specs[node['job']]=original;nodes.append(node);continue
        spec=copy.deepcopy(original);spec['id']=spec['id'].replace('hcf371-','hcf371r4-',1)
        spec['inputs']=[pin(folder/'design.json') if r['path'].endswith('HCF371/design.json') else pin(q.ROOT/r['path']) for r in spec['inputs']]
        if 'training' in spec:spec['training']['membership']=[pin(folder/'design.json')]
        if 'capture' in spec:
            plan=q.load(q.ROOT/spec['capture']['plan']['path'])
            plan['shard']='r4-'+plan['shard']
            for case in plan['cases']:
                case['theme']=case['recipe']['theme'];case['recipe']['theme']='dark'
            path=folder/(plan['shard']+'-plan.json');q.save(path,plan)
            spec['capture']['plan']=pin(path)
        for dependency in spec.get('dependencies',[]):
            parent=specs[dependency['job']]
            dependency.update(job=parent['id'],specSHA256=q.text_digest(parent))
        path=folder/(spec['id']+'.json');q.save(path,spec);q.submit(path)
        specs[node['job']]=spec
        nodes.append(dict(node,job=spec['id'],specSHA256=q.text_digest(spec)))
        additions.append(dict(id=spec['id'],sha256=q.text_digest(spec)))
    result=dict(version='research-graph-v1',id='HCF371-r4',nodes=nodes)
    print(research_graph.validate_graph(result));q.save(folder/'graph.json',result);q.save(folder/'additions.json',additions)


if __name__=='__main__':register()
