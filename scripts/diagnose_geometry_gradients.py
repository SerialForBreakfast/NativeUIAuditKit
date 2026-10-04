"""Retrospective coordinate-gradient analysis; no optimization or data-role changes."""
import argparse
import focus_direct_transition as d
import focus_spatial_transition as s


def run(result_path,output):
    out=d.h.fresh(output);result=d.h.read(d.h.local(result_path))
    protocol=d.h.read(d.h.checked(d.h.ROOT,result['protocol']))
    corpus=d.collect(protocol['sources'])
    d.h.require(corpus['corpusSHA256']==protocol['corpusSHA256'],'corpus_changed')
    rows=d.admitted(corpus,d.h.read(d.h.checked(d.h.ROOT,protocol['admission'])))
    selected={r['id']:r for r in rows if r['id'] in result['trainingIDs']}
    expected=d.training_rows([r for r in rows if r['split']=='train'],protocol['configuration'])
    d.h.require(len(selected)==len(result['trainingIDs']) and
        [r['id'] for r in expected]==result['trainingIDs'],'diagnostic_membership')
    t=d.torch_runtime();t.set_num_threads(2)
    state=t.load(d.h.checked(d.h.ROOT,result['model']),map_location='cpu',weights_only=True)
    d.h.require(state['configuration']==protocol['configuration'] and state['version']==d.VERSION,'checkpoint_contract')
    net=d.model(state['configuration']);net.load_state_dict(state['state']);net.eval()
    details=[]
    for ident in result['trainingIDs']:
        row=selected[ident];truth=t.tensor([[v for b in row['boxes'] for v in d.target_box(b,row['size'])]])
        indices,targets=s.targets(t,truth)
        with t.no_grad():
            _,fields,_=net.fields(t.from_numpy(d.encode(*(d.pixels(v) for v in row['images']))).unsqueeze(0))
        logits=fields.flatten(3).gather(3,indices[:,:,None,None].expand(-1,-1,4,1)).squeeze(3).detach().requires_grad_(True)
        objectives={'sigmoidL1':s.geometry_loss(t,logits,targets),
                    'bceLogits':s.geometry_loss(t,logits,targets,True),
                    'logitSmoothL1':s.geometry_loss(t,logits,targets,logit_regression=True),
                    'giou':s.giou_loss(t,s.decode_geometry(t,indices,logits.sigmoid(),16,24),truth)}
        details.append(dict(id=ident,target=targets.tolist(),logits=logits.detach().tolist(),
            predicted=logits.detach().sigmoid().tolist(),
            gradients={name:t.autograd.grad(value,logits,retain_graph=True)[0].tolist() for name,value in objectives.items()}))
    out.parent.mkdir(parents=True,exist_ok=True)
    d.h.write(out,dict(version='geometry-gradient-diagnostic-v1',source=d.h.ref(d.h.local(result_path)),
        model=result['model'],coordinateOrder=['cellOffsetX','cellOffsetY','width','height'],details=details,
        implementation=d.h.ref(d.h.ROOT/'scripts/diagnose_geometry_gradients.py'),pins=d.pins(),
        trainingEligible=False,modelGatePassed=False,
        limitation='Current analysis of frozen checkpoint logits at scoring-only true cells; gradients are derivatives of each mean objective, not actual optimizer steps.'),sealed=True)
    print('analyzed fitted pairs',len(details))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--result',required=True);p.add_argument('--output',required=True)
    a=p.parse_args();run(a.result,a.output)
