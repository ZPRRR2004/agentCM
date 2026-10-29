// Dialogs for experiment design, feedback, and research tasks.
import {
  $,
  $$,
  esc,
  json,
  icon,
  labels,
  statusLabels,
  pill,
  btn,
  state,
  toast,
  api,
  query,
  head,
  metric,
  empty,
  nav,
  progress,
  experimentTable,
  chart,
} from "./core.js";
import { experimentOptions } from "./views.js";
import { preprocessComparison } from "./preprocessing.js";
import { splitComparison } from "./splitting.js";
import { cancelSplitPreview, scheduleSplitPreview } from "./split-preview.js";
import { selectedData, datasetControls, controlValues } from "./datasets.js";
import { fillPredicateWindows } from "./predicate-selection.js";
function modal(title, body, footer = "", wide = false) {
  cancelSplitPreview();
  const el = $("#modal");
  el.classList.toggle("wide", wide);
  $("#modal-content").innerHTML =
    `<div class="modal-head"><h2>${title}</h2><button class="close" data-action="close-modal" aria-label="关闭">×</button></div><div class="modal-body">${body}</div>${footer ? `<div class="modal-footer">${footer}</div>` : ""}`;
  if (!el.open) el.showModal();
}
function closeModal() {
  cancelSplitPreview();
  $("#modal").close();
}
function newExperiment() {
  modal(
    "选择实验类型",
    `<div class="experiment-kinds"><button class="experiment-kind" data-action="new-preprocess"><span class="eyebrow">01 / PREPROCESS</span><h3>轨迹预处理</h3><p>选择字段精简规则，对照处理前后的轨迹，生成后续切分的输入。</p></button><button class="experiment-kind" data-action="new-split"><span class="eyebrow">02 / SPLIT</span><h3>轨迹切分</h3><p>选择已完成的预处理结果，填写事件数与重叠事件数，预览窗口长度，再运行切分。</p></button><button class="experiment-kind" data-action="new-predicate"><span class="eyebrow">03 / DISCOVER</span><h3>谓词发现</h3><p>选择一次已完成的切分实验，固定窗口与 Prompt，发现并审核谓词。</p></button></div>`,
  );
}
async function newSplit(sourceId) {
  state.experiments = await api("experiments");
  const source = state.experiments.find(e => e.id === sourceId && e.kind === "preprocess" && e.status === "completed");
  const selection = source ? { dataset_id: source.dataset_id } : state.dataSelection;
  const { dataset } = selectedData(selection);
  if (!dataset) return toast("请先添加数据集", true);
  modal(
    "设计轨迹切分实验",
    `<form id="new-split-form"><div class="modal-error" id="modal-error"></div>
    <div class="form-row"><label>实验名称<input name="title" required placeholder="例如：Terminal-Bench · 事件窗口对照"></label><label>研究问题<input name="question" placeholder="例如：重叠事件如何影响谓词发现？"></label></div>
    ${datasetControls("split", selection)}
    <label>已完成的预处理结果<select id="split-preprocess-source" name="preprocess_experiment_id" required></select></label>
    <p class="helper" id="split-source-status" role="status">切分使用上一阶段保存的预处理产物。选择一次已完成的预处理实验，再选择其中的轨迹。</p>
    <details class="split-inputs"><summary id="split-selection-summary">选择执行轨迹</summary><div class="trajectory-picker" id="split-trajectory-picker"></div></details>
    <div class="split-design-grid"><section><h3>切分边界</h3><div class="form-row"><label>每窗口核心事件上限<input name="max_window_events" type="number" min="1" max="100000" placeholder="例如 10" required></label><label>重叠事件数<input name="overlap_events" type="number" min="0" max="100000" placeholder="例如 2" required></label></div>
    <p class="helper">每个核心窗口按事件数切分，再加入前方的重叠事件。事件内容完整保留。</p>
    <h3>前后文摘要</h3><div class="form-row"><label>前文摘要 Token 上限<input name="max_previous_summary_tokens" type="number" min="0" max="100000" placeholder="0 关闭，例如 150" required></label><label>后文摘要 Token 上限<input name="max_future_summary_tokens" type="number" min="0" max="100000" placeholder="0 关闭，例如 150" required></label></div>
    <p class="helper">摘要设置控制前后文概括长度。两项均为 0 时本地执行；开启摘要会使用 ${esc(state.settings.model)}，运行时产生模型用量。</p><p class="helper">保存草稿时固定预处理来源、参数、所选轨迹与摘要 Prompt。</p></section>
    <section class="split-preview-panel"><h3>窗口长度分布预览</h3><p class="helper">调整事件数、重叠数或所选轨迹后自动更新。预览在本地计算。</p><div id="split-preview" aria-live="polite"></div></section></div></form>`,
    btn("取消", "close-modal") +
      '<button class="btn primary" type="submit" form="new-split-form" disabled>创建切分实验草稿</button>',
    true,
  );
  return fillSplitSources(source?.id);
}
function preprocessSourceOptions(dataset, selected = '') {
  const sources = state.experiments.filter(e => e.kind === 'preprocess'
    && e.status === 'completed' && e.dataset_id === dataset);
  return sources.map(e => `<option value="${e.id}" ${e.id === selected ? 'selected' : ''}>${esc(e.title)} · ${e.trajectory_count} 条轨迹 · ${e.id.slice(0, 8)}</option>`).join('')
    || '<option value="">请先完成该数据集的预处理实验</option>';
}
function fillSplitSources(selected = '') {
  $('#split-preprocess-source').innerHTML = preprocessSourceOptions($('#split-dataset').value, selected);
  return fillSplitPicker();
}
const inputRevisions = { split: 0, attach: 0 };
async function fillPreprocessedPicker(prefix) {
  const dataset = $(`#${prefix}-dataset`).value;
  const source = $(`#${prefix}-preprocess-source`).value;
  const target = $(`#${prefix}-trajectory-picker`);
  const status = $(`#${prefix}-source-status`);
  const submit = $(`[form=${prefix === 'split' ? 'new-split-form' : 'attach-input-form'}][type=submit]`);
  const revision = ++inputRevisions[prefix];
  const current = () => revision === inputRevisions[prefix] && target === $(`#${prefix}-trajectory-picker`);
  target.dataset.ready = 'false';
  submit.disabled = true;
  target.innerHTML = '';
  status.textContent = '正在读取预处理结果…';
  if (prefix === 'split') scheduleSplitPreview();
  if (!source) {
    status.textContent = '这个数据集需要先完成一次轨迹预处理实验。完成后可在这里选择处理结果。';
    return;
  }
  try {
    const experiment = await api('experiment?' + query({ id: source }));
    if (!current()) return;
    if (experiment.kind !== 'preprocess' || experiment.status !== 'completed' || experiment.dataset_id !== dataset)
      throw new Error('请选择已完成且属于当前数据集的预处理实验');
    target.innerHTML = trajectoryChoices({ trajectories: experiment.trajectories });
    status.textContent = `已读取 ${experiment.trajectories.length} 条预处理轨迹；保存时固定所选产物与来源。`;
    target.dataset.ready = 'true';
    submit.disabled = !experiment.trajectories.length;
    if (prefix === 'split') scheduleSplitPreview();
  } catch (error) {
    if (current()) status.textContent = error.message;
  }
}
function fillSplitPicker() { return fillPreprocessedPicker('split'); }
function fillAttachPicker() { return fillPreprocessedPicker('attach'); }
function trajectoryChoices(dataset) {
  if (!dataset?.trajectories.length)
    return `<p class="helper">该预处理结果包含 0 条轨迹，请选择其他已完成的预处理实验。</p>`;
  return (
    `<p class="helper">${dataset.trajectories.length} 条执行轨迹${dataset.trajectory_source ? " · " + esc(dataset.trajectory_source.label) : ""}</p>` +
    dataset.trajectories
      .map(
        (t) =>
          `<label><input type="checkbox" name="split_trajectory_ids" value="${esc(t.id)}" checked>${esc(t.title)}<small>${t.events} 个事件</small></label>`,
      )
      .join("")
  );
}
async function attachInputModal() {
  state.experiments = await api('experiments');
  const dataset = state.detail.dataset_id;
  modal(
    "接入预处理结果",
    `<form id="attach-input-form"><div class="modal-error" id="modal-error"></div><input type="hidden" id="attach-dataset" value="${esc(dataset)}"><p class="helper">${esc(state.detail.dataset_name)} · 选择已完成的预处理结果，使用草稿中已填写的切分参数。</p><label>已完成的预处理结果<select id="attach-preprocess-source" name="preprocess_experiment_id" required>${preprocessSourceOptions(dataset)}</select></label><p class="helper" id="attach-source-status" role="status"></p><div class="trajectory-picker" id="attach-trajectory-picker"></div></form>`,
    btn("取消", "close-modal") +
      '<button class="btn primary" type="submit" form="attach-input-form" disabled>保存轨迹快照</button>',
  );
  return fillAttachPicker();
}
async function newPredicate(sourceId) {
  const available = state.experiments.filter(
    (e) => e.kind === "split" && e.status === "completed",
  );
  if (!available.length)
    return toast("先创建并完成一次切分实验，再使用其结果发现谓词");
  const source =
    available.find((e) => e.id === sourceId) ||
    available.find((e) => e.dataset_id === state.dataSelection?.dataset_id) ||
    available[0];
  modal(
    "设计谓词发现实验",
    `<form id="new-experiment-form"><div class="modal-error" id="modal-error"></div><input type="hidden" name="kind" value="predicate"><label>实验名称<input name="title" required placeholder="例如：机制粒度 v1 · 首批定义审核"></label><label>研究问题<textarea name="question" placeholder="这次希望验证什么？" style="min-height:75px"></textarea></label>${datasetControls("new", { dataset_id: source.dataset_id })}<label>切分实验结果<select id="new-source-experiment" name="source_experiment_id" required></select></label><div class="helper" id="source-description"></div><p class="helper">先点“取消全选”，再展开任务，勾选想试的窗口。选中的窗口按轨迹和编号顺序处理。</p><div class="trajectory-selection-toolbar"><label><input id="predicate-select-all" type="checkbox" aria-label="全选窗口">全选</label><span id="predicate-selection-count" class="muted" role="status"></span><button class="btn small" type="button" data-action="clear-predicate-selection">取消全选</button></div><div class="trajectory-picker predicate-window-picker" id="trajectory-picker"></div><div class="form-row"><label>最多处理窗口<input name="window_limit" id="window-limit" type="number" min="1" value="10" required></label><label>每批审核间隔<input name="batch_size" type="number" min="1" max="1000" value="5" required></label></div><input type="hidden" name="max_retries" value="3"><p class="helper">每个 agent event 会展开成独立的 reasoning、action 和 observation 节点。谓词的参数指向这些节点；切分参数仍按 agent event 计数。</p><p class="helper">模型：${esc(state.settings.model)} · 创建时保存所选窗口、节点、Prompt 与模型配置。保存草稿后，在实验详情页点击“开始运行”。</p></form>`,
    btn("取消", "close-modal") +
      '<button class="btn primary" type="submit" form="new-experiment-form" disabled>创建实验草稿</button>',
  );
  await fillSourceOptions(source.id);
}
async function fillSourceOptions(selected) {
  const dataset = controlValues("new").dataset_id;
  const sources = state.experiments.filter(
    (e) =>
      e.kind === "split" &&
      e.status === "completed" &&
      e.dataset_id === dataset,
  );
  $("#new-source-experiment").innerHTML = sources
    .map(
      (e) =>
        `<option value="${e.id}" ${e.id === selected ? "selected" : ""}>${esc(e.title)} · ${e.produced_windows} 窗口</option>`,
    )
    .join("");
  await fillPredicateWindows();
}
function editTask(id) {
  const t = state.tasks.find((t) => t.id === id) || {
    title: "",
    notes: "",
    status: "backlog",
    experiment_id: "",
  };
  modal(
    id ? "编辑研究任务" : "添加研究任务",
    `<form id="task-form" data-id="${id || ""}"><div class="modal-error" id="modal-error"></div><label>任务名称<input name="title" required value="${esc(t.title)}" placeholder="一个具体、可推进的研究问题"></label><label>备注与验收依据<textarea name="notes">${esc(t.notes)}</textarea></label><div class="form-row"><label>状态<select name="status">${["backlog", "doing", "review", "done"].map((s) => `<option value="${s}" ${s === t.status ? "selected" : ""}>${statusLabels[s]}</option>`).join("")}</select></label><label>关联实验<select name="experiment_id"><option value="">选择关联实验</option>${t.experiment_id && !state.experiments.some(e => e.id === t.experiment_id) ? `<option value="${esc(t.experiment_id)}" selected>已删除的关联实验（可从回收站恢复）</option>` : ""}${experimentOptions(t.experiment_id)}</select></label></div></form>`,
    (id ? btn("删除任务", "delete-task", "danger", `data-id="${id}"`) : "") +
      btn("取消", "close-modal") +
      '<button class="btn primary" type="submit" form="task-form">保存任务</button>',
  );
}
function feedbackModal() {
  const e = state.detail;
  if (!e.pending) return toast("批次状态已变化，请刷新实验", true);
  const notes = Object.entries(e.reviews || {})
    .filter(
      ([name, r]) =>
        r.decision !== "pending" &&
        !r.stale &&
        e.registry.some((p) => p.name === name),
    )
    .map(([name, r]) => `${name}: ${statusLabels[r.decision]}。${r.notes}`)
    .join("\n\n");
  modal(
    `第 ${e.batch} 批 · 人工反馈`,
    `<form id="feedback-form"><div class="modal-error" id="modal-error"></div><p class="definition-text">下面汇总了这个实验保存的审核意见。提交后，现有流程会调用模型修订定义库，然后继续处理下一批窗口。</p><label>本批反馈<textarea name="feedback" style="min-height:230px" placeholder="写下需要调整的定义、合并关系或排除条件。留空提交表示保留当前定义库。">${esc(notes)}</textarea></label><p class="helper">本次提交会保存反馈原文和修订结果。留空提交将直接继续。</p></form>`,
    btn("继续检查", "close-modal") +
      '<button class="btn primary" type="submit" form="feedback-form">提交反馈并继续</button>',
  );
}
async function compareModal() {
  if (state.experiments.length < 2) return toast("积累两组实验后即可对比");
  modal(
    "实验对比",
    `<div class="form-row"><label>实验 A<select id="compare-a">${experimentOptions(state.experiments[1].id)}</select></label><label>实验 B<select id="compare-b">${experimentOptions(state.experiments[0].id)}</select></label></div><p class="helper">按定义名称与结构比较，帮助定位需要进一步语义审核的差异。</p><div id="comparison-result"></div>`,
    "",
    true,
  );
  await renderComparison();
}
async function renderComparison() {
  const [a, b] = await Promise.all([
    api("experiment?" + query({ id: $("#compare-a").value })),
    api("experiment?" + query({ id: $("#compare-b").value })),
  ]);
  if (a.id !== $("#compare-a")?.value || b.id !== $("#compare-b")?.value)
    return;
  if (a.kind !== b.kind) {
    $("#comparison-result").innerHTML = empty("请选择相同类型的实验进行对比。");
    return;
  }
  if (a.kind === "preprocess") {
    $("#comparison-result").innerHTML = preprocessComparison(a, b);
    return;
  }
  if (a.kind === "split") {
    $("#comparison-result").innerHTML = splitComparison(a, b);
    return;
  }
  const am = new Map(a.registry.map((p) => [p.name, p])),
    bm = new Map(b.registry.map((p) => [p.name, p]));
  const changes = [...new Set([...am.keys(), ...bm.keys()])].map((name) => ({
    name,
    type: !am.has(name)
      ? "新增"
      : !bm.has(name)
        ? "移除"
        : JSON.stringify(am.get(name)) !== JSON.stringify(bm.get(name))
          ? "结构变化"
          : "相同",
  }));
  $("#comparison-result").innerHTML =
    `<div class="comparison-columns"><section class="panel"><div class="panel-head"><h2>${esc(a.title)}</h2></div>${chart(a)}</section><section class="panel"><div class="panel-head"><h2>${esc(b.title)}</h2></div>${chart(b)}</section></div><p class="helper">A：${a.total} 窗口 / ${a.schema}　 B：${b.total} 窗口 / ${b.schema}</p><section class="panel">${changes.map((c) => `<div class="change-row">${pill(c.type === "新增" ? "keep" : c.type === "移除" ? "delete" : c.type === "相同" ? "" : "revise", c.type)}<code>${esc(c.name)}</code></div>`).join("") || empty("两组实验都没有产生定义。")}</section>`;
}

export {
  modal,
  closeModal,
  newExperiment,
  newSplit,
  attachInputModal,
  newPredicate,
  fillSourceOptions,
  fillSplitPicker,
  fillAttachPicker,
  fillSplitSources,
  editTask,
  feedbackModal,
  compareModal,
  renderComparison,
};
