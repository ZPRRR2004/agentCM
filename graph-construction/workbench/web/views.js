// Page rendering and evidence inspection.
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
  experimentNavigation,
  chart,
} from "./core.js";
import { preprocessDetail } from "./preprocessing.js";
import { splitDetail } from "./splitting.js";
import {
  selectedData,
  datasetControls,
  controlValues,
  sourceQuery,
} from "./datasets.js";
function overview() {
  const { dataset: source } = selectedData(state.dataSelection);
  const splits = state.experiments.filter((e) => e.kind === "split");
  const latest = state.experiments.find((e) => e.batches.length),
    active = state.experiments.filter((e) =>
      ["running", "waiting"].includes(e.status),
    ),
    tasks = state.tasks.filter((t) => t.status !== "done");
  $("#main").innerHTML =
    head(
      "让每次实验，都成为下一步的依据。",
      "从执行轨迹中发现语义，用可追溯的审核推进研究。",
      btn("新建实验", "new-experiment", "primary", "", "plus"),
      "AGENTCM / RESEARCH OVERVIEW",
    ) +
    `<div class="cards">${metric(source?.format === "harbor-tasks" ? "官方任务" : "完整轨迹", source?.format === "harbor-tasks" ? source.task_count : source?.trajectories.length || 0, source?.format === "harbor-tasks" ? "个任务" : "条轨迹", "数据集 <b>" + esc(source?.name || "—") + "</b>", "data")}${metric("切分实验", splits.length, "组实验", "由你填写参数并运行生成窗口", "overview")}${metric("实验记录", state.experiments.length, "组实验", `<b>${active.length}</b> 组运行或等待反馈`, "experiments")}${metric("研究任务", tasks.length, "项进行中", `<b>${state.tasks.filter((t) => t.status === "done").length}</b> 项已完成`, "tasks")}</div><div class="overview-grid"><section class="panel"><div class="panel-head"><div><h2>定义库如何随反馈变化</h2><p>批次记录 / 发现与人工反馈后的定义数量</p></div>${pill("", "谓词实验")}</div>${chart(latest)}<div class="chart-note">${latest ? "绿色为批次最终保存的定义数量；有人工反馈的批次取反馈后的结果。" : "创建实验后，工作台会自动记录每个批次。"}</div></section><section class="next-step"><span class="step-mark">↗</span><div><span class="eyebrow">NEXT EXPERIMENT</span><h2>${!source?.trajectories.length ? "从原版任务出发，<br>收集执行轨迹。" : "从预处理结果开始，<br>设计第一轮切分。"}</h2><p>${!source?.trajectories.length ? "收集执行轨迹并完成预处理后，再创建切分实验。" : "选择已完成的预处理结果，填写窗口大小与重叠参数，再基于切分窗口发现谓词。"}</p></div>${btn("设计切分实验", "new-split", "primary", "", "arrow")}</section></div><div class="overview-grid section-gap"><section class="panel"><div class="panel-head"><h2>最近实验</h2><a class="link-btn" href="#experiments">全部实验 ↗</a></div>${experimentTable(state.experiments.slice(0, 4))}</section><section class="panel"><div class="panel-head"><h2>接下来要做</h2><a class="link-btn" href="#tasks">任务看板 ↗</a></div>${
      tasks
        .slice(0, 4)
        .map(
          (t) =>
            `<div class="todo-item"><button class="check" data-action="task-done" data-id="${t.id}" aria-label="完成任务：${esc(t.title)}"></button><div><p class="shortened">${esc(t.title)}</p><small>${esc(statusLabels[t.status])} · 研究任务</small></div></div>`,
        )
        .join("") || empty("任务已全部完成，添加下一个研究问题。")
    }</section></div>`;
}
function experiments() {
  $("#main").innerHTML =
    head(
      "实验管理",
      "固定输入、模型与 Prompt 快照，积累可比较的研究记录。",
      btn("回收站", "deleted-experiments", "", "", "trash") +
        btn("对比实验", "compare", "", "", "compare") +
        btn("新建实验", "new-experiment", "primary", "", "plus"),
      "EXPERIMENTS / RUN & COMPARE",
    ) +
    `<div class="toolbar"><input class="search" id="experiment-search" value="${esc(state.experimentFilters.search)}" placeholder="搜索实验名称或模型…" aria-label="搜索实验"><select id="experiment-filter" aria-label="按数据集筛选实验"><option value="all">全部数据集</option>${state.datasets.map((d) => `<option value="${esc(d.id)}" ${state.experimentFilters.dataset === d.id ? 'selected' : ''}>${esc(d.name)}</option>`).join("")}</select><span class="spacer"></span><span class="refresh-indicator">${state.experiments.length} 条本地记录</span></div><section class="panel" id="experiment-list"></section>`;
  filterExperiments();
}
function filterExperiments() {
  const term = $("#experiment-search").value.toLowerCase(),
    kind = $("#experiment-filter").value;
  state.experimentFilters = { search: $("#experiment-search").value, dataset: kind };
  $("#experiment-list").innerHTML = experimentTable(
    state.experiments.filter(
      (e) =>
        (kind === "all" || kind === e.dataset_id) &&
        (e.title + " " + (e.model || "")).toLowerCase().includes(term),
    ),
  );
}
function experimentDetail(e) {
  const oldConsole = $("#execution-console");
  const oldLog = $("#execution-output");
  const same = oldConsole?.dataset.experiment === e.id;
  const follow = same ? $("#execution-follow").checked : true;
  const scrollTop = same ? oldLog.scrollTop : 0;
  const focusFollow = document.activeElement?.id === "execution-follow";
  if (e.kind === "preprocess") preprocessDetail(e);
  else if (e.kind === "split") splitDetail(e);
  else predicateDetail(e);
  $("#main .cards").insertAdjacentHTML("afterend", executionConsole(e, follow));
  const log = $("#execution-output");
  log.scrollTop = follow ? log.scrollHeight : scrollTop;
  log.addEventListener("scroll", () => {
    $("#execution-follow").checked = log.scrollHeight - log.clientHeight - log.scrollTop < 16;
  });
  $("#execution-follow").addEventListener("change", (event) => {
    if (event.target.checked) log.scrollTop = log.scrollHeight;
  });
  if (focusFollow) $("#execution-follow").focus({ preventScroll: true });
  updateExecutionClock();
}
function predicateDetail(e) {
  state.detail = e;
  state.experiments = state.experiments.map((item) =>
    item.id === e.id
      ? {
          ...item,
          status: e.status,
          completed: e.completed,
          registry_count: e.registry_count,
          batches: e.batches,
        }
      : item,
  );
  $("#main").innerHTML =
    `<div class="experiment-detail">${experimentNavigation(e)}${head(e.title, "谓词定义发现 · " + e.dataset_name + " · 来源：" + e.source_title, `${e.status === "running" || e.status === "waiting" ? btn("停止运行", "stop-experiment", "danger") : e.status === "completed" ? "" : btn(e.status === "draft" ? "开始运行" : "恢复实验", "start-experiment", "primary", "", "play")}${btn("审核定义", "open-review", "", "", "review")}${btn("导出 JSON", "export", "", "", "download")}`, "EXPERIMENT / " + "PREDICATE DISCOVERY")}${e.question ? `<div class="experiment-question"><span class="eyebrow">RESEARCH QUESTION</span>${esc(e.question)}</div>` : ""}${e.status === "waiting" ? `<div class="status-banner"><strong>第 ${e.batch} 批等待你的审核</strong>查看这一批的定义和轨迹，把修改意见提交给流程后继续下一个批次。 ${btn("填写批次反馈", "feedback", "small")}</div>` : ""}${e.lifecycle?.error ? `<div class="status-banner"><strong>本次运行记录</strong>${esc(e.lifecycle.error)}</div>` : ""}<div class="cards">${metric("执行状态", pill(e.status), "", esc(executionStatus(e)), "experiments")}${metric("窗口进度", e.completed + "/" + e.total, "", "按轨迹及窗口索引顺序处理", "data")}${metric("谓词定义", e.registry_count, "个", `已保存 ${e.batches.length} 个批次`, "review")}${metric("Prompt 快照", e.prompt_hash.slice(0, 6), "", "创建时固定 · SHA-256 摘要", "prompts")}</div><div class="subtabs">${[
      ["registry", "定义库"],
      ["windows", "窗口与阶段"],
      ["batches", "批次与反馈"],
      ["log", "运行记录"],
    ]
      .map(
        ([id, label]) =>
          `<button class="${state.experimentTab === id ? "selected" : ""}" data-action="experiment-tab" data-tab="${id}">${label}</button>`,
      )
      .join("")}</div><div id="experiment-tab"></div></div>`;
  experimentTab(e);
}

