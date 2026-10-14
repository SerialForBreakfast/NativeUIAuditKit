#!/usr/bin/env python3
"""Render a local research dashboard. Static exports cannot start jobs."""
import argparse
import html
import json
from pathlib import Path
import research_queue as queue
from research_dashboard_descriptions import describe_jobs

ROOT = queue.ROOT


def build_dashboard_data():
    return queue.summarize(write=False)


def render_html(data, token=''):
    payload = json.dumps(data, allow_nan=False).replace('<', '\\u003c').replace('&', '\\u0026')
    descriptions = json.dumps(describe_jobs(data), allow_nan=False).replace('<', '\\u003c').replace('&', '\\u0026')
    page = """<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>NUIAK research queue</title>
<style>
*{box-sizing:border-box}
body{background:#0d1117;color:#c9d1d9;font:12px/1.35 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,sans-serif;margin:8px;padding:0}
#top-bar{display:flex;justify-content:space-between;align-items:center;padding:2px 0 6px;border-bottom:1px solid #21262d;margin-bottom:6px}
#brand{display:flex;align-items:center;gap:6px}
h1{font-size:14px;font-weight:700;margin:0;color:#f0f6fc}
.badge{font-size:10px;font-weight:600;padding:1px 5px;border-radius:4px;letter-spacing:0.3px}
.badge-running{background:#0e333d;color:#5ce1dc;border:1px solid #165b6d}
.badge-ready{background:#0f3824;color:#55d790;border:1px solid #1c6843}
.badge-blocked{background:#382c0f;color:#ffc77e;border:1px solid #664f19}
.badge-idle{background:#21262d;color:#8b949e;border:1px solid #30363d}
.badge-failed{background:#3d1518;color:#ff9299;border:1px solid #6b232a}
.priority-badge{font-size:10px;font-weight:700;color:#55d790;background:#0d2319;padding:1px 4px;border-radius:3px}
.btn-toggle{font-size:12px;font-weight:700;padding:4px 14px;border-radius:5px;border:1px solid;cursor:pointer;transition:all .15s}
.btn-start{background:#12623b;border-color:#55d790;color:#fff}
.btn-start:hover{background:#187748}
.btn-stop{background:#852d34;border-color:#ff9299;color:#fff}
.btn-stop:hover{background:#a33740}
.btn-stopping{background:#6e4014;border-color:#ffaa44;color:#fff;cursor:not-allowed}
#stats-bar{display:flex;gap:4px;margin-bottom:6px;flex-wrap:wrap}
.chip{font-size:11px;padding:1px 6px;border-radius:8px;background:#161b22;border:1px solid #30363d;color:#8b949e}
.chip strong{color:#f0f6fc}
#active{border:1px solid #30363d;border-radius:6px;background:#161b22;padding:6px 8px;margin-bottom:8px}
#active:not(.idle){border-color:#5ce1dc;background:#0d222b;position:sticky;top:4px;z-index:10;box-shadow:0 4px 12px #0008}
.active-title-row{display:flex;align-items:center;gap:6px;margin-bottom:2px}
#active-title{font-size:12px;font-weight:600;color:#f0f6fc;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
#active-step{font-size:11px;color:#8b949e;margin-bottom:2px}
#active progress{width:100%;height:5px;border-radius:3px;overflow:hidden;margin-bottom:2px}
.active-meta{font-size:10px;color:#8b949e;display:flex;gap:6px}
.toolbar{display:flex;gap:4px;margin-bottom:6px}
input,select{font:inherit;padding:3px 6px;background:#161b22;color:#c9d1d9;border:1px solid #30363d;border-radius:4px}
#search{flex:1}
select{font-size:11px}
.section-header{display:flex;justify-content:space-between;align-items:center;font-size:11px;font-weight:600;color:#8b949e;padding:2px 0;margin-bottom:2px}
table{border-collapse:collapse;width:100%;margin-bottom:6px}
th{font-size:10px;text-transform:uppercase;color:#8b949e;padding:3px 4px;border-bottom:1px solid #21262d;text-align:left}
td{padding:4px;border-bottom:1px solid #21262d;vertical-align:top}
tr.running{background:#0d222b;border-left:3px solid #5ce1dc}
.job-item{display:flex;flex-direction:column;gap:1px}
.job-title-row{display:flex;align-items:center;gap:4px;flex-wrap:wrap}
.job-title{font-size:11px;font-weight:600;color:#f0f6fc}
.job-sub{display:flex;gap:4px;align-items:center}
.job-id{font-size:10px;color:#8b949e;font-family:monospace}
.job-hypo{font-size:10px;color:#8b949e;line-height:1.2;margin-top:1px}
.btn-sm{font-size:10px;padding:2px 6px;background:#21262d;color:#c9d1d9;border:1px solid #30363d;border-radius:4px;cursor:pointer}
.btn-sm:hover{background:#30363d}
.btn-danger{background:#3d1518;border-color:#6b232a;color:#ff9299}
details{border:1px solid #21262d;border-radius:4px;background:#161b22;padding:4px 6px;margin-bottom:4px}
summary{font-size:10px;font-weight:600;color:#8b949e;cursor:pointer}
summary:hover{color:#c9d1d9}
.small{font-size:10px}.muted{color:#8b949e}.warning{color:#ffc77e}.error-text{color:#ffaaa3}
#detail{white-space:pre-wrap;overflow:auto;max-height:50vh;font-size:10px}
dialog{background:#161b22;color:#c9d1d9;width:92%;max-width:550px;border:1px solid #30363d;border-radius:6px;padding:10px}
</style>
<header id="top-bar">
  <div id="brand"><h1 id="app-title">NUIAK Queue</h1><span id="run-mode" class="badge">Idle</span></div>
  <div id="top-actions"><button id="toggle-run" class="btn-toggle btn-start">Start</button></div>
</header>
<div id="stats-bar">
  <span class="chip" id="chip-running"><strong>0</strong> running</span>
  <span class="chip" id="chip-ready"><strong>0</strong> ready</span>
  <span class="chip" id="chip-blocked"><strong>0</strong> blocked</span>
  <span class="chip" id="chip-complete"><strong>0</strong> done</span>
</div>
<section id="active" aria-live="polite" aria-label="Current task">
  <div class="active-title-row"><span id="active-badge" class="badge badge-idle">IDLE</span> <span id="active-title">No task is running</span></div>
  <div id="active-step">The queue is idle.</div>
  <div id="active-progress"></div>
  <div class="active-meta"><span id="active-time"></span> <span id="active-eta"></span></div>
  <details id="active-more" style="margin-top:4px"><summary class="small muted">Task description & decision rule</summary>
    <p id="active-description" class="small"></p>
    <p id="active-answer" class="small"></p>
    <p id="active-decision" class="small"></p>
  </details>
  <div id="active-controls" style="margin-top:4px" hidden>
    <button id="active-stop" class="btn-sm">Stop after this task</button>
    <button id="active-cancel" class="btn-sm btn-danger">Cancel this task</button>
  </div>
</section>
<div class="toolbar">
  <input id="search" placeholder="Filter backlog..." aria-label="Search">
  <select id="filter" aria-label="State"><option value="">All</option><option>pending</option><option>blocked</option><option>running</option><option>failed</option><option>cancelled</option><option>interrupted</option></select>
  <select id="sort" aria-label="Sort"><option value="job">ID</option><option value="state">State</option><option value="wallSeconds">Time</option></select>
</div>
<div class="section-header"><span>Upcoming Backlog</span> <span id="backlog-count" class="small muted"></span></div>
<table><thead><tr><th style="width:24px">#</th><th>Experiment / Task</th><th style="width:70px;text-align:right">Status</th></tr></thead><tbody id="rows"></tbody></table>
<details id="completed"><summary id="completed-count">Completed test outcomes</summary>
  <p class="small muted">Completed jobs stay here. Completion does not mean model acceptance.</p>
  <table><thead><tr><th style="width:24px">#</th><th>Experiment / Outcome</th><th style="width:70px;text-align:right">Status</th></tr></thead><tbody id="completed-rows"></tbody></table>
</details>
<details id="batch-tools"><summary class="small muted">Batch selection & controls</summary>
  <div style="display:flex;gap:4px;flex-wrap:wrap;margin:4px 0">
    <button id="start" class="btn-sm">Start selected batch</button>
    <button id="approve-add" class="btn-sm">Add selected to approved queue</button>
    <button id="cancel" class="btn-sm">Cancel current job</button>
    <label class="small"><input type="checkbox" id="retry"> Explicit retry</label>
  </div>
  <p id="status" class="small muted"></p><p id="error" class="error-text" role="alert"></p>
  <span style="display:none"><button id="run-all">▶ Run all ready</button><button id="stop">■ Stop after task</button></span>
</details>
<details id="coverage-box"><summary class="small muted">Measured coverage report</summary>
  <p><select id="coverage-report" class="btn-sm"><option value="">No measured report</option></select></p>
  <div id="coverage" class="small muted">Coverage is unavailable without measured evidence.</div>
</details>
<details id="rules-box"><summary class="small muted">Rules & disclaimers</summary>
  <p class="warning small">Execution completion is not model acceptance. Placeholder scores are excluded.</p>
  <p id="mode" class="small muted"></p>
  <div id="summary" class="small muted"></div>
</details>
<dialog id="modal"><div style="display:flex;justify-content:space-between;align-items:center"><strong id="modal-title">Job Details</strong><button id="close" class="btn-sm">Close</button></div><section id="detail-description" style="margin-top:6px"></section><details style="margin-top:6px"><summary class="small">Technical details and registered decision rule</summary><pre id="detail"></pre></details></dialog>
<script>
const TOKEN=__TOKEN__;
let data=__DATA__;
const DESCRIPTIONS=__DESCRIPTIONS__;
let busy=Boolean(data.busy);
const selected=new Set();
const $=id=>document.getElementById(id);
function add(parent,tag,text){const e=document.createElement(tag);e.textContent=text;parent.append(e);return e;}
function description(row){return DESCRIPTIONS[row.job]||{
 title:row.question||row.hypothesis||row.job,
 test:row.hypothesis||'',
 answers:row.decisionRule||'',
 source:'job'};}
function explain(parent,row){
 const d=description(row);add(parent,'strong',d.title);
 const test=add(parent,'p','');add(test,'strong','What this tests: ');add(test,'span',d.test);
 const answer=add(parent,'p','');add(answer,'strong','What the result tells us: ');add(answer,'span',d.answers);
 if(d.source==='study')add(parent,'p','This job contributes to the study question. It does not answer the whole question alone.').className='small';
 if(row.state==='blocked')add(parent,'p','Blocked: this is a planned test, not a measured result.').className='warning';
}
function show(row){$('detail-description').replaceChildren();explain($('detail-description'),row);
 $('detail').textContent=JSON.stringify(row,null,2);$('modal').showModal();}
function render(){
 const jobs=data.jobs||[];
 let active=jobs.find(j=>j.job===data.current)||jobs.find(j=>j.state==='running');
 if(!active&&data.current){active={job:data.current,state:'running',hypothesis:'Executing task '+data.current};}
 const isRunning=busy||Boolean(data.current)||Boolean(active);
 const toggleBtn=$('toggle-run');
 if(data.stopping){toggleBtn.textContent='Stopping';toggleBtn.className='btn-toggle btn-stopping';toggleBtn.disabled=true;}
 else if(isRunning){toggleBtn.textContent='Stop';toggleBtn.className='btn-toggle btn-stop';toggleBtn.disabled=!TOKEN;}
 else{toggleBtn.textContent='Start';toggleBtn.className='btn-toggle btn-start';toggleBtn.disabled=!TOKEN;}
 $('run-mode').textContent=data.stopping?'Stopping':(isRunning?'Running':(data.continuous?'Auto':'Idle'));
 $('run-mode').className='badge '+(data.stopping?'badge-blocked':(isRunning?'badge-running':'badge-idle'));
 const countState=s=>jobs.filter(j=>j.state===s).length;
 $('chip-running').innerHTML='<strong>'+countState('running')+'</strong> running';
 const readyJobs=jobs.filter(j=>j.state==='pending'&&j.approved);
 const awaiting=jobs.filter(j=>j.state==='pending'&&!j.approved).length;
 $('chip-ready').innerHTML='<strong>'+readyJobs.length+'</strong> ready'+(awaiting?' · '+awaiting+' awaiting approval':'');
 $('chip-blocked').innerHTML='<strong>'+countState('blocked')+'</strong> blocked';
 $('chip-complete').innerHTML='<strong>'+countState('complete')+'</strong> done';
 $('active').className=(active||busy)?'':'idle';
 const badgeEl=$('active-badge');
 if(badgeEl){
  if(data.stopping){badgeEl.textContent='STOPPING';badgeEl.className='badge badge-blocked';}
  else if(active){badgeEl.textContent='RUNNING';badgeEl.className='badge badge-running';}
  else if(busy){badgeEl.textContent=data.waiting?'WAITING':'ACTIVE';badgeEl.className='badge '+(data.waiting?'badge-blocked':'badge-running');}
  else{badgeEl.textContent='IDLE';badgeEl.className='badge badge-idle';}
 }
 if(active){
  $('active-title').textContent=description(active).title+' · '+active.job;
  $('active-description').textContent='What this tests: '+description(active).test;
  $('active-answer').textContent='What the result tells us: '+description(active).answers;
  $('active-step').textContent=active.progress?.step||'Preparing the job; waiting for a worker event.';
  if(active.progress?.updatedAt)$('active-step').textContent+=' · '+new Date(active.progress.updatedAt*1000).toLocaleTimeString();
 }else if(busy){
  if(data.waiting){
   $('active-title').textContent=data.waiting;
   $('active-description').textContent='The runner is waiting for ready jobs or scheduler wakeup.';
   $('active-step').textContent='Waiting for ready jobs in approved queue.';
  }else{
   const nextReady=readyJobs[0];
   $('active-title').textContent=nextReady?'Runner active — next approved job':'Runner active — no approved job is ready';
   $('active-description').textContent=nextReady?('Next approved job: '+nextReady.job):'No approved job is ready. The runner does not create work.';
   $('active-step').textContent=nextReady?('Preparing '+nextReady.job+' for execution'):'Waiting. Report starvation instead of adding work.';
  }
  $('active-answer').textContent='';
 }else{
  $('active-title').textContent='No task is running';
  $('active-description').textContent='Select ready jobs below or click Start to begin.';
  $('active-answer').textContent='';
  $('active-step').textContent='The queue is idle.';
 }
 $('active-progress').replaceChildren();
 if(active?.progress){const p=document.createElement('progress');const event=active.progress;
  if(Number.isFinite(event.total)&&event.total>0){p.max=event.total;p.value=event.completed;
   add($('active-progress'),'span',event.completed+' / '+event.total+' '+(event.unit||'steps')+' ').className='small muted';}
  $('active-progress').append(p);}
 const elapsed=active?.startedAt?Math.max(0,Date.now()/1000-active.startedAt):null;
 $('active-time').textContent=active?(elapsed==null?'Elapsed unavailable':elapsed.toFixed(1)+' s elapsed'):'';
 $('active-eta').textContent=active&&active.eta?('ETA '+active.eta.low.toFixed(0)+'–'+active.eta.high.toFixed(0)+' s ('+active.eta.samples+' runs)'):'';
 $('active-decision').textContent=active?'Decision rule: '+active.decisionRule:'';
 $('active-controls').hidden=!active||!TOKEN;
 $('active-stop').disabled=!busy;$('active-cancel').disabled=!data.current;
 const countKind=kind=>jobs.filter(j=>j.evidenceKind===kind).length;
 const trust={};for(const j of jobs)if(j.trust)trust[j.trust]=(trust[j.trust]||0)+1;
 $('summary').textContent=jobs.length+' jobs; '+countState('complete')+' completed runs (completion is not acceptance); '+countKind('measured')+' measured reports'+
  (Object.keys(trust).length?'; trust: '+Object.entries(trust).map(([k,v])=>k+' '+v).join(', '):'')+'.';
 $('mode').textContent=TOKEN?'Local controls enabled. Start 1–10 selected jobs; use 5 for a normal batch.':'Read-only snapshot. Start the local dashboard server for controls.';
 $('start').disabled=!TOKEN||busy||Boolean(active);
 $('approve-add').disabled=!TOKEN;
 if($('run-all'))$('run-all').disabled=!TOKEN||busy;
 if($('stop'))$('stop').disabled=!TOKEN||!busy;
 $('cancel').disabled=!TOKEN||!data.current;
 $('status').textContent=data.stopping?'Stopping after the current job.':(data.current?'Running: '+data.current:
  (data.waiting||(active?'Another queue runner owns this task. Use that runner to stop it.':'No task is running.')));
 if(data.error)$('error').textContent=data.error;
 $('rows').replaceChildren();
 $('completed-rows').replaceChildren();
 for(const id of selected){if(!jobs.some(j=>j.job===id&&!['complete','blocked','running','exhausted'].includes(j.state)))selected.delete(id);}
 const previous=$('coverage-report').value;
 $('coverage-report').replaceChildren();
 const measured=jobs.filter(j=>j.measured);
 if(!measured.length)add($('coverage-report'),'option','No measured report').value='';
 for(const j of measured)add($('coverage-report'),'option',j.job+' — '+j.measured.task+' — '+j.measured.dataRole).value=j.job;
 if(measured.some(j=>j.job===previous))$('coverage-report').value=previous;
 showCoverage();
 const query=$('search').value.toLowerCase(), filter=$('filter').value, key=$('sort').value;
 const visible=jobs.filter(j=>{const d=description(j);return (['complete','drifted'].includes(j.state)||!filter||j.state===filter)&&
  [j.job,j.hypothesis,d.title,d.test,d.answers].join(' ').toLowerCase().includes(query);});
 visible.sort((a,b)=>key==='wallSeconds'?(a[key]||0)-(b[key]||0):String(a[key]).localeCompare(String(b[key])));
 let readyPriority=1;
 const backlogReady=visible.filter(j=>j.state==='pending'&&j.approved);
 $('backlog-count').textContent=backlogReady.length+' ready';
 for(const j of visible){
  const isCompleted=['complete','drifted'].includes(j.state);
  const tr=document.createElement('tr');if(j.state==='running'||j.job===data.current)tr.className='running';
  const tdSelect=add(tr,'td','');tdSelect.style.width='24px';
  const box=document.createElement('input');box.type='checkbox';box.checked=selected.has(j.job);
  box.disabled=['complete','drifted','blocked','running','exhausted'].includes(j.state);
  box.onchange=()=>box.checked?selected.add(j.job):selected.delete(j.job);tdSelect.append(box);
  const tdMain=add(tr,'td','');
  const item=add(tdMain,'div','');item.className='job-item';
  const topRow=add(item,'div','');topRow.className='job-title-row';
  const badge=add(topRow,'span',j.state.toUpperCase());
  badge.className='badge badge-'+(j.state==='running'?'running':(j.state==='pending'?'ready':(j.state==='blocked'?'blocked':'idle')));
  if(j.state==='pending'){const pBadge=add(topRow,'span','#'+(readyPriority++));pBadge.className='priority-badge';}
  const d=description(j);
  const titleSpan=add(topRow,'span',d.title);titleSpan.className='job-title';
  const idRow=add(item,'div','');idRow.className='job-sub';
  add(idRow,'span',j.job).className='job-id';
  if(j.evidenceKind&&j.evidenceKind!=='unverified')add(idRow,'span',' · '+j.evidenceKind).className='small muted';
  if(j.trust)add(idRow,'span',' · trust: '+j.trust).className='small muted';
  if(j.jobKind)add(idRow,'span',' · '+j.jobKind).className='small muted';
  if(j.state==='pending'&&!j.approved)add(idRow,'span',' · not approved').className='small muted';
  if(j.driftedModules&&j.driftedModules.length)add(idRow,'span',' · code changed since run').className='small muted';
  const testRow=add(item,'div',d.test);testRow.className='job-hypo';
  const tdAction=add(tr,'td','');tdAction.style.textAlign='right';tdAction.style.whiteSpace='nowrap';
  const elTime=j.state==='running'&&j.startedAt?Date.now()/1000-j.startedAt:j.wallSeconds;
  if(elTime!=null)add(tdAction,'div',Math.max(0,elTime).toFixed(1)+' s').className='small muted';
  if(j.eta)add(tdAction,'div','ETA '+j.eta.low.toFixed(0)+'–'+j.eta.high.toFixed(0)+' s').className='small muted';
  const btnInspect=add(tdAction,'button','Inspect');btnInspect.className='btn-sm';btnInspect.onclick=()=>show(j);
  $(isCompleted?'completed-rows':'rows').append(tr);
 }
 $('completed-count').textContent='Recorded outcomes, including changed code ('+jobs.filter(j=>['complete','drifted'].includes(j.state)).length+')';
}
function showCoverage(){
 const job=(data.jobs||[]).find(j=>j.job===$('coverage-report').value&&j.measured);
 $('coverage').replaceChildren();
 if(!job){$('coverage').textContent='Coverage is unavailable without measured evidence.';return;}
 const table=document.createElement('table');
 const header=add(table,'tr','');for(const title of ['Archetype / theme','Support','Correct'])add(header,'th',title);
 for(const [name,cell] of Object.entries(job.measured.coverage)){
  const row=add(table,'tr','');add(row,'td',name);add(row,'td',String(cell.support));
  add(row,'td',cell.support?cell.correct+'/'+cell.support:'Unsupported');
 }
 $('coverage').append(table);
}
async function request(path,body){
 const response=await fetch(path,{method:body?'POST':'GET',headers:{'Authorization':'Bearer '+TOKEN,'Content-Type':'application/json'},
 ...(body?{body:JSON.stringify(body)}:{})});
 const value=await response.json();if(!response.ok)throw Error(value.error||'Request failed');return value;
}
async function refresh(){if(!TOKEN)return;try{data=await request('/api/state');busy=data.busy;render();}catch(e){$('error').textContent=e.message;}}
async function action(name,body){try{$('error').textContent='';await request('/api/'+name,body);await refresh();}catch(e){$('error').textContent=e.message;}}
$('toggle-run').onclick=()=>{if(busy||Boolean(data.current))action('stop',{});else action('start-all',{});};
$('start').onclick=()=>action('start',{jobs:[...selected],retry:$('retry').checked});
if($('run-all'))$('run-all').onclick=()=>action('start-all',{});
$('approve-add').onclick=()=>action('add',{jobs:data.jobs.filter(j=>selected.has(j.job)).map(j=>({id:j.job,sha256:j.specSHA256}))});
if($('stop'))$('stop').onclick=()=>action('stop',{});
$('cancel').onclick=()=>action('cancel',{});
$('active-stop').onclick=()=>action('stop',{});$('active-cancel').onclick=()=>action('cancel',{});
$('close').onclick=()=>$('modal').close();
$('coverage-report').onchange=showCoverage;
for(const id of ['search','filter','sort'])$(id).oninput=render;
render();if(TOKEN)setInterval(refresh,1500);
</script></html>"""
    return page.replace('__TOKEN__', json.dumps(token)).replace('__DATA__', payload).replace('__DESCRIPTIONS__', descriptions)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'reports/research_dashboard.html')
    args=parser.parse_args()
    args.output.write_text(render_html(build_dashboard_data()))
    print(args.output)


if __name__=='__main__':
    main()
