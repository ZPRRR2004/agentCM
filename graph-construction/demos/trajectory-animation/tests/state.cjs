#!/usr/bin/env node
'use strict';

// State and SVG structure regression checks. No browser or package install needed.
// This DOM stub deliberately does not test actual layout, fonts, or interaction focus.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const crypto = require('node:crypto');
const base = path.resolve(__dirname, '..');

function playerFixture(reducedMotion = false, width = 900) {
  const elements = new Map();
  let nextFrame;
  function element(id) {
    if (!elements.has(id)) elements.set(id, {
      id, style: {}, dataset: {}, listeners: {}, classList: { toggle() {} },
      clientWidth: width, innerHTML: '', hidden: false,
      addEventListener(name, handler) { this.listeners[name] = handler; },
      setAttribute(name, value) { this[name] = value; },
      getAttribute(name) { return this[name]; },
      contains() { return false; }, querySelector() { return null; },
    });
    return elements.get(id);
  }
  const context = vm.createContext({
    window: {},
    document: {
      getElementById: element, querySelectorAll() { return []; }, activeElement: null,
      createElement() {
        return { getContext() { return { measureText(text) { return { width: text.length * 7 }; } }; } };
      },
    },
    matchMedia: () => ({ matches: reducedMotion }),
    ResizeObserver: class { observe() {} },
    requestAnimationFrame: callback => { nextFrame = callback; },
    performance: { now: () => 0 },
  });
  for (const filename of ['data.js', 'app.js']) {
    vm.runInContext(fs.readFileSync(path.join(base, filename), 'utf8'), context, { filename });
  }
  const player = context.window.TrajectoryPlayer;
  function render() {
    nextFrame(1);
    const html = element('graph').innerHTML;
    assert(!/\b(?:NaN|undefined)\b/.test(html), 'SVG contains invalid coordinates or values');
    return html;
  }
  function snapshot() {
    const html = render();
    const edges = [...html.matchAll(/data-dependency="([^"]+)" data-evidence-count="(\d+)"/g)]
      .map(match => ({ key: match[1].replace(/&gt;/g, '>'), count: Number(match[2]) }));
    const atomicCount = [...html.matchAll(/data-node="[^"]+"/g)].length;
    const summaryCount = [...html.matchAll(/data-group="[^"]+"/g)].length;
    return { state: player.getState(), html, edges, atomicCount, summaryCount, nodeCount: atomicCount + summaryCount };
  }
  function toggle(id) {
    const controls = element('group-controls').innerHTML;
    assert(controls.includes(`data-toggle-group="${id}"`), `Missing available toggle ${id}`);
    element('group-controls').listeners.click({ target: { closest: () => ({ dataset: { toggleGroup: id } }) } });
    return snapshot();
  }
  return { player, element, snapshot, toggle };
}

const fixture = playerFixture();
const { player } = fixture;
const D=player.dataset;
assert.equal(player.events.length, 63);
assert.equal(D.steps.length, 14);
assert.equal(D.nodes.length, 56);
assert.equal(D.structuralEdges.length, 28);
assert.deepEqual(JSON.parse(JSON.stringify(D.meta.nodeCounts)),{reasoning:14,action:28,observation:14});
const rawSource = fs.readFileSync(path.resolve(base, D.meta.source));
assert.equal(crypto.createHash('sha256').update(rawSource).digest('hex'), D.meta.sourceSha256);
const allKeys=new Set(D.nodes.map(n=>n.id));
for(const edge of [...D.dependencies,...D.structuralEdges]){
  assert(allKeys.has(edge.source)&&allKeys.has(edge.target));
  assert.notEqual(edge.source,edge.target);
}
// Every phase reveals just the recorded node for that phase, including before feedback.
for(const event of player.events){
  player.seek(event.start+(['compress','merge'].includes(event.type)?event.duration*.8:.01));
  const frame=fixture.snapshot(),state=frame.state;
  assert.equal(frame.nodeCount,state.visibleCount,`count at ${event.index} ${event.type}`);
  for(const match of frame.html.matchAll(/data-node="([^"]+)"/g)) assert(state.nodeIds.has(match[1]),'Future node leaked');
  for(const edge of player.projectEdges())for(const original of edge.members){
    assert(state.nodeIds.has(original.source)&&state.nodeIds.has(original.target));
  }
}
const firstTool=player.events.find(e=>e.type==='tool');
player.seek(firstTool.start+.01);
assert.equal(player.getState().nodeIds.size,2);
assert.equal(player.getState().nodeCounts.observation,0);
const firstObservation=player.events.find(e=>e.type==='observe');
player.seek(firstObservation.start+.01);
assert.equal(player.getState().nodeIds.size,5); // reasoning + 3 actions + shared observation
let frame=fixture.snapshot();
assert.equal(frame.edges.reduce((sum,e)=>sum+e.count,0),6); // 3 planned actions + 3 feedback links
const shared=D.structuralEdges.filter(e=>e.target===firstObservation.nodeId);
assert.equal(shared.length,3);
assert(shared.every(e=>e.kind==='batch_feedback'&&e.actionIds.length===3));
// Inspecting one node cannot expose the event's later feedback.
player.seek(firstTool.start+.01);
fixture.element('graph').listeners.click({target:{closest:()=>({dataset:{node:firstTool.nodeId}})}});
assert(fixture.element('evidence-body').innerHTML.includes('tool_calls[0]'));
assert(!fixture.element('evidence-body').innerHTML.includes('New Terminal Output'));

const merge=player.events.find(e=>e.type==='merge');
player.seek(merge.start-.001);
assert.equal(fixture.snapshot().nodeCount,4);
player.seekEvent(merge.index);
frame=fixture.snapshot();
assert.equal(frame.nodeCount,3);
assert(!frame.state.arrived.has(13));
assert(!frame.html.includes('data-box="pdf"'));
assert.equal(fixture.element('result-records').hidden,false);
// Incoming and outgoing semantic projections keep all original node bindings.
player.seek(player.total);
frame=fixture.snapshot();
assert.equal(frame.nodeCount,15); // 3 summaries + 12 typed nodes from output and final checks
const collapsed=player.projectEdges();
assert(collapsed.some(e=>e.source==='group:classification'));
assert(collapsed.every(e=>e.members.every(m=>m.source!==m.target)));
frame=fixture.toggle('classification');assert.equal(frame.nodeCount,16);
for(const id of ['env','extract','pdf','jpg'])frame=fixture.toggle(id);
assert.equal(frame.nodeCount,56);
assert.equal(frame.summaryCount,0);
assert.equal(frame.edges.reduce((sum,e)=>sum+e.count,0),D.dependencies.length+D.structuralEdges.length);
assert.deepEqual(new Set(player.projectEdges().flatMap(e=>e.members.map(m=>m.id))),new Set([...D.dependencies,...D.structuralEdges].map(e=>e.id)));
// Re-folding then expanding restores the same node IDs, edges and role order.
fixture.toggle('classification');frame=fixture.toggle('classification');assert.equal(frame.nodeCount,56);
for(const fraction of [.01,.25,.4,.65]){
  player.seek(merge.start+merge.duration*fraction);fixture.snapshot();
  fixture.toggle('classification');fixture.toggle('pdf');fixture.toggle('classification');frame=fixture.toggle('classification');
  assert.equal(frame.nodeCount,12); // env + extract + 9 PDF nodes + JPG summary
}
player.seek(player.events.find(e=>e.type==='plan'&&e.stepId===9).start+.01);
assert.equal(fixture.snapshot().state.merged.size,0);
assert.equal(fixture.element('result-records').hidden,true);
player.seek(0);assert.equal(fixture.snapshot().nodeCount,0);
for(const [reduced,width] of [[false,390],[false,640],[true,900]]){
  const other=playerFixture(reduced,width);
  for(const event of other.player.events){other.player.seek(event.start+(['compress','merge'].includes(event.type)?event.duration*.8:.01));other.snapshot();}
  other.player.seek(other.player.total);assert.equal(other.snapshot().nodeCount,15);
}
console.log(`PASS: 63 phases; 56 typed nodes; ${D.dependencies.length} semantic assertions; 28 feedback links; collapse, restore, temporal visibility and narrow geometry.`);
