// Predicate semantic clustering: registry sources, allocation, and result analysis.
import { $, $$, api, btn, empty, esc, experimentNavigation, head, json, metric,
  pill, query, state, toast } from './core.js';
import { modal } from './forms.js';

const arityNames = { 1: 'Unary', 2: 'Binary', 3: 'Ternary', 4: 'Quaternary' };
const arityLabel = (arity) => `${arityNames[arity] || arity + '-ary'}（${arity} 元）`;
const similarity = (value) => value == null ? '—' : Number(value).toFixed(4);
const fieldOrder = ['definition', 'parameters', 'assertion', 'exclusion'];
const fieldLabels = { definition: 'Definition', parameters: 'Parameters', assertion: 'Assertion Conditions', exclusion: 'Exclusion Conditions' };
const defaultFieldPercentages = { definition: 50, parameters: 30, assertion: 10, exclusion: 10 };
let draft = null;
let sourceRevision = 0;
let browser = { experiment: null, arity: 'all', search: '', sort: 'size-desc', singleton: false, selected: null };

function embeddingSummary() {
  const s = state.settings;
  return `<strong>${esc(s.embedding_model || '尚未配置')}</strong><p class="helper cluster-wrap">${esc(s.embedding_base_url || '请先填写 Embedding API Base URL')}<br>维度：${esc(s.embedding_dimensions ?? '模型默认')} · API Key：${s.embedding_key_configured ? '已配置' : '未配置'}</p>
    <strong>LLM Predicate Abstraction：${esc(s.model || '尚未配置')}</strong><p class="helper cluster-wrap">${esc(s.base_url || '请先配置实验模型')}<br>使用“实验模型”的当前密钥，创建时冻结模型和地址。</p>`;
}

function representationOf(e) {
  return e.embedding_representation || e.config?.embedding_representation || { mode: 'single_text' };
}

function representationLabel(e) {
  return representationOf(e).mode === 'fieldwise_concat' ? '多字段加权拼接' : '单文本 Embedding（原版）';
}

function weightPercent(weight) { return Number((weight * 100).toPrecision(10)) + '%'; }

function weightPanel() {
  return `<section class="cluster-config-panel cluster-representation"><h3>Embedding 表示方式</h3>
    <label>表示策略<select id="cluster-representation" name="embedding_representation"><option value="single_text">单文本 Embedding（原版）</option><option value="fieldwise_concat" selected>多字段加权拼接（推荐）</option></select></label>
    <div id="cluster-field-weights"><div class="panel-head"><h3>字段权重配置</h3>${btn('恢复默认权重', 'clustering-reset-weights', 'small', 'type="button"')}</div>
    <div class="cluster-weight-grid">${fieldOrder.map(field => `<label>${fieldLabels[field]}<span class="cluster-weight-input"><input class="cluster-field-weight" data-field="${field}" type="number" min="0" max="100" step="1" value="${defaultFieldPercentages[field]}" required aria-label="${fieldLabels[field]}权重百分比"><span>%</span></span></label>`).join('')}</div>
    <p class="cluster-weight-total" id="cluster-weight-total" aria-live="polite">总权重：100%</p><div id="cluster-weight-error" class="form-error" role="status"></div>
    <p class="helper">四字段独立 L2 归一化后，按原始权重的平方根加权，固定顺序拼接，再做整体 L2 归一化。空字段或零权重字段保留零块，不调用 API；总权重需为 100%。</p></div>
    <p class="helper" id="cluster-representation-dimensions"></p></section>`;
}

function validateWeights() {
  if (!$('#cluster-field-weights')) return '';
  const fieldwise = $('#cluster-representation').value === 'fieldwise_concat';
  const values = $$('.cluster-field-weight').map(input => Number(input.value));
  const sum = values.reduce((total, value) => total + value, 0);
  $('#cluster-weight-total').textContent = `总权重：${Number.isFinite(sum) ? Number(sum.toFixed(8)) : '—'}%`;
  let error = '';
  if (fieldwise) {
    if ($$('.cluster-field-weight').some(input => !input.value || !Number.isFinite(Number(input.value)) || Number(input.value) < 0 || Number(input.value) > 100))
      error = '每个字段权重必须是 0–100 之间的有限非负数。';
    else if (Math.abs(sum - 100) > 1e-7) error = '四个字段权重之和必须等于 100%。';
    else if (draft?.preview?.empty_exclusion_count && values.slice(0, 3).every(value => value === 0))
      error = 'Registry 中存在空 Exclusion；仅给 Exclusion 配置权重会产生全零向量，请调整权重。';
  }
  $('#cluster-weight-error').textContent = error;
  $('#cluster-weight-total').classList.toggle('invalid', Boolean(error));
  return error;
}

function updateRepresentationPanel() {
  if (!$('#new-clustering-form')) return;
  const fieldwise = $('#cluster-representation').value === 'fieldwise_concat';
  $('#cluster-field-weights').hidden = !fieldwise;
  $$('.cluster-field-weight').forEach(input => { input.disabled = !fieldwise; });
  const d = state.settings.embedding_dimensions;
  $('#cluster-representation-dimensions').textContent = fieldwise
    ? `每字段维度：${d ?? '模型默认，运行后确定'} · 预计拼接维度：${d ? 4 * d : '4 × 模型实际输出维度'}`
    : `向量维度：${d ?? '模型默认，运行后确定'} · 使用原版 predicate-embedding-input/v1 模板。`;
  validateWeights();
}

