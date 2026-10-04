"""Non-executable exact membership proposal; never grants training admission."""
import argparse
from collections import Counter
import human_annotation_review as h
import focus_direct_transition as d
from evaluate_retained_negatives64 import connected_components,validate_negative
from focus_corrected_transition_audit import validate_case
from synth05_intake import verify_package


def validate_proposal(doc):
    h.require(doc['version']=='focus-negative-role-proposal-v1' and doc['approved'] is False and
        doc['executionEligible'] is False and doc['reviewer'] is None,'proposal_not_approval')
    rows=doc['members'];h.require(len(rows)==8 and len({r['id'] for r in rows})==8,'proposal_membership')
    h.require(all(r['sourceRole']=='calibration' and r['requestedRole']=='train' and
        r['changed'] is False and r['group']=='fixture-procedural-renderer-v1' for r in rows),'proposal_roles')
    h.require(Counter(r['condition'] for r in rows)==dict(boundary_unchanged=4,content_only=4),'proposal_conditions')
    return doc


def verified_records(source):
    """Rebuild labels from native evidence, never from evaluation predictions."""
    doc=h.sealed(source,'retained-negative-evaluation-v1')
    h.require(doc['expected']==doc['accepted']==8 and not doc['blocked'],'negative_source_incomplete')
    root=h.checked(h.ROOT,doc['manifest']).parent
    manifest=verify_package(root/'file-manifest.json');campaign=h.read(root/'campaign-manifest.json')
    rows=[]
    for row in doc['records']:
        matches=[c for c in campaign['cases'] if c['case_id']==row['id']];h.require(len(matches)==1,'proposal_case')
        raw,b,a=validate_case(root,h.checked(h.ROOT,row['evidence'][0]),matches[0]);validate_negative(raw,b,a)
        for ref in row['images']+row['evidence']:h.checked(h.ROOT,ref)
        h.require(row['condition']==raw['specification']['condition'] and row['changed'] is False and
            [b['image'],a['image']]==row['images'],'proposal_source_binding')
        rebuilt=d.record(row['id'],'fixture-procedural-renderer-v1','calibration',b,a,False,
            [h.ref(h.checked(h.ROOT,row['evidence'][0])),h.ref(root/'campaign-manifest.json')],None)
        h.require(all(row.get(k)==v for k,v in rebuilt.items()) and row['recipe']==matches[0]['recipe'],
            'proposal_annotation_or_lineage_changed')
        rows.append(dict(rebuilt,condition=row['condition'],recipe=row['recipe']))
    h.require(verify_package(root/'file-manifest.json')==manifest,'proposal_source_changed')
    return rows


def run(source_path,output):
    source=h.local(source_path);out=h.fresh(output)
    rows=[dict(row,requestedRole='train') for row in verified_records(source)]
    proposal=validate_proposal(dict(version='focus-negative-role-proposal-v1',approved=False,reviewer=None,
        executionEligible=False,source=h.ref(source),members=rows,memberSHA256=h.digest(rows),
        decodedPixelComponents=connected_components(rows),
        recipeThemeCounts=dict(Counter(r['recipe']['theme'] for r in rows)),
        proposedCombinedCounts=dict(train=32,development=5,independentEvaluation=0),
        pendingDecision='Maintainer approval of these exact8calibration pairs for training; no candidate launch granted here.',
        exclusions=['Whole Fixture renderer ancestry remains connected to prior training.',
            'Previously scored pairs and their related variants cannot become independent final evaluation.',
            'Four connected groups, not eight independent journeys. All recipe themes are dark; palette variants are not native light-theme coverage.',
            'No positive no-scroll focus switches; content mutations remain distinct from navigation.'],
        futureExperiment='Define one controlled32pair comparison only after data-role approval; no automated admission or launch.'))
    out.parent.mkdir(parents=True,exist_ok=True);h.write(out,proposal,sealed=True)
    print(proposal['memberSHA256'],proposal['recipeThemeCounts']);return proposal


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',required=True);p.add_argument('--output',required=True)
    a=p.parse_args();run(a.source,a.output)
