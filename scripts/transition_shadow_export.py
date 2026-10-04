"""Explicit DTM025 change-only extension to the existing Core ML exporter."""
import json
import hashlib
import os
from pathlib import Path

CHECKPOINT='28f10dc5ac2c6a0fb324cabeb778b2acad2539c97f7f9cc48a20c8ff534a9409'
MODEL_ID='focus-transition-experimental-dtm025-change-v1'
ENCODING='paired-rgb-letterbox192x128-pillow-bilinear-v1'
RESIDUAL_CHECKPOINT='cc55f4e9e06605f00e511de01b09ea56707971aa753b20ac940438a50c841f43'
RESIDUAL_MODEL_ID='focus-transition-experimental-dtm030-change-v1'


def residual_wrapper(state):
    import torch
    import focus_direct_transition as d
    import focus_identity_residual as r
    import adapt_reflow117 as a
    if state['version']!=r.VERSION or state['configuration']!=a.CONFIG:
        raise ValueError('residual_configuration_mismatch')
    trained=r.model(d.model(d.PAIRED_TEMPORAL_CONFIG))
    trained.load_state_dict(state['state'],strict=True)
    class ResidualOnly(torch.nn.Module):
        def __init__(self):
            super().__init__();self.encoder=trained.encoder;self.readout=trained.base_readout;self.correction=trained.change.linear
        def forward(self,pair):
            a,b=pair[:,:3],pair[:,3:]
            phi=self.encoder(torch.cat(((b-a).abs(),a,b),dim=1))
            aa=self.encoder(torch.cat((torch.zeros_like(a),a,a),dim=1))
            bb=self.encoder(torch.cat((torch.zeros_like(b),b,b),dim=1))
            return (self.readout(phi)+self.correction(phi-(aa+bb)/2)).sigmoid().reshape(1)
    return ResidualOnly().eval()


def export(args,weights,weights_hash,out):
    if weights_hash not in (CHECKPOINT,RESIDUAL_CHECKPOINT):raise ValueError('transition_checkpoint_mismatch')
    if args.precision!='fp32' or args.trace_receipt or args.pixel_contract:
        raise ValueError('transition_requires_fp32_own_contract')
    import torch
    import coremltools as ct
    import numpy as np
    from export_focus_ring_coreml import package_size_report
    import focus_direct_transition as d
    import focus_change_adaptation as change
    torch.set_num_threads(2)
    state=torch.load(weights,map_location='cpu',weights_only=True)
    if weights_hash==CHECKPOINT and (state['configuration']!=d.PAIRED_TEMPORAL_CONFIG or state['adaptation']!=change.COLLECTION_CONFIG):
        raise ValueError('transition_configuration_mismatch')
    if weights_hash==CHECKPOINT:
        trained=d.model(state['configuration']);trained.load_state_dict(state['state'],strict=True);trained.eval()

    class ChangeOnly(torch.nn.Module):
        def __init__(self):
            super().__init__();self.change=trained.change
        def forward(self,pair):
            features=torch.cat(((pair[:,3:]-pair[:,:3]).abs(),pair),dim=1)
            return self.change(features).sigmoid().reshape(1)

    wrapper=ChangeOnly().eval() if weights_hash==CHECKPOINT else residual_wrapper(state)
    traced=torch.jit.trace(wrapper,torch.zeros(1,6,128,192)).eval()
    example=torch.rand(1,6,128,192)
    with torch.inference_mode():
        if not torch.equal(wrapper(example),traced(example)):raise ValueError('transition_trace_parity')
    out.mkdir(parents=True,exist_ok=False)
    traced.save(str(out/'change-trace.pt'))
    print('stage=convert-transition',flush=True)
    model=ct.convert(traced,inputs=[ct.TensorType(name='pair',shape=(1,6,128,192),dtype=np.float32)],
        outputs=[ct.TensorType(name='focus_change_probability',dtype=np.float32)],
        convert_to='mlprogram',compute_precision=ct.precision.FLOAT32,
        minimum_deployment_target=ct.target.macOS15,compute_units=ct.ComputeUnit.CPU_ONLY)
    metadata=dict(modelID=MODEL_ID if weights_hash==CHECKPOINT else RESIDUAL_MODEL_ID,task='focus-change-only',checkpointSHA256=weights_hash,
        inputEncoding=ENCODING,releaseEligible='false',backend='cpuOnly',
        changedThreshold='0.85',unchangedThreshold='0.15',schemaVersion='1')
    for k,v in metadata.items():model.user_defined_metadata[k]=v
    model.short_description='Experimental paired-frame focus change; no localization or action authority'
    model.author='NativeUIAuditKit'
    model.save(str(out/'FocusTransitionChange.mlpackage'))
    report=dict(version='transition-change-export-v1',metadata=metadata,
        checkpointSHA256=weights_hash,torchVersion=torch.__version__,coremltoolsVersion=ct.__version__,
        precision='float32',inputShape=[1,6,128,192],outputShape=[1],releaseEligible=False,
        **package_size_report(out/'FocusTransitionChange.mlpackage'))
    if hashlib.sha256(weights.read_bytes()).hexdigest()!=weights_hash:raise ValueError('checkpoint_changed')
    (out/'export.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report,flush=True)
    return 0 if report['size_gate_pass'] else 1