function clusteringProgress(e, p = e.execution || {}) {
  const s = e.state || {}, rep = representationOf(e);
  let text = `已生成 ${e.completed}/${e.total} 个 Embedding`;
  if (rep.mode === 'fieldwise_concat') {
    const total = p.total_embedding_vectors ?? s.total_embedding_vectors ?? (e.input_registry || []).reduce((sum, predicate) => sum +
      fieldOrder.filter(field => rep.weights[field] > 0 && (field !== 'exclusion' || predicate.exclusion_conditions.length > 0)).length, 0);
    const current = p.current_embedding_field ?? s.current_embedding_field;
    text = `Embedding：${p.completed_embedding_vectors ?? s.completed_embedding_vectors ?? 0}/${total} 条字段向量 · ` +
      `当前字段：${current ? current.split(', ').map(field => fieldLabels[field] || field).join(' / ') : '—'} · ` +
      `已完成 ${e.completed}/${e.total} 个 Predicate`;
  }
  if (e.abstraction) {
    if (s.clustering_completed) text = 'Embedding：已完成';
    const count = s.completed_abstraction_clusters ?? 0, total = e.config.target_clusters;
    text += ` · Clustering：${s.completed_clusters ?? 0}/${total} · LLM Predicate Abstraction：${count}/${total}`;
    if (s.current_abstraction_cluster) text += ` · 当前 Cluster：${s.current_abstraction_cluster}`;
    text += ` · 已生成 Predicate：${s.generated_predicates ?? 0} 个`;
  }
  return text;
}

function representationSnapshot(e) {
  const rep = representationOf(e), fieldwise = rep.mode === 'fieldwise_concat';
  const d = rep.field_dimensions ?? e.state?.field_dimensions ?? (fieldwise ? e.embedding.dimensions : e.statistics.embedding_dimensions ?? e.embedding.dimensions);
  const final = rep.final_dimensions ?? e.statistics.embedding_dimensions ?? e.state?.final_dimensions ?? (d ? (fieldwise ? 4 : 1) * d : null);
  return `<p><strong>Embedding 策略</strong>${representationLabel(e)}</p><p><strong>${fieldwise ? '单字段维度 / 最终向量维度' : '向量维度'}</strong>${esc(fieldwise ? `${d ?? '运行后确定'} / ${final ?? '4 × 实际单字段维度'}` : final ?? '运行后确定')}</p>
    ${fieldwise ? `<p><strong>字段顺序与权重</strong>${fieldOrder.map(field => `${fieldLabels[field]} ${weightPercent(rep.weights[field])}`).join(' → ')}</p><p><strong>归一化与加权</strong>Per-field L2 + Final L2 Normalization · Square-root Weight Concatenation<br>空字段补零，保留原始权重</p>` : '<p><strong>归一化</strong>L2 Normalization</p>'}`;
}

async function newClustering(sourceId) {
  const data = await api('bootstrap');
  state.experiments = data.experiments;
  state.settings = data.settings;
  const sources = state.experiments.filter(e => e.kind === 'predicate' && e.status === 'completed');
  draft = { preview: null, upload: null, filename: '', sourceType: sources.length ? 'experiment' : 'upload' };
  modal('设计谓词聚类实验', `<form id="new-clustering-form">
    <div class="modal-error" id="modal-error"></div><input type="hidden" name="kind" value="clustering">
    <div class="form-row"><label>实验名称<input name="title" required maxlength="200" placeholder="例如：谓词机制 · 语义聚类 v1"></label>
      <label>研究问题<input name="question" placeholder="例如：哪些定义可能表达相近机制？"></label></div>
    <label>Predicate Registry 来源<select id="cluster-source-type" name="source_type"><option value="experiment" ${sources.length ? '' : 'disabled'}>已有谓词发现实验</option><option value="upload" ${sources.length ? '' : 'selected'}>上传本地 JSON</option></select></label>
    <div id="cluster-experiment-source"><label>已完成的谓词发现实验<select id="cluster-source" name="source_experiment_id">${sources.map(e => `<option value="${esc(e.id)}" ${e.id === sourceId ? 'selected' : ''}>${esc(e.title)} · ${e.registry_count} 个谓词 · ${esc(e.id)}</option>`).join('') || '<option value="">暂无已完成的谓词发现实验</option>'}</select></label></div>
    <div id="cluster-upload-source" hidden><label>Registry JSON 文件<input id="cluster-file" type="file" accept=".json,application/json"></label><p class="helper">支持 JSON 数组，或仅包含 predicates / registry 字段的对象。使用现有 v2 定义校验器；请求内容最多 2 MB。</p></div>
    <section class="cluster-source-summary" id="cluster-source-summary" aria-live="polite"></section>
    <section class="cluster-config-panel"><div class="panel-head"><h3>Embedding 模型</h3><div class="cluster-actions"><a class="btn small" href="#settings" target="_blank" rel="noopener">打开模型设置 ↗</a>${btn('刷新配置摘要', 'clustering-refresh-settings', 'small', 'type="button"')}</div></div>
      <div id="cluster-embedding-summary">${embeddingSummary()}</div><p class="helper">创建时冻结模型、地址和维度；运行时使用当前保存的 Embedding 密钥。密钥不写入实验快照。</p></section>
    ${weightPanel()}
    <section class="cluster-config-panel"><div class="panel-head"><h3>聚类数量分配</h3>${btn('自动分配', 'clustering-allocate', 'small', 'type="button"')}</div>
      <div class="cluster-allocation-summary"><span>Predicate 总数<strong id="cluster-predicate-count">—</strong></span>
        <label>目标总类数<input id="cluster-total" name="target_clusters" type="number" min="1" value="50" step="1" required></label>
        <span>非空元数组<strong id="cluster-arity-count">—</strong></span><span>平均每类谓词<strong id="cluster-average">—</strong></span></div>
      <p class="helper" id="cluster-total-hint">读取 Registry 后按实际元数生成配置。</p>
      <div class="table-wrap"><table><thead><tr><th>元数</th><th>Predicate 数量</th><th>目标类数</th><th>每类平均谓词</th></tr></thead><tbody id="cluster-allocation"></tbody></table></div>
      <div class="form-error" id="cluster-allocation-error" role="status"></div></section>
    <section class="cluster-config-panel"><h3>聚类算法</h3><label>算法<select id="cluster-algorithm" name="algorithm"><option value="agglomerative">Agglomerative Clustering</option><option value="kmeans">K-Means</option></select></label>
      <div id="cluster-agglomerative-options"><label>Linkage<select name="linkage"><option value="average">Average Linkage</option><option value="complete">Complete Linkage</option></select></label><p class="helper">Cosine Distance · 每个元数组独立执行。</p></div>
      <div id="cluster-kmeans-options" hidden><div class="form-row"><label>n_init<input name="n_init" type="number" min="1" max="1000" step="1" value="20" disabled required></label><label>random_state<input name="random_state" type="number" min="0" max="4294967295" step="1" value="42" disabled required></label></div><p class="helper">普通 K-Means 在 L2 归一化向量上优化簇内平方欧氏距离。结果统计统一使用 Cosine Similarity。</p></div>
    </section><p class="helper">保存草稿不会调用 API。运行时按所选表示方式生成 Embedding，多字段模式包含成立和排除条件；原始定义库保持完整。</p>
    <p class="cluster-abstraction-notice">聚类完成后，系统将对每个 Cluster 独立调用 LLM，生成一个新的五字段谓词，并保存完整的抽象 Registry。包含单元素簇；每次进入抽象阶段都会重新处理全部 Cluster。</p></form>`,
    btn('取消', 'close-modal') + '<button class="btn primary" type="submit" form="new-clustering-form" disabled>创建聚类实验草稿</button>', true);
  updateRepresentationPanel();
  await loadClusteringSource();
}

