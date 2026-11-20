/* Read-only graph projection. No execution decisions or network mutations. */
(function (root) {
  'use strict';
  const terminal = new Set(['complete', 'superseded']);
  const state = j => j.displayState || j.state || 'unknown';
  const isHistory = j => terminal.has(state(j));
  const reasons = j => (j.readinessReasons || j.requirements || []).map(r=>typeof r==='object'?JSON.stringify(r):String(r));
  function branchConditions(j) {
    if(!Array.isArray(j.conditions))return 'Branch conditions are not supplied by this snapshot.';
    if(!j.conditions.length)return 'No outcome condition is recorded.';
    return j.conditions.map(c=>c&&['supported','contradicted'].includes(c.outcome)&&typeof c.job==='string'&&typeof c.output==='string'?
      c.job+' / '+c.output+' must report '+c.outcome:'Invalid condition record; inspect the specification.').join('; ');
  }
  const campaign = j => String(j.task || j.batch || 'Unassigned');
  function index(snapshot) {
    const jobs = new Map(), incoming = new Map(), outgoing = new Map(), issues = [];
    for (const j of snapshot.jobs || []) {
      if (!j.job || jobs.has(j.job)) { issues.push('Missing or duplicate job ID: ' + j.job); continue; }
      jobs.set(j.job, j); incoming.set(j.job, new Set()); outgoing.set(j.job, new Set());
    }
    for (const j of jobs.values()) for (const dependency of j.dependencies || []) {
      const id = typeof dependency === 'string' ? dependency : dependency.job;
      if (!id) { issues.push('Invalid dependency: ' + j.job); continue; }
      if (!jobs.has(id)) {
        jobs.set(id, {job:id, state:'missing', task:'Missing records'});
        incoming.set(id, new Set()); outgoing.set(id, new Set());
        issues.push('Missing dependency record: ' + id);
      }
      incoming.get(j.job).add(id); outgoing.get(id).add(j.job);
    }
    // Kahn's algorithm avoids recursion and never invents an order for cycles.
    const degree = new Map([...incoming].map(([id, deps]) => [id, deps.size]));
    const todo = [...degree].filter(([,n]) => !n).map(([id]) => id);
    let visited = 0;
    for (let i=0; i<todo.length; i++) {
      visited++;
      for (const id of outgoing.get(todo[i])) { degree.set(id, degree.get(id)-1); if (!degree.get(id)) todo.push(id); }
    }
    if (visited !== jobs.size) issues.push('Dependency cycle: inspect unresolved edges.');
    return {jobs, incoming, outgoing, issues};
  }
  function reach(id, edges) {
    const found = new Set(), todo = [id];
    for (let i=0; i<todo.length; i++) for (const next of edges.get(todo[i]) || []) {
      if (next !== id && !found.has(next)) { found.add(next); todo.push(next); }
    }
    return found;
  }
  function blockers(graph) {
    return [...graph.jobs.values()].filter(j => ['blocked','failed','exhausted','missing','awaiting-approval','interrupted'].includes(state(j)))
      .map(j => ({job:j, impact:[...reach(j.job, graph.outgoing)].filter(id => !terminal.has(state(graph.jobs.get(id)))).length}))
      .sort((a,b) => b.impact-a.impact || a.job.job.localeCompare(b.job.job));
  }
  function project(snapshot, options={}) {
    const graph = index(snapshot), limit = options.limit !== undefined ? options.limit : 180;
    let ids = new Set([...graph.jobs.values()].filter(j => !options.campaign || campaign(j) === options.campaign).map(j => j.job));
    if (options.focus && graph.jobs.has(options.focus)) {
      ids = new Set([options.focus, ...reach(options.focus,graph.incoming), ...reach(options.focus,graph.outgoing)]);
    }
    // Keep direct prerequisites. They explain cross-campaign blockers.
    for (const id of [...ids]) for (const dep of graph.incoming.get(id)) ids.add(dep);
    const hidden = [...ids].filter(id => terminal.has(state(graph.jobs.get(id))));
    if (!options.history) for (const id of hidden) ids.delete(id);
    if (options.state && options.state !== 'all') {
      ids = new Set([...ids].filter(id => {
        const j = graph.jobs.get(id);
        const s = id === snapshot.current ? 'running' : state(j);
        return s === options.state;
      }));
    }
    if (options.search) {
      const q = options.search.toLowerCase();
      ids = new Set([...ids].filter(id => {
        const j = graph.jobs.get(id);
        return id.toLowerCase().includes(q) || String(j?.task||'').toLowerCase().includes(q) || String(j?.hypothesis||'').toLowerCase().includes(q);
      }));
    }
    const ordered = [...ids].sort((a,b) => Number(b===snapshot.current)-Number(a===snapshot.current) || a.localeCompare(b));
    ids = new Set(limit > 0 ? ordered.slice(0,limit) : ordered);
    const nodes = [...ids].map(id => {
      const j=graph.jobs.get(id), s=id===snapshot.current?'running':state(j);
      return {data:{id, label:id+'\n'+s, state:s}, classes:s};
    });
    const edges = [];
    for (const id of ids) for (const dep of graph.incoming.get(id)) if (ids.has(dep)) {
      const conditions=graph.jobs.get(id).conditions;
      const label=Array.isArray(conditions)?conditions.filter(c=>c&&c.job===dep)
        .map(c=>['supported','contradicted'].includes(c.outcome)?'requires '+c.outcome:'invalid condition').join('; '):'';
      edges.push({data:{id:JSON.stringify([dep,id]), source:dep, target:id, label}});
    }
    return {schemaVersion:1, graph, nodes, edges, hidden:hidden.length, omitted:limit>0?Math.max(0,ordered.length-limit):0, issues:graph.issues};
  }
  function workflow(snapshot, name) {
    const graph=index(snapshot), memo=new Map();
    const category=id=>memo.get(id)||'needs action';
    function derive(id) {
      const j=graph.jobs.get(id), s=state(j||{});
      if(!j||s==='missing')return 'needs action';
      if(id===snapshot.current||s==='running')return 'running';
      if(terminal.has(s))return 'history';
      if(s==='ready')return 'ready';
      if(['failed','exhausted','interrupted','invalid','cancelled','awaiting-approval','drifted'].includes(s))return 'needs action';
      const deps=[...(graph.incoming.get(id)||[])];
      const why=reasons(j);
      if(why.length&&why.every(r=>r.startsWith('condition_not_met:')&&['supported','contradicted'].includes(r.split(':')[2])))return 'branch not selected';
      const dependencyOnly=why.length>0&&why.every(r=>r.startsWith('dependency_incomplete:'));
      let result='pending checks';
      if(s==='blocked'&&!dependencyOnly)result='needs action';
      else if(deps.some(d=>category(d)==='needs action'))result='needs action';
      else if(deps.some(d=>category(d)==='branch not selected'))result='branch not selected';
      else if(deps.some(d=>category(d)==='history'&&graph.jobs.get(d).state!=='complete'))result='needs action';
      else if(deps.some(d=>category(d)!=='history'))result='waiting';
      else if(s==='blocked')result='needs action';
      return result;
    }
    const degree=new Map([...graph.incoming].map(([id,deps])=>[id,deps.size]));
    const todo=[...degree].filter(([,n])=>n===0).map(([id])=>id);
    for(let i=0;i<todo.length;i++){
      const id=todo[i];memo.set(id,derive(id));
      for(const next of graph.outgoing.get(id)){degree.set(next,degree.get(next)-1);if(degree.get(next)===0)todo.push(next);}
    }
    const selected=[...graph.jobs.values()].filter(j=>!name||campaign(j)===name);
    const counts={};
    for(const j of selected){const c=category(j.job);counts[c]=(counts[c]||0)+1;}
    const relevant=new Set(selected.map(j=>j.job));
    for(const j of selected)for(const dep of reach(j.job,graph.incoming))relevant.add(dep);
    const affected=[...relevant].filter(id=>category(id)==='needs action');
    const roots=affected.filter(id=>{
      const why=reasons(graph.jobs.get(id));
      const inherited=[...(graph.incoming.get(id)||[])].some(d=>category(d)==='needs action');
      return !inherited||!why.length||!why.every(r=>r.startsWith('dependency_incomplete:'));
    });
    const actions=roots.map(id=>({
      job:graph.jobs.get(id), impact:[...reach(id,graph.outgoing)].filter(next=>selected.some(j=>j.job===next)&&category(next)!=='history').length
    })).sort((a,b)=>b.impact-a.impact||a.job.job.localeCompare(b.job.job));
    const running=(snapshot.jobs||[]).find(j=>j.job===snapshot.current);
    const capacity={};
    for(const kind of ['ready','waiting','needs action','pending checks']){
      const rows=selected.filter(j=>category(j.job)===kind);
      const times=rows.map(j=>j.workflowDuration).filter(t=>t&&Number.isInteger(t.samples)&&t.samples>0&&Number.isFinite(t.low)&&
        Number.isFinite(t.high)&&t.low>=0&&t.high>=t.low);
      capacity[kind]={jobs:rows.length,measured:times.length,low:times.length===rows.length?times.reduce((s,t)=>s+t.low,0):null,
        high:times.length===rows.length?times.reduce((s,t)=>s+t.high,0):null,samples:times.reduce((s,t)=>s+t.samples,0)};
    }
    return {counts,actions,running,issues:graph.issues,affectedJobs:affected.length,capacity,categories:memo};
  }
  function readiness(snapshot) {
    const w=workflow(snapshot), lanes={};
    for(const lane of ['priority','reserve','conditional','unassigned'])lanes[lane]={counts:{},jobs:[],knownSeconds:0,unknownReady:0};
    for(const j of snapshot.jobs||[]) {
      let category=w.categories.get(j.job)||'needs action';
      const s=state(j);
      if(s==='superseded')category='superseded';
      else if(s==='exhausted')category='exhausted';
      else if(category==='history')category='complete';
      const lane=Array.isArray(j.conditions)&&j.conditions.length?'conditional':
        (['priority','reserve','conditional'].includes(j.workflowLane)?j.workflowLane:'unassigned');
      const item=lanes[lane];item.counts[category]=(item.counts[category]||0)+1;
      if(!['complete','superseded','branch not selected'].includes(category))item.jobs.push({job:j,category});
      if(category==='ready') {
        const t=j.workflowDuration;
        if(t&&Number.isInteger(t.samples)&&t.samples>0&&Number.isFinite(t.high)&&Number.isFinite(t.low)&&t.low>=0&&t.high>=t.low)item.knownSeconds+=t.low;
        else item.unknownReady++;
      }
    }
    return {lanes,actions:w.actions,running:w.running,stale:!!snapshot.stale};
  }
  function measuredETA(job) {
    const eta=job?.eta;
    if(!eta||!Number.isFinite(eta.low)||!Number.isFinite(eta.high)||eta.low<0||eta.high<eta.low)return 'ETA unavailable';
    if(['progress','parent-progress'].includes(eta.basis))
      return Math.ceil(eta.low)+'–'+Math.ceil(eta.high)+' s remaining (from '+(eta.basis==='progress'?'worker progress':'parent attempt progress')+')';
    if(!Number.isInteger(eta.samples)||eta.samples<1)return 'ETA unavailable';
    return Math.ceil(eta.low)+'–'+Math.ceil(eta.high)+' s remaining ('+eta.samples+' measured runs)';
  }
  root.QueueGraph = {index, reach, blockers, project, campaign, state, workflow, readiness, measuredETA, isHistory, branchConditions};
  if (typeof module !== 'undefined') module.exports=root.QueueGraph;
})(typeof globalThis !== 'undefined' ? globalThis : this);

