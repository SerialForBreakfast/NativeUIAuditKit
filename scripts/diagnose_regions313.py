"""Separate frozen scores from added detail scores on retained tiny cases."""
import math
import numpy as np
import regions313 as r


def main():
    b=r.b;t=r.t;t.set_num_threads(2);out=r.OUT/'tiny-diagnosis.json'
    b.require((r.OUT/'completion.json').exists() and not out.exists(),'diagnostic_state')
    values,rows,pin=r.s.tiny_rows();reports={}
    for count in (1,2):
        net=r.load_candidate(r.OUT/f'regions-{count}/last.pt')
        detail,audit=r.prepare(values,rows,count);inputs=t.from_numpy(np.concatenate((values,detail),1))
        with t.inference_mode():
            whole=net.change.whole(r.s.c.model.change_inputs(None,inputs[:,:6])).flatten()
            total=net.change(inputs).flatten();correction=total-whole
        reports[str(count)]=[dict(index=i,condition=row['condition'],wholeLogit=float(whole[i]),
            correctionLogit=float(correction[i]),finalLogit=float(total[i]),
            correctionNeededForChanged=math.log(.85/.15)-float(whole[i]),
            windows=audit[i]['windows'],energyFraction=audit[i]['energyFraction']) for i,row in enumerate(rows)]
    b.write(out,dict(input=pin,models=reports,thresholds=[.15,.85],decisionChanged=False,
        limitation='Diagnostic logits only. No threshold or model changes.'))
    for name,rows in reports.items():
        print(name,[x for x in rows if x['condition']=='forward'])


if __name__=='__main__':main()
