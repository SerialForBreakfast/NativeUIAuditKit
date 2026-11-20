"""Validate the spatial request before the cached iOS loss audit."""
import research_queue as q
from template_inputs398 import checked
import campaign_audits586 as audits

OUT=None


def run():
    spec=q.load(OUT.parents[2]/'spec.json');first=spec['evidence']['reads'][0]
    ref=next((r for r in spec['inputs'] if r['path']==first),None)
    q.require(ref is not None,'ios_spatial_request_pin')
    request=q.load(checked(ref))
    q.require(request.get('version')=='spatial-loss-preparation586-v1' and request.get('dataRole')=='development' and
              request.get('confidence')==.5 and request.get('matchingIoU')==.5 and
              request.get('modelAccepted') is False and request.get('trainingOrInferenceRepeated') is False,
              'ios_spatial_request_contract')
    prior=audits.OUT
    try:
        audits.OUT=OUT
        audits.ios()
    finally:audits.OUT=prior