if (typeof document !== 'undefined') {
  (() => {
    const get=id=>document.getElementById(id);
    let cy=null, chosen='', topology='', lastGood=Date.now();
    const panel=get('graph-panel'), selector=get('graph-campaign'), mode=get('graph-layout');
    const write=(parent,tag,text)=>{const el=document.createElement(tag);el.textContent=text;parent.append(el);return el;};
    const batchPanel=document.createElement('section');batchPanel.id='workflow-status';
    batchPanel.style.cssText='border:1px solid #52697f;border-radius:10px;padding:14px;margin:12px 0;background:#101923';
    batchPanel.setAttribute('aria-label','Experiment workflow status');
    get('graph-tools').after(batchPanel);
    write(batchPanel,'h2','Experiment workflow');
    const batchLabel=write(batchPanel,'label','Batch '), batchSelect=document.createElement('select');
    batchSelect.setAttribute('aria-label','Workflow batch');batchLabel.append(batchSelect);
    const batchActive=write(batchPanel,'p',''), batchCounts=write(batchPanel,'p',''), batchTiming=write(batchPanel,'p','');
    const batchActions=write(batchPanel,'div','');
    const batchHistory=document.createElement('details');batchPanel.append(batchHistory);
    const historyTitle=write(batchHistory,'summary','Completed outcomes'), historyBody=write(batchHistory,'div','');
    const overviewPanel=document.createElement('section');overviewPanel.id='research-overview';
    overviewPanel.style.cssText=batchPanel.style.cssText;batchPanel.after(overviewPanel);
    function updateOverview(){
      overviewPanel.replaceChildren();write(overviewPanel,'h2','Research decisions and queue readiness');
      const ready=QueueGraph.readiness(data);
      if(ready.stale)write(overviewPanel,'strong','STALE — readiness is not current. Execution is unchanged.');
      write(overviewPanel,'p','Standard comes first. HCF is optional. Completion does not grant model acceptance.');
      for(const [lane,value] of Object.entries(ready.lanes)){
        const details=document.createElement('details');overviewPanel.append(details);
        write(details,'summary',lane+' — '+Object.entries(value.counts).map(([k,n])=>n+' '+k).join(' · '));
        write(details,'p','Ready work: '+Math.floor(value.knownSeconds)+' measured seconds; '+value.unknownReady+' ready jobs have unknown duration. Budget limits are not estimates.');
        for(const item of value.jobs.slice(0,30)){
          const b=write(details,'button',item.job.job+' — '+item.category);b.onclick=()=>show(item.job);
          write(details,'p',description(item.job).test);
        }
        if(value.jobs.length>30)write(details,'p',(value.jobs.length-30)+' more upcoming jobs. Use the campaign list.');
      }
      const total=Object.values(ready.lanes).reduce((s,l)=>s+(l.counts.ready||0),0);
      write(overviewPanel,'p',total<10?'REFILL NEEDED: fewer than 10 ready jobs. Conditional and blocked work do not supply overnight capacity.':
        'Ready count is not proof of overnight capacity. Check measured duration and missing estimates.');
      write(overviewPanel,'p','Capacity target: 24 hours of useful ready work. '+(total===0?'Unmet: no ready work.':
        'Compare measured time with this target. Unknown durations do not establish coverage.'));
      write(overviewPanel,'p','Exhausted attempts need a checkpoint and budget review. Blocked jobs need their stated requirement. Neither automatically restarts.');
      const reports=data.researchOverview||{};
      if(reports.issue)write(overviewPanel,'p',reports.issue);
      write(overviewPanel,'p',reports.limitation||'No combined research evidence is configured.');
      const history=document.createElement('details');overviewPanel.append(history);
      write(history,'summary','Campaign findings ('+(reports.campaigns||[]).length+')');
      for(const report of reports.campaigns||[]){
        const card=document.createElement('details');history.append(card);
        write(card,'summary',report.title+' — '+(report.outcome||report.execution));
        write(card,'p','Execution: '+report.execution+'. Evidence: '+report.evidence+'. Model acceptance: '+report.modelAcceptance+'.');
        if(report.report)write(card,'p','Receipt source: '+report.report+'; attempt '+report.attempt+'.');
        if(report.issue)write(card,'p',report.issue);
        for(const s of report.slices||[])write(card,'p',s.profile+' / '+s.arm+': '+s.gains+' gains, '+s.losses+' losses, '+s.newWrong+' new wrong; '+s.observations+' observations, '+s.groups+' recorded groups, '+s.noFocus+' no-focus. Outcomes: '+JSON.stringify(s.outcomes));
        write(card,'p',report.limitation||'Measurements unavailable.');
        write(card,'p',report.nextAction||'Wait for verified evidence.');
        for(const r of report.nextRequirements||[])write(card,'p','Next requirement: '+r);
        const cases=document.createElement('details');card.append(cases);write(cases,'summary','Case-linked changes');
        for(const r of report.cases||[])write(cases,'p',r.id+' / '+r.group+' / '+r.profile+' / '+r.arm+': '+r.baseline+' → '+r.candidate);
        if(report.omittedCases)write(cases,'p',report.omittedCases+' more cases in the original report.');
      }
    }
    function updateWorkflow(){
      const names=[...new Set((data.jobs||[]).map(QueueGraph.campaign))].sort();
      const previous=batchSelect.value;
      if(JSON.stringify(names)!==batchSelect.dataset.names){
        batchSelect.replaceChildren();for(const name of names)write(batchSelect,'option',name).value=name;
        batchSelect.dataset.names=JSON.stringify(names);
        batchSelect.value=names.includes(previous)?previous:(names.includes('workflow434-standard')?'workflow434-standard':names[0]||'');
      }
      const value=QueueGraph.workflow(data,batchSelect.value);
      batchActive.textContent=(data.stale?'STALE SNAPSHOT — ':'')+(value.running?'RUNNING: '+value.running.job+' — '+description(value.running).test:'No running task is recorded in this snapshot.');
      batchActive.style.cssText='font-size:16px;font-weight:bold;border-left:4px solid #70ffff;padding-left:10px';
      batchCounts.textContent=Object.entries(value.counts).map(([key,n])=>n+' '+key).join(' · ');
      const duration=kind=>{const c=value.capacity[kind];return kind+': '+c.jobs+' jobs, '+
        (c.low===null?'duration unavailable ('+c.measured+'/'+c.jobs+' measured)':Math.ceil(c.low)+'–'+Math.ceil(c.high)+' s ('+c.samples+' history samples)');};
      batchTiming.textContent='Running task: '+QueueGraph.measuredETA(value.running)+'. '+duration('ready')+'. '+duration('waiting')+
        '. Durations sum serial work; they are not completion deadlines. Completion is not model acceptance.';
      batchActions.replaceChildren();
      write(batchActions,'strong','Actionable requirements');
      for(const item of value.actions.slice(0,8)){
        const j=item.job, button=write(batchActions,'button',j.job+' · '+item.impact+' dependent jobs');
        button.onclick=()=>show(j);
        write(batchActions,'p','Owner: '+(j.owner||'not recorded')+'. '+
          ((j.readinessReasons||j.requirements||[]).map(r=>typeof r==='object'?JSON.stringify(r):String(r)).join('; ')||j.reason||'Exact requirement is not recorded.'));
      }
      if(!value.actions.length)write(batchActions,'p','No actionable blocker is recorded. Dependency waits are counted separately.');
      if(value.actions.length>8)write(batchActions,'p',(value.actions.length-8)+' more root requirements. Use the graph to inspect dependencies.');
      if(value.affectedJobs>value.actions.length)write(batchActions,'p',(value.affectedJobs-value.actions.length)+' downstream jobs wait on these requirements.');
      historyBody.replaceChildren();
      const completed=(data.jobs||[]).filter(j=>QueueGraph.campaign(j)===batchSelect.value&&QueueGraph.isHistory(j));
      historyTitle.textContent='Completed outcomes ('+completed.length+')';
      for(const j of completed){const button=write(historyBody,'button',j.job+' · '+QueueGraph.state(j));button.onclick=()=>show(j);}
    }
    batchSelect.onchange=updateWorkflow;
    const inspect=id=>{
      chosen=id;
      const graph=QueueGraph.index(data), j=graph.jobs.get(id); if(!j)return;
      const insp=get('graph-inspector');
      if(insp) insp.hidden=false;
      const el=get('graph-detail');el.replaceChildren();
      write(el,'h3',id);
      const d=description(j);
      for(const [label,value] of [
        ['Test',d.test],['Result decides',d.answers],['Execution',QueueGraph.state(j)],
        ['Owner',j.owner||'Not recorded'],['Required action',(j.readinessReasons||j.requirements||[]).join('; ')||j.reason||'No blocker recorded'],
        ['Branch requirements',QueueGraph.branchConditions(j)],
        ['Specification metadata',j.metadataVerified===true?'Hash matches this snapshot':j.metadataIssue||'Not supplied'],
        ['Downstream jobs',QueueGraph.reach(id,graph.outgoing).size],
        ['Evidence',j.trust||j.evidenceKind||'Not verified'],['Model acceptance',j.modelAcceptance||'Not recorded'],
        ['Delivery',j.deliveryState||'Not recorded']]) {
        write(el,'strong',label);write(el,'p',typeof value==='object'?JSON.stringify(value):String(value??'Unavailable'));
      }
      if(j.state==='exhausted'&&j.extension&&!j.extension.blocker){
        const ext=j.extension, to=ext.suggested?.timeoutSeconds||800;
        const mb=Math.round((ext.suggested?.maxOutputBytes||100000000)/1e6);
        const box=document.createElement('div');box.className='extend-box';
        const h4=document.createElement('h4');h4.textContent='1-Button Approval: Give More Time';
        const p=document.createElement('p');p.style.fontSize='11px';p.style.color='#c9d1d9';
        p.textContent='Task exhausted due to limits ('+(j.reason||'timeout/output limit')+'). Increase limits to '+to+' s and '+mb+' MB to restart this task.';
        const btn=document.createElement('button');btn.id='btn-extend-detail-'+j.job;btn.className='btn-approve-time';
        btn.style.fontSize='11px';btn.style.padding='5px 12px';btn.textContent='+ Approve & Restart ('+to+' s, '+mb+' MB)';
        btn.onclick=()=>approveMoreTime(j.job,to,ext.suggested?.maxOutputBytes||(mb*1e6));
        box.append(h4,p,btn);el.append(box);
      }
      if(cy){cy.nodes().unselect();cy.getElementById(id).select();}
    };
    const layout=()=>{
      if(!cy||!cy.nodes().length)return;
      const m = mode.value;
      if (m === 'grid') {
        cy.layout({name: 'grid', fit: true, padding: 40, avoidOverlap: true, spacingFactor: 1.25, condense: true, nodeDimensionsIncludeLabels: true}).run();
      } else if (m === 'cose') {
        cy.layout({name: 'cose', animate: false, fit: true, padding: 50, nodeRepulsion: 15000, idealEdgeLength: 100, edgeElasticity: 100, gravity: 80, numIter: 800, nodeDimensionsIncludeLabels: true}).run();
      } else if (m === 'blockers') {
        const focus=chosen||cy.nodes()[0]?.id();
        const distance=new Map([[focus,0]]), todo=[focus];
        for(let i=0;i<todo.length;i++) for(const node of cy.getElementById(todo[i]).neighborhood().nodes()){
          if(!distance.has(node.id())){distance.set(node.id(),distance.get(todo[i])+1);todo.push(node.id());}
        }
        cy.layout({name:'concentric',animate:false,padding:40,concentric:n=>1000-(distance.get(n.id())??999),levelWidth:()=>1,minNodeSpacing:60}).run();
      } else {
        // Hierarchical DAG flow (Left -> Right) with wrapped columns for wide suites
        const nodes = cy.nodes();
        const inDegree = new Map(), outgoing = new Map();
        for (const n of nodes) {
          inDegree.set(n.id(), n.incomers('node').length);
          outgoing.set(n.id(), n.outgoers('node').map(o => o.id()));
        }
        const rank = new Map();
        const queue = nodes.filter(n => inDegree.get(n.id()) === 0).map(n => n.id());
        for (const id of queue) rank.set(id, 0);
        for (let i = 0; i < queue.length; i++) {
          const u = queue[i];
          const r = rank.get(u) || 0;
          for (const v of outgoing.get(u) || []) {
            const cur = rank.get(v) || 0;
            if (r + 1 > cur) rank.set(v, r + 1);
            const rem = inDegree.get(v) - 1;
            inDegree.set(v, rem);
            if (rem === 0) queue.push(v);
          }
        }
        for (const n of nodes) if (!rank.has(n.id())) rank.set(n.id(), 0);
        const colGroups = new Map();
        for (const n of nodes) {
          const r = rank.get(n.id());
          if (!colGroups.has(r)) colGroups.set(r, []);
          colGroups.get(r).push(n);
        }
        const colWidth = 240, rowHeight = 75, MAX_PER_SUBCOL = 10;
        let currentX = 0;
        cy.batch(() => {
          const sortedRanks = [...colGroups.keys()].sort((a,b)=>a-b);
          for (const r of sortedRanks) {
            const groupNodes = colGroups.get(r);
            const subCols = Math.ceil(groupNodes.length / MAX_PER_SUBCOL);
            for (let sc = 0; sc < subCols; sc++) {
              const slice = groupNodes.slice(sc * MAX_PER_SUBCOL, (sc + 1) * MAX_PER_SUBCOL);
              slice.forEach((node, idx) => {
                node.position({
                  x: currentX + (sc * colWidth),
                  y: idx * rowHeight
                });
              });
            }
            currentX += subCols * colWidth + 50;
          }
        });
      }
      readable();
    };
    const MIN_READABLE_ZOOM=0.25;
    function readable(){
      if(!cy||!cy.nodes().length)return;
      cy.resize();cy.fit(undefined,40);
      if(cy.zoom()<MIN_READABLE_ZOOM){
        const target=(chosen&&cy.getElementById(chosen).length)?cy.getElementById(chosen):cy.nodes()[0];
        cy.zoom(MIN_READABLE_ZOOM);cy.center(target);
      }
    }
    function update(force=false) {
      updateWorkflow();
      updateOverview();
      const jobs=data.jobs||[], old=selector.value;
      const setStat=(id,cnt)=>{const el=get(id);if(el){const s=el.querySelector?.('strong');if(s)s.textContent=cnt;}};
      setStat('stat-total',jobs.length);
      setStat('stat-running',jobs.filter(j=>j.job===data.current||j.state==='running').length);
      setStat('stat-ready',jobs.filter(j=>QueueGraph.state(j)==='ready').length);
      setStat('stat-blocked',jobs.filter(j=>QueueGraph.state(j)==='blocked').length);
      setStat('stat-exhausted',jobs.filter(j=>j.state==='exhausted').length);
      setStat('stat-done',jobs.filter(j=>['complete','superseded'].includes(QueueGraph.state(j))).length);

      const runJob = jobs.find(j=>j.job===data.current||j.state==='running');
      const hudStatus = get('hud-status');
      const hudStatusText = get('hud-status-text');
      const hudTaskInfo = get('hud-task-info');
      if (hudStatus && hudStatusText && hudTaskInfo) {
        if (runJob) {
          hudStatus.className = 'hud-pill running';
          hudStatusText.textContent = 'Running';
          hudTaskInfo.textContent = runJob.job + ' — ' + (description(runJob).title || runJob.hypothesis || 'Running experiment');
        } else {
          hudStatus.className = 'hud-pill idle';
          hudStatusText.textContent = 'Idle';
          const rCnt = jobs.filter(j=>QueueGraph.state(j)==='ready').length;
          const bCnt = jobs.filter(j=>QueueGraph.state(j)==='blocked').length;
          const eCnt = jobs.filter(j=>j.state==='exhausted').length;
          hudTaskInfo.textContent = 'Queue idle · ' + rCnt + ' ready · ' + bCnt + ' blocked · ' + eCnt + ' can extend';
        }
      }

      const campaigns=[...new Set(jobs.map(QueueGraph.campaign))].sort();
      if(JSON.stringify(campaigns)!==selector.dataset.keys){
        selector.replaceChildren();
        const optAll=write(selector,'option','All Campaigns');optAll.value='';
        for(const name of campaigns){const option=write(selector,'option',name);option.value=name;}
        selector.dataset.keys=JSON.stringify(campaigns);
        selector.value=campaigns.includes(old)?old:'';
      }
      const g=QueueGraph.index(data), attention=get('graph-blockers');
      if(attention){
        attention.replaceChildren();
        const urgent=QueueGraph.workflow(data,selector.value).actions;
        const bCnt=get('blocked-count');if(bCnt)bCnt.textContent=urgent.length;
        for(const b of urgent.slice(0,15)){
          const item=document.createElement('div');item.className='item-card';
          const hdr=document.createElement('div');hdr.className='item-header';
          const btn=document.createElement('button');btn.className='item-title';btn.textContent=b.job.job;
          btn.onclick=()=>{chosen=b.job.job;if(cy&&cy.getElementById(chosen).length){cy.center(cy.getElementById(chosen));cy.getElementById(chosen).select();}inspect(chosen);};
          const badge=document.createElement('span');badge.className='badge badge-blocked';badge.textContent=b.impact+' downstream';
          hdr.append(btn,badge);
          const meta=document.createElement('div');meta.className='item-warning';
          meta.textContent=(b.job.readinessReasons||b.job.requirements||[]).join('; ')||b.job.reason||'Requirement pending';
          item.append(hdr,meta);attention.append(item);
        }
        if(!urgent.length){const em=document.createElement('p');em.className='item-meta';em.textContent='No actionable blockers in this selection.';attention.append(em);}
      }

      const extList=get('graph-extendable');
      if(extList){
        extList.replaceChildren();
        const extendable=jobs.filter(j=>j.state==='exhausted'&&j.extension&&!j.extension.blocker);
        const eCnt=get('extendable-count');if(eCnt)eCnt.textContent=extendable.length;
        for(const j of extendable.slice(0,15)){
          const item=document.createElement('div');item.className='item-card';
          const hdr=document.createElement('div');hdr.className='item-header';
          const btn=document.createElement('button');btn.className='item-title';btn.textContent=j.job;
          btn.onclick=()=>{chosen=j.job;if(cy&&cy.getElementById(chosen).length){cy.center(cy.getElementById(chosen));cy.getElementById(chosen).select();}inspect(chosen);};
          hdr.append(btn);
          const ext=j.extension, to=ext.suggested?.timeoutSeconds||800;
          const mb=Math.round((ext.suggested?.maxOutputBytes||100000000)/1e6);
          const meta=document.createElement('div');meta.className='item-meta';
          meta.textContent='Exhausted: '+(j.reason||'limits reached')+' · Suggest: '+to+' s, '+mb+' MB';
          const act=document.createElement('div');act.style.marginTop='4px';
          const appBtn=document.createElement('button');appBtn.id='btn-extend-'+j.job;appBtn.className='btn-approve-time';
          appBtn.textContent='+ Give More Time ('+to+' s, '+mb+' MB)';
          appBtn.onclick=()=>{if(typeof approveMoreTime==='function')approveMoreTime(j.job,to,ext.suggested?.maxOutputBytes||(mb*1e6));};
          act.append(appBtn);item.append(hdr,meta,act);extList.append(item);
        }
        if(!extendable.length){const em=document.createElement('p');em.className='item-meta';em.textContent='No exhausted tasks eligible for extension.';extList.append(em);}
      }

      get('graph-freshness').textContent=data.stale?'STALE — last snapshot; do not infer completion.':'Snapshot '+(data.snapshotId||'export')+' · '+new Date(lastGood).toLocaleTimeString();
      if((panel && panel.hidden && !get('graph-canvas')) || document.hidden)return;
      if(typeof cytoscape==='undefined'){get('graph-warning').textContent='Graph library unavailable. Use the list view.';return;}
      const stateFilter=get('graph-filter-state')?.value||'';
      const limitFilter=get('graph-limit')?Number(get('graph-limit').value):180;
      const p=QueueGraph.project(data,{campaign:selector.value,focus:mode.value==='blockers'?chosen:'',history:get('graph-history').checked,state:stateFilter,limit:limitFilter,search:get('graph-find')?.value});
      get('graph-warning').textContent=[...p.issues.slice(0,10),p.issues.length>10?(p.issues.length-10)+' more graph warnings.':'',p.hidden+' completed or superseded nodes hidden.',p.omitted?p.omitted+' nodes omitted. Narrow the campaign or increase limit.':'',
        'Arrows show recorded prerequisites, not inferred decision rules.'].filter(Boolean).join(' ');
      const signature=JSON.stringify([mode.value,selector.value,stateFilter,limitFilter,p.nodes.map(n=>n.data.id),p.edges.map(e=>e.data.id)]);
      if(!cy){cy=cytoscape({container:get('graph-canvas'),elements:[],layout:{name:'preset'},autoungrabify:true,boxSelectionEnabled:false,
        style:[{selector:'node',style:{'shape':'round-rectangle','width':210,'height':50,'background-color':'#182330','color':'#f0f6fc','label':'data(label)','text-wrap':'wrap','font-size':11,'font-weight':600,'text-valign':'center','border-width':1.5,'border-color':'#3b4c5e'}},
          {selector:'edge',style:{'width':2,'line-color':'#52697f','target-arrow-color':'#52697f','target-arrow-shape':'triangle','curve-style':'bezier',
            'label':'data(label)','font-size':10,'color':'#ffc77e','text-background-color':'#0d1117','text-background-opacity':0.8,'arrow-scale':1.1}},
          {selector:'.running',style:{'background-color':'#0b4952','border-color':'#5ce1dc','border-width':3}},
          {selector:'.blocked, .failed, .missing',style:{'background-color':'#3a2c0f','border-color':'#ffc77e','border-width':2}},
          {selector:'.exhausted',style:{'background-color':'#3d1a10','border-color':'#ffaa44','border-width':2}},
          {selector:'.ready',style:{'background-color':'#125430','border-color':'#55d790','border-width':2}},
          {selector:'.complete, .superseded',style:{'background-color':'#161b22','border-color':'#30363d','color':'#8b949e','opacity':0.7}},
          {selector:':selected',style:{'border-color':'#ffffff','border-width':3,'opacity':1}},
          {selector:'.highlighted-incoming',style:{'border-color':'#5ce1dc','border-width':3,'line-color':'#5ce1dc','target-arrow-color':'#5ce1dc'}},
          {selector:'.highlighted-outgoing',style:{'border-color':'#ffc77e','border-width':3,'line-color':'#ffc77e','target-arrow-color':'#ffc77e'}},
          {selector:'.dimmed',style:{'opacity':0.25}}]});
        cy.on('tap','node',event=>{
          const node=event.target, id=node.id();
          inspect(id);
          cy.elements().removeClass('dimmed highlighted-incoming highlighted-outgoing');
          cy.elements().addClass('dimmed');
          node.removeClass('dimmed');
          node.incomers().removeClass('dimmed').addClass('highlighted-incoming');
          node.outgoers().removeClass('dimmed').addClass('highlighted-outgoing');
        });
        cy.on('tap',event=>{
          if(event.target===cy){
            cy.elements().removeClass('dimmed highlighted-incoming highlighted-outgoing');
            const insp=get('graph-inspector');if(insp)insp.hidden=true;
          }
        });
        const btnIn=get('btn-zoom-in'), btnOut=get('btn-zoom-out'), btnFit=get('btn-zoom-fit');
        if(btnIn)btnIn.onclick=()=>{cy.zoom({level:cy.zoom()*1.25,renderedPosition:{x:cy.width()/2,y:cy.height()/2}});};
        if(btnOut)btnOut.onclick=()=>{cy.zoom({level:cy.zoom()*0.8,renderedPosition:{x:cy.width()/2,y:cy.height()/2}});};
        if(btnFit)btnFit.onclick=()=>readable();
      }
      if(signature!==topology||force){cy.elements().remove();cy.add([...p.nodes,...p.edges]);topology=signature;layout();}
      else cy.batch(()=>{for(const n of p.nodes){const item=cy.getElementById(n.data.id);item.data(n.data);item.classes(n.classes);}});
      const list=get('graph-node-list'), previous=list?.value;
      if(list){
        list.replaceChildren();
        write(list,'option','Select a job to inspect').value='';
        for(const n of p.nodes)write(list,'option',n.data.label.replace('\n',' · ')).value=n.data.id;
        list.value=p.nodes.some(n=>n.data.id===chosen)?chosen:previous;
      }
      const rowsTable=get('rows');
      if(rowsTable){
        rowsTable.replaceChildren();
        const lCnt=get('list-count');if(lCnt)lCnt.textContent=p.nodes.length;
        for(const n of p.nodes.slice(0,60)){
          const tr=document.createElement('tr');tr.style.borderBottom='1px solid #21262d';
          const td=document.createElement('td');td.style.padding='2px 4px';
          const b=document.createElement('button');b.className='item-title';b.style.fontSize='10px';
          b.textContent=n.data.id+' · '+n.data.state;b.onclick=()=>inspect(n.data.id);
          td.append(b);tr.append(td);rowsTable.append(tr);
        }
      }
      if(chosen&&g.jobs.has(chosen))inspect(chosen);
      get('graph-count').textContent=p.nodes.length+' visible jobs · '+p.edges.length+' dependencies';
    }
    get('graph-show').onclick=()=>{panel.hidden=false;get('graph-show').setAttribute('aria-pressed','true');update();readable();};
    get('graph-hide').onclick=()=>{panel.hidden=true;get('graph-show').setAttribute('aria-pressed','false');};
    selector.onchange=()=>{chosen='';update(true);};
    const filterState=get('graph-filter-state');if(filterState)filterState.onchange=()=>update(true);
    const filterLimit=get('graph-limit');if(filterLimit)filterLimit.onchange=()=>update(true);
    mode.onchange=()=>{
      if(mode.value==='blockers')chosen=QueueGraph.blockers(QueueGraph.index(data)).find(b=>!selector.value||QueueGraph.campaign(b.job)===selector.value)?.job.job||chosen;
      update(true);if(chosen)inspect(chosen);
    };
    get('graph-history').onchange=()=>update(true);get('graph-fit').onclick=()=>readable();
    get('graph-node-list').onchange=e=>inspect(e.target.value);
    get('graph-running').onclick=()=>{const j=(data.jobs||[]).find(j=>j.job===data.current);if(!j)return;
      selector.value=QueueGraph.campaign(j);mode.value='execution';chosen=j.job;update(true);inspect(j.job);cy?.center(cy.getElementById(j.job));};
    get('graph-find').oninput=()=>{update(true);};
    const oldRender=typeof render==='function'?render:null;
    render=function(){get('superseded-rows')?.replaceChildren?.();if(oldRender)oldRender();update();};
    document.addEventListener('visibilitychange',()=>{if(!document.hidden)update();});
    // The companion only reads snapshots. It has no mutation token or POST path.
    if(data.graphCompanion){
      let fetching=false;
      setInterval(async()=>{if(document.hidden||fetching)return;fetching=true;
        try{const r=await fetch('/api/state');if(!r.ok)throw Error('Snapshot unavailable');
          data=await r.json();busy=data.busy;lastGood=Date.now();render();}
        catch(e){data.stale=true;updateWorkflow();updateOverview();get('graph-freshness').textContent='DISCONNECTED — last successful contact '+new Date(lastGood).toLocaleTimeString();}
        finally{fetching=false;}
      },10000);
    }
    update();
  })();
}

