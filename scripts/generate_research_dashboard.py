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
    from research_dashboard_states import annotate
    return annotate(queue.summarize(write=False), queue.QUEUE, queue.MODULES)


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
#backlog{border:1px solid #30363d;border-radius:6px;padding:4px 8px;margin-bottom:8px}
#glance{border:1px solid #30363d;border-radius:6px;background:#161b22;padding:6px 8px;margin-bottom:8px}#glance ol{margin:2px 0 0 18px;padding:0}.glance-state{font-size:13px;font-weight:600;color:#f0f6fc}
#backlog-table{width:100%;border-collapse:collapse}#backlog-table td,#backlog-table th{text-align:left;padding:1px 4px;border-bottom:1px solid #21262d}
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
.extend-form{display:grid;grid-template-columns:auto 1fr;gap:4px 6px;align-items:center;margin:4px 0}
.extend-form textarea{font:inherit;min-height:44px;background:#161b22;color:#c9d1d9;border:1px solid #30363d;border-radius:4px;padding:3px 6px}
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
  <span class="chip" id="chip-awaiting"><strong>0</strong> awaiting approval</span>
  <span class="chip" id="chip-blocked"><strong>0</strong> blocked</span>
  <span class="chip" id="chip-exhausted"><strong>0</strong> exhausted</span>
  <span class="chip" id="chip-superseded"><strong>0</strong> superseded</span>
  <span class="chip" id="chip-complete"><strong>0</strong> done</span>
</div>
<section id="glance" aria-live="polite" aria-label="Queue state at a glance">
  <div id="glance-state" class="glance-state">Loading queue state…</div>
  <div class="small muted">Next steps</div>
  <ol id="glance-next" class="small"></ol>
</section>
<details id="backlog"><summary><strong>Backlog</strong> <span id="backlog-summary" class="small muted"></span></summary>
  <p id="backlog-warning" class="warning small" hidden></p>
  <table id="backlog-table" class="small"><thead><tr><th>Record</th><th>Title</th><th>Jobs done</th><th>Ready</th><th>Result</th></tr></thead><tbody></tbody></table>
</details>
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
  <select id="filter" aria-label="State"><option value="">All</option><option value="pending">Pending (all not started)</option><option value="ready">Ready</option><option value="awaiting-approval">Awaiting approval</option><option value="blocked">Blocked</option><option value="unchecked">Readiness unchecked</option><option>running</option><option value="exhausted">Exhausted (no attempts left)</option><option value="superseded">Superseded (completed successor)</option><option>failed</option><option>cancelled</option><option>interrupted</option></select>
  <select id="sort" aria-label="Sort"><option value="job">ID</option><option value="state">State</option><option value="wallSeconds">Time</option></select>
</div>
<div class="section-header"><span>Active and waiting jobs</span> <span id="backlog-count" class="small muted"></span></div>
<table><thead><tr><th style="width:24px">#</th><th>Experiment / Task</th><th style="width:70px;text-align:right">Status</th></tr></thead><tbody id="rows"></tbody></table>
<details id="completed"><summary id="completed-count">Completed test outcomes</summary>
  <p class="small muted">Completed jobs stay here. Completion does not mean model acceptance.</p>
  <table><thead><tr><th style="width:24px">#</th><th>Experiment / Outcome</th><th style="width:70px;text-align:right">Status</th></tr></thead><tbody id="completed-rows"></tbody></table>
</details>
<details id="superseded"><summary id="superseded-count">Superseded history</summary>
  <p class="small muted">A completed successor answers each of these questions. They are history, not pending work. Their specifications and attempts stay unchanged.</p>
  <table><thead><tr><th style="width:24px">#</th><th>Experiment / Successor</th><th style="width:70px;text-align:right">Status</th></tr></thead><tbody id="superseded-rows"></tbody></table>
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
<dialog id="modal"><div style="display:flex;justify-content:space-between;align-items:center"><strong id="modal-title">Job Details</strong><button id="close" class="btn-sm">Close</button></div><section id="detail-description" style="margin-top:6px"></section><section id="extend" style="margin-top:6px" hidden></section><details style="margin-top:6px"><summary class="small">Technical details and registered decision rule</summary><pre id="detail"></pre></details></dialog>
<script>
const TOKEN=__TOKEN__;
let data=__DATA__;
const DESCRIPTIONS=__DESCRIPTIONS__;
let busy=Boolean(data.busy);
const selected=new Set();
const $=id=>document.getElementById(id);
const stateOf=j=>j.displayState||(j.state==='pending'?'unchecked':j.state);
const stateLabel=j=>({'awaiting-approval':'AWAITING APPROVAL',unchecked:'READINESS UNCHECKED',complete:'COMPLETED'}[stateOf(j)]||stateOf(j).toUpperCase());
const reasonLabel=r=>({input_changed:'A registered input file changed or is missing. Review its pinned identity.',not_approved:'Approval is required.',storage_insufficient:'Available storage is below the required reserve.'}[r]||r);
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
 if(row.displayState==='superseded')add(parent,'p','Superseded: the completed job '+row.supersededBy+' answers this question. This record is history, not pending work.').className='small';
 else if(row.state==='blocked')add(parent,'p','Blocked: this is a planned test, not a measured result.').className='warning';
}
function dur(s){if(s==null||!Number.isFinite(s))return 'unknown';s=Math.max(0,Math.round(s));const h=Math.floor(s/3600),m=Math.round(s%3600/60);
 return h?h+' h '+m+' min':s>=60?Math.round(s/60)+' min':s+' s';}
