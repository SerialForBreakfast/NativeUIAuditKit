"""Inventory retained observation fields without changing labels, roles or admission."""
import argparse
from collections import Counter
import json
import math
import focus_direct_transition as d


def offsets(scene):
    inventory=scene.get('semantic_inventory',{})
    result={}
    for element in inventory.get('elements',[]):
        container=element.get('scroll_container_id');value=element.get('scroll_offset_points')
        if container is None or value is None:continue
        if not (isinstance(container,str) and isinstance(value,list) and len(value)==2
                and all(type(v) in (int,float) and math.isfinite(v) for v in value)):
            return None
        if container in result and result[container]!=value:return None
        result[container]=value
    return result or None


def observed_scroll(raw):
    """Only stable native offset observations; absence is unknown, never false."""
    endpoints={v.get('role'):v for v in raw.get('endpoints',[])}
    values=[]
    for role in ('before','after'):
        bracket=endpoints.get(role,{}).get('capture_endpoint',{})
        a,b=(offsets(bracket.get(k,{})) for k in ('before_scene','after_scene'))
        if a is None or a!=b:return None,'missing_or_unstable_offset_observation'
        values.append(a)
    if set(values[0])!=set(values[1]):return None,'scroll_container_membership_changed'
    return values[0]!=values[1],'native_semantic_inventory_offsets'


def run(protocol_path,output):
    out=d.h.fresh(output);protocol=d.h.read(d.h.local(protocol_path))
    corpus=d.collect(protocol['sources'])
    d.h.require(corpus['corpusSHA256']==protocol['corpusSHA256'],'corpus_changed')
    rows=d.admitted(corpus,d.h.read(d.h.checked(d.h.ROOT,protocol['admission'])))
    reference=d.h.read(d.h.checked(d.h.ROOT,protocol['sources']['reference']))
    native={p['id']:p for p in reference['pairs']}
    settings=d.h.read(d.h.checked(d.h.ROOT,protocol['sources']['settings']))
    comparison=d.h.read(d.h.checked(d.h.ROOT,settings['baseline']))
    sem=d.h.read(d.h.checked(d.h.ROOT,comparison['semantics']))
    events_path=d.h.checked(d.h.ROOT,sem['inputs']['events'])
    actions={}
    with events_path.open() as stream:
        for line in stream:
            event=json.loads(line).get('action',{}).get('_0',{})
            if event.get('actionID'):
                d.h.require(event['actionID'] not in actions,'duplicate_action_event')
                actions[event['actionID']]=event
    details=[];counts=Counter()
    for row in rows:
        ident=row['id'].split(':',1)[1]
        if row['group']=='fixture-procedural-renderer-v1':
            source=native[ident]['inputs'][2];raw=d.h.read(d.h.checked(d.h.ROOT,source))
            scroll,reason=observed_scroll(raw)
            action=raw.get('action_receipt',{})
            mutation=raw.get('mutation_receipt',{})
            entry=dict(id=row['id'],partition=row['split'],journeyGroup=row['group'],
                focusChanged=row['changed'],scrolled=scroll,scrollEvidence=reason,source=source,
                observationPointers=['/endpoints/0/capture_endpoint','/endpoints/1/capture_endpoint'],
                actionPointer='/action_receipt' if action else None,actionState=action.get('state'),
                mutationPointer='/mutation_receipt' if mutation else None,mutationState=mutation.get('state'),
                actionEffectStatus=action.get('effectStatus'),cleanupPointer='/cleanup',
                cleanupVerified=raw.get('cleanup')=='verified',
                missing=[] if scroll is not None else [reason])
            if not action and not mutation:entry['missing'].append('action_or_mutation_receipt')
        else:
            event=actions.get(ident)
            entry=dict(id=row['id'],partition=row['split'],journeyGroup=row['group'],
                focusChanged=row['changed'],scrolled=None,scrollEvidence='no_explicit_native_offset_binding',
                source=comparison['semantics'],actionSource=sem['inputs']['events'],
                actionID=ident,actionState=event.get('outcome') if event else None,
                cleanupVerified=None,missing=['observed_scroll_state','source_bound_cleanup_receipt'],
                observationSources={k:v for k,v in sem['inputs'].items() if k!='events'})
            if event is None:entry['missing'].append('action_event')
        counts[(row['split'],str(entry['scrolled']),row['changed'])]+=1;details.append(entry)
    report=dict(version='transition-source-inventory-v1',sources=protocol['sources'],
        corpusSHA256=corpus['corpusSHA256'],records=details,
        coverage=[dict(partition=k[0],scrolled=k[1],focusChanged=k[2],pairs=v) for k,v in sorted(counts.items())],
        trainingEligible=False,rolesChanged=False,
        limitations=['Existing admission unchanged; inventory is not a new source adapter or data approval.',
            'Delivered/completed actions do not prove effects; observed focus labels remain separate.',
            'Missing native scrolling is unknown; bounding-box displacement is not substituted.',
            'Embedded evidence pointers are not fabricated standalone receipt files.'],
        implementation=d.h.ref(d.h.ROOT/'scripts/inventory_transition_sources.py'))
    d.h.write(out,report,sealed=True);print(report['coverage'])


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--protocol',required=True);p.add_argument('--output',required=True)
    a=p.parse_args();run(a.protocol,a.output)
