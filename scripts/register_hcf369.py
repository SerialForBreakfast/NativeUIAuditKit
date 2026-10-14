"""Register spatial attribution of completed native captures without recapture."""
import research_queue as q
from research_campaign340 import pin


def register():
    folder = q.ROOT/'Research/ResearchSpecs/HCF369'
    folder.mkdir(exist_ok=True)
    additions = []
    for name in ('small-dark', 'large-dark', 'small-light'):
        spec = q.load(q.ROOT/'Research/ResearchSpecs/HCF368'/('hcf368-'+name+'-compare.json'))
        spec.update(id='hcf369-'+name+'-spatial', task='HCF369',
            hypothesis='Test whether HCF pixel differences follow the observed focused control: '+name,
            decisionRule='Require repeatable differences near focus. Compare every unfocused control. Do not infer detection accuracy.',
            adapter=dict(type='python-callable', steps=['hcf_spatial369.run'], outputAttributes=['hcf_spatial369.OUT']),
            inputs=[pin(q.ROOT/'scripts'/filename) for filename in ('hcf_spatial_audit.py', 'hcf_spatial369.py')])
        path = folder/(spec['id']+'.json')
        q.save(path, spec)
        q.submit(path)
        additions.append(dict(id=spec['id'], sha256=q.text_digest(spec)))
    q.save(folder/'additions.json', additions)


if __name__ == '__main__':
    register()
