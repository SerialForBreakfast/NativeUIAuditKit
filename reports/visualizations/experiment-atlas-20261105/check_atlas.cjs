const { createRequire } = require('node:module');
// Optional: set NUIAK_NODE_RUNTIME_PACKAGE to a package.json that provides playwright; otherwise normal Node lookup.
const requireBundled=process.env.NUIAK_NODE_RUNTIME_PACKAGE?createRequire(process.env.NUIAK_NODE_RUNTIME_PACKAGE):require;
const {chromium}=requireBundled('playwright');
const fs=require('node:fs');const path=require('node:path');const root=__dirname;
(async()=>{
 const errors=[];const browser=await chromium.launchPersistentContext(path.join(root,'.browser-profile'),{headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',viewport:{width:1100,height:1500},args:['--no-first-run','--disk-cache-dir='+path.join(root,'.browser-cache')],env:{...process.env,TMPDIR:path.join(root,'.browser-tmp')}});
 try{
  const page=browser.pages()[0];page.on('pageerror',e=>errors.push(e.message));
  await page.goto('file://'+path.join(root,'preview.html'));
  const frame=page.frames().find(f=>f.parentFrame());
  await page.waitForTimeout(1500);console.log('FRAME DEBUG',page.frames().map(f=>f.url()),'ERRORS',errors);console.log('INNER',await frame.evaluate(()=>({length:document.documentElement.outerHTML.length,body:document.body.innerText.slice(-900),scripts:[...document.scripts].map(s=>s.type)})));
  await frame.waitForSelector('#nuiak-atlas[data-ready="true"],#nuiak-atlas[data-error]',{timeout:3000});
  console.log(JSON.stringify(await frame.evaluate(()=>({data:document.querySelector('#nuiak-atlas').dataset,diagnostics:document.querySelector('#nuiak-atlas').atlasDiagnostics?.(),overflow:document.documentElement.scrollWidth>innerWidth})),null,2));
  console.log('Errors:',errors);
  await page.screenshot({path:path.join(root,'preview-desktop.png'),fullPage:true});
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
