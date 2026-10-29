// Isolated headless rendering; the user's browser and foreground remain untouched.
const {chromium}=require('playwright');
const {pathToFileURL}=require('node:url');
const fs=require('node:fs');const path=require('node:path');const assert=require('node:assert/strict');
const base=path.resolve(__dirname,'..'),out=path.join(base,'share-with-chatgpt');
fs.mkdirSync(path.join(base,'runs'),{recursive:true});
(async()=>{
  const browser=await chromium.launch({headless:true,executablePath:process.env.CHROME_BIN||'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});
  try {
    const page=await browser.newPage({viewport:{width:1600,height:1100},deviceScaleFactor:1});
    const errors=[];page.on('pageerror',e=>errors.push(e.message));
    const url=pathToFileURL(path.join(base,'index.html')).href;
    await page.goto(url);await page.waitForFunction(()=>!!window.TrajectoryPlayer);
    const seek=async t=>{await page.evaluate(t=>window.TrajectoryPlayer.seek(t),t);await page.waitForTimeout(850);};
    const frames=JSON.parse(fs.readFileSync(path.join(out,'keyframes.json')));
    for(const f of frames){
      await seek(f.time);
      assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
      const counts=await page.evaluate(()=>({display:document.querySelectorAll('[data-node],[data-group].graph-node').length,expected:window.TrajectoryPlayer.getState().visibleCount}));
      assert.equal(counts.display,counts.expected,f.file);
      await page.screenshot({path:path.join(out,f.file),type:'jpeg',quality:90,fullPage:true});
    }
    // A single action is inspectable before the batch observation arrives.
    const first=await page.evaluate(()=>window.TrajectoryPlayer.events.find(e=>e.type==='tool'));
    await seek(first.start+.01);
    await page.getByRole('button',{name:'查看 action a2.1',exact:true}).click();
    assert((await page.locator('#action-code').textContent()).includes('keystrokes'));
    assert.equal(await page.locator('[data-type="observation"]').count(),0);
    await page.locator('#node-relations summary').click();
    assert((await page.locator('#node-relations-body').textContent()).includes('PLANS_ACTION'));
    await page.screenshot({path:path.join(base,'runs','action-inspection.png'),fullPage:true});
    // All 56 original nodes and their contents survive both levels of unfolding.
    await seek(await page.evaluate(()=>window.TrajectoryPlayer.total));
    for(const id of ['classification','env','extract','pdf','jpg'])await page.locator(`[data-toggle-group="${id}"]`).click();
    await page.waitForTimeout(900);
    assert.equal(await page.locator('[data-node]').count(),56);
    const graph=await page.evaluate(()=>window.TrajectoryPlayer.dataset);
    const obs=graph.nodes.find(n=>n.type==='observation'&&n.stepId===7);
    await page.locator(`[data-node="${obs.id}"]`).click();
    assert.deepEqual(JSON.parse(await page.locator('#action-code').textContent()),obs.content);
    assert((await page.locator('#node-relations-body').textContent()).includes('ATTEMPTS_REPAIR'));
    // A short real-time run creates nodes and can be paused mid-animation.
    await seek(0);await page.locator('#speed').selectOption('3');await page.locator('#play').click();
    await page.waitForTimeout(1800);await page.locator('#play').click();
    assert.equal(await page.evaluate(()=>window.TrajectoryPlayer.getState().playing),false);
    assert((await page.locator('[data-node]').count())>=2);
    await page.setViewportSize({width:390,height:844});
    await seek(frames.find(f=>f.file==='01-growth.jpg').time);
    assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
    assert(await page.evaluate(()=>{
      const id=window.TrajectoryPlayer.getState().event.nodeId;
      const node=document.querySelector(`[data-node="${id}"]`).getBoundingClientRect();
      const viewport=document.getElementById('graph-viewport').getBoundingClientRect();
      return node.top>=viewport.top&&node.bottom<=viewport.bottom;
    }),'The current node should remain visible after the mobile layout settles');
    await page.screenshot({path:path.join(base,'runs','mobile.png'),fullPage:true});
    // Exported HTML works on its own, without loading source modules.
    await page.setViewportSize({width:1600,height:1100});
    await page.goto(pathToFileURL(path.join(out,'animation-standalone.html')).href);
    await page.waitForFunction(()=>!!window.TrajectoryPlayer);
    await seek(frames.find(f=>f.file==='06-higher-summary.jpg').time);
    assert.equal(await page.locator('[data-group="classification"].graph-node').count(),1);
    assert.deepEqual(errors,[]);
    // Generate the preview as a rendered page of screenshots, not a synthetic graphic.
    await page.setContent(`<html><body style="margin:0;background:#f7f8fa;font:16px sans-serif;padding:24px"><h2>三类节点：出现、归并、继续执行</h2><main style="display:grid;grid-template-columns:1fr 1fr;gap:18px">${frames.filter((_,i)=>[1,2,3,6].includes(i)).map(f=>`<section><p>${f.title}</p><img style="width:100%;border-radius:10px" src="${pathToFileURL(path.join(out,f.file)).href}"></section>`).join('')}</main></body></html>`);
    await page.locator('img').evaluateAll(images=>Promise.all(images.map(i=>i.decode())));
    await page.screenshot({path:path.join(out,'process-preview.jpg'),type:'jpeg',quality:90,fullPage:true});
    console.log('PASS: desktop/mobile, node content, typed edges, both collapse levels, playback, standalone HTML and nine keyframes.');
  } finally {await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