// Readable order (maintainer request, 2026-11-07): current task first; long reference sections collapsed.
// Presentation only: elements move or fold; none are removed and no data or control changes.
if (typeof document !== 'undefined') {
(function tidyLayout(){
  if (!document.head || !document.querySelector) return;
  const byId=id=>document.getElementById(id);
  const top=byId('top-bar'); if(!top)return;
  const fold=(nodes,title)=>{
    nodes=nodes.filter(Boolean); if(!nodes.length)return null;
    const box=document.createElement('details'); box.className='tidy-fold';
    const summary=document.createElement('summary'); summary.textContent=title; box.append(summary);
    nodes[0].before?.(box); nodes.forEach(n=>box.append(n)); return box;
  };
  const TITLES={'glance':'At a glance — next steps and reviews','accuracy-scope':'Accuracy scope note'};
  const headline=(el,fallback)=>{const h=el&&el.querySelector('h1,h2,h3,summary');return ((h&&h.textContent)||fallback).replace(/\s+/g,' ').trim().slice(0,80);};
  // 1. Current task, stats and graph go directly under the header.
  let anchor=top;
  for(const id of ['active','stats-bar','graph-tools','graph-panel']){const el=byId(id);if(el){anchor.after(el);anchor=el;}}
  // 2. Fold long reference sections, keeping their original order after the graph.
  for(const id of ['glance','backlog','model-tracks','workflow-status','research-overview','accuracy-scope']){
    const el=byId(id); if(!el)continue;
    if(el.tagName==='DETAILS'){el.open=false;anchor.after(el);anchor=el;continue;}
    const box=fold([el],TITLES[id]||headline(el,id)); if(box){anchor.after(box);anchor=box;}
  }
  // 3. Fold the job table with its toolbar and header; show the row count in the title.
  const table=[...document.body.children].find(e=>e.tagName==='TABLE');  // The main job list, not tables inside sections.
  if(table){
    const parts=[document.querySelector('div.toolbar'),document.querySelector('div.section-header'),table,byId('rows-empty')];
    const rows=table.querySelectorAll('tbody tr').length;
    const box=fold(parts,`Job list (${rows} rows) — filter and inspect`); if(box){anchor.after(box);anchor=box;}
  }
  const style=document.createElement('style');
  style.textContent='details.tidy-fold{margin:8px 0;border:1px solid #30363d;border-radius:8px;padding:6px 10px}details.tidy-fold>summary{cursor:pointer;font-weight:600}';
  document.head.appendChild(style);
})();
}
