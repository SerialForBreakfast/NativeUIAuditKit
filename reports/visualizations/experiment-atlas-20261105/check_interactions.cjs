const {createRequire}=require('node:module');
// Optional: set NUIAK_NODE_RUNTIME_PACKAGE to a package.json that provides playwright; otherwise normal Node lookup.
const req=process.env.NUIAK_NODE_RUNTIME_PACKAGE?createRequire(process.env.NUIAK_NODE_RUNTIME_PACKAGE):require;
const {chromium}=req('playwright');const fs=require('node:fs');const path=require('node:path');const assert=require('node:assert/strict');const root=__dirname;
(async()=>{
 const browser=await chromium.launchPersistentContext(path.join(root,'.browser-profile'),{headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',viewport:{width:1060,height:1550},args:['--no-first-run','--disk-cache-dir='+path.join(root,'.browser-cache')],env:{...process.env,TMPDIR:path.join(root,'.browser-tmp')}});
 const checks=[],errors=[];
 try{
  const page=browser.pages()[0];page.on('pageerror',e=>errors.push(e.message));await page.goto('file://'+path.join(root,'preview.html'));
  const f=page.frames().find(f=>f.parentFrame());await f.waitForSelector('#nuiak-atlas[data-ready="true"]');
  const diag=()=>f.evaluate(()=>document.getElementById('nuiak-atlas').atlasDiagnostics());
  const set=(k,v)=>f.locator('[data-control="'+k+'"]').selectOption(v);
  assert.equal((await diag()).totalJobs,4757);checks.push('Full snapshot count');
  for(const view of ['dependencies','lanes','outcomes','timeline']){
   await f.locator('[data-view="'+view+'"]').click();assert.equal((await diag()).state.view,view);assert.ok(await f.locator('#atlas-panel').isVisible());
   assert.equal(await f.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);checks.push('View '+view);if(view==='timeline'){assert.equal((await diag()).timelineLocked,true);checks.push('Timeline dates cannot be moved by dragging');}
   await page.screenshot({path:path.join(root,'view-'+view+'.png'),fullPage:true});
  }
  await f.locator('[data-view="dependencies"]').click();
  await set('scope','latest');assert.equal((await diag()).nodes,2);checks.push('Latest experiment scope');
  await set('inspect','B405-277');assert.match(await f.locator('[data-role="detail"]').innerText(),/12 aligned review-only frames/);checks.push('Native evidence is review-only');
  await f.locator('[data-action="jobs"]').click();assert.equal((await diag()).nodes,8);assert.equal((await diag()).state.scope,'members');checks.push('Experiment drill-down binds 8 member jobs');
  await set('scope','latest');assert.equal((await diag()).nodes,15);checks.push('Latest batch contains 15 jobs');
  await set('inspect','ios575-loss-summary');assert.match(await f.locator('[data-role="detail"]').innerText(),/missed/);checks.push('iOS recorded cause counts');
  await f.locator('[data-action="path"]').click();assert.ok((await diag()).nodes>=7);checks.push('Path tracing includes upstream reuse');
  await f.locator('[data-action="path"]').click();await set('scope','all');assert.equal((await diag()).nodes,4757);checks.push('Every execution job remains inspectable');
  await set('color','execution');assert.match(await f.locator('[data-role="legend"]').innerText(),/Running/);checks.push('Execution color is independent from outcomes');
  await set('model','Optional HCF');assert.ok((await diag()).nodes>0);checks.push('Independent HCF filter');
  await set('level','experiments');await set('scope','recent');await set('model','all');await set('color','outcome');
  await set('inspect','HCF574');assert.match(await f.locator('[data-role="detail"]').innerText(),/16 to 14/);checks.push('HCF rejection is visible');
  await set('scope','open');assert.ok((await diag()).nodes>0);checks.push('Open paths contain recorded blockers');
  await set('scope','recent');
  await page.emulateMedia({colorScheme:'dark'});await page.waitForTimeout(200);await page.screenshot({path:path.join(root,'preview-dark.png'),fullPage:true});checks.push('Dark theme');
  await page.setViewportSize({width:360,height:1700});await page.waitForTimeout(200);
  assert.equal(await f.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);checks.push('360 px layout has no overflow');
  await page.screenshot({path:path.join(root,'preview-mobile.png'),fullPage:true});
  await page.setViewportSize({width:320,height:1700});await page.waitForTimeout(200);assert.equal(await f.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);checks.push('320 px layout has no overflow');
  assert.deepEqual(errors,[]);checks.push('No browser runtime errors');
  const report={checks,passed:checks.length,errors,verifiedAt:new Date().toISOString()};fs.writeFileSync(path.join(root,'interaction-checks.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));
 }finally{await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1;});
