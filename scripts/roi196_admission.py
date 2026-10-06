"""Explicit expanded-membership receipt; legacy193 prose is not its data contract."""
import collections
import roi196 as r
h,p,e=r.h,r.p,r.e


def run():
    destination=r.OUT/'admission.json';h.require(not destination.exists(),'output_collision')
    proposal=p.sealed(r.OUT/'proposal.json');old=p.sealed(r.r.OUT/'proposal.json')
    request=e.load_request(h.checked(h.ROOT,proposal['membership']),41)
    lineage=proposal['rows']+proposal['duplicateAliases']
    original={v['parent'] for v in old['rows']+old['duplicateAliases']}
    additional={v['id'] for v in proposal['ancestry']}
    h.require(not original&additional and {v['parent'] for v in lineage}==original|additional,'parent_accounting')
    h.require(len(request.images)==len(proposal['rows'])==1173 and len(original)==216 and len(additional)==96,'membership_count')
    h.require(len({v['id'] for v in lineage})==len(lineage),'duplicate_identifier')
    canonical={v['id'] for v in proposal['rows']}
    h.require(all(v['canonical'] in canonical for v in proposal['duplicateAliases']),'dangling_alias')
    h.write(destination,dict(proposal=h.ref(r.OUT/'proposal.json'),membership=proposal['membership'],
        cropCount=len(request.images),originalSources=len(original),additionalSources=len(additional),
        distinctSourceGroups=len({v['group'] for v in lineage}),duplicateAliases=len(proposal['duplicateAliases']),
        additionalFamilyCounts=dict(collections.Counter(v['family'] for v in proposal['ancestry'])),
        eligibleRole='training-only crops derived from312existing admitted sources; no evaluation role changes',
        clarification='The inherited193 trainAdmission prose refers only to the original216source prefix. This source-bound receipt describes the full expanded membership; frozen launch inputs are preserved.',
        source=h.ref(__file__),productionEligible=False),sealed=True)
    print('Expanded admission receipt verified',flush=True)


if __name__=='__main__':run()
