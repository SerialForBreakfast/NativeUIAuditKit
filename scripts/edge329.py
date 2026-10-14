"""Add image-gradient channels while preserving original detail channels."""
import argparse
from pathlib import Path
import numpy as np
import contrast328 as previous
import boundary329 as audit

b=previous.b;r=previous.r;t=previous.t;f=previous.f
OUT=audit.OUT; VERSION='edge329-v1'


def gradient_channels(images):
    b.require(images.ndim==4 and images.shape[1:]==(6,128,192),'detail_shape')
    b.require(bool(t.isfinite(images).all()),'finite_detail')
    dx=t.nn.functional.pad((images[:,:,:,1:]-images[:,:,:,:-1]).abs(),(0,1,0,0))
    dy=t.nn.functional.pad((images[:,:,1:,:]-images[:,:,:-1,:]).abs(),(0,0,0,1))
    return (dx+dy)/2


class EdgeChange(r.RegionChange):
    def forward(self,images):
        b.require(images.shape[1] in (6,18),'region_channels')
        whole=images[:,:6]
        details=images[:,6:] if images.shape[1]==18 else r.encoded_details(whole,2)
        context=self.whole[:10](r.s.c.model.change_inputs(None,whole))
        features=[]
        for j in range(2):
            part=details[:,6*j:6*(j+1)]
            inputs=t.cat((r.s.c.model.change_inputs(None,part),gradient_channels(part)),1)
            features.append(self.detail(inputs))
        return self.whole[10](context)+self.correction(t.cat((context,t.stack(features).mean(0)),1))


def extend(net):
    old=net.change.detail[0]
    b.require(isinstance(old,t.nn.Conv2d) and old.in_channels==12 and old.groups==1,'detail_convolution')
    new=t.nn.Conv2d(18,old.out_channels,old.kernel_size,old.stride,old.padding,
        old.dilation,old.groups,old.bias is not None,old.padding_mode).to(old.weight)
    with t.no_grad():
        new.weight.zero_();new.weight[:,:12].copy_(old.weight)
        if old.bias is not None:new.bias.copy_(old.bias)
    net.change.detail[0]=new;net.change.__class__=EdgeChange
    return net


def image_model(pin):return extend(f.image_model(pin))


def load_candidate(path):
    saved=t.load(path,map_location='cpu',weights_only=True)
    b.require(saved.get('representation')==VERSION and saved.get('windows')==2,'checkpoint_version')
    net=extend(r.extend(r.s.c.model.extend(b.worker.make_model(t,paired_context=True)),2))
    net.load_state_dict(saved['state']);return net.eval()


def register():
    b.require(not (OUT/'inputs.json').exists(),'output_collision');t.set_num_threads(2)
    diagnostic=b.read(OUT/'audit.json');b.checked(b.read(b.checked(diagnostic['registration']))['runner'])
    decision=b.read(OUT/'decision.json');b.require(decision['candidateJustified'],'diagnostic_failed')
    parent=b.read(f.OUT/'inputs.json')
    net=image_model(parent['initializer']);control=f.image_model(parent['initializer'])
    t.manual_seed(42);x=t.rand(2,18,128,192)
    with t.inference_mode():error=float((net.change(x)-control.change(x)).abs().max())
    b.require(error<=1e-5,'initial_parity')
    b.write(OUT/'inputs.json',dict(parent,parent=b.ref(f.OUT/'inputs.json'),control=b.ref(f.OUT/'run/last.pt'),
        runner=b.ref(Path(__file__)),preparer=b.ref(Path(f.__file__)),reporter=b.ref(b.ROOT/'scripts/report_authored319.py'),
        reusableRunner=b.ref(Path(previous.__file__)),diagnostic=b.ref(OUT/'audit.json'),decision=b.ref(OUT/'decision.json'),
        representation=VERSION,probe=None,maximumInitialLogitError=error,
        hypothesis='Additional edge channels expose outline changes without removing raw appearance.',
        addedChannels='Six per-frame RGB gradient magnitudes. Fixed forward differences, averaged over x and y.',
        initializerEdgeWeights='Zero. Copy all existing weights without change.',
        normalization='None. Preserve raw channels and existing detail windows.'))


def run():
    reg=b.read(OUT/'inputs.json');b.checked(reg['reusableRunner']);b.checked(reg['decision'])
    previous.OUT=OUT;previous.VERSION=VERSION
    previous.image_model=image_model;previous.load_candidate=load_candidate
    previous.run()


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('mode',choices=['register','run'])
    globals()[parser.parse_args().mode]()
