"""Summarize fixed effect comparisons without selecting another model."""
import numpy as np
import effect326 as e


def main():
    b=e.b;t=e.t;t.set_num_threads(2);reg=b.read(e.OUT/'inputs.json');corpus=b.read(b.checked(reg['corpus']))
    validation=b.read(e.OUT/'validation.json');result={}
    for arm in e.ARMS:
        data=np.load(b.checked(reg['cache'][arm]),allow_pickle=False);rows=corpus['rows'][arm]
        done=b.read(e.OUT/arm/'run/completion.json');net=e.p.load(b.checked(done['model']))
        initial=e.p.load(b.checked(reg['initializer']));scores={}
        for name,model in [('initial',initial),('candidate',net)]:
            with t.inference_mode():prob=model.change(t.from_numpy(data['auxiliary'][240:])).sigmoid().flatten().numpy()
            groups={}
            for size in (3,6):
                for width in (1,3):
                    for contrast in (.25,.75):
                        for condition in ('movement','artwork-only','identical'):
                            ids=[i for i,row in enumerate(rows) if (row['sizePixels'],row['widthPixels'],row['contrast'],row['condition'])==(size,width,contrast,condition)]
                            groups[str((size,width,contrast,condition))]=b.trainer.w.summary(prob[ids],data['auxiliaryLabels'][240:][ids])
            scores[name]=dict(summary=b.trainer.w.summary(prob,data['auxiliaryLabels'][240:]),cells=groups)
        effects={}
        for size in (3,6):
            for width in (1,3):
                for contrast in (.25,.75):
                    values=[v['metrics'] for v in validation['reports'][arm]['effects'] if (v['size'],v['width'],v['contrast'])==(size,width,contrast)]
                    effects[str((size,width,contrast))]={k:np.quantile([v[k] for v in values],[0,.5,1]).tolist() for k in ('areaAbove1','areaAbove8','maximum','windowEnergyFraction')}
        result[arm]=dict(training=scores,effects=effects,completion=done)
    b.write(e.OUT/'comparison.json',dict(inputs=b.ref(e.OUT/'inputs.json'),arms=result,
        limitation='Training cells share 3 artwork families. They are not independent deployment trials.',productionEligible=False))
    print({k:v['training'] for k,v in result.items()})


if __name__=='__main__':main()
