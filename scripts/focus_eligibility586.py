"""Validate the declared focus request before the retained eligibility audit."""
import research_queue as q
from template_inputs398 import checked
import campaign_audits586 as audits

OUT=None


def run():
    spec=q.load(OUT.parents[2]/'spec.json')
    first=spec['evidence']['reads'][0]
    ref=next((r for r in spec['inputs'] if r['path']==first),None)
    q.require(ref is not None,'focus_eligibility_request_pin')
    request=q.load(checked(ref))
    q.require(set(request)=={'version','sources','modelAccepted'} and
              request['version']=='focus-eligibility-preparation586-v1' and
              request['modelAccepted'] is False and request['sources']==spec['focusSources'],
              'focus_eligibility_request_contract')
    # Preserve the submitted runtime and pending iOS jobs. Only this successor adds the missing request read.
    prior=audits.OUT
    try:
        audits.OUT=OUT
        audits.focus()
    finally:audits.OUT=prior
