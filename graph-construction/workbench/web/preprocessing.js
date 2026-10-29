// Local field rules and before/after review, separate from splitting and discovery.
import { $, $$, esc, json, state, api, query, head, btn, metric, pill, empty, toast, experimentNavigation } from './core.js';
import { modal } from './forms.js';
import { datasetControls, selectedData } from './datasets.js';
import { selectionSummary, scheduleSelectionPreview, trajectoryBadges, selectionLabel } from './preprocess-selection.js';

const rules = {
  deduplicate_observation: ['去除重复工具输出结构', '当 content 仅含纯文本，且与 raw 正文完全相同时，保留 raw，移除重复的 content。'],
  remove_source_lines: ['移出事件中的来源行号', '从事件与工具返回中移除 source_line；处理前的快照保留原始行号，可在对照页查回。'],
  simplify_call_ids: ['精简调用标识', '将 tool_call_id 换成 call-0001 等短编号，移除 source_call_id。整条轨迹内编号唯一，切分后沿用；新旧编号映射单独保存，可在对照页查看。'],
};
let selection = { experiment: '', trajectory: '', event: '' };
let revision = 0;
const number = (n) => Number(n || 0).toLocaleString('zh-CN');

function newPreprocess() {
  if (!state.datasets.length) return toast('请先添加数据集', true);
  modal('设计轨迹预处理实验', `<form id="new-preprocess-form"><div class="modal-error" id="modal-error"></div>
    <div class="form-row"><label>实验名称<input name="title" required placeholder="例如：工具输出去重 · 第一轮"></label><label>研究问题<input name="question" placeholder="例如：去除重复字段能减少多少输入？"></label></div>
    ${datasetControls('preprocess', state.dataSelection)}
    <p class="helper">先排除环境 / 运行器故障中断的轨迹。只要有工具调用或 reasoning 内容，成功、任务失败与重跑记录都默认保留；仅有 reasoning 的轨迹也可以参与后续建图。同一任务的不同尝试分别保留，相同记录的重复导入只保留一份，再按下方规则精简字段。</p>
    <label>执行结果范围<select id="preprocess-result-scope" name="selection_mode"><option value="all">全部结果（默认）</option><option value="success_only">仅成功</option></select></label>
    <section id="preprocess-selection-preview" aria-live="polite"></section>
    <h3>字段处理规则</h3><div class="preprocess-rules">${Object.entries(rules).map(([key, [label, text]]) => `<label><input type="checkbox" name="${key}" ${key === 'deduplicate_observation' ? 'checked' : ''}><span><b>${label}</b><small>${text}</small></span></label>`).join('')}</div>
    <p class="helper">保留轨迹的事件顺序、任务说明、思考文本、工具参数及输出正文保持完整。取消全部字段规则可建立字段原样保留的对照组。处理在本地执行。</p>
    <details class="split-inputs"><summary>选择轨迹</summary><div class="trajectory-selection-toolbar"><label><input id="preprocess-select-all" type="checkbox" aria-label="全选轨迹">全选</label><span id="preprocess-selection-count" class="muted" role="status"></span><button class="btn small" type="button" data-action="clear-preprocess-selection">全不选</button></div><div id="preprocess-picker" class="trajectory-picker"></div></details></form>`,
    btn('取消', 'close-modal') + '<button class="btn primary" type="submit" form="new-preprocess-form">创建预处理实验草稿</button>', true);
  fillPreprocessPicker();
}

function fillPreprocessPicker() {
  const { dataset } = selectedData({ dataset_id: $('#preprocess-dataset').value });
  $('#preprocess-picker').innerHTML = dataset.trajectories.map(t => `<label><input type="checkbox" name="preprocess_trajectory_ids" value="${esc(t.id)}" checked><span class="trajectory-choice-body">${esc(t.title)}${trajectoryBadges(t)}</span><small>${t.events} 个事件</small></label>`).join('') || '<p class="helper">接入执行轨迹后即可创建预处理实验。</p>';
  updatePreprocessSelection();
}