const executionStages = {
  prepare: "读取实验输入", discovery: "发现候选谓词", comparison: "与已有谓词比较",
  review: "模型审核谓词", commit: "保存结果", registry_revision: "根据你的反馈修改谓词库",
  preprocess: "精简轨迹字段", split: "切分轨迹", previous_summary: "生成前文摘要",
  future_summary: "生成后文摘要", revising_registry: "根据你的反馈修改谓词库",
  applying_revision: "保存反馈修订结果", collecting_feedback: "等待你提交审核意见",
};
function currentExecution(e) {
  const p = e.execution || {};
  // A just-started worker can briefly coexist with the previous run's progress file.
  return e.lifecycle?.started_at && p.run_started_at < e.lifecycle.started_at ? {} : p;
}
function executionStatus(e) {
  if (e.status === "waiting") return `第 ${e.batch} 批已完成，等待你提交审核意见`;
  const ended = { draft: "点击“开始运行”后，这里会显示执行过程", completed: "实验已完成，结果已保存",
    stopped: "实验已停止", interrupted: "运行已中断，可以恢复实验", failed: "运行失败，查看下方记录" };
  if (ended[e.status]) return ended[e.status];
  const p = currentExecution(e);
  return p.message || executionStages[e.state?.pending_feedback_stage || e.stage] || e.stage || "正在启动实验";
}
function executionConsole(e, follow) {
  const active = ["running", "waiting"].includes(e.status), p = currentExecution(e);
  const waitingModel = e.status === "running" && ["model_wait", "summary_wait"].includes(p.event);
  const since = active ? (waitingModel ? p.waiting_since : e.lifecycle?.started_at) : "";
  const feedbackStage = e.state?.pending_feedback_stage;
  const currentIndex = e.status === "waiting" || e.status === "completed" || feedbackStage
    ? Math.max(0, e.completed - 1) : (e.state?.next_window_index || 0);
  const w = e.windows?.[currentIndex];
  const context = e.kind === "predicate" && e.status === "running" && feedbackStage
    ? `第 ${e.batch} 批反馈 · 已处理 ${e.completed}/${e.total} 个窗口`
    : e.kind === "predicate" && w
    ? `第 ${currentIndex + 1}/${e.total} 个窗口 · ${w.title} / ${w.window_id}`
    : p.trajectory_id ? `${p.trajectory_id}${p.window_id ? " / " + p.window_id : ""}`
      : `已处理 ${e.completed}/${e.total} 条轨迹`;
  const stages = ["discovery", "comparison", "review", "commit"];
  const stageIndex = e.status === "completed" || e.status === "waiting" || feedbackStage ? stages.length
    : stages.indexOf(p.stage || e.stage);
  const timeline = e.kind === "predicate" && e.status !== "draft" ? `<ol class="execution-stages">${stages.map((s, i) =>
    `<li class="${i < stageIndex ? "done" : i === stageIndex ? "current" : ""}">${i < stageIndex ? "✓" : i + 1} ${executionStages[s]}</li>`).join("")}</ol>` : "";
  const error = e.lifecycle?.error ? `\n运行失败：${e.lifecycle.error}` : "";
  const log = (e.log || "").trimEnd() + error;
  return `<section id="execution-console" class="execution-console" data-experiment="${esc(e.id)}" aria-label="执行过程">
    <div class="execution-heading"><h2><span class="execution-dot ${active ? "active" : ""}"></span>执行过程</h2><div>
      <span id="execution-clock" data-since="${esc(since || "")}" data-label="${waitingModel ? "已等待" : "本次运行"}"></span>
      <label><input type="checkbox" id="execution-follow" ${follow ? "checked" : ""}>跟随最新记录</label></div></div>
    <div class="execution-current"><strong role="status">${esc(executionStatus(e))}</strong>
      <span>${esc(context)}</span></div>${timeline}
    <pre id="execution-output" class="execution-output" tabindex="0" aria-label="运行输出">${esc(log || (active ? "正在读取运行记录…" : executionStatus(e)))}</pre>
    <div class="execution-footer">${active ? "每 2 秒更新 · 向上滚动可查看前面的记录" : "运行记录保存在本地"}${waitingModel ? " · 模型返回后继续下一步" : ""}</div>
  </section>`;
}
let executionClockTimer;
function updateExecutionClock() {
  clearTimeout(executionClockTimer);
  const el = $("#execution-clock");
  if (!el || !el.dataset.since || document.hidden) return;
  const seconds = Math.max(0, Math.floor((Date.now() - Date.parse(el.dataset.since)) / 1000));
  if (!Number.isFinite(seconds)) return;
  el.textContent = `${el.dataset.label} ${seconds >= 60 ? Math.floor(seconds / 60) + " 分 " : ""}${seconds % 60} 秒`;
  executionClockTimer = setTimeout(updateExecutionClock, 1000);
}
document.addEventListener("visibilitychange", updateExecutionClock);

