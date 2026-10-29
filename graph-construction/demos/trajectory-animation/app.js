/* Editable playback timing in seconds. Evidence and storyboard live in data.js. */
(() => {
  'use strict';
  const TIMING = { start: 2.3, plan: 1.3, tool: 1.15, observe: 1.8, compress: 3.3, merge: 5.0, finish: 3.0 };
  const D = window.TRAJECTORY_DEMO;
  if (!D) { document.getElementById('event-description').textContent = '数据未加载，请先运行 build_data.py 生成 data.js。'; return; }
  const $ = id => document.getElementById(id);
  const steps = new Map(D.steps.map(s => [s.id, s]));
  const higherGroups = D.higherGroups || [];
  const groups = new Map([...D.groups,...higherGroups].map(g => [g.id, g]));
  const nodes = new Map(D.nodes.map(n => [n.id, n]));
  const definitions = new Map(D.predicateDefinitions.map(p => [p.name, p]));
  const edges = [...D.structuralEdges, ...D.dependencies];
  const NODE_STYLE = {
    reasoning:{fill:'#f5effb',stroke:'#bca5d2',ink:'#80629a',rx:12},
    action:{fill:'#edf6f1',stroke:'#9cbbaf',ink:'#2e7061',rx:4},
    observation:{fill:'#eef4fc',stroke:'#9fb9d7',ink:'#426e99',rx:9},
  };
  const events = [];
  let total = 0, actionNumber = 0;
  function append(type, fields = {}) { const duration = TIMING[type]; events.push({type, start:total, end:total+duration, duration, index:events.length, ...fields}); total += duration; }
  append('start');
  D.steps.forEach(step => {
    const members=step.nodeIds.map(id=>nodes.get(id));
    const reasoning=members.find(n=>n.type==='reasoning');
    if(reasoning)append('plan',{stepId:step.id,groupId:step.groupId,nodeId:reasoning.id});
    step.toolCalls.forEach((tool, toolIndex) => append('tool', {stepId:step.id, groupId:step.groupId,
      toolIndex, tool, nodeId:members.find(n=>n.type==='action'&&n.index===toolIndex).id, actionNumber:++actionNumber}));
    members.filter(n=>n.type==='observation').forEach(n=>append('observe',{stepId:step.id,groupId:step.groupId,nodeId:n.id}));
    D.compressions.filter(c => c.afterStep === step.id).forEach(c => append('compress', {groupId:c.groupId, stepId:step.id, label:c.label}));
    (D.merges||[]).filter(c=>c.afterStep===step.id).forEach(c=>append('merge',{groupId:c.groupId,stepId:step.id,label:c.label}));
  });
  append('finish');
  const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
  let time = 0, playing = false, speed = 1, lastFrame = 0, dirty = true, settling = 0;
  let selectedNode = null, selectedGroup = null, lastDescriptionKey = '', manualOpen = new Set();
  let width = 900, height = 510, lastEventIndex = -1;
  const positions = new Map();
  const mergeOrigins = new Map();
  const clamp = (n, lo = 0, hi = 1) => Math.max(lo, Math.min(hi, n));
  const mix = (a, b, t) => a + (b - a) * t;
  const ease = t => { t = clamp(t); return t * t * (3 - 2 * t); };
  const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const fmt = seconds => `${String(Math.floor(seconds / 60)).padStart(2,'0')}:${String(Math.floor(seconds % 60)).padStart(2,'0')}`;
  const short = (text, max) => text.length > max ? text.slice(0, max-1) + '…' : text;
  const textCanvas = document.createElement('canvas').getContext('2d');
  function wrap(text, limit, fontSize = 11) {
    textCanvas.font = `${fontSize}px -apple-system, BlinkMacSystemFont, sans-serif`;
    const lines = []; let line = '';
    const tokens=text.match(/[A-Za-z0-9_/.]+|./gu)||[];
    for (const token of tokens) {
      if(textCanvas.measureText(line+token).width>limit&&line&&!/^[。，；、]$/.test(token)){lines.push(line);line=token;}
      else line+=token;
    }
    if (line) lines.push(line); return lines;
  }
  function svgText(text, x, y, size = 11, fill = '#536178', extra = '') { return `<text class="graph-text" x="${x}" y="${y}" font-size="${size}" fill="${fill}" ${extra}>${esc(text)}</text>`; }
  function eventAt(t) { if (t <= 0) return null; return events.find(e => t < e.end) || events.at(-1); }
  function stateAt(t) {
    const state = {started:t>0, arrived:new Set(), nodeIds:new Set(), completed:new Set(), calls:new Map(), compressed:new Set(), folds:new Map(), merged:new Set(), mergeProgress:new Map(), event:eventAt(t), toolCount:0};
    for (const e of events) {
      if (t <= e.start) break;
      if (e.nodeId) { state.arrived.add(e.stepId); state.nodeIds.add(e.nodeId); }
      if (e.type === 'tool') { state.calls.set(e.stepId, e.toolIndex+1); state.toolCount++; }
      if (e.type === 'compress') { state.compressed.add(e.groupId); state.folds.set(e.groupId, reduced ? 1 : ease((t-e.start)/(e.duration*.62))); }
      if(e.type==='merge'){state.merged.add(e.groupId);state.mergeProgress.set(e.groupId,reduced?1:ease((t-e.start)/(e.duration*.72)));}
    }
    for(const step of D.steps)if(step.nodeIds.length&&step.nodeIds.every(id=>state.nodeIds.has(id)))state.completed.add(step.id);
    for(const g of manualOpen){if(state.merged.has(g))state.mergeProgress.set(g,0);else state.folds.set(g,0);}
    state.baseGroups=D.groups.filter(g=>g.stepIds.some(id=>state.arrived.has(id)));
    state.visibleGroups=[...state.baseGroups];
    for(const parent of higherGroups){
      if(!(state.mergeProgress.get(parent.id)>0))continue;
      const first=state.visibleGroups.findIndex(g=>parent.memberGroupIds.includes(g.id));
      state.visibleGroups=state.visibleGroups.filter(g=>!parent.memberGroupIds.includes(g.id));
      state.visibleGroups.splice(first,0,parent);
    }
    state.visibleCount=new Set([...state.nodeIds].map(id=>representative(id,state).key)).size;
    state.nodeCounts=Object.fromEntries(Object.keys(NODE_STYLE).map(type=>[type,[...state.nodeIds].filter(id=>nodes.get(id).type===type).length]));
    return state;
  }
  function representative(nodeId,state){
    const leafId=nodes.get(nodeId).groupId;
    const parent=higherGroups.find(g=>g.memberGroupIds.includes(leafId)&&(state.mergeProgress.get(g.id)||0)>.5);
    const owner=parent?.id||leafId;
    return {owner,key:parent||(state.folds.get(leafId)||0)>.5?`group:${owner}`:nodeId};
  }
  function projectEdges(state){
    const projected=new Map();
    edges.forEach(edge=>{
      if(!state.nodeIds.has(edge.source)||!state.nodeIds.has(edge.target))return;
      const a=representative(edge.source,state),b=representative(edge.target,state);
      if(a.key===b.key)return;
      const family=edge.kind==='semantic'?'semantic':'structural';
      const key=`${family}:${a.key}>${b.key}`;
      if(!projected.has(key))projected.set(key,{key,source:a.key,target:b.key,sg:a.owner,tg:b.owner,family,members:[]});
      projected.get(key).members.push(edge);
    });
    return [...projected.values()];
  }
  function seek(t, resetInspection = true) {
    time = clamp(Number(t) || 0, 0, total);
    mergeOrigins.clear();
    if (resetInspection) { selectedNode = null; selectedGroup = null; manualOpen.clear(); }
    dirty = true; settling = reduced ? 1 : 45;
    if (time >= total) playing = false;
    refreshUI(stateAt(time));
  }
  function pause() { playing = false; dirty = true; refreshUI(stateAt(time)); }
  function play() { if (time >= total) seek(0); manualOpen.clear(); selectedNode = null; selectedGroup = null; playing = true; lastFrame = performance.now(); dirty = true; refreshUI(stateAt(time)); }
  function seekEvent(index) {
    pause();
    const event=events[Math.min(index,events.length-1)];
    seek(index<0?0:event.start+(['compress','merge'].includes(event.type)?event.duration*.8:.002));
  }
  function inspectionButtons(state) {
    $('inspect-section').hidden = !state.started;
    const key = [...state.compressed].join(',') + '|' + [...state.merged].join(',') + '|' + [...manualOpen].join(',');
    if ($('group-controls').dataset.key === key) return;
    $('group-controls').dataset.key = key;
    const hidden=new Set(higherGroups.filter(g=>state.merged.has(g.id)&&!manualOpen.has(g.id)).flatMap(g=>g.memberGroupIds));
    const order=[...state.merged,...state.compressed].filter(id=>!hidden.has(id));
    $('group-controls').innerHTML=order.map(id=>{const high=groups.get(id).memberGroupIds;return `<div class="group-control ${high?'higher-control':''}"><span>${esc(groups.get(id).title)}</span><button type="button" data-toggle-group="${esc(id)}">${high?(manualOpen.has(id)?'恢复合并':'展开两子图'):(manualOpen.has(id)?'恢复压缩':'展开子图')}</button></div>`;}).join('');
  }
  function signature(edge){
    if(edge.kind==='semantic'){
      const parameters=definitions.get(edge.predicate).parameters;
      return `${edge.predicate}(${edge.arguments.map((id,i)=>`${parameters[i].name}: ${nodes.get(id).label}`).join(', ')})`;
    }
    return edge.kind==='returns'?`returns(${nodes.get(edge.source).label}, ${nodes.get(edge.target).label})`
      :`batch_feedback([${edge.actionIds.map(id=>nodes.get(id).label).join(', ')}], ${nodes.get(edge.target).label})`;
  }
  function describe(state) {
    const e=state.event;
    let group=selectedGroup?groups.get(selectedGroup):null;
    let node=selectedNode?nodes.get(selectedNode):e?.nodeId?nodes.get(e.nodeId):null;
    let type='预期成果演示',title='让轨迹开始生长',description='reasoning、action、observation 分别出现，再逐步归并为子图。';
    if(group)node=null;
    if(!selectedNode&&!selectedGroup&&['compress','merge'].includes(e?.type)){group=groups.get(e.groupId);node=null;}
    if(node){
      const step=steps.get(node.stepId);
      type=`${node.type.toUpperCase()} · ${node.label}`;title=step.label;
      description=node.type==='reasoning'?'这段 agent 文本单独保存为 reasoning 节点。'
        :node.type==='action'?`第 ${node.index+1} 次调用：${node.content.tool_name}。工具名和参数保存在这个 action 中。`
        :step.toolCalls.length>1?`本轮 ${step.toolCalls.length} 次调用的整块反馈，保存在一个 observation 中。`:step.result;
    }
    if(group){type=group.memberGroupIds?'LEVEL 2 · 高层归并':'SUBGRAPH · 子图摘要';title=group.title;
      description=group.memberGroupIds?`两个子图收拢为一个阶段摘要。里面的 ${group.nodeIds.length} 个原始节点和谓词参数绑定继续保存。`
        :`${group.nodeIds.length} 个 reasoning、action、observation 节点收拢为一个摘要。展开后可以逐个查看。`;}
    if(e?.type==='start'&&!node&&!group){type='任务开始';title='整理 17 份文档';description=D.meta.task;}
    if(e?.type==='finish'&&!node&&!group){type='演示完成';title='图已生长完成';description='17 份文件已归档，10 份发票已汇总。三类节点经过子图压缩和高层归并，对外的谓词连接继续保留。';}
    $('event-type').textContent=type; $('event-title').textContent=title; $('event-description').textContent=description;
    $('event-type').style.color=node?NODE_STYLE[node.type].ink:group?'var(--purple)':'var(--blue)';
    $('action-box').hidden=!node; $('action-label').textContent=node?`${node.type} · 原始内容`:'';
    $('action-code').textContent=node?(typeof node.content==='string'?node.content:JSON.stringify(node.content,null,2)):'';
    $('compression-box').hidden=!group;
    $('retained-list').innerHTML=group?group.retained.map(x=>`<li>${esc(x)}</li>`).join(''):'';
    $('result-records').hidden=!group?.records;
    if(group?.records){
      $('result-records-body').innerHTML=`<table class="records-table"><thead><tr><th>发票文件</th><th>总额</th><th>VAT</th></tr></thead><tbody>${group.records.invoices.map(r=>`<tr><td>${esc(r.filename)}<small>证据 s${r.evidenceStepId}</small></td><td>${esc(r.total_amount)}</td><td>${esc(r.vat_amount)}</td></tr>`).join('')}</tbody></table><div class="records-other">其他文档（${group.records.other.length}）</div><ul class="records-files">${group.records.other.map(r=>`<li>${esc(r.filename)} <small>s${r.evidenceStepId}</small></li>`).join('')}</ul>`;
    }
    const ids=group?new Set(group.nodeIds):new Set(node?[node.id]:[]);
    const related=edges.filter(edge=>state.nodeIds.has(edge.source)&&state.nodeIds.has(edge.target)&&(ids.has(edge.source)||ids.has(edge.target)));
    const unique=new Map(related.map(edge=>[signature(edge),edge]));
    $('node-relations').hidden=!unique.size;
    $('node-relations-body').innerHTML=[...unique.values()].map(edge=>`<div class="relation-card"><code>${esc(signature(edge))}</code><small>${edge.kind==='semantic'?'人工标注的谓词':'调用与反馈的对应'}</small><p>${esc(edge.evidence)}</p></div>`).join('');
    $('evidence-details').hidden=!node;
    if(node)$('evidence-body').innerHTML=`<h3>${esc(node.id)}</h3><p>来源：step ${node.stepId} · ${esc(node.source.field)}</p><pre>${esc(JSON.stringify(node,null,2))}</pre>`;
  }
  function refreshUI(state) {
    const e=state.event; const finished=time>=total;
    $('play').textContent=playing?'Ⅱ 暂停':finished?'▶ 再播一次':time===0?'▶ 从零播放':'▶ 继续播放';
    $('live-dot').classList.toggle('playing',playing);
    $('mode-label').textContent=finished?'轨迹完成':playing?'执行中':time>0?'已暂停':'准备开始';
    $('event-number').textContent=`${String(e?e.index+1:0).padStart(2,'0')} / ${events.length}`;
    $('empty-state').hidden=state.started;
    $('visible-count').textContent=state.visibleCount; $('original-count').textContent=state.nodeIds.size;
    $('stat-bar').style.width=`${state.nodeIds.size?state.visibleCount/state.nodeIds.size*100:0}%`;
    $('stat-note').textContent=`已出现 ${state.nodeCounts.reasoning} 个 reasoning、${state.nodeCounts.action} 个 action、${state.nodeCounts.observation} 个 observation。${state.compressed.size?`已压缩 ${state.compressed.size} 个子图。`:''}`;
    $('player-status').textContent=e?`${e.type==='merge'?'二级压缩':e.type==='compress'?'子图压缩':e.type==='tool'?'工具调用':e.type==='observe'?'接收反馈':e.type==='finish'?'完成':'主 Agent 执行'} · ${state.toolCount} / ${D.meta.toolCallCount} actions`:'准备好开始';
    $('elapsed').textContent=fmt(time); $('duration').textContent=fmt(total); $('timeline').value=time;
    $('previous').disabled=time===0; $('next').disabled=finished;
    $('graph-caption').textContent=e?.type==='merge'?'两份子图摘要 → 一个阶段摘要 → 保留对外依赖':e?.type==='compress'?'收拢三类节点 → 形成摘要 → 对外连接保留':state.merged.size?'可逐层展开：阶段摘要 → PDF / JPG 子图 → 三类节点。':state.compressed.size?'点击节点查看证据；已压缩子图可在右侧展开。':'每个 event 中，reasoning、action、observation 分别出现。';
    document.querySelectorAll('.chapter-button').forEach(b=>b.classList.toggle('active',b.dataset.group===(e?.groupId||'')));
    inspectionButtons(state);
    const key=`${e?.index}|${selectedNode}|${selectedGroup}|${state.nodeIds.size}`;
    if(key!==lastDescriptionKey){describe(state);lastDescriptionKey=key;}
  }
  function interpolate(id,target,origin){
    let current=positions.get(id);
    if(!current){current={x:origin?.x??target.x,y:origin?.y??target.y,w:target.w,h:target.h,opacity:reduced?1:0};positions.set(id,current);}
    const k=reduced?1:.2;
    for(const key of ['x','y','w','h','opacity'])current[key]=mix(current[key]??target[key],target[key]??1,k);
    return current;
  }
  function draw(state) {
    const stage=$('graph-stage'); width=stage.clientWidth;
    const pad=26,gap=32,cols=width<620?1:width<1140?2:3;
    const cell=(width-pad*2-gap*(cols-1))/cols;
    const boxes=new Map(),nodePositions=new Map();
    function rawLayout(group){
      let y=40;const entries=[],headers=[];
      for(const sid of group.stepIds.filter(id=>state.arrived.has(id))){
        headers.push({sid,y:y+12});y+=20;
        const ns=steps.get(sid).nodeIds.map(id=>nodes.get(id)).filter(n=>state.nodeIds.has(n.id));
        const reasoning=ns.find(n=>n.type==='reasoning'),actions=ns.filter(n=>n.type==='action'),observations=ns.filter(n=>n.type==='observation');
        if(reasoning){entries.push({id:reasoning.id,x:14,y,w:cell-28,h:34});y+=42;}
        const half=(cell-44)/2;
        actions.forEach((n,i)=>entries.push({id:n.id,x:14,y:y+i*42,w:half,h:34}));
        observations.forEach((n,i)=>entries.push({id:n.id,x:30+half,y:y+i*42+Math.max(0,(actions.length-observations.length)*21),w:half,h:34}));
        y+=Math.max(actions.length,observations.length)*42+10;
      }
      return {entries,headers,height:y+10};
    }
    const rawLayouts=new Map(D.groups.map(g=>[g.id,rawLayout(g)]));
    function layout(items){
      const result=new Map();let y=172;
      for(let row=0;row<Math.ceil(items.length/cols);row++){
        let maxH=0;
        for(let col=0;col<cols;col++){
          const g=items[row*cols+col];if(!g)continue;
          const high=!!g.memberGroupIds,fold=high?1:state.folds.get(g.id)||0;
          const h=high?148:mix(rawLayouts.get(g.id).height,118,fold);maxH=Math.max(maxH,h);
          result.set(g.id,{x:pad+col*(cell+gap),y,w:cell,h,opacity:1,g,fold,row});
        }
        y+=maxH+50;
      }
      return {items:result,bottom:y-20};
    }
    const targetLayout=layout(state.visibleGroups),baseLayout=layout(state.baseGroups);
    for(const target of targetLayout.items.values()){
      const b=interpolate(`group-${target.g.id}`,target,{x:target.x,y:target.y-10});
      boxes.set(target.g.id,{...target,...b,opacity:target.g.memberGroupIds?(state.mergeProgress.get(target.g.id)||0):b.opacity});
    }
    for(const parent of higherGroups){
      const q=state.mergeProgress.get(parent.id)||0;if(q<=0||q>=1)continue;
      const destination=boxes.get(parent.id);
      for(const childId of parent.memberGroupIds){
        const base=baseLayout.items.get(childId),key=`${parent.id}:${childId}`;
        if(!mergeOrigins.has(key))mergeOrigins.set(key,{...base,...positions.get(`group-${childId}`)});
        const origin=mergeOrigins.get(key);
        const b={...base,fold:1,x:mix(origin.x,destination.x,q),y:mix(origin.y,destination.y,q),w:mix(origin.w,destination.w,q),h:mix(origin.h,destination.h,q),opacity:1-q};
        boxes.set(childId,b);positions.set(`group-${childId}`,{x:b.x,y:b.y,w:b.w,h:b.h,opacity:b.opacity});
      }
    }
    const desired=Math.max(490,targetLayout.bottom,...[...boxes.values()].map(b=>b.y+b.h+30));
    height=reduced?desired:mix(height,desired,.18);stage.style.height=`${height}px`;
    $('graph').setAttribute('viewBox',`0 0 ${width} ${height}`);$('graph').style.height=`${height}px`;
    const root={x:Math.max(22,(width-300)/2),y:28,w:Math.min(width-44,300),h:58};
    const representatives=new Set([...state.nodeIds].map(id=>representative(id,state).key));
    for(const b of boxes.values()){
      const key=`group:${b.g.id}`;
      if(representatives.has(key))nodePositions.set(key,{x:b.x+12,y:b.y+44,w:b.w-24,h:b.g.memberGroupIds?70:58});
      if(b.g.memberGroupIds)continue;
      for(const entry of rawLayouts.get(b.g.id).entries){
        if(!representatives.has(entry.id))continue;
        const target={x:b.x+entry.x,y:mix(b.y+entry.y,b.y+48,b.fold),w:entry.w,h:entry.h,opacity:1};
        const p=interpolate(`node-${entry.id}`,target,{x:target.x,y:target.y-7});
        nodePositions.set(entry.id,p);
      }
    }
    const s=[`<defs><marker id="arrow" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto"><path d="M0 0 L6 3 L0 6" fill="#96a6bb"/></marker><marker id="structural-arrow" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto"><path d="M0 0 L6 3 L0 6" fill="#5c8da8"/></marker></defs><title id="graph-title">三类节点的轨迹生长与层级压缩</title><desc id="graph-desc">${state.nodeIds.size} 个原始节点，当前显示 ${state.visibleCount} 个节点。实线为反馈对应，虚线为人工标注的谓词。</desc>`];
    if(!state.started){$('graph').innerHTML=s.join('');$('graph-viewport').scrollTo?.({top:0,behavior:'instant'});return;}
    const current=state.event;
    const railY=119,railWidth=Math.min(width-75,Math.max(90,D.steps.length*24)),railX=(width-railWidth)/2;
    s.push(`<path d="M${root.x+root.w/2} ${root.y+root.h} V${railY-9}" stroke="#d2dcf0" fill="none"/>`);
    if(state.arrived.size){
      const end=railX+(state.arrived.size-1)*(railWidth/(D.steps.length-1));
      s.push(`<path d="M${railX} ${railY} H${end}" stroke="#d7e1f5" stroke-width="2"/>`);
      D.steps.filter(step=>state.arrived.has(step.id)).forEach((step,i)=>{
        const x=railX+i*railWidth/(D.steps.length-1),active=step.id===current?.stepId;
        s.push(`<circle cx="${x}" cy="${railY}" r="${active?5:3}" fill="${active?'#3567dc':'#b2c5ee'}"/>`,svgText(step.id,x,railY+20,9,'#8395af','text-anchor="middle"'));
      });
    }
    // Group backgrounds precede edges so links inside an event stay visible.
    for(const b of boxes.values()){
      const high=!!b.g.memberGroupIds,collapsed=representatives.has(`group:${b.g.id}`);
      s.push(`<g data-box="${esc(b.g.id)}" opacity="${b.opacity}"><rect x="${b.x}" y="${b.y}" width="${b.w}" height="${b.h}" rx="11" fill="${high?'#f3effb':collapsed?'#f8f5fd':'#fafbfd'}" stroke="#dce3ee"/>`,svgText(b.g.title,b.x+14,b.y+24,12,'#45546d','font-weight="550"'),svgText(high?'L2':collapsed?'摘要':'子图',b.x+b.w-14,b.y+24,9,'#8b789d','text-anchor="end"'),'</g>');
      if(!collapsed&&!high)rawLayouts.get(b.g.id).headers.forEach(h=>s.push(svgText(`event ${h.sid}`,b.x+14,b.y+mix(h.y,40,b.fold),8,'#9aa5b4')));
    }
    const projected=projectEdges(state);
    projected.forEach((edge,index)=>{
      const a=nodePositions.get(edge.source),b=nodePositions.get(edge.target);if(!a||!b)return;
      const ga=boxes.get(edge.sg),gb=boxes.get(edge.tg),semantic=edge.family==='semantic';
      const sourceNode=nodes.get(edge.source),targetNode=nodes.get(edge.target);
      const internal=edge.sg===edge.tg;
      let path;
      if(internal&&sourceNode?.type==='action'&&targetNode?.type==='observation'&&sourceNode.stepId===targetNode.stepId){
        const sx=a.x+a.w,sy=a.y+a.h/2,tx=b.x,ty=b.y+b.h/2;
        path=`M${sx} ${sy} C${sx+10} ${sy} ${tx-10} ${ty} ${tx-2} ${ty}`;
      }else if(internal){
        const sx=a.x,sy=a.y+a.h/2,tx=b.x,ty=b.y+b.h/2,channel=ga.x+5;
        path=`M${sx} ${sy} C${channel} ${sy} ${channel} ${ty} ${tx-2} ${ty}`;
      }else{
        // Individual node ports remain explicit even when several links share a gutter.
        const right=gb.x>ga.x+10,sx=right?a.x+a.w:a.x,tx=right?b.x:b.x+b.w;
        const sy=a.y+a.h/2,ty=b.y+b.h/2;
        if(Math.abs(ga.y-gb.y)<12){
          const channel=right?ga.x+ga.w+gap/2:ga.x-gap/2;
          path=`M${sx} ${sy} C${channel} ${sy} ${channel} ${ty} ${tx+(right?-2:2)} ${ty}`;
        }else{
          const channel=right?width-10-(index%3)*4:10+(index%3)*4;
          path=`M${sx} ${sy} C${channel} ${sy} ${channel} ${ty} ${tx+(right?-2:2)} ${ty}`;
        }
      }
      const focused=selectedNode&&edge.members.some(e=>e.source===selectedNode||e.target===selectedNode);
      const opacity=focused ? .95 : semantic ? .27 : .8;
      const evidence=edge.members.map(e=>`${signature(e)}\n${e.evidence}`).join('\n\n');
      s.push(`<path data-dependency="${esc(edge.key)}" data-evidence-count="${edge.members.length}" data-family="${edge.family}" d="${path}" fill="none" stroke="${semantic?'#a28bbd':'#5c8da8'}" stroke-width="${focused?2:semantic?1.1:1.25}" ${semantic?'stroke-dasharray="3 3"':''} marker-end="url(#${semantic?'arrow':'structural-arrow'})" opacity="${opacity}"><title>${esc(evidence)}</title></path>`);
    });
    for(const key of representatives){
      const p=nodePositions.get(key);if(!p)continue;
      if(key.startsWith('group:')){
        const g=groups.get(key.slice(6)),high=!!g.memberGroupIds;
        s.push(`<g class="graph-node" data-group="${esc(g.id)}" role="button" tabindex="0" aria-label="查看${esc(g.title)}摘要"><rect x="${p.x}" y="${p.y}" width="${p.w}" height="${p.h}" rx="8" fill="${high?'#e9def7':'#f0e9fa'}"/>`);
        wrap(g.summary,p.w-22,10).slice(0,3).forEach((line,i)=>s.push(svgText(line,p.x+11,p.y+18+i*14,10,'#79608f')));
        s.push('</g>');const box=boxes.get(g.id);
        s.push(svgText(`${g.nodeIds.length} 个原始节点 · ${high?'逐层展开':'可展开'}`,box.x+14,box.y+box.h-9,9,'#8c789d'));
      }else{
        const node=nodes.get(key),style=NODE_STYLE[node.type],active=key===selectedNode||(!selectedNode&&current?.nodeId===key);
        const detail=node.type==='reasoning'?steps.get(node.stepId).label:node.type==='action'?(node.content.arguments.keystrokes||node.content.tool_name).trim():`本轮${steps.get(node.stepId).toolCalls.length>1?'批量':''}反馈`;
        s.push(`<g class="graph-node typed-node" data-node="${esc(key)}" data-type="${node.type}" role="button" tabindex="0" aria-label="查看 ${node.type} ${node.label}" opacity="${p.opacity}"><rect x="${p.x}" y="${p.y}" width="${p.w}" height="${p.h}" rx="${style.rx}" fill="${style.fill}" stroke="${style.stroke}" stroke-width="${active?2:1}"/>`,svgText(`${node.type} · ${node.label}`,p.x+8,p.y+13,9,style.ink,'font-weight="600"'),svgText(short(detail,Math.max(6,Math.floor((p.w-16)/7))),p.x+8,p.y+27,9,'#7a8795'),'</g>');
      }
    }
    const rootTitle=current?.type==='finish'?'主 Agent · 任务完成':current?.type==='merge'?'主 Agent · 归并子图':current?.type==='compress'?'主 Agent · 压缩子图':current?.stepId?`主 Agent · event ${current.stepId}`:'主 Agent · 接收任务';
    const rootSubtitle=current?.nodeId?`${nodes.get(current.nodeId).type} 单独成为节点`:'reasoning / action / observation';
    s.push(`<g><rect x="${root.x}" y="${root.y}" width="${root.w}" height="${root.h}" rx="12" fill="#fff" stroke="#b7caef"/><rect x="${root.x+13}" y="${root.y+13}" width="32" height="32" rx="9" fill="#edf2fd"/>`,svgText('A',root.x+29,root.y+35,15,'#3567dc','text-anchor="middle"'),svgText(rootTitle,root.x+57,root.y+25,12,'#3f5579'),svgText(rootSubtitle,root.x+57,root.y+43,9,'#8b9ab0'),'</g>');
    const focused=document.activeElement,focusNode=focused?.getAttribute('data-node'),focusGroup=focused?.getAttribute('data-group'),hadFocus=$('graph').contains(focused);
    $('graph').innerHTML=s.join('');
    if(hadFocus){const replacement=focusNode?$('graph').querySelector(`[data-node="${focusNode}"]`):focusGroup?$('graph').querySelector(`[data-group="${focusGroup}"]`):null;replacement?.focus({preventScroll:true});}
    const viewport=$('graph-viewport');
    // Recheck after the layout settles: a narrow viewport can initially clamp
    // the scroll position while the SVG is still growing to its target height.
    if(viewport.dataset.event!==String(current?.index)||(settling===1&&!selectedNode&&!selectedGroup)){
      viewport.dataset.event=String(current?.index);
      const pos=current?.nodeId?nodePositions.get(representative(current.nodeId,state).key):boxes.get(current?.groupId);
      if(pos)viewport.scrollTo?.({top:Math.max(0,pos.y-170),behavior:playing&&!reduced?'smooth':'instant'});
      else if(time===0)viewport.scrollTo?.({top:0,behavior:'instant'});
    }
  }
  $('play').addEventListener('click',()=>playing?pause():play());
  $('restart').addEventListener('click',()=>{pause();positions.clear();seek(0);});
  $('previous').addEventListener('click',()=>seekEvent((eventAt(time)?.index??0)-1));
  $('next').addEventListener('click',()=>{const i=(eventAt(time)?.index??-1)+1;if(i>=events.length){pause();seek(total);}else seekEvent(i);});
  $('timeline').max=total;
  $('timeline').addEventListener('input',e=>{pause();seek(e.target.value);});
  $('speed').addEventListener('change',e=>{speed=Number(e.target.value);});
  $('overview').addEventListener('click',()=>{pause();seek(total);});
  $('group-controls').addEventListener('click',e=>{
    const button=e.target.closest('[data-toggle-group]');if(!button)return;pause();
    const id=button.dataset.toggleGroup;
    if(manualOpen.has(id))manualOpen.delete(id);else manualOpen.add(id);
    selectedGroup=id;selectedNode=null;lastDescriptionKey='';dirty=true;settling=45;refreshUI(stateAt(time));
  });
  function selectNode(target){
    const node=target.closest('[data-node],[data-group]');if(!node)return;pause();
    selectedNode=node.dataset.node||null;
    selectedGroup=node.dataset.group||null;lastDescriptionKey='';dirty=true;refreshUI(stateAt(time));
  }
  $('graph').addEventListener('click',e=>selectNode(e.target));
  $('graph').addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();selectNode(e.target);}});
  $('timeline-markers').innerHTML=events.filter(e=>['compress','merge'].includes(e.type)).map(e=>`<span class="timeline-marker ${e.type==='merge'?'higher-marker':''}" style="left:${e.start/total*100}%"></span>`).join('');
  const chapterItems=D.groups.flatMap((g,i)=>[{id:g.id,label:`${String(i+1).padStart(2,'0')} ${g.title}`},...higherGroups.filter(p=>p.memberGroupIds.at(-1)===g.id).map(p=>({id:p.id,label:'L2 二级压缩'}))]);
  $('chapters').innerHTML=chapterItems.map(g=>`<button class="chapter-button" data-group="${esc(g.id)}" type="button">${esc(g.label)}</button>`).join('');
  $('chapters').addEventListener('click',e=>{const b=e.target.closest('[data-group]');if(b)seekEvent(events.findIndex(v=>v.groupId===b.dataset.group));});
  let lastStageWidth=0;
  new ResizeObserver(()=>{
    const nextWidth=$('graph-stage').clientWidth;
    if(nextWidth===lastStageWidth)return;
    lastStageWidth=nextWidth;dirty=true;settling=45;
    $('graph-viewport').dataset.event='';
  }).observe($('graph-stage'));
  function frame(now){
    const dt=Math.min((now-lastFrame)/1000,.15);lastFrame=now;
    if(playing){time=Math.min(total,time+dt*speed);dirty=true;if(time>=total)playing=false;}
    if(dirty||settling>0){const state=stateAt(time);if((state.event?.index??-1)!==lastEventIndex){lastEventIndex=state.event?.index??-1;settling=45;}draw(state);refreshUI(state);dirty=false;settling--;}
    requestAnimationFrame(frame);
  }
  window.TrajectoryPlayer={events,total,dataset:D,seek,seekEvent,play,pause,projectEdges:()=>projectEdges(stateAt(time)),getState:()=>({time,playing,speed,...stateAt(time),manualOpen:[...manualOpen]})};
  // A timestamp link opens paused at that exact frame, useful for sharing/export.
  const linkedTime=/(?:^\?|&)t=(\d+(?:\.\d+)?)(?:&|$)/.exec(window.location?.search||'');
  if(linkedTime)seek(Number(linkedTime[1]));
  refreshUI(stateAt(time));requestAnimationFrame(frame);
})();
