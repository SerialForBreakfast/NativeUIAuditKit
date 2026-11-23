"""Export a read-only research snapshot. Never dispatch jobs or accept model claims."""
from pathlib import Path
import sys,json,time,re,gzip,base64,hashlib
from collections import Counter,defaultdict
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'scripts'))
import research_queue as q
from research_dashboard_states import annotate
import experiment_backlog as backlog
OUT=Path(__file__).resolve().parent

def stream(text):
 t=text.lower()
 if re.search(r'\bios|ios\d|iphone|ipad|row545',t):return 'iOS detection'
 if any(x in t for x in ['hcf','high contrast']):return 'Optional HCF'
 if any(x in t for x in ['temporal','transition','dtm','before-after','paired-image','departure','arrival','moving-background']):return 'Temporal focus'
 if any(x in t for x in ['native572','sdk572','fixture','capture','acquisition','native scene','native-focus','sdk','generation']):return 'Data and SDK'
 if any(x in t for x in ['focus','ring','crop','fdr','retention']):return 'Standard focus'
 if any(x in t for x in ['detector','tvos','roles','pills','cells','classification','localization','geometry']):return 'tvOS detection'
 return 'Workflow and evidence'

def text(value,limit=360):
 value=re.sub(r'\s+',' ',str(value or '')).strip()
 return value[:limit]+('…' if len(value)>limit else '')

def fact(doc):
 # Read only explicit decisions. Completion and a high score are not a scientific outcome.
 if not isinstance(doc,dict):return ''
 o=doc.get('outcome')
 return o if o in ('supported','contradicted','inconclusive') else ''