function experimentTab(e) {
  const el = $("#experiment-tab");
  if (state.experimentTab === "registry") {
    renderRegistry(e);
  } else if (state.experimentTab === "windows") {
    el.innerHTML = `<section class="panel"><div class="panel-head"><h2>输入窗口与处理阶段</h2><span class="muted">${e.windows.length} 个窗口</span></div><div class="table-wrap"><table><thead><tr><th>任务</th><th>窗口</th><th>事件</th><th>状态</th><th></th></tr></thead><tbody>${e.windows.map((w) => `<tr><td>${esc(w.title)}</td><td class="mono">${esc(w.window_id)}</td><td>${w.events}</td><td>${pill(w.status)}</td><td>${btn("打开证据", "window-modal", "small", `data-window="${esc(w.id)}" data-dataset="${esc(e.dataset_id)}" data-experiment="${e.id}"`)}</td></tr>`).join("")}</tbody></table></div></section>`;
  } else if (state.experimentTab === "batches") {
    el.innerHTML = `<section class="panel"><div class="panel-head"><h2>批次变化</h2></div>${chart(e)}<div class="table-wrap"><table><thead><tr><th>批次</th><th>累计窗口</th><th>发现后定义</th><th>反馈后定义</th><th>人工反馈</th><th></th></tr></thead><tbody>${e.batches.map((b) => `<tr><td>Batch ${b.index}</td><td>${b.end}</td><td>${b.before}</td><td>${b.after}</td><td>${b.feedback ? "已完成" : "流程终点或等待反馈"}</td><td>${btn("反馈记录", "batch-record", "small", `data-index="${b.index}"`)}</td></tr>`).join("")}</tbody></table></div></section>`;
  } else {
    el.innerHTML = `<div class="panel panel-pad"><h3>执行状态</h3><pre class="json">${json(e.state)}</pre>${e.log ? `<h3>进程日志 · 最近 18 KB</h3><pre class="log">${esc(e.log)}</pre>` : ""}</div>`;
  }
}
function experimentOptions(selected, kind) {
  return state.experiments
    .filter((e) => !kind || e.kind === kind)
    .map(
      (e) =>
        `<option value="${e.id}" ${e.id === selected ? "selected" : ""}>${esc(e.title)} · ${e.kind === "preprocess" ? "轨迹预处理" : e.kind === "split" ? "轨迹切分" : "谓词发现"} · ${esc(e.dataset_name)}</option>`,
    )
    .join("");
}
function renderRegistry(e) {
  $("#experiment-tab").innerHTML = `<section class="panel"><div class="panel-head"><h2>当前谓词库</h2><span class="review-counter">${Object.keys(e.reviews).length} 条人工审核意见</span></div>${e.registry.length ? `<div class="table-wrap"><table><thead><tr><th>名称与定义</th><th>结构</th><th>审核意见</th></tr></thead><tbody>${e.registry.map(p =>
    `<tr><td class="registry-definition" lang="en"><a class="experiment-name" href="#review/${e.id}/${encodeURIComponent(p.name)}">${esc(p.name)}</a><p class="definition-text">${esc(p.definition)}</p></td><td>${p.parameters.length} 个参数</td><td>${pill(e.reviews[p.name]?.decision || "pending")}</td></tr>`
  ).join("")}</tbody></table></div>` : empty("开始实验后，接受的定义会出现在这里。")}</section>`;
}
function predicateDefinition(p) {
  return `<h2 class="definition-name" lang="en">${esc(p.name)}</h2>
    <div class="signature"><code>${esc(p.name)}(${p.parameters.map(a => esc(a.name) + ": " + esc(a.type)).join(", ")})</code></div>
    <section class="definition-section"><h3>定义</h3><p class="definition-text" lang="en">${esc(p.definition)}</p></section>
    <section class="definition-section"><h3>参数说明</h3>${p.parameters.map(a =>
      `<div class="parameter node-${["action", "observation", "reasoning"].includes(a.type.replace("[]", "")) ? a.type.replace("[]", "") : "legacy"}" lang="en"><code>${esc(a.name)}: ${esc(a.type)}</code><p>${esc(a.description)}</p></div>`).join("")}</section>
    ${[["assertion_conditions", "何时成立"], ["exclusion_conditions", "何时排除"]].map(([key, title]) =>
      `<section class="definition-section"><h3>${title}</h3>${p[key].length ? `<ol class="condition" lang="en">${p[key].map(text =>
        `<li>${esc(text)}</li>`).join("")}</ol>` : '<p class="definition-text" lang="en">No conditions listed.</p>'}</section>`).join("")}`;
}
async function reviewView(id, name) {
  const predicateExperiments = state.experiments.filter(
    (e) => e.kind === "predicate",
  );
  if (!predicateExperiments.length) {
    state.detail = null;
    $("#main").innerHTML =
      head(
        "谓词审核",
        "每个定义都可以关联窗口、参数与人工意见。",
        btn("新建实验", "new-experiment", "primary", "", "plus"),
        "PREDICATE REVIEW",
      ) +
      `<section class="panel">${empty("创建并运行一次谓词实验后，在这里逐项审核定义。")}</section>`;
    return;
  }
  const e = await api(
    "experiment?" +
      query({
        id: predicateExperiments.some((e) => e.id === id)
          ? id
          : predicateExperiments[0]?.id,
      }),
  );
  if (state.view !== "review") return;
  state.detail = e;
  state.selectedPredicate =
    name && e.registry.some((p) => p.name === name)
      ? name
      : e.registry[0]?.name;
  $("#main").innerHTML =
    head(
      "把语义边界，审清楚。",
      "并排阅读定义、参数与原始窗口，为每次修改留下理由。",
      btn("导出 JSON", "export", "", "", "download") +
        (e.status === "waiting"
          ? btn("提交批次反馈", "feedback", "primary", "", "arrow")
          : ""),
      "PREDICATE REVIEW / HUMAN IN THE LOOP",
    ) +
    `<div class="toolbar"><select id="review-experiment" aria-label="选择审核实验">${experimentOptions(e.id, "predicate")}</select><input class="search" id="predicate-search" placeholder="搜索谓词名称或定义…" aria-label="搜索定义"><span class="spacer"></span>${pill("", e.schema)}<span class="review-counter" id="review-count"></span></div><div class="split review-workspace"><div class="list-pane" id="predicate-list"></div><div class="review-grid"><section class="panel" id="predicate-detail"></section><aside class="side-note"><span class="eyebrow">REVIEW LENS</span><h3>这条谓词抓住了哪个机制？</h3><p>把相似名字拆开看：参数角色、成立条件和排除条件是否真的相同。</p><ul><li>替换工具后，机制是否保持？</li><li>是否存在一个明确反例？</li><li>两个定义能否双向替换？</li><li>是否把输入、判断和修复混在一起？</li></ul><p>审核意见单独保存。运行中的实验可在批次反馈中引用这些意见，交由现有修订流程更新定义库。</p>${e.status === "waiting" ? btn("进入批次反馈", "feedback", "primary") : ""}</aside></div></div>`;
  renderPredicateList();
  await renderPredicate();
}
function renderPredicateList() {
  const e = state.detail,
    term = ($("#predicate-search")?.value || "").toLowerCase();
  $("#predicate-list").innerHTML =
    `<div class="list-heading"><span>定义队列</span><span>${e.registry.length}</span></div>` +
    e.registry
      .filter((p) => (p.name + " " + p.definition).toLowerCase().includes(term))
      .map(
        (p) =>
          `<button class="list-item ${p.name === state.selectedPredicate ? "selected" : ""}" data-action="select-predicate" data-name="${esc(p.name)}"><b>${esc(p.name)}</b><small>${p.parameters.map((a) => a.type).join(" → ")} &nbsp; · &nbsp; ${e.reviews[p.name]?.stale ? "定义已变更 · 需复审" : esc(statusLabels[e.reviews[p.name]?.decision || "pending"])}</small></button>`,
      )
      .join("");
  $("#review-count").textContent =
    `${e.registry.filter((p) => e.reviews[p.name] && e.reviews[p.name].decision !== "pending" && !e.reviews[p.name].stale).length} / ${e.registry.length} 已审核`;
}
async function renderPredicate() {
  const e = state.detail,
    p = e.registry.find((p) => p.name === state.selectedPredicate);
  if (!p) {
    $("#predicate-detail").innerHTML =
      empty("实验产生定义后，即可在这里开始审核。");
    return;
  }
  const review = e.reviews[p.name] || { decision: "pending", notes: "" };
  state.decision = review.decision;
  $("#predicate-detail").innerHTML =
    `<div class="detail-body"><div class="detail-title"><span class="eyebrow">PREDICATE DEFINITION</span>${pill(review.stale ? "revise" : review.decision, review.stale ? "定义已变更 · 需复审" : "")}</div><div id="predicate-definition">${predicateDefinition(p)}</div></div><div class="review-form"><h3>我的审核意见</h3><div class="review-controls">${["keep", "revise", "merge", "delete", "pending"].map((d) => `<button class="choice ${d === review.decision ? "selected" : ""}" data-action="decision" data-decision="${d}">${statusLabels[d]}</button>`).join("")}</div><textarea id="review-notes" placeholder="写下理由、反例，或建议的定义与参数…" aria-label="审核意见">${esc(review.notes)}</textarea><div class="actions"><span class="helper">${review.updated_at ? "上次保存 " + new Date(review.updated_at).toLocaleString("zh-CN") : "审核意见会保存在本地工作台。"}</span>${btn("保存审核", "save-review", "primary")}</div></div><div class="review-evidence"><h3>定义出现的窗口</h3><p class="helper">查看发现、比较和审核阶段中出现该名称的窗口。</p><div id="evidence-list" class="helper">正在关联实验记录…</div></div>`;
  const name = p.name;
  const found = await api("evidence?" + query({ experiment: e.id, name }));
  if (state.detail?.id !== e.id || state.selectedPredicate !== name || !$("#evidence-list")) return;
  $("#evidence-list").innerHTML = found.length
    ? found
        .map(
          (w) =>
            `<div class="evidence-item"><div>${esc(w.title)}<br><small>${esc(w.window_id)} · ${w.stages.map((s) => ({ discovery: "发现", comparison: "比较", review: "审核" })[s]).join(" / ")}</small></div>${btn("查看", "window-modal", "small", `data-window="${esc(w.id)}" data-dataset="${esc(e.dataset_id)}" data-experiment="${e.id}"`)}</div>`,
        )
        .join("")
    : "当前阶段记录中没有匹配名称；可从实验的全部窗口继续查阅。";
}
function nodeContent(graph) {
  const counts = Object.fromEntries(["reasoning", "action", "observation"].map(type =>
    [type, graph.nodes.filter(n => n.type === type).length]));
  const byId = new Map(graph.nodes.map(node => [node.id, node]));
  const card = node => {
    const paired = graph.structural_edges.find(edge => edge.target === node.id);
    return `<article class="trajectory-node node-${esc(node.type)}" data-node-id="${esc(node.id)}">
      <header><span class="node-type">${esc(node.type)}</span><code>${esc(node.id)}</code></header>
      ${paired ? `<p class="node-connection">${esc(paired.source)} → returns → 此 observation</p>` : ""}
      <pre>${typeof node.content === "string" ? esc(node.content) : json(node.content)}</pre></article>`;
  };
  return `<div class="node-counts">${Object.entries(counts).map(([type, count]) =>
    `<span class="node-type node-${type}">${count} 个 ${type} 节点</span>`).join("")}</div>
    ${graph.event_groups.map(group => `<section class="node-event-group"><h4>来自 ${esc(group.event_id)}</h4>
      ${group.node_ids.map(id => card(byId.get(id))).join("")}</section>`).join("")}
    ${graph.context_messages.length ? `<details><summary>任务中的其他消息</summary><pre>${json(graph.context_messages)}</pre></details>` : ""}`;
}
function windowContent(result) {
  const w = result.window, g = result.nodes;
  const eventContent = `<div class="definition-section"><h3>核心事件</h3>${w.core.events.map(ev =>
    `<article class="event"><h3>${esc(ev.event_id)} <small class="muted">/ ${esc(ev.source)}</small></h3><p>${esc(ev.thought || "")}</p>${(ev.tool_calls || []).map(t =>
      `<details><summary>${esc(t.tool_name)} · ${esc(t.tool_call_id)}</summary><pre>${json(t.arguments)}</pre><pre>${typeof t.observation?.raw === "string" ? esc(t.observation.raw) : json(t.observation || {})}</pre></details>`).join("")}</article>`).join("")}</div>`;
  return `<div class="detail-title"><div><span class="eyebrow">${esc(w.trajectory_id)} / ${esc(w.window_id)}</span><h2>${esc(w.user_query.title)}</h2></div>${pill("", "CORE · " + w.core.events.length)}</div>
    <div class="definition-section"><h3>任务目标</h3><div class="query-text">${esc(w.user_query.text)}</div></div>
    ${w.previous_summary ? `<details><summary>前文摘要</summary><pre>${esc(w.previous_summary)}</pre></details>` : ""}
    ${g ? `<section class="typed-nodes"><h3>${result.node_source === "snapshot" ? "本次发现使用的节点" : "展开后的节点"}</h3>
      <p class="helper">reasoning 保存 agent 文本，action 保存工具名和参数，observation 保存返回内容。同一 event 中的 reasoning 也单独保存。箭头表示工具调用与返回的对应关系。</p>
      ${g.overlap.nodes.length ? `<details><summary>重叠部分的节点 · ${g.overlap.nodes.length} 个</summary>${nodeContent(g.overlap)}</details>` : ""}
      ${nodeContent(g.core)}<details><summary>查看原始 agent event</summary><pre>${json(w.core.events)}</pre></details></section>`
    : `${result.node_source === "legacy_events" ? '<p class="helper">这是旧版实验，下面展示它当时使用的 event 输入。</p>' : ''}${w.overlap.events.length ? `<details><summary>重叠事件 · ${w.overlap.events.length}</summary><pre>${json(w.overlap.events)}</pre></details>` : ""}${eventContent}`}
    ${w.future_summary ? `<details><summary>后文摘要</summary><pre>${esc(w.future_summary)}</pre></details>` : ""}
    ${Object.entries(result.stages || {}).map(([stage, value]) =>
      `<details><summary>${{ discovery: "发现候选", comparison: "与现有库比较", review: "模型审核" }[stage]} · 原始结构化结果</summary><pre>${json(value)}</pre></details>`).join("")}
    <p class="helper mono">SHA-256 ${esc(result.sha256)}</p>`;
}
async function dataView() {
  const { dataset } = selectedData(state.dataSelection);
  if (!dataset) {
    $("#main").innerHTML =
      head("轨迹数据", "选择完整轨迹，设计切分实验。") +
      empty("在数据集目录中添加完整轨迹后即可开始。");
    return;
  }
  $("#main").innerHTML =
    head(
      dataset.format === "harbor-tasks"
        ? "官方任务，完整收录。"
        : "从完整轨迹，开始实验。",
      dataset.format === "harbor-tasks"
        ? "浏览官方原版任务说明、环境、参考解法和验证脚本。任务运行后产生执行轨迹。"
        : "选择数据集并浏览完整执行轨迹；完成预处理后，再将切分作为独立实验运行。",
      btn("创建预处理实验", "new-preprocess", "primary", "", "plus") + btn("创建切分实验", "new-split", "", "", "plus"),
      dataset.format === "harbor-tasks"
        ? "DATASETS / OFFICIAL TASKS"
        : "DATASETS / COMPLETE TRAJECTORIES",
    ) +
    `<section class="panel dataset-panel">${datasetControls("data", state.dataSelection)}<p id="dataset-description" class="helper"></p></section><div class="toolbar"><select id="data-content" aria-label="浏览内容"><option value="tasks">官方任务</option><option value="trajectories">执行轨迹</option></select><input class="search" id="window-search" placeholder="搜索任务名…" aria-label="搜索任务"><div class="dataset-stats" id="dataset-stats"></div></div><div class="split"><div class="list-pane" id="window-list"></div><section class="panel"><div class="detail-body" id="window-detail"></div></section></div>`;
  await loadDataWindows();
}
async function loadDataWindows() {
  state.dataSelection = controlValues("data");
  const selection = { ...state.dataSelection };
  const { dataset } = selectedData(selection);
  const content = $("#data-content");
  content.hidden = dataset.format !== "harbor-tasks";
  const official =
    dataset.format === "harbor-tasks" && content.value === "tasks";
  $("#main h1").textContent = official
    ? "官方任务，完整收录。"
    : "从完整轨迹，开始实验。";
  $("#main .page-head p").textContent = official
    ? "浏览官方原版任务说明、环境、参考解法和验证脚本。任务运行后产生执行轨迹。"
    : "选择数据集并浏览完整执行轨迹；完成预处理后，再将切分作为独立实验运行。";
  $("#main .page-head .eyebrow").textContent = official
    ? "DATASETS / OFFICIAL TASKS"
    : "DATASETS / COMPLETE TRAJECTORIES";
  const splitButton = $("#main [data-action=new-split]");
  splitButton.disabled = false;
  splitButton.title = "选择已完成的预处理结果并填写切分参数";
  const trajectories = await api(
    (official ? "dataset-tasks?" : "trajectories?") +
      query(sourceQuery(selection)),
  );
  if (
    state.view !== "data" ||
    selection.dataset_id !== state.dataSelection.dataset_id
  )
    return;
  state.dataWindows = trajectories;
  state.dataMode = official ? "tasks" : "trajectories";
  $("#dataset-stats").textContent = official
    ? `${dataset.task_count} 个官方任务 · ${dataset.trajectories.length} 条执行轨迹`
    : `${trajectories.length} 条完整规范化轨迹 · ${dataset.events} 个事件`;
  $("#dataset-description").textContent =
    (official
      ? dataset.description
      : dataset.trajectory_source?.label || dataset.description) +
    (official
      ? ` 官方 commit ${dataset.source.commit.slice(0, 12)}；原版文件已按上游 Git 内容摘要校验。`
      : dataset.raw_tasks
        ? ` 原始任务 ${dataset.raw_tasks} 个，可用规范化轨迹 ${trajectories.length} 条。`
        : "");
  state.window = trajectories[0]?.id;
  renderDataList();
  if (state.window) await selectDataWindow(state.window);
}
function renderDataList() {
  const term = ($("#window-search")?.value || "").toLowerCase();
  $("#window-list").innerHTML = state.dataWindows
    .filter((t) => t.title.toLowerCase().includes(term))
    .map(
      (t) =>
        `<button class="list-item ${t.id === state.window ? "selected" : ""}" data-action="data-window" data-id="${esc(t.id)}"><b>${esc(t.title)}</b><small>${state.dataMode === "tasks" ? esc([t.category, t.difficulty].filter(Boolean).join(" · ") || "官方原版任务") : "完整轨迹 · " + t.events + " 个事件"}</small></button>`,
    )
    .join("");
}
async function selectDataWindow(id) {
  state.window = id;
  renderDataList();
  const dataset = state.dataSelection.dataset_id;
  const official = state.dataMode === "tasks";
  const result = await api(
    (official ? "dataset-task?" : "trajectory?") + query({ dataset, id }),
  );
  if (
    state.window !== id ||
    dataset !== state.dataSelection.dataset_id ||
    !$("#window-detail")
  )
    return;
  if (official) {
    $("#window-detail").innerHTML = taskContent(result);
    return;
  }
  const t = result.trajectory;
  const html = windowContent({
    window: {
      trajectory_id: result.id,
      window_id: "完整轨迹",
      user_query: t.query,
      previous_summary: "",
      future_summary: "",
      overlap: { events: [] },
      core: { events: t.events },
    },
    sha256: result.sha256,
    nodes: result.nodes ? { core: result.nodes, overlap: { nodes: [], context_messages: [] } } : null,
  });
  $("#window-detail").innerHTML = html
    .replace("CORE · ", "事件 · ")
    .replace("<h3>核心事件</h3>", "<h3>完整事件序列</h3>");
}
function taskContent(task) {
  return `<div class="detail-title"><div><span class="eyebrow">OFFICIAL TASK / ${esc(task.id)}</span><h2>${esc(task.title)}</h2></div>${pill("", "原版任务")}</div><p class="helper">${esc([task.category, task.difficulty, ...task.tags].filter(Boolean).join(" · "))}</p><div class="definition-section"><h3>原版任务说明</h3><pre class="query-text task-instruction">${esc(task.instruction)}</pre></div><details><summary>任务配置 · task.toml</summary><pre>${esc(task.config_toml)}</pre></details><details><summary>原版文件清单 · ${task.files.length} 个文件</summary><div class="task-file-list">${task.files.map((f) => `<div class="task-file"><code>${esc(f.path)}</code><span>${(f.bytes / 1024).toFixed(1)} KB</span></div>`).join("")}</div></details><p class="helper mono">instruction.md SHA-256 ${esc(task.instruction_sha256)}</p><p class="helper">官方任务包提供任务说明、运行环境、参考解法和验证脚本。执行轨迹由 Agent 运行任务产生，之后可用于切分与谓词发现。</p>`;
}
function tasks() {
  $("#main").innerHTML =
    head(
      "让研究问题，有清晰的下一步。",
      "从仓库 TODO 初始化，记录你的实验问题、审核任务和设计决策。",
      btn("添加任务", "new-task", "primary", "", "plus"),
      "RESEARCH BOARD / KEEP MOVING",
    ) +
    `<div class="toolbar"><span class="muted" style="font-size:11px">拖动卡片切换状态，点击卡片编辑内容。</span><span class="spacer"></span><span class="refresh-indicator">${state.tasks.filter((t) => t.status === "done").length} / ${state.tasks.length} 已完成</span></div><div class="kanban">${[
      "backlog",
      "doing",
      "review",
      "done",
    ]
      .map(
        (status) =>
          `<section class="kanban-column" data-status="${status}"><div class="column-head">${statusLabels[status]}<span>${state.tasks.filter((t) => t.status === status).length}</span></div>${state.tasks
            .filter((t) => t.status === status)
            .map(
              (t) =>
                `<article class="task-card ${status === "done" ? "all-done" : ""}" tabindex="0" role="button" draggable="true" data-action="edit-task" data-id="${t.id}" aria-label="编辑任务：${esc(t.title)}"><h3>${esc(t.title)}</h3><div class="task-meta"><span>${t.experiment_id ? "关联实验 ↗" : "RESEARCH TASK"}</span><span>${t.notes ? "有备注 · " : ""}${t.id.slice(0, 4)}</span></div></article>`,
            )
            .join("")}</section>`,
      )
      .join("")}</div>`;
}
const promptStages = {
  common: "共享粒度规则",
  discovery: "01 · 候选发现",
  comparison: "02 · 定义比较",
  review: "03 · 模型审核",
  registry_revision: "04 · 反馈修订",
};
async function promptsView() {
  if (!state.promptDirty) {
    state.prompts = await api("prompts");
  }
  $("#main").innerHTML =
    head(
      "让每一次 Prompt 改动，都可追溯。",
      "编辑工作副本；创建实验时自动保存完整快照。",
      btn("恢复当前文件", "reset-prompt") +
        btn("校验并保存", "save-prompts", "primary"),
      "PROMPT STUDIO / DEFINE THE MECHANISM",
    ) +
    `<div class="prompt-layout"><div class="list-pane" id="prompt-list"></div><section class="panel"><div class="editor-head"><span class="mono" id="prompt-filename"></span><span class="pill" id="prompt-save-status">已保存</span></div><textarea class="editor" id="prompt-editor" spellcheck="false" aria-label="Prompt 内容"></textarea><div class="editor-note">保留 {{模板变量}}；保存时会校验所有阶段的必需变量。<span class="mono" id="prompt-hash"></span></div></section></div>`;
  renderPrompt();
}
function stashPrompt() {
  if ($("#prompt-editor"))
    state.prompts.files[state.promptFile] = $("#prompt-editor").value;
}
function renderPrompt() {
  $("#prompt-list").innerHTML = Object.keys(state.prompts.files)
    .map(
      (f) =>
        `<button class="list-item prompt-file ${f === state.promptFile ? "selected" : ""}" data-action="prompt-file" data-file="${f}"><b>${promptStages[f.split("/")[0]]}</b><small>${f.endsWith("system.txt") ? "System instruction" : f.endsWith("user.txt") ? "User template" : "Examples & granularity"}</small></button>`,
    )
    .join("");
  $("#prompt-filename").textContent = state.promptFile;
  $("#prompt-editor").value = state.prompts.files[state.promptFile];
  $("#prompt-save-status").textContent = state.promptDirty
    ? "有修改"
    : "已保存";
  $("#prompt-hash").textContent = " · " + state.prompts.hash.slice(0, 12);
}
function settingsView() {
  $("#main").innerHTML =
    head(
      "模型连接",
      "设置摘要生成与谓词发现使用的模型服务。",
      "",
      "SETTINGS / MODEL PROVIDER",
    ) +
    `<div class="settings-grid"><section class="panel settings-panel"><h2>实验模型</h2><form id="settings-form"><label>模型名称<input name="model" required value="${esc(state.settings.model)}" autocomplete="off"></label><label>API Base URL<input name="base_url" type="url" required value="${esc(state.settings.base_url)}" autocomplete="off"></label><label>API Key<input name="api_key" type="text" value="${esc(state.settings.api_key)}" placeholder="${state.settings.key_configured ? "留空保留当前密钥" : "输入 API Key"}" autocomplete="off" spellcheck="false" autocapitalize="none"></label><p class="helper">密钥保存在本机权限为 600 的独立文件中；新实验记录模型名称与 API 地址。开启切分摘要或运行谓词发现时，会向该地址发送相关轨迹、窗口和 Prompt，并产生模型用量。</p><div class="form-error" id="settings-error"></div><button class="btn primary" type="submit">保存模型设置</button></form></section><aside class="side-note"><span class="eyebrow">CURRENT PIPELINE</span><h3>DeepSeek 兼容的发现流程</h3><p>工作台调用仓库中的 PredicateDiscoveryLLM。请求使用 JSON 输出与当前代码中的 thinking、reasoning_effort 设置。</p><ul><li>发现 → 比较 → 模型审核</li><li>每批次人工审核反馈</li><li>修订定义库后继续</li></ul><p>连接状态表示密钥已配置；实际请求结果会记录在实验日志中。</p></aside></div>`;
}

export {
  overview,
  experiments,
  filterExperiments,
  experimentDetail,
  experimentTab,
  experimentOptions,
  reviewView,
  renderPredicateList,
  renderPredicate,
  windowContent,
  dataView,
  loadDataWindows,
  renderDataList,
  selectDataWindow,
  tasks,
  promptsView,
  stashPrompt,
  renderPrompt,
  settingsView,
};
