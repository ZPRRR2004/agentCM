// Flat dataset choices; generated windows belong to splitting experiments.
import { $, esc, state } from "./core.js";

function selectedData(values = {}) {
  const dataset =
    state.datasets.find((d) => d.id === values.dataset_id) || state.datasets[0];
  return { dataset };
}
function datasetControls(prefix, values = {}) {
  const { dataset } = selectedData(values);
  return `<div class="dataset-controls"><label>数据集<select id="${prefix}-dataset" name="dataset_id" aria-label="选择数据集">${state.datasets.map((d) => `<option value="${esc(d.id)}" ${d.id === dataset?.id ? "selected" : ""}>${esc(d.name)}</option>`).join("")}</select></label></div>`;
}
function controlValues(prefix) {
  return { dataset_id: $(`#${prefix}-dataset`).value };
}
function sourceQuery(values) {
  return { dataset: values.dataset_id };
}
export { selectedData, datasetControls, controlValues, sourceQuery };