function updatePreprocessSelection(checked) {
  const choices = $$('#preprocess-picker input[type=checkbox]');
  if (typeof checked === 'boolean') choices.forEach(el => { el.checked = checked; });
  const count = choices.filter(el => el.checked).length;
  const master = $('#preprocess-select-all');
  master.checked = choices.length > 0 && count === choices.length;
  master.indeterminate = count > 0 && count < choices.length;
  master.disabled = choices.length === 0;
  $('#preprocess-selection-count').textContent = `已选 ${count} / ${choices.length} 条轨迹`;
  if (count > 0 && $('#modal-error')?.textContent === '请至少选择一条轨迹') $('#modal-error').textContent = '';
  $('[data-action=clear-preprocess-selection]').disabled = choices.length === 0;
  scheduleSelectionPreview({ dataset_id: $('#preprocess-dataset').value,
    selection_mode: $('#preprocess-result-scope').value,
    trajectory_ids: choices.filter(el => el.checked).map(el => el.value) });
}

function preprocessBody(form) {
  const body = Object.fromEntries(new FormData(form));
  body.kind = 'preprocess';
  body.config = Object.fromEntries(Object.keys(rules).map(key => [key, form.elements[key].checked]));
  body.trajectory_ids = $$('#preprocess-picker input:checked').map(el => el.value);
  if (!body.trajectory_ids.length) throw new Error('请至少选择一条轨迹');
  for (const key of [...Object.keys(rules), 'preprocess_trajectory_ids']) delete body[key];
  return body;
}

function preprocessDetail(e) {
  state.detail = e;
  state.experiments = state.experiments.map(item => item.id === e.id ? { ...item, ...e } : item);
  if (selection.experiment !== e.id) selection = { experiment: e.id, trajectory: '', event: '' };
  const stats = e.statistics;
  const controls = e.status === 'running' ? btn('停止运行', 'stop-experiment', 'danger')
    : e.status === 'completed' ? btn('基于此结果创建切分', 'new-split', 'primary', `data-source="${e.id}"`, 'arrow')
    : btn(e.status === 'draft' ? '开始运行' : '恢复实验', 'start-experiment', 'primary', '', 'play');
  const completed = e.status === 'completed';
  $('#main').innerHTML = experimentNavigation(e) + head(e.title, '轨迹预处理 · ' + e.dataset_name + ' · 完整事件轨迹 → 精简后的事件轨迹', controls, 'EXPERIMENT / PREPROCESSING') +
    (e.question ? `<div class="experiment-question">${esc(e.question)}</div>` : '') +
    (e.lifecycle?.error ? `<div class="status-banner">${esc(e.lifecycle.error)}</div>` : '') +
    `<div class="cards">${metric('执行状态', pill(e.status), '', esc(e.stage || '可预览处理规则'), 'experiments')}${metric('轨迹进度', e.completed + '/' + e.total, '', '输入与规则在创建时固定', 'data')}${metric('字段变化', completed ? number(stats.removed_fields + (stats.replaced_fields || 0)) : '—', '', completed ? `删除 ${number(stats.removed_fields)} · 替换 ${number(stats.replaced_fields)}` : '运行后汇总全部轨迹', 'overview')}${metric('输入长度减少', completed ? stats.reduction_percent + '%' : '—', '', completed ? '减少约 ' + number(stats.saved_tokens) + ' Token' : '下方可预览单条轨迹', 'review')}</div>
    ${e.selection ? `<section class="panel preprocess-selection">${selectionSummary(e.selection)}<p class="helper">筛选清单与输入已随实验固定。下方对照和后续切分使用保留的轨迹；字段长度变化只统计这些轨迹。</p></section>` : ''}
    <section class="panel preprocess-summary"><h2>本次处理规则</h2><div class="preprocess-rule-tags">${Object.entries(rules).map(([key, [label]]) => `<span class="pill ${e.config[key] ? 'keep' : ''}">${e.config[key] ? '✓' : '○'} ${label}</span>`).join('')}</div><p class="helper">长度统计按事件 JSON 字符数 ÷ 4 向上取整估算，任务说明与轨迹元信息另计。来源：数据集中的完整事件轨迹。</p></section>
    <section class="panel preprocess-review"><div class="panel-head"><div><h2>处理前后对照</h2><p>${completed ? '查看已保存的处理结果' : '根据当前实验规则预览；开始运行后保存结果'}</p></div>${pill('', completed ? '已保存结果' : '规则预览')}</div>
    <div class="preprocess-controls"><label>执行轨迹<select id="preprocess-trajectory">${e.trajectories.map(t => `<option value="${esc(t.id)}" ${selection.trajectory === t.id ? 'selected' : ''}>${esc(t.title)} · ${t.events} 事件</option>`).join('')}</select></label><label>查看范围<select id="preprocess-event"><option value="">正在读取事件…</option></select></label></div>
    <div id="preprocess-comparison" aria-live="polite"><p class="helper">正在读取对照…</p></div></section>`;
  if (e.trajectories.length) loadPreprocessComparison().catch(error => toast(error.message, true));
}