const mb=b=>(b/1e6).toLocaleString(undefined,{maximumFractionDigits:3})+' MB';
function extendPanel(row){
 const box=$('extend');box.replaceChildren();box.hidden=!row.extension;
 if(!row.extension)return;
 const x=row.extension,e=x.estimate||{};
 add(box,'strong','Exhausted job: restart with new limits');
 if(x.limits){
  add(box,'p','Last attempt: '+(x.status||'unknown')+' — '+(x.reason||'no reason')+' after '+dur(x.wallSeconds)+'. Attempts used: '+x.attempts+'.').className='small';
  add(box,'p','Current limits: '+dur(x.limits.timeoutSeconds)+' and '+mb(x.limits.maxOutputBytes)+'. Default policy: '+
   dur(x.defaultLimits.timeoutSeconds)+' and '+mb(x.defaultLimits.maxOutputBytes)+'. Larger limits record a maintainer override.').className='small';
  add(box,'p',e.available?('Progress: '+e.completed+' of '+e.total+' '+e.unit+'. Estimated restart time: '+dur(e.restartSeconds)+
   '. Work left after the recorded progress: '+dur(e.remainingAfterProgressSeconds)+'. '+e.basis):('Estimate unavailable: '+(e.basis||'no progress record.'))).className='small';
 }
 if(x.warning)add(box,'p',x.warning).className='warning small';
 if(x.successors?.length)add(box,'p','Successors: '+x.successors.join(', ')).className='small muted';
 if(x.blocker){add(box,'p','Restart unavailable: '+x.blocker).className='warning small';return;}
 if(!TOKEN){add(box,'p','Start the local dashboard server to save a restart.').className='small muted';return;}
 add(box,'p','A restart is new job '+x.successorId+'. It starts from step 0. It runs after ordinary ready work, in save order. The parent stays as history.').className='small muted';
 const form=add(box,'div','');form.className='extend-form';
 add(form,'label','Timeout (s)');const t=add(form,'input','');t.type='number';t.min=x.limits.timeoutSeconds;t.max=86400;t.step=60;t.value=x.suggested.timeoutSeconds;
 add(form,'label','Output (MB)');const o=add(form,'input','');o.type='number';o.step='any';o.min=x.limits.maxOutputBytes/1e6;o.value=x.suggested.maxOutputBytes/1e6;
 add(form,'label','Reason');const r=add(form,'textarea','');r.placeholder='Name the repair or the unresolved question (20 characters or more).';
 const hint=add(box,'p','');hint.className='small muted';
 const update=()=>{hint.textContent=e.available?'This timeout is '+Math.round(Number(t.value)/e.restartSeconds*100)+' % of the estimated restart time.':'';};
 t.oninput=update;update();
 const save=add(box,'button','Save restart at end of queue');save.className='btn-sm';
 const out=add(box,'p','');out.className='small';
 save.onclick=async()=>{save.disabled=true;out.textContent='Saving...';
  try{const v=await request('/api/extend',{job:row.job,timeoutSeconds:Math.round(Number(t.value)),
   maxOutputBytes:Math.max(x.limits.maxOutputBytes,Math.round(Number(o.value)*1e6)),reason:r.value});
   out.textContent='Saved '+v.result.job+'. '+(v.result.approved?'Approved. The runner starts it after ordinary ready work.':'Not approved: '+v.result.approvalError);
   await refresh();}
  catch(err){out.textContent=err.message;out.className='small error-text';save.disabled=false;}};
}
function show(row){$('detail-description').replaceChildren();explain($('detail-description'),row);extendPanel(row);
 $('detail').textContent=JSON.stringify(row,null,2);$('modal').showModal();}