function sourceBody() {
  const type = $('#cluster-source-type').value;
  return type === 'experiment'
    ? { source_type: type, source_experiment_id: $('#cluster-source').value }
    : { source_type: type, registry: draft.upload, filename: draft.filename };
}

async function loadClusteringSource() {
  const form = $('#new-clustering-form');
  if (!form) return;
  const currentDraft = draft, revision = ++sourceRevision;
  const type = $('#cluster-source-type').value;
  draft.sourceType = type;
  draft.preview = null;
  $('#cluster-experiment-source').hidden = type !== 'experiment';
  $('#cluster-upload-source').hidden = type !== 'upload';
  $('#cluster-allocation').innerHTML = '';
  $('#cluster-predicate-count').textContent = '—';
  $('#cluster-arity-count').textContent = '—';
  $('#cluster-average').textContent = '—';
  $('#cluster-total-hint').textContent = '读取 Registry 后生成合法的类数配置。';
  const summary = $('#cluster-source-summary');
  summary.textContent = type === 'upload' && !draft.filename ? '请选择本地 Registry JSON 文件。' : '正在读取并校验 Registry…';
  validateClusteringDraft();
  if ((type === 'upload' && !draft.filename) || (type === 'experiment' && !$('#cluster-source').value)) return;
  try {
    const value = await api('experiment/clustering-preview', sourceBody());
    if (revision !== sourceRevision || draft !== currentDraft || form !== $('#new-clustering-form')) return;
    draft.preview = value;
    summary.innerHTML = `<p><strong>${esc(value.source.type === 'upload' ? value.source.filename : value.source.title)}</strong>${value.source.experiment_id ? `<br><span class="mono">实验 ID：${esc(value.source.experiment_id)}</span>` : ''}</p>
      <p class="helper">${esc(value.validation)} · ${value.predicate_count} 个 Predicate<br>${Object.entries(value.arity_counts).map(([a, n]) => `${arityLabel(a)}：${n}`).join(' · ')}</p>
      <details><summary>Registry 内容摘要</summary>${value.summary.map(p => `<p class="definition-text"><strong>${esc(p.name)}</strong><br>${esc(p.definition)}</p>`).join('')}<p class="helper">展示前 ${value.summary.length} 个定义；创建时保存全部定义。</p></details>
      <p class="helper mono cluster-wrap">SHA-256 ${esc(value.input_hash)}</p>`;
    renderAllocation(value);
  } catch (error) {
    if (revision === sourceRevision && draft === currentDraft && form === $('#new-clustering-form')) {
      summary.textContent = 'JSON 校验失败：' + error.message;
      validateClusteringDraft();
    }
  }
}

function allocate(counts, total) {
  const arities = Object.keys(counts).sort((a, b) => Number(a) - Number(b));
  const result = Object.fromEntries(arities.map(a => [a, 1]));
  let remaining = total - arities.length;
  while (remaining > 0) {
    const active = arities.filter(a => result[a] < counts[a]);
    const weight = active.reduce((sum, a) => sum + counts[a], 0);
    const quotas = active.map(a => ({ a, exact: remaining * counts[a] / weight }));
    for (const item of quotas) {
      const extra = Math.min(counts[item.a] - result[item.a], Math.floor(item.exact));
      result[item.a] += extra;
      remaining -= extra;
    }
    quotas.sort((a, b) => (b.exact - Math.floor(b.exact)) - (a.exact - Math.floor(a.exact)) || Number(a.a) - Number(b.a));
    for (const { a } of quotas) {
      if (remaining > 0 && result[a] < counts[a]) { result[a]++; remaining--; }
    }
  }
  return result;
}

