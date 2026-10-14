"""Prepare the missing cells of a controlled HCF crop comparison. Do not submit."""
import copy
import research_queue as q


def prepare(owner):
    folder=q.ROOT/'Research/ResearchSpecs/HCF376'
    original=q.load(q.QUEUE/'jobs/hcf375c-70-crop-train/spec.json')
    evaluator=q.load(q.QUEUE/'jobs/hcf375c-80-crop-evaluate/spec.json')
    original_cfg=q.load(q.ROOT/original['stage'][0]['from']['path'])
    for name,profile,deduplicate in [('hcf-repeated','hcf',False),('balanced-repeated','balanced',False),('hcf-unique','hcf',True)]:
        spec=copy.deepcopy(original);ident='hcf376-'+name+'-train-v1'
        spec.update(id=ident,task='HCF376',owner=owner,
            hypothesis='Matched fixed-last crop training isolates profile coverage from duplicate weighting.',
            question='Does '+name+' explain the recovered Standard selections without losing HCF successes?',
            controlledComparison='Use seed 371, the same initialization and membership, 30 epochs, batch 16, and fixed-last selection across all 4 cells.',
            decisionRule='Compare all cells on unchanged development predictions. Preserve prior successes. Epoch matching is not update matching.')
        cfg=dict(original_cfg,profile=profile,deduplicate=deduplicate,seed=371)
        config_path=folder/(ident+'-config.json');q.require(not config_path.exists(),'immutable_config_exists');q.save(config_path,cfg)
        spec['stage']=[{'from':dict(path=q.relative(config_path),sha256=q.digest(config_path)),'to':'config.json'}]
        code=q.ROOT/'scripts/hcf_factor_train376.py'
        spec['inputs'].append(dict(path=q.relative(code),sha256=q.digest(code)))
        spec['adapter']=dict(type='python-callable',steps=['hcf_factor_train376.train'],outputAttributes=['hcf_factor_train376.OUT'])
        spec['training']['experimentLogRunId']='HCF376'
        spec['training']['acceptanceEvidence']='Matched 4-cell comparison on development frames; no model acceptance from training.'
        q.validate(spec);path=folder/(ident+'.json');q.require(not path.exists(),'immutable_spec_exists');q.save(path,spec)
        evaluation=copy.deepcopy(evaluator);evaluation.update(id='hcf376-'+name+'-evaluate-v1',task='HCF376',owner=owner)
        evaluation['dependencies'][0]=dict(job=ident,specSHA256=q.text_digest(spec),outputs=['model.json'])
        q.validate(evaluation);path=folder/(evaluation['id']+'.json');q.require(not path.exists(),'immutable_spec_exists');q.save(path,evaluation)
        print(ident,evaluation['id'])


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--owner',required=True)
    prepare(parser.parse_args().owner)
