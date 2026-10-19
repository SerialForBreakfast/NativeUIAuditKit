const assert=require('node:assert/strict');
const {performance}=require('node:perf_hooks');
const G=require('./research_graph_view.js');
const cyto=require('./vendor/cytoscape-3.33.1/cytoscape.min.js');
const snapshot={current:'train',jobs:[
  {job:'capture',task:'A',state:'complete'},
  {job:'prepare',task:'A',state:'blocked',dependencies:[{job:'capture'},{job:'missing'}]},
  {job:'train',task:'A',state:'running',dependencies:[{job:'prepare'}]},
  {job:'score',task:'B',state:'pending',dependencies:[{job:'train'}]},
  {job:'report',task:'B',state:'pending',dependencies:[{job:'score'},{job:'train'}]}
]};
let p=G.project(snapshot,{campaign:'A'});
assert.equal(p.hidden,1);assert.equal(p.nodes.length,3);
assert(p.issues.some(i=>i.includes('missing')));
assert.equal(G.reach('prepare',p.graph.outgoing).size,3);
assert.equal(G.blockers(p.graph).find(b=>b.job.job==='prepare').impact,3);
p=G.project(snapshot,{focus:'prepare',history:true});assert.equal(p.nodes.length,6);
assert.equal(p.nodes.find(n=>n.data.id==='train').classes,'running');
assert.equal(G.project(snapshot,{limit:2}).nodes[0].data.id,'train');
assert(G.index({jobs:[{job:'a',dependencies:['b']},{job:'b',dependencies:['a']}]}).issues.some(i=>i.includes('cycle')));
assert(G.index({jobs:[{job:'a'},{job:'a'}]}).issues.some(i=>i.includes('duplicate')));
assert.equal(G.index({jobs:[{job:'<script>alert(1)</script>'}]}).jobs.size,1);
const cy=cyto({headless:true,elements:[...p.nodes,...p.edges]});
for(const name of ['breadthfirst','concentric']){cy.layout({name,animate:false}).run();assert(cy.nodes().every(n=>Number.isFinite(n.position('x'))));}
cy.destroy();
const large={jobs:Array.from({length:2500},(_,i)=>({job:'job'+i,task:'batch'+Math.floor(i/100),state:'pending',dependencies:i?[{job:'job'+(i-1)}]:[]}))};
const start=performance.now();p=G.project(large,{campaign:'batch20'});
assert(p.nodes.length<=180);assert(performance.now()-start<1000);
console.log('Graph projection and 2 layouts pass. 2500-job projection: '+(performance.now()-start).toFixed(1)+' ms.');
const batch={current:'train',jobs:[
 {job:'train',task:'training',state:'running'},
 {job:'score',task:'comparison',state:'blocked',readinessReasons:['dependency_incomplete:train'],dependencies:['train']},
 {job:'decision',task:'comparison',state:'blocked',readinessReasons:['dependency_incomplete:score'],dependencies:['score']},
 {job:'prior',task:'comparison',state:'complete'}
]};
let workflow=G.workflow(batch,'comparison');
assert.equal(workflow.counts.waiting,2);assert.equal(workflow.counts.history,1);
assert.equal(workflow.actions.length,0);assert.equal(workflow.running.job,'train');
batch.jobs[0].state='exhausted';batch.current=null;
workflow=G.workflow(batch,'comparison');
assert.equal(workflow.actions[0].job.job,'train');assert.equal(workflow.actions[0].impact,2);
assert.equal(workflow.counts['needs action'],2);
assert.equal(workflow.actions.length,1);
assert.equal(workflow.affectedJobs,3);
let capacity=G.workflow({jobs:[{job:'ready',task:'X',state:'ready',workflowDuration:{low:3,high:5,samples:2}},
 {job:'unknown',task:'X',state:'ready'}]},'X').capacity;
assert.equal(capacity.ready.low,null);assert.equal(capacity.ready.measured,1);
capacity=G.workflow({jobs:[{job:'ready',task:'X',state:'ready',workflowDuration:{low:3,high:5,samples:2}}]},'X').capacity;
assert.equal(capacity.ready.low,3);assert.equal(capacity.ready.high,5);
assert.equal(G.measuredETA({eta:{low:2,high:5,samples:3}}),'2–5 s remaining (3 measured runs)');
assert.equal(G.measuredETA({eta:{low:2,high:5,basis:'progress'}}),'2–5 s remaining (from worker progress)');
for(const eta of [null,{low:2,high:1,samples:3},{low:-1,high:5,samples:3},{low:2,high:5,samples:0},{low:NaN,high:5,samples:3}])
 assert.equal(G.measuredETA({eta}),'ETA unavailable');