function renderAllocation(value) {
  const counts = value.arity_counts, groups = Object.keys(counts).length;
  const total = Math.max(groups, Math.min(50, value.predicate_count));
  const assigned = allocate(counts, total);
  $('#cluster-predicate-count').textContent = value.predicate_count;
  $('#cluster-arity-count').textContent = groups;
  const input = $('#cluster-total');
  input.min = groups; input.max = value.predicate_count; input.value = total;
  $('#cluster-total-hint').textContent = `合法总类数：${groups}–${value.predicate_count}。${value.predicate_count < 50 ? `默认 50 已调整为 ${total}。` : ''}修改总数会重新分配；修改单组只更新合计。`;
  $('#cluster-allocation').innerHTML = Object.entries(counts).map(([a, n]) => `<tr><td>${arityLabel(a)}</td><td>${n}</td><td><input class="cluster-arity-target" data-arity="${a}" aria-label="${arityLabel(a)}目标类数" type="number" min="1" max="${n}" step="1" required value="${assigned[a]}" ${n === 1 ? 'readonly' : ''}></td><td data-cluster-average="${a}"></td></tr>`).join('');
  validateClusteringDraft();
}

function automaticAllocation() {
  const preview = draft?.preview;
  if (!preview || !$('#new-clustering-form')) return;
  const total = Number($('#cluster-total').value);
  if (!Number.isSafeInteger(total) || total < Object.keys(preview.arity_counts).length || total > preview.predicate_count) {
    validateClusteringDraft(); return;
  }
  const targets = allocate(preview.arity_counts, total);
  $$('.cluster-arity-target').forEach(input => { input.value = targets[input.dataset.arity]; });
  validateClusteringDraft();
}

function validateClusteringDraft() {
  if (!$('#new-clustering-form')) return false;
  const submit = $('[form="new-clustering-form"][type="submit"]');
  const preview = draft?.preview;
  let error = preview ? '' : '请先读取并通过 Registry 校验。';
  const total = Number($('#cluster-total').value);
  if (preview) {
    const counts = preview.arity_counts;
    const inputs = $$('.cluster-arity-target');
    if (!Number.isSafeInteger(total) || total < Object.keys(counts).length || total > preview.predicate_count)
      error = `目标总类数必须是 ${Object.keys(counts).length}–${preview.predicate_count} 范围内的整数。`;
    let sum = 0;
    for (const input of inputs) {
      const k = Number(input.value), arity = input.dataset.arity;
      if (!Number.isSafeInteger(k) || k < 1 || k > counts[arity]) error = `${arityLabel(arity)}的目标类数必须是 1–${counts[arity]} 范围内的整数。`;
      sum += k;
      $(`[data-cluster-average="${arity}"]`).textContent = k > 0 ? (counts[arity] / k).toFixed(2) : '—';
    }
    if (!error && sum !== total) error = '各元数组目标类数之和必须等于总目标类数。';
    $('#cluster-average').textContent = total > 0 ? (preview.predicate_count / total).toFixed(2) : '—';
  }
  if (!error && (!state.settings.embedding_base_url || !state.settings.embedding_model)) error = '请先在模型设置中保存 Embedding 模型和 API Base URL，再刷新配置摘要。';
  const weightError = validateWeights();
  if (weightError) error = weightError;
  if (!error && $('#cluster-algorithm').value === 'kmeans') {
    const nInit = Number($('[name="n_init"]', $('#new-clustering-form')).value);
    const seedInput = $('[name="random_state"]', $('#new-clustering-form'));
    const seed = Number(seedInput.value);
    if (!Number.isSafeInteger(nInit) || nInit < 1 || nInit > 1000 || !seedInput.value || !Number.isSafeInteger(seed) || seed < 0 || seed > 4294967295) error = '请填写合法的 K-Means n_init 和 random_state。';
  }
  $('#cluster-allocation-error').textContent = error;
  submit.disabled = Boolean(error);
  return !error;
}

function clusteringBody(form) {
  if (!validateClusteringDraft()) throw new Error($('#cluster-allocation-error').textContent);
  const data = Object.fromEntries(new FormData(form));
  const config = { algorithm: data.algorithm, target_clusters: Number(data.target_clusters),
    clusters_by_arity: Object.fromEntries($$('.cluster-arity-target').map(input => [input.dataset.arity, Number(input.value)])) };
  config.embedding_representation = data.embedding_representation === 'fieldwise_concat'
    ? { mode: 'fieldwise_concat', weights: Object.fromEntries($$('.cluster-field-weight').map(input => [input.dataset.field, Number(input.value) / 100])) }
    : { mode: 'single_text' };
  if (data.algorithm === 'agglomerative') config.linkage = data.linkage;
  else { config.n_init = Number(data.n_init); config.random_state = Number(data.random_state); }
  return { kind: 'clustering', title: data.title, question: data.question, ...sourceBody(),
    input_hash: draft.preview.input_hash, config };
}