// Highlight exact reported JSON paths, preserving the original pretty-printed text.
function highlightChangedFields(value, changes, rootPath, side) {
  const marked = new Map(changes.filter(c => side === 'before' || c.operation === 'replace').map(c => [c.path, c]));
  function render(item, path, depth) {
    if (item === null || typeof item !== 'object') return json(item);
    const array = Array.isArray(item);
    const entries = Object.entries(item);
    const open = array ? '[' : '{', close = array ? ']' : '}';
    if (!entries.length) return open + close;
    const indent = '  '.repeat(depth + 1);
    const lines = entries.map(([key, child]) => {
      const childPath = array ? `${path}[${key}]` : (path ? `${path}.${key}` : key);
      let content = (array ? '' : json(key) + ': ') + render(child, childPath, depth + 1);
      if (marked.has(childPath)) {
        const change = marked.get(childPath);
        const replaced = change.operation === 'replace';
        const kind = replaced ? 'replaced' : 'removed';
        const description = replaced ? `已替换：${JSON.stringify(change.before)} → ${JSON.stringify(change.after)}` : '已删除：' + change.reason;
        content = `<span class="preprocess-${kind}" data-${kind}-path="${esc(childPath)}" title="${esc(description)}">${content}</span>`;
      }
      return indent + content;
    });
    return open + '\n' + lines.join(',\n') + '\n' + '  '.repeat(depth) + close;
  }
  return render(value, rootPath, 0);
}