assert.equal(G.workflow({jobs:[{job:'bad',task:'X',state:'blocked',readinessReasons:['approval_missing']}]},'X').counts['needs action'],1);
assert.equal(G.workflow({jobs:[{job:'a',task:'X',state:'pending',dependencies:['b']},{job:'b',task:'X',state:'pending',dependencies:['a']}]},'X').counts['needs action'],2);
assert.equal(G.workflow({jobs:[{job:'safe',task:'X',state:'pending',dependencies:['<img onerror=alert(1)>']}]},'X').actions.length,2);
console.log('Workflow waits, blockers, history, cycles, and measured ETA checks pass.');
const workflowStart=performance.now();
assert.equal(G.workflow(large,'batch20').counts.waiting,100);
assert(performance.now()-workflowStart<1000);
console.log('2500-job workflow projection: '+(performance.now()-workflowStart).toFixed(1)+' ms.');
assert.equal(G.isHistory({state:'drifted'}),false);
assert.equal(G.workflow({jobs:[{job:'changed',task:'X',state:'drifted'}]},'X').counts['needs action'],1);
const gated={jobs:[
 {job:'decision',task:'X',state:'complete'},
 {job:'branch',task:'X',state:'blocked',dependencies:['decision'],readinessReasons:['condition_not_met:decision:contradicted:no gain']},
 {job:'next',task:'X',state:'blocked',dependencies:['branch'],readinessReasons:['dependency_incomplete:branch']}
]};
assert.equal(G.workflow(gated,'X').counts['branch not selected'],2);
assert.equal(G.workflow(gated,'X').actions.length,0);
gated.jobs[1].readinessReasons=['condition_not_met:decision:inconclusive:not enough support'];
assert.equal(G.workflow(gated,'X').counts['needs action'],2);
gated.jobs[1].readinessReasons=['condition_not_met:decision:contradicted:no gain'];
gated.jobs[1].readinessReasons.push('approval_missing');
assert.equal(G.workflow(gated,'X').counts['needs action'],2);
assert.equal(G.workflow(gated,'X').actions.length,1);
assert.match(G.branchConditions({}),/not supplied/);
assert.match(G.branchConditions({conditions:[{job:'gate',output:'gate.json',outcome:'supported'}]}),/must report supported/);
assert.match(G.branchConditions({conditions:[{}]}),/Invalid/);
assert.equal(G.project({jobs:[{job:'gate',state:'complete'},{job:'child',state:'blocked',dependencies:['gate'],
 conditions:[{job:'gate',output:'gate.json',outcome:'supported'}]}]},{history:true}).edges[0].data.label,'requires supported');
assert.equal(G.workflow({jobs:[{job:'old',state:'failed',displayState:'superseded',task:'X'},
 {job:'child',state:'blocked',task:'X',dependencies:['old'],readinessReasons:['dependency_incomplete:old']}]},'X').counts['needs action'],1);

// Execute browser initialization, not only the exported projection functions.
// This catches references that exist in one closure but not the browser closure.
const vm=require('node:vm'), fs=require('node:fs');
class Element {
 constructor(){this.children=[];this.dataset={};this.style={};this.value='';this.hidden=true;this.textContent='';}
 append(...els){this.children.push(...els);if(!this.value&&els[0]?.value)this.value=els[0].value;}
 replaceChildren(...els){this.children=els;}
 setAttribute(){} after(...els){for(const el of els)if(el.id)elements.set(el.id,el);}
}
const elements=new Map();
const doc={hidden:false,getElementById:id=>{if(!elements.has(id))elements.set(id,new Element());return elements.get(id);},
 createElement:()=>new Element(),addEventListener:()=>{}};
const context={document:doc,data:{current:null,jobs:[{job:'done',task:'X',state:'complete'}]},
 description:j=>({test:j.job,answers:'Preserve successes',title:j.job}),show:()=>{},render:()=>{},busy:false,console};
vm.createContext(context);
vm.runInContext(fs.readFileSync(require.resolve('./research_graph_view.js'),'utf8'),context);
context.render();
assert.equal(elements.get('workflow-status').children.some(el=>el.textContent==='Experiment workflow'),true);
console.log('Browser initialization, branch conditions, source drift, and root blocker checks pass.');