function clusteringInput(target) {
  if (target.closest('#new-clustering-form')) {
    if (target.id === 'cluster-total') automaticAllocation();
    else if (target.matches('.cluster-arity-target')) {
      const inputs = $$('.cluster-arity-target');
      if (inputs.every(input => input.value !== '' && Number.isFinite(Number(input.value))))
        $('#cluster-total').value = inputs.reduce((sum, input) => sum + Number(input.value), 0);
      validateClusteringDraft();
    } else validateClusteringDraft();
  }
  if (target.id === 'cluster-search') { browser.search = target.value; renderClusterBrowser(); }
}

async function clusteringChange(target) {
  if (target.id === 'cluster-representation') { updateRepresentationPanel(); validateClusteringDraft(); }
  if (['cluster-source-type', 'cluster-source'].includes(target.id)) await loadClusteringSource();
  if (target.id === 'cluster-file') {
    const currentDraft = draft, revision = ++sourceRevision, file = target.files[0];
    draft.upload = null; draft.preview = null; draft.filename = '';
    validateClusteringDraft();
    if (!file) { await loadClusteringSource(); return; }
    try {
      if (file.size > 2_000_000) throw new Error('文件超过 2 MB 请求限制');
      const text = await file.text();
      if (draft !== currentDraft || revision !== sourceRevision || target !== $('#cluster-file')) return;
      draft.upload = JSON.parse(text.replace(/^\uFEFF/, '')); draft.filename = file.name;
      await loadClusteringSource();
    } catch (error) {
      if (draft === currentDraft && revision === sourceRevision && target === $('#cluster-file')) {
        draft.upload = null; draft.preview = null; draft.filename = '';
        $('#cluster-source-summary').textContent = 'JSON 校验失败：' + error.message;
        $('#cluster-allocation').innerHTML = '';
        validateClusteringDraft();
      }
    }
  }
  if (target.id === 'cluster-algorithm') {
    const kmeans = target.value === 'kmeans';
    $('#cluster-agglomerative-options').hidden = kmeans;
    $('#cluster-kmeans-options').hidden = !kmeans;
    $$('input', $('#cluster-kmeans-options')).forEach(input => { input.disabled = !kmeans; });
    $('[name="linkage"]', $('#cluster-agglomerative-options')).disabled = kmeans;
    validateClusteringDraft();
  }
  if (target.id === 'cluster-arity-filter') { browser.arity = target.value; renderClusterBrowser(); }
  if (target.id === 'cluster-sort') { browser.sort = target.value; renderClusterBrowser(); }
  if (target.id === 'cluster-singletons') { browser.singleton = target.checked; renderClusterBrowser(); }
}

