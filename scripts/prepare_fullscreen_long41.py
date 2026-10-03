"""Record the explicit time-limit amendment and fixed FSF002 comparison."""
import human_annotation_review as h

def main():
    base=h.ROOT/'reports/work/FULLSCREEN-EXPERIMENT-41'
    authority=dict(version='local-training-time-override-v1',approved=True,wallTimeLimit=None,
        approvedBy='Maintainer: You are no longer bound by time constraints until further notice continue training',
        scope='Approved local model experiments; output and data boundaries unchanged.')
    h.write(base/'time-authority.json',authority)
    doc=h.read(base/'run.json');doc['epochs']=10;doc['budget']['seconds']=None
    doc['timeLimitOverride']=h.ref(base/'time-authority.json')
    h.write(base/'run-long.json',doc)
    print('FSF002 configured:10epochs, same initializer/data, no time limit,2GiB output cap.')

if __name__=='__main__':main()