function etaText(eta){
 const range=Math.round(eta.low)===Math.round(eta.high)?dur(eta.low):dur(eta.low)+'–'+dur(eta.high);
 return range+' left ('+(eta.basis==='progress'?'from progress':eta.basis==='parent-progress'?'from the parent attempt':eta.samples+' runs')+')';}
function renderGlance(){
 const b=data.backlog, jobs=data.jobs||[], next=$('glance-next');next.replaceChildren();
 const running=data.current||jobs.find(j=>j.state==='running')?.job;
 const ready=b?b.readyJobs:jobs.filter(j=>stateOf(j)==='ready').length;
 $('glance-state').textContent=data.stopping?'Stopping after the current job.':running?'Running '+running+'.':
  ready?'Waiting to start '+ready+' ready job'+(ready===1?'':'s')+'.':'Idle: no approved work is ready.';
 if(data.stale)$('glance-state').textContent+=' (Showing the last snapshot while a new one builds.)';
 const step=t=>add(next,'li',t);
 if(b&&b.readyJobs)step(b.readyJobs+' ready job'+(b.readyJobs===1?'':'s')+' will run next (about '+dur(b.readySeconds)+(b.readyUnknown?', '+b.readyUnknown+' without an estimate':'')+').');
 if(b&&b.reviewPending.length)step('Review completed results: '+b.reviewPending.slice(0,6).map(r=>r.id).join(', ')+(b.reviewPending.length>6?' and '+(b.reviewPending.length-6)+' more':'')+'. Run backlog_pipeline review, then confirm.');
 if(b&&b.awaitingApproval)step(b.awaitingApproval+' job'+(b.awaitingApproval===1?' passes':'s pass')+' every check except approval.');
 if(b&&b.blockedJobs)step(b.blockedJobs+' job'+(b.blockedJobs===1?' is':'s are')+' blocked or exhausted. Use the Blocked or Exhausted filter for the exact reason.');
 if(b&&b.refill)step('Fewer than 10 ready jobs. Run the backlog-grooming cycle: review, confirm, then expand planned records.');
 for(const g of (b?.topBlockers||[]).slice(0,3))
  step((g.kind==='adapter'?(g.missingTemplate?'Build the '+g.template+' template':'Extend '+g.template+': '+g.example):g.kind==='decision'?'Decide: '+g.example:'Supply data for '+g.template+': '+g.example)+' ('+g.owner+'). Unblocks '+g.unblocks+' record'+(g.unblocks===1?'':'s')+'.');
 if(b)add(next,'li','Catalog: '+b.answered+' questions answered, '+b.open+' open ('+(b.open-b.needsPlan)+' with a plan, '+b.needsPlan+' waiting for a template, data, or decision).').className='muted';
 if(!next.children.length)step('No action is due.');
}
function renderBacklog(){
 renderGlance();
 const b=data.backlog;$('backlog').hidden=!b;if(!b)return;
 $('backlog-summary').textContent=b.readyJobs+' ready jobs, about '+dur(b.readySeconds)+(b.readyUnknown?' plus '+b.readyUnknown+' without an estimate':'')+
  ' · '+b.planned+' planned records · '+b.needsPlan+' records need a plan';
 $('backlog-warning').hidden=!b.refill;
 $('backlog-warning').textContent='Fewer than 10 ready jobs remain. Run the backlog-grooming cycle: review, then expand the next planned records.';
 const body=$('backlog-table').tBodies[0];body.replaceChildren();
 for(const r of b.records.filter(r=>r.planned||r.jobs)){const tr=add(body,'tr','');
  for(const v of [r.id,r.title,r.complete+'/'+r.jobs,r.ready,r.result||(r.jobs&&r.complete===r.jobs?'review pending':'–')])add(tr,'td',String(v));}
}
function render(){
 renderBacklog();
 const jobs=data.jobs||[];
 let active=jobs.find(j=>j.job===data.current)||jobs.find(j=>j.state==='running');
 if(!active&&data.current){active={job:data.current,state:'running',hypothesis:'Executing task '+data.current};}
 const isRunning=busy||Boolean(data.current)||Boolean(active);
 const toggleBtn=$('toggle-run');
 if(data.stopping){toggleBtn.textContent='Stopping';toggleBtn.className='btn-toggle btn-stopping';toggleBtn.disabled=true;}
 else if(isRunning){toggleBtn.textContent='Stop';toggleBtn.className='btn-toggle btn-stop';toggleBtn.disabled=!TOKEN;}
 else{toggleBtn.textContent='Start';toggleBtn.className='btn-toggle btn-start';toggleBtn.disabled=!TOKEN;}
 $('run-mode').textContent=data.stopping?'Stopping':(active?'Running':(busy?'Runner active — waiting':'Idle'));
 $('run-mode').className='badge '+(data.stopping?'badge-blocked':(active?'badge-running':(busy?'badge-blocked':'badge-idle')));
 const countState=s=>jobs.filter(j=>stateOf(j)===s).length;
 $('chip-running').innerHTML='<strong>'+countState('running')+'</strong> running';
 const readyJobs=jobs.filter(j=>stateOf(j)==='ready');
 const awaiting=jobs.filter(j=>stateOf(j)==='awaiting-approval').length;
 $('chip-ready').innerHTML='<strong>'+readyJobs.length+'</strong> ready';
 $('chip-awaiting').innerHTML='<strong>'+awaiting+'</strong> awaiting approval';
 $('chip-blocked').innerHTML='<strong>'+countState('blocked')+'</strong> blocked';
 $('chip-exhausted').innerHTML='<strong>'+countState('exhausted')+'</strong> exhausted';
 $('chip-superseded').innerHTML='<strong>'+countState('superseded')+'</strong> superseded';
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
 $('active-eta').textContent=active&&active.eta?('ETA '+etaText(active.eta)):'';
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
 for(const id of selected){if(!jobs.some(j=>j.job===id&&(stateOf(j)==='ready'||(['failed','cancelled','interrupted'].includes(j.state)&&j.approved))))selected.delete(id);}
 const previous=$('coverage-report').value;
 $('coverage-report').replaceChildren();
 const measured=jobs.filter(j=>j.measured);
 if(!measured.length)add($('coverage-report'),'option','No measured report').value='';
 for(const j of measured)add($('coverage-report'),'option',j.job+' — '+j.measured.task+' — '+j.measured.dataRole).value=j.job;
 if(measured.some(j=>j.job===previous))$('coverage-report').value=previous;
 showCoverage();
 const query=$('search').value.toLowerCase(), filter=$('filter').value, key=$('sort').value;
 const visible=jobs.filter(j=>{const d=description(j);return (['complete','drifted'].includes(j.state)||stateOf(j)==='superseded'||!filter||(filter==='pending'?['pending','blocked'].includes(j.state):stateOf(j)===filter))&&
  [j.job,j.hypothesis,d.title,d.test,d.answers].join(' ').toLowerCase().includes(query);});
 visible.sort((a,b)=>key==='wallSeconds'?(a[key]||0)-(b[key]||0):String(a[key]).localeCompare(String(b[key])));
 let readyPriority=1;
 const backlogReady=visible.filter(j=>stateOf(j)==='ready');
 $('backlog-count').textContent=backlogReady.length+' ready';
 for(const j of visible){
  const isCompleted=['complete','drifted'].includes(j.state);
  const tr=document.createElement('tr');if(j.state==='running'||j.job===data.current)tr.className='running';
  const tdSelect=add(tr,'td','');tdSelect.style.width='24px';
  const box=document.createElement('input');box.type='checkbox';box.checked=selected.has(j.job);
  box.disabled=!(stateOf(j)==='ready'||(['failed','cancelled','interrupted'].includes(j.state)&&j.approved));
  box.onchange=()=>box.checked?selected.add(j.job):selected.delete(j.job);tdSelect.append(box);
  const tdMain=add(tr,'td','');
  const item=add(tdMain,'div','');item.className='job-item';
  const topRow=add(item,'div','');topRow.className='job-title-row';
  const badge=add(topRow,'span',stateLabel(j));
  badge.className='badge badge-'+(stateOf(j)==='running'?'running':(stateOf(j)==='ready'?'ready':(['blocked','awaiting-approval'].includes(stateOf(j))?'blocked':(['failed','exhausted'].includes(stateOf(j))?'failed':'idle'))));
  if(stateOf(j)==='ready'){const pBadge=add(topRow,'span','#'+(readyPriority++));pBadge.className='priority-badge';}
  const d=description(j);
  const titleSpan=add(topRow,'span',d.title);titleSpan.className='job-title';
  const idRow=add(item,'div','');idRow.className='job-sub';
  add(idRow,'span',j.job).className='job-id';
  if(j.evidenceKind&&j.evidenceKind!=='unverified')add(idRow,'span',' · '+j.evidenceKind).className='small muted';
  if(j.trust)add(idRow,'span',' · trust: '+j.trust).className='small muted';
  if(j.jobKind)add(idRow,'span',' · '+j.jobKind).className='small muted';
  if(j.readinessReasons?.length)add(item,'div','Needs: '+j.readinessReasons.map(reasonLabel).join('; ')).className='small warning';
  if(j.driftedModules&&j.driftedModules.length)add(idRow,'span',' · code changed since run').className='small muted';
  const testRow=add(item,'div',d.test);testRow.className='job-hypo';
  if(j.continuation)add(item,'div','Continuation: '+j.continuation.state+' — '+j.continuation.reason).className='small muted';
  if(j.extension)add(item,'div','Exhausted: '+(j.extension.reason||'unknown')+'. '+(j.extension.blocker?'Restart unavailable.':
   'Inspect to restart with new limits'+(j.extension.estimate?.available?' (estimated '+dur(j.extension.estimate.restartSeconds)+')':'')+'.')).className='small warning';
  if(j.extendedFrom)add(item,'div','Restart of '+j.extendedFrom.parent+'. Runs after ordinary ready work, in save order.').className='small muted';
  const tdAction=add(tr,'td','');tdAction.style.textAlign='right';tdAction.style.whiteSpace='nowrap';
  const elTime=j.state==='running'&&j.startedAt?Date.now()/1000-j.startedAt:j.wallSeconds;
  if(elTime!=null)add(tdAction,'div',Math.max(0,elTime).toFixed(1)+' s').className='small muted';
  if(j.eta)add(tdAction,'div','ETA '+etaText(j.eta)).className='small muted';
  const btnInspect=add(tdAction,'button','Inspect');btnInspect.className='btn-sm';btnInspect.onclick=()=>show(j);
  if(j.supersededBy)add(item,'div','Answered by '+j.supersededBy+'.').className='small muted';
  $(stateOf(j)==='superseded'?'superseded-rows':isCompleted?'completed-rows':'rows').append(tr);
 }
 if(!$('rows').children.length){const tr=add($('rows'),'tr','');const td=add(tr,'td',filter||query?'No job matches this filter.':
  'No active or waiting jobs. See Next steps at the top.');td.colSpan=3;td.className='small muted';}
 $('completed-count').textContent='Recorded outcomes, including changed code ('+jobs.filter(j=>['complete','drifted'].includes(j.state)).length+')';
 $('superseded-count').textContent='Superseded history ('+jobs.filter(j=>stateOf(j)==='superseded').length+')';
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
let polling=false;
async function refresh(){if(!TOKEN||polling)return;polling=true;
 try{const v=await request('/api/state'+(data.snapshotId?'?since='+data.snapshotId:''));
  if(v.unchanged){const {unchanged,...live}=v;Object.assign(data,live);}else data=v;
  busy=data.busy;render();}
 catch(e){$('error').textContent=e.message;}finally{polling=false;}}
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