function clusteringDetail(e) {
  state.detail = e;
  state.experiments = state.experiments.map(item => item.id === e.id ? {
    ...item, status: e.status, completed: e.completed, actual_clusters: e.actual_clusters, statistics: e.statistics,
  } : item);
  if (browser.experiment !== e.id) browser = { experiment: e.id, arity: 'all', search: '', sort: 'size-desc', singleton: false, selected: null };
  const completed = e.status === 'completed';
  const clusteringReady = completed || e.state?.clustering_completed;
  const active = ['running', 'waiting'].includes(e.status);
  const stats = e.statistics || {}, embedding = e.embedding, config = e.config;
  const source = e.source.type === 'upload' ? `本地 JSON · ${e.source.filename}` : `${e.source.title} · ${e.source.experiment_id}`;
  const rows = stats.arities || Object.entries(e.arity_counts).map(([arity, count]) => ({ arity: Number(arity), predicate_count: count, target_clusters: config.clusters_by_arity[arity] }));
  const actual = stats.actual_clusters ?? e.actual_clusters;
  const distribution = stats.cluster_size_distribution || {};
  const buckets = [1, 2, 3, '4+'].map(size => ({ size, count: Object.entries(distribution).reduce((sum, [s, n]) => sum + ((size === '4+' ? Number(s) >= 4 : Number(s) === size) ? n : 0), 0) }));
  const max = Math.max(1, ...buckets.map(b => b.count));
  $('#main').innerHTML = `<div class="experiment-detail clustering-detail">${experimentNavigation(e)}${head(e.title, '谓词语义聚类 · ' + source,
    (active ? btn('停止运行', 'stop-experiment', 'danger') : completed ? '' : btn(e.status === 'draft' ? '开始运行' : '恢复实验', 'start-experiment', 'primary', '', 'play')) +
    btn('导出聚类 JSON', 'clustering-export', '', clusteringReady ? '' : 'disabled', 'download') +
    btn('导出 Predicate-Cluster 映射', 'clustering-export-mapping', '', clusteringReady ? '' : 'disabled', 'download') +
    (e.abstraction ? btn('导出抽象 Predicate Registry', 'clustering-export-abstracted', '', completed ? '' : 'disabled', 'download') +
      btn('导出抽象映射', 'clustering-export-abstraction-mapping', '', completed ? '' : 'disabled', 'download') : ''), 'EXPERIMENT / PREDICATE CLUSTERING')}
    ${e.question ? `<div class="experiment-question"><span class="eyebrow">RESEARCH QUESTION</span>${esc(e.question)}</div>` : ''}
    <div class="cards">${metric('执行状态', pill(e.status), '', esc(clusteringProgress(e)), 'experiments')}${metric('输入谓词', e.predicate_count, '个', `${Object.keys(e.arity_counts).length} 个非空元数组`, 'data')}${metric('目标 / 实际类数', `${config.target_clusters} / ${actual ?? '—'}`, '', '不同元数严格独立聚类', 'overview')}${metric('Embedding 模型', esc(embedding.model), '', `最终维度：${esc(stats.embedding_dimensions ?? e.state?.final_dimensions ?? (representationOf(e).mode === 'fieldwise_concat' ? (embedding.dimensions ? 4 * embedding.dimensions : '运行后确定') : embedding.dimensions ?? '模型默认'))}`, 'settings')}</div>
    <section class="panel cluster-config-panel"><h2>输入与配置快照</h2><div class="cluster-metadata"><p><strong>来源</strong>${e.source.experiment_id ? `<a href="#experiment/${esc(e.source.experiment_id)}">${esc(source)}</a>` : esc(source)}</p><p><strong>Embedding 服务</strong>${esc(embedding.base_url)}</p><p><strong>文本模板</strong>${esc(embedding.input_template)}</p><p><strong>算法</strong>${esc(config.algorithm)} · ${config.algorithm === 'agglomerative' ? `Cosine Distance · ${esc(config.linkage)} linkage` : `平方欧氏距离 · n_init=${config.n_init} · random_state=${config.random_state}`}</p><p class="mono"><strong>输入 SHA-256</strong>${esc(e.input_hash)}</p></div>
    <details><summary>查看完整输入 Registry · ${e.predicate_count} 个定义</summary><pre class="json cluster-wrap">${json(e.input_registry)}</pre></details></section>
    <div class="cluster-overview-grid"><section class="panel"><div class="panel-head"><h2>元数与聚类分配</h2></div><div class="table-wrap"><table><thead><tr><th>元数</th><th>谓词数</th><th>目标类数</th><th>实际类数</th><th>Singleton</th></tr></thead><tbody>${rows.map(r => `<tr><td>${arityLabel(r.arity)}</td><td>${r.predicate_count}</td><td>${r.target_clusters}</td><td>${r.actual_clusters ?? '—'}</td><td>${r.singleton_count ?? '—'}</td></tr>`).join('')}<tr><th>Total</th><td>${e.predicate_count}</td><td>${config.target_clusters}</td><td>${actual ?? '—'}</td><td>${stats.singleton_count ?? '—'}</td></tr></tbody></table></div></section>
    <section class="panel cluster-config-panel"><h2>Cluster Size Distribution</h2>${buckets.map(b => `<div class="cluster-size-bar"><span>Size ${b.size}</span><div><i style="width:${100 * b.count / max}%"></i></div><strong>${b.count}</strong></div>`).join('')}
      <p class="helper">非单元素簇的总体两两相似度：均值 ${similarity(stats.pairwise_similarity?.mean)} · 最低 ${similarity(stats.pairwise_similarity?.min)} · ${stats.pairwise_similarity?.pair_count ?? 0} 对。</p><p class="helper">相似度反映 Embedding 空间的几何关系，不能自动解释为逻辑等价概率。单元素簇的两两相似度为 null。</p></section></div>
    <section class="cluster-results"><div class="panel-head"><h2>Cluster 浏览器</h2><span class="muted">${actual ?? 0} 类</span></div>
      <div class="toolbar cluster-toolbar"><input id="cluster-search" class="search" value="${esc(browser.search)}" placeholder="搜索 Predicate Name 或 Definition" aria-label="搜索聚类成员">
      <select id="cluster-arity-filter" aria-label="按元数筛选"><option value="all">全部元数</option>${Object.keys(e.arity_counts).map(a => `<option value="${a}" ${browser.arity === a ? 'selected' : ''}>${arityLabel(a)}</option>`).join('')}</select>
      <select id="cluster-sort" aria-label="聚类排序">${[['size-desc', '成员数 ↓'], ['size-asc', '成员数 ↑'], ['similarity-desc', '平均相似度 ↓'], ['similarity-asc', '平均相似度 ↑']].map(([value, label]) => `<option value="${value}" ${browser.sort === value ? 'selected' : ''}>${label}</option>`).join('')}</select><label class="cluster-check"><input id="cluster-singletons" type="checkbox" ${browser.singleton ? 'checked' : ''}>仅 Singleton</label></div>
      <div class="cluster-browser"><div class="list-pane cluster-list" id="cluster-list"></div><section class="panel cluster-members" id="cluster-detail"></section></div></section></div>`;
  $('.cluster-metadata', $('#main')).insertAdjacentHTML('beforeend', representationSnapshot(e));
  if (e.abstraction) $('.cluster-metadata', $('#main')).insertAdjacentHTML('beforeend',
    `<p><strong>抽象 Chat 模型</strong>${esc(e.abstraction.model)}<br>${esc(e.abstraction.base_url)}</p><p class="mono"><strong>抽象 Prompt SHA-256</strong>${esc(e.abstraction.prompt_hash)}</p><p class="helper">每个 Cluster 生成一个同元数谓词，包含 Singleton。恢复时重新调用全部 Cluster；原始聚类与输入保持完整。</p>`);
  if (representationOf(e).mode === 'fieldwise_concat') $('.cluster-results', $('#main')).insertAdjacentHTML('afterbegin',
    '<p class="helper cluster-representation-note">当前相似度基于多字段加权拼接并完成最终整体归一化后的向量计算。</p>');
  renderClusterBrowser();
}

