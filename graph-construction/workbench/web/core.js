/* AgentCM Workbench — local-first, dependency-free client. */
const $ = (s, el = document) => el.querySelector(s);
const $$ = (s, el = document) => [...el.querySelectorAll(s)];
const esc = (v) =>
  String(v ?? "").replace(
    /[&<>"']/g,
    (c) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[
        c
      ],
  );
const json = (v) => esc(JSON.stringify(v, null, 2));
const paths = {
  overview: "M3 3h7v7H3z M14 3h7v7h-7z M3 14h7v7H3z M14 14h7v7h-7z",
  experiments: "M9 3h6 M10 3v7l-6 9a1 1 0 001 2h14a1 1 0 001-2l-6-9V3 M7 15h10",
  review: "M14 3H5v18h14V9 M14 3v6h5 M8 14l2 2 5-5",
  tasks: "M4 4h16v16H4z M9 4v16 M15 4v16 M6 8h1 M11 8h2 M17 8h1",
  data: "M4 6c0-4 16-4 16 0s-16 4-16 0v12c0 4 16 4 16 0V6 M4 12c0 4 16 4 16 0",
  prompts: "M8 5L2 12l6 7 M16 5l6 7-6 7 M14 3l-4 18",
  settings:
    "M12 8a4 4 0 100 8 4 4 0 000-8 M12 1v4 M12 19v4 M1 12h4 M19 12h4 M4 4l3 3 M17 17l3 3 M4 20l3-3 M17 7l3-3",
  plus: "M12 4v16 M4 12h16",
  arrow: "M5 12h14 M13 6l6 6-6 6",
  back: "M19 12H5 M11 6l-6 6 6 6",
  trash: "M3 6h18 M9 6V3h6v3 M5 6l1 15h12l1-15 M10 10v7 M14 10v7",
  download: "M12 3v12 M7 10l5 5 5-5 M4 16v5h16v-5",
  play: "M7 4l14 8-14 8z",
  compare: "M4 5h6v14H4z M14 5h6v14h-6z",
  search: "M16 16l5 5 M10 3a7 7 0 100 14 7 7 0 000-14",
};
const icon = (name) =>
  `<span class="icon"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="${paths[name] || paths.overview}"/></svg></span>`;
const labels = {
  overview: "研究概览",
  experiments: "实验管理",
  review: "谓词审核",
  tasks: "任务看板",
  data: "数据集",
  prompts: "Prompt 工作室",
  settings: "模型设置",
};
const statusLabels = {
  draft: "草稿",
  running: "运行中",
  waiting: "等待审核",
  completed: "已完成",
  failed: "运行失败",
  stopped: "已停止",
  interrupted: "可恢复",
  ready: "就绪",
  keep: "保留",
  revise: "修订",
  merge: "合并",
  delete: "删除",
  pending: "待审核",
  backlog: "待开始",
  doing: "进行中",
  review: "待 Review",
  done: "已完成",
};
const pill = (status, text) =>
  `<span class="pill ${esc(status)}">${esc(text || statusLabels[status] || status)}</span>`;
const btn = (label, action, style = "", attrs = "", ico = "") =>
  `<button class="btn ${style}" data-action="${action}" ${attrs}>${ico ? icon(ico) : ""}${label}</button>`;
const state = {
  datasets: [],
  experiments: [],
  tasks: [],
  settings: {},
  token: "",
  view: "overview",
  epoch: 0,
  detail: null,
  selectedPredicate: null,
  decision: "pending",
  dataset: null,
  dataSelection: {},
  window: null,
  prompts: null,
  promptFile: "common/granularity_examples.txt",
  promptDirty: false,
  experimentTab: "registry",
  experimentFilters: { search: "", dataset: "all" },
  search: "",
};
let toastTimer;
function toast(message, error = false) {
  const el = $("#toast");
  el.textContent = message;
  el.className = "show" + (error ? " error" : "");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => (el.className = ""), 4500);
}
async function api(path, body) {
  const result = await fetch(
    "/api/" + path,
    body === undefined
      ? {}
      : {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-Workspace-Token": state.token,
          },
          body: JSON.stringify(body),
        },
  );
  const value = await result.json();
  if (!result.ok) throw new Error(value.error || "请求失败");
  return value;
}
function query(values) {
  return new URLSearchParams(
    Object.entries(values).filter(([, v]) => v !== null && v !== undefined),
  ).toString();
}
function head(title, subtitle, actions = "", eyebrow = "RESEARCH WORKSPACE") {
  return `<div class="page-head"><div><span class="eyebrow">${eyebrow}</span><h1>${esc(title)}</h1><p>${esc(subtitle)}</p></div><div class="head-actions">${actions}</div></div>`;
}
function experimentDeleteButton(e, small = false) {
  const active = ["running", "waiting"].includes(e.status);
  return btn(small ? '删除' : '删除实验', 'delete-experiment', 'danger' + (small ? ' small' : ''),
    `data-id="${esc(e.id)}" ${active ? 'disabled title="请先停止实验，再删除"' : ''} aria-label="删除实验：${esc(e.title)}"`, 'trash');
}
function experimentNavigation(e) {
  return `<div class="experiment-navigation"><a class="btn" href="#experiments">${icon('back')}返回实验管理</a>${e ? experimentDeleteButton(e) : ''}</div>`;
}
function metric(title, value, unit, note, ico) {
  return `<div class="metric"><div class="metric-top">${title}${icon(ico)}</div><div class="metric-value">${value}<span>${unit}</span></div><div class="metric-note">${note}</div></div>`;
}
function empty(text) {
  return `<div class="empty">${icon("data")}<div>${text}</div></div>`;
}
function nav() {
  $("#navigation").innerHTML = Object.entries(labels)
    .map(
      ([id, label]) =>
        `<a href="#${id}" class="nav-item ${state.view === id ? "active" : ""}">${icon(id)}<span>${label}</span>${id === "experiments" ? `<span class="nav-count">${state.experiments.length}</span>` : ""}</a>`,
    )
    .join("");
  $("#page-label").textContent = labels[state.view] || "实验详情";
  $("#connection").classList.toggle("ready", state.settings.key_configured);
  $("#connection span").textContent = state.settings.key_configured
    ? state.settings.model
    : "配置模型，开始实验";
}
function progress(e) {
  return `${e.completed}<span class="muted"> / ${e.total}</span><div class="progress"><i style="width:${Math.round((e.completed / Math.max(1, e.total)) * 100)}%"></i></div>`;
}
function experimentTable(experiments) {
  if (!experiments.length)
    return empty("创建预处理、轨迹切分或谓词发现实验。");
  return `<div class="table-wrap"><table><thead><tr><th>实验名称</th><th>类型 / 数据集</th><th>执行进度</th><th>产物</th><th>状态</th><th>操作</th></tr></thead><tbody>${experiments.map((e) => `<tr data-experiment-id="${e.id}"><td><a class="experiment-name" href="#experiment/${e.id}">${esc(e.title)}<small>${esc(e.model || "本地处理")} · ${esc((e.prompt_hash || e.input_hash).slice(0, 8))}</small></a></td><td>${e.kind === "preprocess" ? "轨迹预处理" : e.kind === "split" ? "轨迹切分" : "谓词发现"}<small class="muted"> · ${esc(e.dataset_name)}</small></td><td>${progress(e)}<small class="muted">${e.unit}</small></td><td>${e.kind === "preprocess" ? e.completed + " 条轨迹" : e.kind === "split" ? e.produced_windows + " 窗口" : e.registry_count + " 谓词"}</td><td>${pill(e.status)}</td><td><div class="experiment-row-actions"><a class="table-action" href="#experiment/${e.id}">查看 ↗</a>${experimentDeleteButton(e, true)}</div></td></tr>`).join("")}</tbody></table></div>`;
}
function chart(e) {
  if (!e?.batches.length)
    return empty("完成一个批次后，这里将显示定义数量的变化。");
  const bs = e.batches,
    max = Math.max(...bs.flatMap((b) => [b.before, b.after]), 1);
  const width = 600,
    height = 170,
    x = (i) => 48 + (i * (width - 74)) / Math.max(bs.length - 1, 1),
    y = (v) => height - 23 - (v / max) * (height - 45);
  const points = (key) => bs.map((b, i) => `${x(i)},${y(b[key])}`).join(" ");
  return `<div class="chart"><div class="chart-labels"><span><i class="legend"></i>批次最终库</span><span><i class="legend muted"></i>窗口发现后</span><span style="margin-left:auto">${esc(e.title)}</span></div><svg viewBox="0 0 ${width} ${height}" role="img" aria-label="每批次定义数量：${esc(bs.map((b) => "批次" + b.index + "反馈前" + b.before + "反馈后" + b.after).join("；"))}">${[0, 0.5, 1].map((f) => `<path d="M40 ${y(max * f)}H584" stroke="#e9eee2" stroke-dasharray="3 4"/><text x="25" y="${y(max * f) + 3}" fill="#9ba68f" font-size="9" text-anchor="end">${Math.round(max * f)}</text>`).join("")}<polygon points="${x(0)},${y(0)} ${points("after")} ${x(bs.length - 1)},${y(0)}" fill="#ecf2e6"/><polyline points="${points("before")}" fill="none" stroke="#d1b17a" stroke-width="2" stroke-dasharray="4 4"/><polyline points="${points("after")}" fill="none" stroke="#7e9e6e" stroke-width="2.5"/>${bs.map((b, i) => `<circle cx="${x(i)}" cy="${y(b.after)}" r="4" fill="#fff" stroke="#7e9e6e" stroke-width="2"/><text x="${x(i)}" y="${y(b.after) - 10}" text-anchor="middle" fill="#6e875b" font-size="10">${b.after}</text><text x="${x(i)}" y="${height - 3}" text-anchor="middle" fill="#9ba68f" font-size="9">B${b.index} · ${b.end} 窗口</text>`).join("")}</svg></div>`;
}

export {
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
};
