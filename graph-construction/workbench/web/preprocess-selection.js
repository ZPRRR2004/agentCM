// Dataset-level selection stays separate from per-event field comparisons.
import { $, esc, api } from './core.js';

let timer, revision = 0;
const labels = { failed: '测试失败', unscored: '无有效评分', unknown_result: '缺少成功评分',
  missing_task_id: '缺少任务编号', empty: '空轨迹', duplicate_success: '重复成功执行',
  duplicate_record: '重复导入', result_filter: '结果条件排除', infrastructure_failure: '环境故障中断',
  no_tool_calls: '无工具调用', no_node_content: '没有可建模的内容' };
const outcomes = { success: '成功', failure: '任务失败', unscored: '无有效评分', unknown: '结果未知' };
const flags = { infrastructure_failure: '环境 / 运行器故障', no_tool_calls: '无工具调用' };

function trajectoryBadges(row) {
  if (!row?.outcome) return '';
  return `<span class="trajectory-badges"><span class="pill ${row.outcome === 'success' ? 'keep' : ''}">${esc(outcomes[row.outcome] || row.outcome)}</span>${(row.flags || []).map(flag => `<span class="pill trajectory-flag" data-trajectory-flag="${esc(flag)}">${esc(flags[flag] || flag)}</span>`).join('')}</span>`;
}

function selectionLabel(experiment) {
  if (experiment.selection_policy === 'successful-task/v1') return '仅成功 · 按任务去重（历史规则）';
  if (!experiment.selection_policy) return '按原快照保留';
  return (experiment.selection_mode === 'success_only' ? '仅成功' : '全部结果') + ' · 相同记录去重'
    + (['execution-record/v3', 'execution-record/v4', 'execution-record/v5'].includes(experiment.selection_policy) ? ' · 排除环境故障中断' : '')
    + (experiment.selection_policy === 'execution-record/v4' ? ' · 排除无工具调用' : '')
    + (experiment.selection_policy === 'execution-record/v5' ? ' · 保留仅有 reasoning 的轨迹' : '');
}

function selectionSummary(report) {
  if (!report) return '';
  const counts = Object.entries(report.excluded_by_reason).map(([key, n]) => `${labels[key] || key} ${n} 条`).join(' · ');
  const legacy = report.policy === 'successful-task/v1';
  const excludeInfrastructure = ['execution-record/v3', 'execution-record/v4', 'execution-record/v5'].includes(report.policy);
  const keepReasoning = report.policy === 'execution-record/v5';
  const excludeNoTools = report.policy === 'execution-record/v4';
  const description = legacy ? '历史规则：仅成功，按任务保留最后一次成功执行。'
    : (keepReasoning ? '排除环境 / 运行器故障中断的轨迹。仅有 reasoning 内容的轨迹也保留；既无工具调用、也无 reasoning 内容的记录排除。'
        : excludeNoTools ? '先排除环境 / 运行器故障中断及整条轨迹无工具调用的执行。'
        : excludeInfrastructure ? '先排除环境 / 运行器故障中断的执行；修复环境后的重跑按本次结果处理。' : '')
      + (report.mode === 'success_only' ? '剩余记录仅保留成功结果。' : '其余记录保留成功、任务失败及无评分或结果未知的执行。')
      + '相同记录的重复导入只保留一份，同一任务的不同尝试分别保留。';
  const resultCounts = Object.entries(report.outcome_counts || {}).map(([key, n]) => `${outcomes[key] || key} ${n} 条`).join(' · ');
  const flagCounts = Object.entries(report.flag_counts || {}).map(([key, n]) => `${flags[key] || key} ${n} 条`).join(' · ');
  return `<div class="trajectory-filter-summary"><h3>轨迹筛选</h3>
    <p class="selection-counts">输入 <b>${report.input_count}</b> 条 → 保留 <b>${report.retained_count}</b> 条 · 排除 <b>${report.excluded_count}</b> 条</p>
    <p class="helper">${esc(description)}${counts ? '<br>' + esc(counts) : ''}</p>
    ${resultCounts ? `<p class="selection-outcomes">保留结果：${esc(resultCounts)}</p>` : ''}
    ${flagCounts ? `<p class="selection-flags">保留轨迹标记：${esc(flagCounts)}<small>${keepReasoning ? '这些无工具调用的轨迹含有 reasoning 内容。' : excludeNoTools ? '各条记录的处理原因见筛选明细。' : excludeInfrastructure ? '无工具调用单独标记，仍保留。' : '标记可重叠，标记本身不排除轨迹。'}</small></p>` : ''}
    ${report.rows.length ? `<details class="trajectory-filter-details"><summary>查看筛选明细 · ${report.rows.length} 条</summary><div class="table-wrap"><table><thead><tr><th>任务 / 执行记录</th><th>处理</th><th>原因</th></tr></thead><tbody>${report.rows.map(row => `<tr data-trajectory-id="${esc(row.id)}"><td>${esc(row.task_id || row.title)}<small>${esc(row.id)}</small>${trajectoryBadges(row)}${row.tool_calls !== undefined ? `<small>${row.tool_calls} 次工具调用${row.reasoning_events !== undefined ? ` · ${row.reasoning_events} 个 reasoning` : ''}</small>` : ''}</td><td><span class="pill ${row.retained ? 'keep' : 'delete'}">${row.retained ? '保留' : '排除'}</span></td><td>${esc(row.reason)}${row.kept_id ? `<small>保留：${esc(row.kept_id)}</small>` : ''}${row.duplicate_of ? `<small>相同记录：${esc(row.duplicate_of)}</small>` : ''}</td></tr>`).join('')}</tbody></table></div></details>` : ''}</div>`;
}

function scheduleSelectionPreview(body) {
  clearTimeout(timer);
  const current = ++revision;
  const target = $('#preprocess-selection-preview');
  if (!target) return;
  const submit = $('[form=new-preprocess-form][type=submit]');
  target.innerHTML = '<p class="helper">正在核对执行结果与重复导入记录…</p>';
  target.setAttribute('aria-busy', 'true');
  if (submit) submit.disabled = true;
  timer = setTimeout(async () => {
    try {
      const report = await api('experiment/preprocess-preview', body);
      if (current !== revision || $('#preprocess-selection-preview') !== target) return;
      target.innerHTML = selectionSummary(report) + (report.input_count && !report.retained_count
        ? '<p class="status-banner">当前结果条件下没有可处理轨迹，请调整轨迹选择或结果范围。</p>' : '');
      if (submit) submit.disabled = report.input_count > 0 && report.retained_count === 0;
    } catch (error) {
      if (current !== revision || $('#preprocess-selection-preview') !== target) return;
      target.innerHTML = `<p class="status-banner">${esc(error.message)}</p>`;
    } finally {
      if (current === revision && $('#preprocess-selection-preview') === target) target.setAttribute('aria-busy', 'false');
    }
  }, 180);
}

export { selectionSummary, scheduleSelectionPreview, trajectoryBadges, selectionLabel };