if __name__=='__main__':
 assert Path('/Volumes/training-drive').is_mount()
 started=time.time();value=annotate(q.summarize(write=False),q.QUEUE,q.MODULES)
 catalog=q.load(ROOT/'Research/Experiments/backlog405.json');backlog.validate(catalog)
 taskstates=backlog.task_states((ROOT/'Tasks.md').read_text())
 specs={};nodes=[];byjob={};issues=[]
 for row in value['jobs']:
  ident=row['job'];job=q.QUEUE/'jobs'/ident;spec=q.load(job/'spec.json');specs[ident]=spec
  attempts=q.attempts_of(job);last=attempts[-1] if attempts else None
  result=q.load(last/'result.json')if last and (last/'result.json').exists()else {}
  outcome='';evidence=[];reason='';facts={}
  if result.get('status')=='complete':
   outputmap={o['path']:o for o in result.get('outputs',[])}
   # A verified digest binds the displayed decision to its terminal receipt, not its scientific correctness.
   for name in ('decision.json','replay-boost-condition.json','benchmark_summary.json','report.json','gate.json'):
    p=last/'out'/name;pin=outputmap.get(name)
    if not pin or not p.is_file() or p.stat().st_size>1000000:continue
    if p.stat().st_size!=pin.get('bytes',p.stat().st_size)or q.digest(p)!=pin['sha256']:
     issues.append('Decision receipt mismatch: '+ident+'/'+name);continue
    try:d=q.load(p)
    except (ValueError,OSError):continue
    o=fact(d)
    if o and not outcome:outcome=o;reason=text(d.get('reason'));evidence.append(q.relative(p))
    if name=='benchmark_summary.json':
     for k in ('counts','focusStates','capturesDispatched','profileObserved','trainingAdmitted','independentApplications'):
      v=d.get(k)
      if isinstance(v,(str,bool,int,float,dict)) and len(json.dumps(v))<800:facts[k]=v
     if facts and q.relative(p)not in evidence:evidence.append(q.relative(p))
  n=dict(id=ident,title=text(spec.get('question')or spec['hypothesis'],150),question=text(spec.get('question')or spec['hypothesis'],600),
   task=spec['task'],track=stream(' '.join([ident,spec['task'],str(spec.get('hypothesis',''))])),
   state=row.get('displayState',row['state']),outcome=outcome or 'not-assessed',reason=reason,
   kind=spec.get('jobKind',spec['kind']),authority=spec['authority'],attempts=len(attempts),
   start=row.get('startedAt'),seconds=row.get('wallSeconds'),metrics='provisional',
   blockers=[text(r,320)for r in row.get('readinessReasons',row.get('requirements',[]))][:4],
   decision=text(spec['decisionRule'],500),next=spec.get('nextActionByOutcome',{}),
   conditions=[dict(job=c['job'],outcome=c['outcome'])for c in spec.get('conditions',[])],
   evidence=evidence,spec=q.relative(job/'spec.json'),facts=facts)
  if not evidence and last and (last/'result.json').exists():n['evidence']=[q.relative(last/'result.json')]
  if 'rc561' in ident.lower():
   n['warning']='Historical RC561 accuracy claims were invalidated. This job does not establish independent real-app accuracy.'
   n['outcome']='not-assessed'
  byjob[ident]=len(nodes);nodes.append(n)
 edges=[]
 for n in nodes:
  for d in specs[n['id']].get('dependencies',[]):
   if d['job']in byjob:edges.append([byjob[d['job']],byjob[n['id']],next((c['outcome']for c in n['conditions']if c['job']==d['job']), '')])
   else:issues.append('Missing dependency: '+d['job'])
 # Scientific catalog nodes keep their actual membership. Referenced controls can belong to more than one experiment.
 experiments=[];membership=defaultdict(list)
 for record in catalog['experiments']:
  ids=set(record.get('existingJobs',[]));plan=record.get('plan',{})
  for arm in plan.get('arms',[]):
   ids.add(arm.get('job',plan.get('jobPrefix','')+'-'+arm['id']))
  if plan.get('jobPrefix'):ids.update(k for k in byjob if k.startswith(plan['jobPrefix']+'-'))
  ids.update(k for k,s in specs.items()if s['task']==record['id'])
  members=sorted(byjob[k]for k in ids if k in byjob)
  state=taskstates.get(record['id'],{}).get('state','Archived record')
  if record['reconciliation']['disposition']=='answered':state='archived'
  e=dict(id=record['id'],title=record['title'],question=record['question'],track=stream(record['track']+' '+record['title']+' '+record['parentTask']),
    task=record['parentTask'],state=state,outcome='not-assessed',reason='',members=members,
    priority=record['priority'],decision=record['acceptance']['rule'],
    next=record['outcomes'],blockers=[r['missing']for r in record.get('requirements',[])][:3],evidence=record['sourceEvidence'][:3],
    recordType='Catalog experiment',dependencies=record['dependencies'])
  reuse=record['reconciliation'].get('reuse')
  if isinstance(reuse,str) and (ROOT/reuse).is_file():
   try:
    reused=q.load(ROOT/reuse);e['outcome']=fact(reused)or'not-assessed';e['reason']=text(reused.get('reason'))
   except(ValueError,OSError):pass
  for j in members:membership[j].append(len(experiments))
  experiments.append(e)
 # A reused control is membership, not ownership or evidence that a new arm executed.
 primary={}
 for j,n in enumerate(nodes):
  candidates=membership.get(j,[]);ranked=[]
  for i in candidates:
   r=catalog['experiments'][i];plan=r.get('plan',{});prefix=plan.get('jobPrefix','')
   score=100 if n['task']==r['id'] else 80 if prefix and n['id'].startswith(prefix+'-') else 60 if not plan and n['id'] in r.get('existingJobs',[]) else 0
   if score:ranked.append((score,i))
  if ranked:primary[j]=max(ranked)[1]
 remaining=defaultdict(list)
 for j,n in enumerate(nodes):
  if j not in primary:remaining[n['task']].append(j)
 for task,members in sorted(remaining.items()):
  first=nodes[members[0]];counts=Counter(nodes[j]['track']for j in members);track=counts.most_common(1)[0][0]
  e=dict(id=task,title=task,question=first['question'],track=track,task=task,state='derived',outcome='not-assessed',reason='',members=members,priority=None,
   decision=first['decision'],next=first['next'],blockers=[],evidence=first['evidence'],recordType='Unbound execution campaign',dependencies=[])
  ix=len(experiments);experiments.append(e)
  for j in members:primary[j]=ix;membership[j].append(ix)
 ee={};exids={e['id']:i for i,e in enumerate(experiments)}
 for i,e in enumerate(experiments):
  for d in e['dependencies']:
   if d in exids:ee[(exids[d],i)]='catalog'
 for a,b,c in edges:
  x,y=primary[a],primary[b]
  if x!=y:ee.setdefault((x,y),'condition'if c else'dependency')
 for i,e in enumerate(experiments):
  owned=[j for j in e['members']if primary.get(j)==i];e['owned']=owned
  membernodes=[nodes[j]for j in owned];states=Counter(n['state']for n in membernodes);outcomes=Counter(n['outcome']for n in membernodes if n['outcome']!='not-assessed')
  e['jobCounts']=dict(states);e['outcomes']=dict(outcomes);e['start']=min((n['start']for n in membernodes if n.get('start')),default=None)
  e['last']=max((n['start']for n in membernodes if n.get('start')),default=None);e['seconds']=round(sum(n.get('seconds')or 0 for n in membernodes),2) if any(n.get('seconds')is not None for n in membernodes) else None
  if membernodes:
   if states['running']:e['state']='running'
   elif states['ready']:e['state']='ready'
   elif len(membernodes)==states['complete']:e['state']='complete'
   elif any(states[x]for x in ['blocked','exhausted','failed','interrupted']):e['state']='blocked'
  if e['outcome']=='not-assessed'and outcomes:
   e['outcome']='mixed'if len(outcomes)>1 else next(iter(outcomes))
   e['reason']='Reported outcomes of owned jobs; not an approved experiment conclusion.'
 # Model-specific recent decisions are quoted from audited local evidence. They do not revise accepted metrics.
 notes={
 'B405-271':('contradicted','The matched tvOS initializer comparison loses 4 prior detections.'),
 'B405-272':('contradicted','Frozen features still lose 15 Run013 detections.'),
 'B405-273':('contradicted','Neither native focus fit recovers full-screen selections. The native fit loses 2 legacy successes.'),
 'B405-276':('contradicted','Geometry preservation: 3 gains / 2 losses against its matched control; 21 gains / 15 losses against Run013.'),
 'B405-277':('not-assessed','12 aligned review-only frames: 9 focused, 3 known no-focus; 3 related construction groups. No model comparison or data admission.'),
 'B405-278':('inconclusive','All 9 SDK observations authenticate, but actual focus is unknown in all 9.'),
 'B405-279':('not-assessed','IOS575 diagnoses 16 losses: 8 misses, 3 localization failures, 3 class/assignment failures, 2 baseline-assignment changes.'),
 'HCF574':('contradicted','The strict policy changes correct selections from 16 to 14 on 19 related Fixture frames. No new wrong picks; reject replacement.'),
 'IOS573':('contradicted','Foreground preservation loses 16 Run013 detections. Reject replacement.'),
 'ios573-foreground':('contradicted','Foreground preservation: 1 gain and 2 losses against its matched control. Reject replacement.'),
 'CORRECTION564':('contradicted','Proposal coverage reaches 17/21 development cases; correct focus selections remain 0/21.'),
 'SURGERY562':('contradicted','Weight-surgery arms retain narrow legacy decisions but recover 0/21 full-screen selections.')}
 for e in experiments:
  if e['id']in notes:e['outcome'],e['reason']=notes[e['id']];e['evidence']=list(dict.fromkeys(e['evidence']+['reports/work/UNBLOCK575/handoff.md','Research/NightlyReview20261104.md']))[:5]
  if 'rc561' in (e['id']+' '+e['title']).lower():
   e['warning']='Historical RC561 accuracy claims were invalidated. See MetricClaimsAudit571; these records do not establish independent accuracy.'
   e['evidence']=list(dict.fromkeys(['Research/MetricClaimsAudit571.md']+e['evidence']))[:5]
 latest=max(n.get('start')or 0 for n in nodes)
 snapshot=dict(version=1,generatedAt=datetime.now(timezone.utc).isoformat(),latestExecution=latest,project='Maximum-mini-NUIAK',
   catalogCount=len(catalog['experiments']),experimentCount=len(experiments),jobs=nodes,edges=edges,experiments=experiments,
   experimentEdges=[[a,b,t]for(a,b),t in ee.items()],membership={str(k):v for k,v in membership.items()},
   sources=['Tasks.md','Research/Experiments/backlog405.json','reports/work/research-queue/jobs/*/spec.json','reports/work/research-queue/jobs/*/attempts/*/result.json'],
   counts=dict(Counter(n['state']for n in nodes)),issues=list(dict.fromkeys(issues)),
   limitations=['Snapshot, not a live runner control.','Execution completion does not establish improvement.','Reported scientific outcomes remain provisional.','Inferred model-track tags are for navigation only.','No hand-drawn continuation edges: arrows come from recorded dependencies.','Reused controls remain in membership, but never establish new execution or ownership.','Grouped paths aggregate actual owned-job dependencies. Execution-job paths are exact.'])
 raw=json.dumps(snapshot,separators=(',',':'),ensure_ascii=False).encode();(OUT/'data.json').write_bytes(raw)
 encoded=base64.b64encode(gzip.compress(raw,mtime=0)).decode();(OUT/'payload.txt').write_text(encoded)
 manifest=dict(snapshotSHA256=hashlib.sha256(raw).hexdigest(),sourceCounts=dict(jobs=len(nodes),dependencies=len(edges),catalog=len(catalog['experiments']),unboundCampaigns=len(remaining)),
  compressedBytes=len(encoded),jsonBytes=len(raw),issues=snapshot['issues'],exportSeconds=round(time.time()-started,2),executionStarted=False)
 (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(manifest))
