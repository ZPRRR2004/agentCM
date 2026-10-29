// Debounced, read-only preview; obsolete responses never replace current input.
import { $, $$, esc, api } from "./core.js";

let timer;
let revision = 0;
const number = (value) => Number(value).toLocaleString("zh-CN");

function cancelSplitPreview() {
  revision += 1;
  clearTimeout(timer);
}

function scheduleSplitPreview() {
  cancelSplitPreview();
  const current = revision;
  const target = $("#split-preview");
  if (!target) return;
  const fields = ["max_window_events", "overlap_events"];
  const inputs = fields.map((key) => $(`#new-split-form [name=${key}]`));
  const ids = $$("#split-trajectory-picker input:checked").map(
    (el) => el.value,
  );
  const source = $("#split-preprocess-source").value;
  const ready = $("#split-trajectory-picker").dataset.ready === "true";
  $("[form=new-split-form][type=submit]").disabled = !source || !ready || !ids.length;
  $("#split-selection-summary").textContent =
    `已选 ${ids.length} 条执行轨迹 · 展开选择`;
  target.removeAttribute("data-window-count");
  target.setAttribute("aria-busy", "false");
  if (!source || !ready) {
    target.innerHTML = '<p class="helper">选择已完成的预处理结果后，可以预览窗口长度分布。</p>';
    return;
  }
  if (!ids.length) {
    target.innerHTML =
      '<p class="helper">选择执行轨迹后，可以预览窗口长度分布。</p>';
    return;
  }
  if (inputs.some((el) => !el.value.trim() || !el.checkValidity())) {
    target.innerHTML =
      '<p class="helper">填写每窗口事件数和重叠事件数，自动预览长度分布。</p>';
    return;
  }
  const body = {
    dataset_id: $("#split-dataset").value,
    preprocess_experiment_id: $("#split-preprocess-source").value,
    trajectory_ids: ids,
    config: Object.fromEntries(
      fields.map((key, i) => [key, Number(inputs[i].value)]),
    ),
  };
  target.setAttribute("aria-busy", "true");
  target.innerHTML = '<p class="helper">正在计算所选轨迹的窗口分布…</p>';
  timer = setTimeout(async () => {
    try {
      const value = await api("experiment/split-preview", body);
      if (current !== revision || $("#split-preview") !== target) return;
      target.innerHTML = previewContent(value);
      target.dataset.windowCount = value.window_count;
    } catch (error) {
      if (current !== revision || $("#split-preview") !== target) return;
      target.innerHTML = `<p class="helper">${esc(error.message)}</p>`;
    } finally {
      if (current === revision && $("#split-preview") === target)
        target.setAttribute("aria-busy", "false");
    }
  }, 300);
}

function previewContent(p) {
  const maximum = Math.max(
    1,
    ...p.token_histogram.flatMap((b) => [b.core_count, b.context_count]),
  );
  const metric = (label, value) =>
    `<div><span>${label}</span><strong>${number(value)}</strong></div>`;
  const bars = p.token_histogram
    .map(
      (b) => `<div class="length-bin">
    <span class="length-bin-label">${number(b.min)}–${number(b.max_exclusive - 1)}</span>
    <div class="length-bin-bars"><div class="length-bar core-bar" style="width:${(100 * b.core_count) / maximum}%"></div><div class="length-bar context-bar" style="width:${(100 * b.context_count) / maximum}%"></div></div>
    <span class="length-bin-count" aria-label="核心 ${b.core_count} 个窗口，含重叠 ${b.context_count} 个窗口">${b.core_count} / ${b.context_count}</span></div>`,
    )
    .join("");
  return `<p class="helper">选了 ${number(p.trajectory_count)} 条轨迹，共 ${number(p.core_events)} 个 agent event。每个窗口最多切出 ${p.config.max_window_events} 个${p.config.overlap_events ? `，再附上前面的 ${p.config.overlap_events} 个作为重叠` : ""}。</p>
    <div class="preview-metrics">${metric("预计窗口", p.window_count)}${metric("中位长度 · Token", p.context_tokens.median)}${metric("P90 长度 · Token", p.context_tokens.p90)}${metric("最大长度 · Token", p.context_tokens.max)}</div>
    <h4>事件内容长度分布 <small>Token 估算 / 窗口数</small></h4>
    <div class="length-legend"><span><i class="core-bar"></i>核心事件</span><span><i class="context-bar"></i>核心 + 重叠</span></div>
    <div class="length-histogram" role="img" aria-label="窗口 Token 长度分布，分区间比较核心事件和含重叠事件的窗口数">${bars}</div>
    <h4>每个窗口包含多少个 agent event</h4><p class="helper">这里只数本次切出的 agent event，重叠部分另算。</p><div class="event-distribution">${p.event_histogram.map((b) => `<span>包含 ${b.events} 个 agent event 的窗口有 <b>${number(b.windows)} 个</b></span>`).join("")}</div>
    <details class="preview-longest"><summary>查看最长的 ${p.longest_windows.length} 个窗口</summary>${p.longest_windows.map((w) => `<div><span>${esc(w.title)}<small>${esc(w.window_id)} · 本次切出 ${w.core_events} 个 agent event，另有 ${w.overlap_events} 个重叠</small></span><strong>${number(w.context_tokens)} Token</strong></div>`).join("")}</details>
    <p class="helper">长度按事件 JSON 字符数 ÷ 4 向上取整估算，统计范围为核心与重叠事件；任务说明、摘要与 Prompt 另计。P90 表示 90% 的窗口不超过此长度。</p>`;
}

export { cancelSplitPreview, scheduleSplitPreview };
