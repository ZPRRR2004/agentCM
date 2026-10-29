// Shared experiment deletion and restoration dialogs.
import { api, btn, empty, esc, state, toast } from './core.js';
import { modal } from './forms.js';

function deleteExperimentDialog(id) {
  const experiment = state.experiments.find(e => e.id === id);
  if (!experiment) return toast('实验列表已变化，请刷新后重试', true);
  if (['running', 'waiting'].includes(experiment.status)) return toast('请先停止实验，再删除', true);
  const children = state.experiments.filter(e => e.preprocess_experiment_id === id || e.source_experiment_id === id);
  modal('删除实验', `<div class="modal-error" id="modal-error"></div><p>将「<strong>${esc(experiment.title)}</strong>」移至回收站？</p><p class="helper">实验输入、结果和审核记录会保留，可在回收站恢复。</p>${children.length ? `<p class="helper">已创建的 ${children.length} 个后续实验继续保留各自的输入与结果。</p>` : ''}`,
    btn('取消', 'close-modal') + btn('移至回收站', 'confirm-delete-experiment', 'danger', `data-id="${esc(id)}"`, 'trash'));
}

async function deletedExperimentsDialog() {
  const rows = await api('experiments/deleted');
  const kind = { preprocess: '轨迹预处理', split: '轨迹切分', predicate: '谓词发现' };
  modal('实验回收站', `<div class="modal-error" id="modal-error"></div><p class="helper">恢复后，实验会回到实验管理列表，并保留删除前的结果与记录。</p>${rows.length ? `<div class="deleted-experiments">${rows.map(e => `<article class="deleted-experiment" data-deleted-id="${esc(e.id)}"><div><strong>${esc(e.title)}</strong><p class="helper">${esc(kind[e.kind])} · ${esc(e.dataset_name)}<br>删除于 ${esc(new Date(e.deleted_at).toLocaleString('zh-CN'))}</p></div>${btn('恢复实验', 'restore-experiment', '', `data-id="${esc(e.id)}" aria-label="恢复实验：${esc(e.title)}"`)}</article>`).join('')}</div>` : empty('回收站为空。')}`, btn('关闭', 'close-modal'), true);
}

export { deleteExperimentDialog, deletedExperimentsDialog };