function filteredClusters() {
  const term = browser.search.trim().toLowerCase();
  return (state.detail.clustering?.groups || []).filter(group =>
    (browser.arity === 'all' || String(group.arity) === browser.arity) && (!browser.singleton || group.size === 1) &&
    (!term || group.members.some(p => (p.name + ' ' + p.definition).toLowerCase().includes(term))))
    .sort((a, b) => {
      let difference;
      if (browser.sort.startsWith('similarity')) {
        if (a.mean_similarity == null && b.mean_similarity != null) return 1;
        if (b.mean_similarity == null && a.mean_similarity != null) return -1;
        difference = (a.mean_similarity ?? 0) - (b.mean_similarity ?? 0);
      } else difference = a.size - b.size;
      return (browser.sort.endsWith('desc') ? -difference : difference) || a.medoid_index - b.medoid_index;
    });
}

function renderClusterBrowser() {
  if (!$('#cluster-list')) return;
  const groups = filteredClusters();
  if (!groups.some(g => g.cluster_id === browser.selected)) browser.selected = groups[0]?.cluster_id || null;
  $('#cluster-list').innerHTML = groups.map(g => `<button class="list-item cluster-list-item ${browser.selected === g.cluster_id ? 'selected' : ''}" data-action="clustering-select" data-cluster="${esc(g.cluster_id)}"><b>${esc(g.cluster_id)}</b><span>${arityLabel(g.arity)} · ${g.size} 个成员</span><strong>${esc(g.representative)}</strong><small>平均相似度 ${similarity(g.mean_similarity)}</small></button>`).join('') || empty(state.detail.status === 'completed' ? '没有匹配的 Cluster。' : '完成实验后，这里显示聚类结果。');
  renderCluster();
}

function predicateFields(p) {
  return `<h3 class="cluster-predicate-name" lang="en">${esc(p.name)}</h3><p class="definition-text" lang="en">${esc(p.definition)}</p>
    <h4>有序参数</h4>${p.parameters.map((parameter, i) => `<div class="parameter"><code>${i + 1}. ${esc(parameter.name)}: ${esc(parameter.type)}</code><p class="definition-text" lang="en">${esc(parameter.description)}</p></div>`).join('')}
    ${[['assertion_conditions', 'Assertion Conditions'], ['exclusion_conditions', 'Exclusion Conditions']].map(([field, title]) => `<h4>${title}</h4>${p[field].length ? `<ol class="condition" lang="en">${p[field].map(text => `<li>${esc(text)}</li>`).join('')}</ol>` : '<p class="helper">无排除条件</p>'}`).join('')}`;
}

function renderCluster() {
  const group = state.detail.clustering?.groups?.find(g => g.cluster_id === browser.selected);
  const target = $('#cluster-detail');
  if (!target) return;
  if (!group) { target.innerHTML = empty('选择左侧 Cluster 查看完整定义。'); return; }
  const abstracted = state.detail.abstraction_results?.results?.find(item => item.cluster_id === group.cluster_id);
  const abstraction = state.detail.abstraction ? `<section class="cluster-abstraction-result"><h3>抽象后的 Predicate</h3>${abstracted
    ? `<details class="cluster-member" open><summary>${esc(abstracted.abstracted_predicate.name)}</summary><div>${predicateFields(abstracted.abstracted_predicate)}</div></details>`
    : '<p class="helper">本轮尚未生成此 Cluster 的抽象谓词。每次进入抽象阶段都会重新调用全部 Cluster。</p>'}</section>` : '';
  target.innerHTML = `<div class="panel-head"><div><span class="eyebrow">${esc(group.cluster_id)} · ${arityLabel(group.arity)}</span><h2>${group.size} 个 Predicate</h2></div></div>
    ${abstraction}
    <div class="cluster-quality"><p>Medoid：<strong>${esc(group.representative)}</strong></p><p>Mean Pairwise Cosine Similarity：${similarity(group.mean_similarity)}<br>Minimum Pairwise Cosine Similarity：${similarity(group.min_similarity)}</p>
    ${group.minimum_pair ? `<p>最低相似度谓词对：<strong>${group.minimum_pair.predicates.map(esc).join(' ↔ ')}</strong> · ${similarity(group.minimum_pair.similarity)}</p>` : ''}</div>
    <div class="cluster-member-list">${group.members.map((p, index) => `<details class="cluster-member" ${p.name === group.representative ? 'open' : ''}><summary><span>${esc(p.name)}</span><small>与 Medoid ${similarity(group.member_similarities[p.name])}${p.name === group.representative ? ' · Medoid' : ''}</small></summary><div>${predicateFields(p)}</div></details>`).join('')}</div>
    <section class="cluster-matrix-section"><h3>簇内 Cosine Similarity 矩阵</h3>${group.size === 1 ? '<p class="helper">单元素簇，无簇内两两相似度。</p>' : `<p class="helper">点击单元格，查看对应两条 Predicate 的完整定义。</p><div class="table-wrap cluster-matrix-scroll"><table class="cluster-matrix"><thead><tr><th>Predicate</th>${group.members.map(p => `<th>${esc(p.name)}</th>`).join('')}</tr></thead><tbody>${group.members.map((p, i) => `<tr><th>${esc(p.name)}</th>${group.members.map((q, j) => `<td><button type="button" data-action="clustering-pair" data-row="${i}" data-col="${j}" style="background:rgba(126,158,110,${Math.max(0, (group.similarity_matrix[i][j] + 1) / 2) * 0.65})" aria-label="${esc(p.name)} 与 ${esc(q.name)}：${similarity(group.similarity_matrix[i][j])}">${similarity(group.similarity_matrix[i][j])}</button></td>`).join('')}</tr>`).join('')}</tbody></table></div>`}</section>`;
}

