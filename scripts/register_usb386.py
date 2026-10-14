"""Register explicit USB successors. Preserve old specifications and attempts."""
import copy
import research_queue as q


def register():
    folder=q.ROOT/'Research/ResearchSpecs/USB386-v2';folder.mkdir(parents=True,exist_ok=True)
    originals=['hcf375d-71-detector-train-v2','hcf375d-81-detector-evaluate-v2','hcf375d-90-decision-v2']
    for cell in ('hcf-repeated','balanced-repeated','hcf-unique'):
        originals += [f'hcf376-{cell}-train-v1',f'hcf376-{cell}-evaluate-v1']
    originals += ['hcf376-factor-comparison-v1']
    converted={}
    for old in originals:
        spec=copy.deepcopy(q.load(q.QUEUE/'jobs'/old/'spec.json'))
        spec['id']=old+'-usb2'
        for dep in spec.get('dependencies',[]):
            if dep['job'] in converted:
                new=converted[dep['job']];dep.update(job=new['id'],specSHA256=q.text_digest(new))
        if spec['authority']=='training':
            mode='detector' if 'detector' in old else 'crop'
            spec['adapter']=dict(type='python-callable',steps=['usb_training386.train'],outputAttributes=['usb_training386.OUT'])
            code=q.ROOT/'scripts/usb_training386.py'
            spec['inputs'].append(dict(path=q.relative(code),sha256=q.digest(code)))
            cfg=dict(mode=mode,job=spec['id'],totalBytes=2*1024**3,localBytes=100_000_000)
            path=folder/(spec['id']+'-usb.json');write_once(path,cfg)
            spec['stage'].append(dict(to='usb.json',**{'from':dict(path=q.relative(path),sha256=q.digest(path))}))
            if mode=='detector':
                stage=next(x for x in spec['stage'] if x['to']=='config.json')
                config=q.load(q.ROOT/stage['from']['path']);config['datasetFolder']='yolo-training-hcf386-usb'
                path=folder/(spec['id']+'-config.json');write_once(path,config)
                stage['from']=dict(path=q.relative(path),sha256=q.digest(path))
            spec['limits']['maxOutputBytes']=100_000_000
            spec['training']['storageBudgetBytes']=100_000_000
            spec['training']['acceptanceEvidence']+=' Keep at most 100 MB locally. Enforce the unchanged 2 GiB total across USB and local outputs.'
            spec['training']['experimentLogRunId']='USB386'
        if old=='hcf376-factor-comparison-v1':
            spec['adapter']=dict(type='python-callable',steps=['usb_training386.compare'],outputAttributes=['usb_training386.OUT'])
            code=q.ROOT/'scripts/usb_training386.py'
            spec['inputs'].append(dict(path=q.relative(code),sha256=q.digest(code)))
        converted[old]=spec
        path=folder/(spec['id']+'.json');write_once(path,spec)
        q.validate(spec);q.verify_pins(spec);q.submit(path)
        print(spec['id'])


def write_once(path,value):
    if path.exists():q.require(q.load(path)==value,'immutable_spec_changed')
    else:q.save(path,value)


if __name__=='__main__':register()
