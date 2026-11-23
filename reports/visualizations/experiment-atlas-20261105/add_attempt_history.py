"""Keep retry history visible without replacing each job with multiple experiment nodes."""
from pathlib import Path
import json,sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];sys.path.insert(0,str(ROOT/'scripts'))
import research_queue as q
x=json.loads((HERE/'data.json').read_text());count=0
for n in x['jobs']:
 history=[]
 for folder in q.attempts_of(q.QUEUE/'jobs'/n['id']):
  attempt=q.load(folder/'attempt.json')if(folder/'attempt.json').is_file()else{}
  result=q.load(folder/'result.json')if(folder/'result.json').is_file()else{}
  history.append(dict(attempt=folder.name,status=result.get('status','in progress'),start=attempt.get('startedAt'),seconds=result.get('wallSeconds'),reason=result.get('reason')))
 n['history']=history;n['last']=n.get('start');n['start']=min((r['start']for r in history if r['start']),default=None);count+=len(history)
for e in x['experiments']:
 own=[x['jobs'][j]for j in e['owned']];e['start']=min((n['start']for n in own if n['start']),default=None);e['last']=max((n['last']for n in own if n['last']),default=None)
x['latestExecution']=max(n.get('last')or n.get('start')or 0 for n in x['jobs'])
x['limitations'].append('Job nodes retain every attempt. Timeline uses first execution; recent scopes use latest execution. Duration uses the latest attempt, not full historical occupancy.')
(HERE/'data.json').write_text(json.dumps(x,separators=(',',':'),ensure_ascii=False))
m=json.loads((HERE/'manifest.json').read_text());m['sourceCounts']['attempts']=count;(HERE/'manifest.json').write_text(json.dumps(m,indent=2)+'\n');print('Preserved attempt records:',count)
