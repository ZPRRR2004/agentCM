// Routing, user actions, persistence, and live updates.
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
import {
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
} from "./views.js";
import {
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
} from "./forms.js";

import { newPreprocess, fillPreprocessPicker, updatePreprocessSelection, preprocessBody, loadPreprocessComparison } from "./preprocessing.js";
import { scheduleSplitPreview } from "./split-preview.js";
import { deleteExperimentDialog, deletedExperimentsDialog } from "./experiment-management.js";
import { startBrowserSession } from "./browser-session.js";
import { fillPredicateWindows, selectedPredicateWindows, selectPredicateTrajectory, updatePredicateSelection } from "./predicate-selection.js";

async function refresh() {
  const data = await api("bootstrap");
  Object.assign(state, data);
  if (state.session_mode === 'on-demand') startBrowserSession(state.token);
  scheduleRefresh();
  nav();
  $("#sync-status").textContent =
    "本地数据已同步 · " +
    new Date().toLocaleTimeString("zh-CN", {
      hour: "2-digit",
      minute: "2-digit",
    });
}
async function route() {
  if (state.view === "prompts") stashPrompt();
  const epoch = ++state.epoch;
  const [view = "overview", id, name] = location.hash.slice(1).split("/");
  state.view = view === "experiment" ? "experiments" : view;
  nav();
  try {
    if (view === "experiment") {
      const e = await api("experiment?" + query({ id }));
      if (epoch === state.epoch) experimentDetail(e);
    } else if (view === "review") {
      await reviewView(id, name ? decodeURIComponent(name) : null);
    } else if (view === "data") {
      await dataView();
    } else if (view === "prompts") {
      await promptsView();
    } else if (view === "experiments") {
      experiments();
    } else if (view === "tasks") {
      tasks();
    } else if (view === "settings") {
      settingsView();
    } else {
      state.view = "overview";
      overview();
      nav();
    }
  } catch (error) {
    $("#main").innerHTML = (view === 'experiment' ? experimentNavigation() : '') + empty(esc(error.message));
    toast(error.message, true);
  }
}
const actions = {
  navigate: (el) => (location.hash = el.dataset.view),
  "new-experiment": newExperiment,
  "delete-experiment": (el) => deleteExperimentDialog(el.dataset.id),
  "deleted-experiments": deletedExperimentsDialog,
  "confirm-delete-experiment": async (el) => {
    await api('experiment/delete', { id: el.dataset.id });
    closeModal();
    state.detail = null;
    await refresh();
    if (location.hash === '#experiments') await route();
    else location.hash = 'experiments';
    toast('实验已移至回收站');
  },
  "restore-experiment": async (el) => {
    await api('experiment/restore', { id: el.dataset.id });
    await refresh();
    experiments();
    await deletedExperimentsDialog();
    toast('实验已恢复');
  },
  "new-split": (el) => newSplit(el.dataset.source),
  "new-preprocess": newPreprocess,
  "clear-preprocess-selection": () => updatePreprocessSelection(false),
  "attach-input": attachInputModal,
  "new-predicate": (el) => newPredicate(el.dataset.source),
  "clear-predicate-selection": () => updatePredicateSelection(false),
  "close-modal": closeModal,
  "new-task": () => editTask(),
  "edit-task": (el) => editTask(el.dataset.id),
  "delete-task": async (el) => {
    state.tasks = await api("task", { id: el.dataset.id, delete: true });
    closeModal();
    tasks();
    toast("任务已删除");
  },
  "task-done": async (el) => {
    state.tasks = await api("task", { id: el.dataset.id, status: "done" });
    overview();
    toast("任务已完成");
  },
  "start-experiment": async () => {
    await api("experiment/start", { id: state.detail.id });
    toast("实验已启动");
    await refresh();
    await route();
  },
  "stop-experiment": async () => {
    await api("experiment/stop", { id: state.detail.id });
    toast("实验已停止，可从保存点恢复");
    await refresh();
    await route();
  },
  "open-review": () => (location.hash = "review/" + state.detail.id),
  "experiment-tab": (el) => {
    state.experimentTab = el.dataset.tab;
    experimentDetail(state.detail);
  },
  "select-predicate": async (el) => {
    state.selectedPredicate = el.dataset.name;
    renderPredicateList();
    await renderPredicate();
  },
  decision: (el) => {
    state.decision = el.dataset.decision;
    $$(".choice").forEach((b) => b.classList.toggle("selected", b === el));
  },
  "save-review": async () => {
    const value = await api("review", {
      id: state.detail.id,
      name: state.selectedPredicate,
      decision: state.decision,
      notes: $("#review-notes").value,
    });
    state.detail.reviews[state.selectedPredicate] = value;
    renderPredicateList();
    await renderPredicate();
    toast("审核意见已保存");
  },
  "window-modal": async (el) => {
    const result = await api(
      "window?" +
        query({
          dataset: el.dataset.dataset,
          id: el.dataset.window,
          experiment: el.dataset.experiment,
        }),
    );
    modal("轨迹证据与阶段结果", windowContent(result), "", true);
  },
  "data-window": (el) => selectDataWindow(el.dataset.id),
  "prompt-file": (el) => {
    stashPrompt();
    state.promptFile = el.dataset.file;
    renderPrompt();
  },
  "reset-prompt": () => {
    state.prompts.files[state.promptFile] =
      state.prompts.source[state.promptFile];
    state.promptDirty = true;
    renderPrompt();
    toast("当前文件已恢复为源码版本，点击保存生效");
  },
  "save-prompts": async () => {
    stashPrompt();
    state.prompts = await api("prompts", { files: state.prompts.files });
    state.promptDirty = false;
    renderPrompt();
    toast("全部 Prompt 校验通过并已保存");
  },
  "batch-record": async (el) => {
    const b = await api(
      "batch?" + query({ id: state.detail.id, index: el.dataset.index }),
    );
    modal(
      "批次 " + el.dataset.index + " · 审核记录",
      `<h3>人工反馈原文</h3><pre class="json">${esc(b.feedback || "本批次没有人工反馈正文。")}</pre><h3>修订计划</h3><pre class="json">${json(b.plan)}</pre><details><summary>本批审核材料</summary><pre>${esc(b.packet)}</pre></details>`,
      "",
      true,
    );
  },
  feedback: feedbackModal,
  compare: compareModal,
  export: async () => {
    const value = await api("export?" + query({ id: state.detail.id }));
    const link = document.createElement("a"),
      url = URL.createObjectURL(
        new Blob([JSON.stringify(value, null, 2)], {
          type: "application/json",
        }),
      );
    link.href = url;
    link.download = state.detail.id + "-registry.json";
    link.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
    toast("定义库已导出");
  },
};
document.addEventListener("click", async (event) => {
  const target = event.target.closest("[data-action]");
  if (!target || target.disabled) return;
  const action = actions[target.dataset.action];
  if (!action) return;
  try {
    target.disabled = true;
    await action(target);
  } catch (error) {
    toast(error.message, true);
    if ($("#modal-error")) $("#modal-error").textContent = error.message;
  } finally {
    target.disabled = false;
  }
});
document.addEventListener("keydown", (event) => {
  if (
    (event.key === "Enter" || event.key === " ") &&
    event.target.classList.contains("task-card")
  ) {
    event.preventDefault();
    editTask(event.target.dataset.id);
  }
});
document.addEventListener("input", (event) => {
  const id = event.target.id;
  if (
    event.target.closest("#new-split-form") &&
    ["max_window_events", "overlap_events", "split_trajectory_ids"].includes(
      event.target.name,
    )
  )
    scheduleSplitPreview();
  if (id === "predicate-search") renderPredicateList();
  if (id === "window-limit") updatePredicateSelection();
  if (id === "window-search") renderDataList();
  if (id === "experiment-search") filterExperiments();
  if (id === "prompt-editor") {
    state.promptDirty = true;
    $("#prompt-save-status").textContent = "有修改";
  }
});
document.addEventListener("change", async (event) => {
  try {
    const id = event.target.id;
    if (id === "experiment-filter") filterExperiments();
    if (id === "review-experiment")
      location.hash = "review/" + event.target.value;
    if (id === "data-content") await loadDataWindows();
    if (id === "data-dataset") {
      await loadDataWindows();
    }
    if (id === "new-dataset") await fillSourceOptions();
    if (id === "new-source-experiment") await fillPredicateWindows();
    if (id === "split-dataset") await fillSplitSources();
    if (id === "split-preprocess-source") await fillSplitPicker();
    if (id === "attach-preprocess-source") await fillAttachPicker();
    if (id === "preprocess-dataset") fillPreprocessPicker();
    if (id === "preprocess-select-all") updatePreprocessSelection(event.target.checked);
    if (id === "preprocess-result-scope") updatePreprocessSelection();
    if (event.target.name === "preprocess_trajectory_ids") updatePreprocessSelection();
    if (id === "preprocess-trajectory") await loadPreprocessComparison(true);
    if (id === "preprocess-event") await loadPreprocessComparison();
    if (id === "predicate-select-all") updatePredicateSelection(event.target.checked);
    if (event.target.name === "predicate_trajectory_group") selectPredicateTrajectory(event.target);
    if (event.target.name === "window_ids") updatePredicateSelection();
    if (id === "compare-a" || id === "compare-b") await renderComparison();
  } catch (error) {
    toast(error.message, true);
  }
});
document.addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = event.target,
    body = Object.fromEntries(new FormData(form)),
    submit = $(`[type=submit][form="${form.id}"]`) || $("[type=submit]", form);
  if (submit) submit.disabled = true;
  try {
    if (form.id === "new-preprocess-form") {
      const e = await api('experiment/create', preprocessBody(form));
      closeModal();
      await refresh();
      location.hash = 'experiment/' + e.id;
      toast('预处理草稿已保存，可查看前后差异并开始运行');
    }
    if (form.id === "new-split-form") {
      body.kind = "split";
      body.trajectory_ids = $$("#split-trajectory-picker input:checked").map(
        (el) => el.value,
      );
      if (!body.preprocess_experiment_id) throw new Error("请选择已完成的预处理实验");
      if (!body.trajectory_ids.length) throw new Error("请至少选择一条轨迹");
      body.config = {};
      [
        "max_window_events",
        "overlap_events",
        "max_previous_summary_tokens",
        "max_future_summary_tokens",
      ].forEach((k) => {
        body.config[k] = Number(body[k]);
        delete body[k];
      });
      const e = await api("experiment/create", body);
      closeModal();
      await refresh();
      location.hash = "experiment/" + e.id;
      toast(
        e.input_state === "awaiting_input"
          ? "切分参数已保存，接入执行轨迹后即可运行"
          : "切分实验草稿已保存，点击开始运行生成窗口",
      );
    }
    if (form.id === "attach-input-form") {
      const ids = $$("#attach-trajectory-picker input:checked").map(
        (el) => el.value,
      );
      if (!ids.length) throw new Error("请至少选择一条轨迹");
      await api("experiment/input-attach", {
        id: state.detail.id,
        preprocess_experiment_id: body.preprocess_experiment_id,
        trajectory_ids: ids,
      });
      closeModal();
      await refresh();
      await route();
      toast("轨迹快照已保存，可以开始切分");
    }
    if (form.id === "new-experiment-form") {
      body.window_ids = selectedPredicateWindows();
      delete body.predicate_trajectory_group;
      if (!body.window_ids.length) throw new Error("请至少选择一个窗口");
      ["window_limit", "batch_size", "max_retries"].forEach(
        (k) => (body[k] = Number(body[k])),
      );
      const e = await api("experiment/create", body);
      closeModal();
      await refresh();
      state.experimentTab = "registry";
      location.hash = "experiment/" + e.id;
      toast("实验已创建，输入与 Prompt 快照已保存");
    }
    if (form.id === "task-form") {
      if (form.dataset.id) body.id = form.dataset.id;
      state.tasks = await api("task", body);
      closeModal();
      tasks();
      toast("任务已保存");
    }
    if (form.id === "settings-form") {
      state.settings = await api("settings", body);
      nav();
      settingsView();
      toast("模型设置已保存");
    }
    if (form.id === "feedback-form") {
      await api("experiment/feedback", {
        id: state.detail.id,
        token: state.detail.pending.token,
        feedback: body.feedback,
      });
      closeModal();
      await refresh();
      location.hash = "experiment/" + state.detail.id;
      await route();
      toast("批次反馈已提交，实验继续运行");
    }
  } catch (error) {
    const el = $("#modal-error") || $("#settings-error");
    if (el) el.textContent = error.message;
    toast(error.message, true);
  } finally {
    if (submit) submit.disabled = false;
  }
});
let dragged = null;
document.addEventListener("dragstart", (event) => {
  const card = event.target.closest(".task-card");
  if (card) {
    dragged = card.dataset.id;
    event.dataTransfer.setData("text/plain", dragged);
  }
});
document.addEventListener("dragover", (event) => {
  const column = event.target.closest(".kanban-column");
  if (column && dragged) {
    event.preventDefault();
    column.classList.add("dragover");
  }
});
document.addEventListener("dragleave", (event) =>
  event.target.closest(".kanban-column")?.classList.remove("dragover"),
);
document.addEventListener("dragend", () => {
  dragged = null;
  $$(".dragover").forEach((el) => el.classList.remove("dragover"));
});
document.addEventListener("drop", async (event) => {
  const col = event.target.closest(".kanban-column");
  if (col && dragged) {
    event.preventDefault();
    try {
      state.tasks = await api("task", {
        id: dragged,
        status: col.dataset.status,
      });
      tasks();
      toast("任务状态已更新");
    } catch (error) {
      toast(error.message, true);
    }
    dragged = null;
  }
});
window.addEventListener("hashchange", route);
window.addEventListener("beforeunload", (event) => {
  if (state.promptDirty) {
    event.preventDefault();
    event.returnValue = "";
  }
});
async function boot() {
  try {
    await refresh();
    await route();
  } catch (error) {
    $("#main").innerHTML = empty(esc(error.message));
    toast(error.message, true);
  }
}
boot();
let refreshTimer;
function scheduleRefresh(delay) {
  clearTimeout(refreshTimer);
  const active = [state.detail, ...state.experiments].some(e => ["running", "waiting"].includes(e?.status));
  refreshTimer = setTimeout(pollUpdates, delay ?? (document.hidden ? 60000 : active ? 2000 : 30000));
}
async function pollUpdates() {
  try {
    if (document.hidden || $("#modal").open || document.activeElement.matches("input:not([type=checkbox]),textarea,select") ||
        window.getSelection()?.toString()) return;
    if (
      location.hash.startsWith("#experiment/") &&
      ["running", "waiting"].includes(state.detail?.status)
    ) {
      const hash = location.hash, epoch = state.epoch;
      const e = await api("experiment?" + query({ id: state.detail.id }));
      if (location.hash !== hash || state.epoch !== epoch) return;
      experimentDetail(e);
      $("#sync-status").textContent =
        "实验状态已同步 · " + new Date().toLocaleTimeString("zh-CN");
    } else if (
      location.hash === "#experiments" ||
      !location.hash ||
      location.hash === "#overview"
    ) {
      const exps = await api("experiments");
      if (JSON.stringify(exps) !== JSON.stringify(state.experiments)) {
        state.experiments = exps;
        nav();
        if (state.view === "overview") overview();
        else experiments();
      }
    }
  } catch (error) {
    $("#sync-status").textContent = "同步失败 · " + error.message;
  } finally {
    scheduleRefresh();
  }
}
document.addEventListener('visibilitychange', () => scheduleRefresh(document.hidden ? 60000 : 0));
scheduleRefresh(2000);