async function loadPreprocessComparison(trajectoryChanged = false) {
  const target = $('#preprocess-comparison');
  if (!target) return;
  const current = ++revision;
  const trajectory = $('#preprocess-trajectory').value;
  const event = trajectoryChanged ? '' : ($('#preprocess-event').value || selection.event);
  const experiment = state.detail.id;
  target.setAttribute('aria-busy', 'true');
  try {
    const value = await api('preprocess-comparison?' + query({ id: experiment, trajectory, event }));
    if (current !== revision || $('#preprocess-comparison') !== target) return;
    const chosen = event || value.events[0]?.id || '__all__';
    selection = { experiment, trajectory, event: chosen };
    $('#preprocess-event').innerHTML = `<option value="__all__" ${chosen === '__all__' ? 'selected' : ''}>整条轨迹 JSON</option>` + value.events.map(e => `<option value="${esc(e.id)}" ${e.id === chosen ? 'selected' : ''}>${esc(e.id)} · ${esc(e.source)}${e.tools.length ? ' · ' + esc(e.tools.join(', ')) : ''}</option>`).join('');
    const s = value.statistics;
    const beforePath = chosen === '__all__' ? '' : `events[${value.events.findIndex(e => e.id === chosen)}]`;
    target.innerHTML = `<div class="preprocess-assessment">${trajectoryBadges(value.assessment)}<span>${number(value.assessment?.tool_calls)} 次工具调用</span></div><div class="preprocess-length"><span>本条轨迹 · ${number(s.events)} 个事件</span><span>约 ${number(s.before.tokens)} → <b>${number(s.after.tokens)} Token</b></span><span>减少 <b>${s.reduction_percent}%</b> · 删除 ${number(s.removed_fields)} 个字段 · 替换 ${number(s.replaced_fields)} 个字段</span></div>
      <div class="preprocess-diff"><section class="preprocess-before"><header><span>BEFORE</span><h3>处理前</h3><small>固定输入快照 · <span class="preprocess-removed-legend">红色：删除</span> · <span class="preprocess-replaced-legend">黄色：替换</span></small></header><pre id="preprocess-before">${highlightChangedFields(value.before, value.changes, beforePath, 'before')}</pre></section><section class="preprocess-after"><header><span>AFTER</span><h3>处理后</h3><small>${value.saved ? '已保存结果' : '按规则计算的预览'} · <span class="preprocess-replaced-legend">黄色：替换后的值</span></small></header><pre id="preprocess-after">${highlightChangedFields(value.after, value.changes, beforePath, 'after')}</pre></section></div>
      <details class="preprocess-changes" open><summary>当前范围的字段变化 · ${value.changes.length} 项</summary>${value.changes.length ? value.changes.map(c => `<div class="change-row"><span class="pill ${c.operation === 'replace' ? 'preprocess-replaced' : 'delete'}">${c.operation === 'replace' ? '替换' : '删除'}</span><code>${esc(c.path)}</code><span>${esc(c.reason)}${c.operation === 'replace' ? ` · ${json(c.before)} → ${json(c.after)}` : ''}</span></div>`).join('') : '<p class="helper">当前规则保留了所选内容的全部字段。</p>'}</details>
      ${(value.call_id_mapping || []).length ? `<details class="preprocess-id-mapping"><summary>当前范围的调用编号映射 · ${value.call_id_mapping.length} 项</summary><p class="helper">${value.saved ? '编号映射已随实验结果保存' : '运行后单独保存编号映射'}，用于回查原始调用。</p><div class="table-wrap"><table><thead><tr><th>事件</th><th>短编号</th><th>原始调用编号</th><th>原始来源编号</th></tr></thead><tbody>${value.call_id_mapping.map(c => `<tr><td>${esc(c.event_id)}</td><td>${esc(c.short_id)}</td><td>${esc(c.original_tool_call_id)}</td><td>${esc(c.original_source_call_id ?? '—')}</td></tr>`).join('')}</tbody></table></div></details>` : ''}`;
  } finally {
    if (current === revision && $('#preprocess-comparison') === target) target.setAttribute('aria-busy', 'false');
  }
}

function preprocessComparison(a, b) {
  const rows = [['轨迹筛选', selectionLabel(a), selectionLabel(b)],
    ['保留轨迹', a.trajectory_count, b.trajectory_count],
    ...Object.entries(rules).map(([k, [label]]) => [label, a.config[k] ? '启用' : '关闭', b.config[k] ? '启用' : '关闭']),
    ['移除字段', a.statistics.removed_fields ?? '—', b.statistics.removed_fields ?? '—'],
    ['替换字段', a.statistics.replaced_fields ?? 0, b.statistics.replaced_fields ?? 0],
    ['处理后 Token 估算', a.statistics.after_tokens ?? '—', b.statistics.after_tokens ?? '—']];
  return `<p class="helper">A 输入：${esc(a.input_hash.slice(0, 8))} · B 输入：${esc(b.input_hash.slice(0, 8))}</p><div class="table-wrap"><table><thead><tr><th>规则 / 统计</th><th>${esc(a.title)}</th><th>${esc(b.title)}</th></tr></thead><tbody>${rows.map(([name, x, y]) => `<tr><td>${name}</td><td>${x}</td><td>${y}</td></tr>`).join('')}</tbody></table></div>`;
}

export { newPreprocess, fillPreprocessPicker, updatePreprocessSelection, preprocessBody, preprocessDetail, loadPreprocessComparison, preprocessComparison };
