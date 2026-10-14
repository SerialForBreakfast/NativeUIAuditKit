"""Record prepared successor investigations without changing earlier inventory evidence."""
import research_queue as q


def run():
    folder=q.ROOT/'Research/ResearchSpecs/HCF376'
    document=q.load(folder/'investigations.json')
    document['version']='hcf-investigations-v2'
    document['executionJobs']=11
    document['note']='Prepared specifications are not execution approvals. Five retained-data questions share one report.'
    mapping={'B1':'hcf376-proposal-recall-v1','C1':'hcf376-wrong-selections-v1',
             'C3':'hcf376-boundary-support-v1', 'D1':'hcf376-balanced-repeated-train-v1',
             'D2':'hcf376-hcf-unique-train-v1','D3':'hcf376-factor-comparison-v1'}
    for row in document['rows']:
        if row['id'] in mapping:
            row['state']='prepared';row['requirement']=mapping[row['id']]
        if row['id']=='B1':
            row['qualification']='Existing fixed outline proposals only. Earlier YOLO output does not retain all candidate boxes.'
        if row['id']=='C3':
            row['qualification']='Measures body-edge mask support. True outline closure remains blocked on outline labels.'
        if row['id'] in ('D1','D2','D3'):
            row['qualification']='Includes a new fixed-last HCF repeated control. Equal epochs do not imply equal updates or class weighting.'
    path=folder/'investigations-v2.json';q.require(not path.exists(),'immutable_inventory_exists');q.save(path,document)


if __name__=='__main__':run()
