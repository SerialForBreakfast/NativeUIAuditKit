"""Load only the selected capture contract. Keep unrelated authoring out of runtime pins.

Each module equals its adapter module. research_approval.code_pins starts from that
adapter and still includes its complete static source closure.
"""
import importlib

# Values are fixed source names, never caller-provided module paths.
MODULES = {
    'native_scene572.run': 'native_scene572',
    'sdk_profile538.run': 'sdk_profile538',
    'sdk_capture527.run': 'sdk_capture527',
    'ttr_campaign_queue493.run': 'ttr_campaign_queue493',
    'ttr_campaign_recovery493.run': 'ttr_campaign_recovery493',
}


def module_for(spec):
    steps = spec.get('adapter', {}).get('steps')
    if spec.get('authority') != 'capture' or not isinstance(steps, list) or len(steps) != 1:
        return None
    name = MODULES.get(steps[0])
    if name is not None and name != steps[0].split('.')[0]:
        raise ValueError('capture_contract_module_mismatch')
    return name


def selected(spec):
    name = module_for(spec)
    if name is None:
        raise ValueError('capture_contract_unknown')
    return importlib.import_module(name)