async function showPredicatePair(el) {
  const group = state.detail.clustering.groups.find(g => g.cluster_id === browser.selected);
  if (!group) return;
  const row = Number(el.dataset.row), col = Number(el.dataset.col);
  const first = group.members[row], second = group.members[col];
  if (!first || !second) return;
  const fieldwise = representationOf(state.detail).mode === 'fieldwise_concat';
  modal('Predicate Pair · Cosine ' + similarity(group.similarity_matrix[row][col]),
    `<p class="helper">${esc(group.cluster_id)} · ${arityLabel(group.arity)}</p>${fieldwise ? `<div id="cluster-field-pair"><p class="helper">正在读取已保存的字段向量…</p></div>` : ''}<div class="cluster-pair">${[first, ...(row === col ? [] : [second])].map(p => `<article>${predicateFields(p)}</article>`).join('')}</div>`, btn('关闭', 'close-modal'), true);
  if (fieldwise) {
    const target = $('#cluster-field-pair');
    try {
      const result = await api('clustering/field-pair?' + query({ id: state.detail.id,
        left: group.member_indices[row], right: group.member_indices[col] }));
      if (target !== $('#cluster-field-pair') || !$('#modal').open) return;
      target.innerHTML = `<p><strong>最终拼接向量相似度：${similarity(group.similarity_matrix[row][col])}</strong></p>
        <div class="table-wrap"><table><thead><tr><th>独立字段 Cosine Similarity</th><th>权重</th><th>相似度</th></tr></thead><tbody>${fieldOrder.map(field => {
          const value = result.fields[field];
          return `<tr><td>${fieldLabels[field]}</td><td>${weightPercent(value.weight)}</td><td>${value.status === 'available' ? similarity(value.similarity) : value.status === 'missing' ? '无可比较字段（按缺失规则处理）' : '权重为 0，未请求字段向量'}</td></tr>`;
        }).join('')}</tbody></table></div><p class="helper">字段分数与最终融合分数分别展示；存在空字段时，最终分数取完整拼接向量的 Cosine，不能直接套用固定权重和。</p>`;
    } catch (error) {
      if (target === $('#cluster-field-pair')) target.textContent = '字段相似度读取失败：' + error.message;
    }
  }
}

async function exportClustering(mapping = false) {
  const value = await api(`clustering/${mapping ? 'mapping' : 'export'}?` + query({ id: state.detail.id }));
  const url = URL.createObjectURL(new Blob([JSON.stringify(value, null, 2)], { type: 'application/json' }));
  const link = document.createElement('a');
  link.href = url; link.download = `${state.detail.id}-${mapping ? 'predicate-cluster-mapping' : 'clusters'}.json`; link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
  toast(mapping ? 'Predicate-Cluster 映射已导出' : '聚类结果已导出');
}

async function exportAbstraction(mapping = false) {
  const filename = mapping ? 'abstraction-mapping' : 'abstracted-registry';
  const value = await api(`clustering/${filename}?` + query({ id: state.detail.id }));
  const url = URL.createObjectURL(new Blob([JSON.stringify(value, null, 2)], { type: 'application/json' }));
  const link = document.createElement('a');
  link.href = url; link.download = `${state.detail.id}-${filename}.json`; link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
  toast(mapping ? '抽象映射已导出' : '抽象 Predicate Registry 已导出');
}

function clusteringComparison(a, b) {
  return `<div class="table-wrap"><table><thead><tr><th>实验</th><th>谓词数</th><th>Embedding</th><th>表示策略 / 权重</th><th>算法</th><th>目标 / 实际类数</th><th>Singleton</th></tr></thead><tbody>${[a, b].map(e => `<tr><td>${esc(e.title)}</td><td>${e.predicate_count}</td><td>${esc(e.embedding.model)}</td><td>${representationLabel(e)}${representationOf(e).mode === 'fieldwise_concat' ? `<small>${fieldOrder.map(f => weightPercent(representationOf(e).weights[f])).join(' / ')}</small>` : ''}</td><td>${esc(e.config.algorithm)}</td><td>${e.config.target_clusters} / ${e.actual_clusters ?? '—'}</td><td>${e.statistics.singleton_count ?? '—'}</td></tr>`).join('')}</tbody></table></div><p class="helper">输入内容摘要${a.input_hash === b.input_hash ? '一致' : '不同'}。聚类相似度仅用于语义候选分组。</p>`;
}

const clusteringActions = {
  'new-clustering': (el) => newClustering(el.dataset.source),
  'clustering-allocate': automaticAllocation,
  'clustering-reset-weights': () => {
    $$('.cluster-field-weight').forEach(input => { input.value = defaultFieldPercentages[input.dataset.field]; });
    validateClusteringDraft();
  },
  'clustering-refresh-settings': async () => {
    const data = await api('bootstrap');
    state.settings = data.settings;
    if ($('#cluster-embedding-summary')) {
      $('#cluster-embedding-summary').innerHTML = embeddingSummary();
      updateRepresentationPanel();
      validateClusteringDraft();
    }
  },
  'clustering-select': (el) => { browser.selected = el.dataset.cluster; renderClusterBrowser(); },
  'clustering-pair': showPredicatePair,
  'clustering-export': () => exportClustering(),
  'clustering-export-mapping': () => exportClustering(true),
  'clustering-export-abstracted': () => exportAbstraction(),
  'clustering-export-abstraction-mapping': () => exportAbstraction(true),
};

export { clusteringActions, clusteringBody, clusteringChange, clusteringComparison,
  clusteringDetail, clusteringInput, clusteringProgress, validateClusteringDraft };
