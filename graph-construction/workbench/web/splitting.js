// Review splitting parameters, generated windows, and experiment lineage.
import { $, esc, json, state, head, btn, metric, pill, empty, experimentNavigation } from "./core.js";

const splitLabels = {
  max_window_events: "每窗口核心事件上限",
  overlap_events: "重叠事件数",
  max_previous_summary_tokens: "前文摘要 Token 上限",
  max_future_summary_tokens: "后文摘要 Token 上限",
};

function splitDetail(e) {
  state.detail = e;
  state.experiments = state.experiments.map((item) =>
    item.id === e.id ? { ...item, ...e } : item,
  );
  const stats = e.statistics;
  const awaitingInput = e.input_state === "awaiting_input";
  const controls = awaitingInput
    ? btn("接入预处理结果", "attach-input", "primary", "", "plus")
    : ["running", "waiting"].includes(e.status)
      ? btn("停止运行", "stop-experiment", "danger")
      : e.status === "completed"
        ? btn(
            "基于此切分发现谓词",
            "new-predicate",
            "primary",
            `data-source="${e.id}"`,
            "arrow",
          )
        : btn(
            e.status === "draft" ? "开始运行" : "恢复实验",
            "start-experiment",
            "primary",
            "",
            "play",
          );
  $("#main").innerHTML =
    experimentNavigation(e) +
    head(
      e.title,
      "轨迹切分 · " + e.dataset_name + (e.preprocess_title ? " · 输入：" + e.preprocess_title : " · 输入：数据集完整事件轨迹"),
      controls,
      "EXPERIMENT / TRAJECTORY SPLITTING",
    ) +
    (e.question
      ? `<div class="experiment-question"><span class="eyebrow">RESEARCH QUESTION</span>${esc(e.question)}</div>`
      : "") +
    (e.lifecycle?.error
      ? `<div class="status-banner"><strong>本次运行记录</strong>${esc(e.lifecycle.error)}</div>`
      : "") +
    (awaitingInput
      ? `<div class="status-banner"><strong>切分参数已保存</strong>请选择一次已完成的预处理结果，接入后即可开始运行。</div>`
      : "") +
    `<div class="cards">${metric("执行状态", pill(e.status), "", esc(e.stage || (awaitingInput ? "等待接入轨迹" : "等待运行")), "experiments")}${metric("轨迹进度", e.completed + "/" + e.total, "", "完整轨迹按事件顺序切分", "data")}${metric("生成窗口", e.produced_windows, "个", "切分结果用于后续谓词发现", "overview")}${metric("输入快照", e.input_hash.slice(0, 8) || "等待接入", "", "接入时固定完整轨迹内容", "data")}</div>
    <div class="overview-grid section-gap"><section class="panel panel-pad"><h2>切分参数</h2><div class="parameter-grid">${Object.entries(
      e.config,
    )
      .filter(([key]) => key in splitLabels)
      .map(
        ([k, v]) =>
          `<div><span>${splitLabels[k]}</span><strong>${v}</strong></div>`,
      )
      .join(
        "",
      )}</div><p class="helper">Token 采用紧凑 JSON 字符数 ÷ 4 向上取整估算。事件数决定切分边界，Token 用于观察窗口长度。</p><p class="helper">前后文摘要上限为 0 时关闭对应摘要；大于 0 时调用 ${esc(e.model || "配置的模型")} 生成。</p><span class="helper mono">配置在创建时固定；输入在接入时固定 · ${esc(e.algorithm)}</span></section>
    <section class="panel panel-pad"><h2>切分统计</h2>${stats.window_count ? `<div class="parameter-grid"><div><span>核心事件总数</span><strong>${stats.core_events}</strong></div><div><span>每窗口平均事件</span><strong>${stats.mean_events}</strong></div><div><span>核心事件数范围</span><strong>${stats.min_events}–${stats.max_events}</strong></div><div><span>最大核心 Token 估算</span><strong>${stats.max_core_tokens}</strong></div><div><span>最大含重叠 Token 估算</span><strong>${stats.max_context_tokens ?? "—"}</strong></div></div>` : empty("运行切分实验后，在这里查看窗口数量与事件分布。")}</section></div>
    <section class="panel section-gap"><div class="panel-head"><h2>切分结果</h2><span class="muted">${e.windows.length} 个窗口</span></div>${e.windows.length ? `<div class="table-wrap"><table><thead><tr><th>任务</th><th>窗口</th><th>核心事件</th><th></th></tr></thead><tbody>${e.windows.map((w) => `<tr><td>${esc(w.title)}</td><td class="mono">${esc(w.window_id)}</td><td>${w.events}</td><td>${btn("查看窗口", "window-modal", "small", `data-window="${esc(w.id)}" data-experiment="${e.id}"`)}</td></tr>`).join("")}</tbody></table></div>` : empty("填写参数并运行后，生成的窗口会显示在这里。")}</section>
    <details class="panel panel-pad section-gap"><summary>执行记录与快照</summary><pre class="json">${json(e.state)}</pre><p class="helper mono">输入 SHA-256 ${esc(e.input_hash)}<br>摘要 Prompt SHA-256 ${esc(e.prompt_hash)}</p>${e.log ? `<pre class="log">${esc(e.log)}</pre>` : ""}</details>`;
}

function splitComparison(a, b) {
  const rows = Object.keys(splitLabels).map((k) => [
    splitLabels[k],
    a.config[k],
    b.config[k],
  ]);
  rows.push(
    ["生成窗口", a.produced_windows, b.produced_windows],
    [
      "每窗口平均事件",
      a.statistics.mean_events ?? "—",
      b.statistics.mean_events ?? "—",
    ],
    [
      "最大含重叠 Token 估算",
      a.statistics.max_context_tokens ?? "—",
      b.statistics.max_context_tokens ?? "—",
    ],
  );
  return `<p class="helper">A：${esc(a.dataset_name)} · 输入 ${esc(a.input_hash.slice(0, 8))}<br>B：${esc(b.dataset_name)} · 输入 ${esc(b.input_hash.slice(0, 8))}</p><section class="panel"><div class="table-wrap"><table><thead><tr><th>参数 / 指标</th><th>${esc(a.title)}</th><th>${esc(b.title)}</th></tr></thead><tbody>${rows.map(([k, x, y]) => `<tr class="change-row"><td>${k}</td><td>${x}</td><td>${y}</td></tr>`).join("")}</tbody></table></div></section>`;
}
export { splitLabels, splitDetail, splitComparison };
