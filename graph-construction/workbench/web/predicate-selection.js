// Select concrete windows from one completed split experiment.
import { $, $$, esc, api, query, state, empty } from './core.js';

let revision = 0;
let previousCount = null;

export function selectedPredicateWindows() {
  return $$('#trajectory-picker input[name=window_ids]:checked').map(el => el.value);
}

export async function fillPredicateWindows() {
  const target = $('#trajectory-picker');
  if (!target) return;
  const source = $('#new-source-experiment').value;
  const request = ++revision;
  previousCount = null;
  state.sourceWindows = [];
  target.dataset.ready = 'false';
  target.innerHTML = source ? '<p class="helper">正在读取窗口…</p>' : empty('这个数据集需要先完成一次切分实验。');
  $('#source-description').textContent = '';
  updatePredicateSelection();
  if (!source) return;
  const current = () => request === revision && target === $('#trajectory-picker') && $('#new-source-experiment')?.value === source;
  try {
    const e = await api('experiment?' + query({ id: source }));
    if (!current()) return;
    if (e.kind !== 'split' || e.status !== 'completed' || e.dataset_id !== $('#new-dataset').value)
      throw new Error('请选择这个数据集已经完成的切分实验');
    state.sourceWindows = e.windows;
    $('#source-description').textContent = `每个窗口最多切出 ${e.config.max_window_events} 个 agent event，往前重叠 ${e.config.overlap_events} 个。`;
    const groups = new Map();
    for (const window of e.windows) {
      if (!groups.has(window.trajectory_id)) groups.set(window.trajectory_id, { title: window.title, windows: [] });
      groups.get(window.trajectory_id).windows.push(window);
    }
    target.innerHTML = [...groups].map(([id, group]) => `<details class="predicate-window-group">
      <summary><input type="checkbox" name="predicate_trajectory_group" value="${esc(id)}" aria-label="全选 ${esc(group.title)} 的窗口" checked><span>${esc(group.title)}</span><small class="predicate-group-count"></small></summary>
      <div class="predicate-window-choices">${group.windows.map(w => `<label><input type="checkbox" name="window_ids" value="${esc(w.id)}" checked><span>${esc(w.window_id)}</span><small>包含 ${w.events} 个 agent event</small></label>`).join('')}</div>
    </details>`).join('') || empty('这个切分结果包含 0 个窗口，请选择其他结果。');
    target.dataset.ready = 'true';
    previousCount = null;
    $('#window-limit').value = Math.min(10, e.windows.length) || '';
    updatePredicateSelection();
  } catch (error) {
    if (!current()) return;
    target.innerHTML = `<p class="helper">${esc(error.message)}</p>`;
    updatePredicateSelection();
  }
}

export function selectPredicateTrajectory(input) {
  for (const window of $$('input[name=window_ids]', input.closest('.predicate-window-group')))
    window.checked = input.checked;
  updatePredicateSelection();
}

export function updatePredicateSelection(checked) {
  const picker = $('#trajectory-picker');
  if (!picker) return;
  const windows = $$('input[name=window_ids]', picker);
  if (typeof checked === 'boolean') windows.forEach(input => { input.checked = checked; });
  const count = windows.filter(input => input.checked).length;
  const master = $('#predicate-select-all');
  master.checked = count > 0 && count === windows.length;
  master.indeterminate = count > 0 && count < windows.length;
  master.disabled = !windows.length;
  for (const group of $$('.predicate-window-group', picker)) {
    const inputs = $$('input[name=window_ids]', group);
    const selected = inputs.filter(input => input.checked).length;
    const checkbox = $('input[name=predicate_trajectory_group]', group);
    checkbox.checked = selected === inputs.length;
    checkbox.indeterminate = selected > 0 && selected < inputs.length;
    $('.predicate-group-count', group).textContent = `已选 ${selected}/${inputs.length} 个窗口`;
  }
  const limit = $('#window-limit');
  if (count !== previousCount) {
    const oldLimit = Number(limit.value);
    limit.value = count ? (previousCount === 0 || oldLimit === previousCount ? count : Math.min(oldLimit || count, count)) : '';
  }
  previousCount = count;
  limit.max = count;
  limit.disabled = !count;
  const valid = count > 0 && !!limit.value && limit.checkValidity();
  const capped = valid && Number(limit.value) < count;
  $('#predicate-selection-count').textContent = `已选 ${count} 个窗口${capped ? `，这次处理前 ${Number(limit.value)} 个` : ''}`;
  $('[form=new-experiment-form][type=submit]').disabled = picker.dataset.ready !== 'true' || !valid;
}
