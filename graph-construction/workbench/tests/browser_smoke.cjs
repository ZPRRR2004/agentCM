// NODE_PATH=/path/to/node_modules PYTHON_BIN=/path/to/python3 node tests/browser_smoke.cjs
const { chromium } = require("playwright");
const { spawn } = require("node:child_process");
const fs = require("node:fs");
const path = require("node:path");
const assert = require("node:assert/strict");
const root = path.resolve(__dirname, "..");
const fixture = spawn(
  process.env.PYTHON_BIN || "python3",
  [path.join(__dirname, "browser_fixture.py")],
  { cwd: root, stdio: ["ignore", "pipe", "inherit"] },
);
let browser;
let catalogPath;
const errors = [];
async function run() {
  const url = await new Promise((resolve, reject) => {
    let output = "";
    fixture.stdout.on("data", (chunk) => {
      output += chunk;
      if (output.includes("\n")) {
        try {
          const setup = JSON.parse(output.split("\n")[0]);
          catalogPath = setup.catalog_path;
          resolve(setup.url);
        } catch (e) {
          reject(e);
        }
      }
    });
    fixture.on("exit", (code) => reject(new Error("Fixture exited " + code)));
  });
  browser = await chromium.launch({
    executablePath:
      process.env.CHROME_BIN ||
      "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    headless: true,
  });
  const page = await browser.newPage({
    viewport: { width: 1440, height: 1000 },
  });
  page.on("pageerror", (err) => errors.push(err.message));
  const open = async (hash) => {
    await page.goto(url + "/" + hash);
    await page.locator("#main h1").waitFor();
  };
  const token = (await (await page.request.get(url + '/api/bootstrap')).json()).token;
  const post = async (route, body) => {
    const response = await page.request.post(url + '/api/' + route, {
      headers: { 'X-Workspace-Token': token }, data: body });
    assert(response.ok(), await response.text());
    return response.json();
  };
  const prepare = async dataset => {
    const e = await post('experiment/create', { kind: 'preprocess', title: 'Prepared ' + dataset,
      dataset_id: dataset, config: { deduplicate_observation: false, remove_source_lines: false } });
    await post('experiment/start', { id: e.id });
    for (let i = 0; i < 100; i++) {
      const status = await (await page.request.get(url + '/api/experiment?id=' + e.id)).json();
      if (status.status === 'completed') return e.id;
      assert.notEqual(status.status, 'failed');
      await new Promise(resolve => setTimeout(resolve, 100));
    }
    throw new Error('Preprocessing did not finish');
  };
  await prepare('fixture-v1');
  const preparedAlternative = await prepare('alternative-v2');
  await open("#overview");
  assert.equal(await page.locator(".metric").count(), 4);
  await open("#tasks");
  await page.getByRole("button", { name: "添加任务", exact: true }).click();
  await page.locator("[name=title]").fill("Browser <script>test</script>");
  await page.locator("[name=notes]").fill("A reproducible review task.");
  await page.locator("[name=status]").selectOption("doing");
  await page.getByRole("button", { name: "保存任务", exact: true }).click();
  await page
    .locator(".kanban-column[data-status=doing]")
    .getByText("Browser <script>test</script>")
    .waitFor();
  await page.reload();
  await page
    .getByRole("button", { name: "编辑任务：Browser <script>test</script>" })
    .click();
  await page.locator("[name=status]").selectOption("review");
  await page.getByRole("button", { name: "保存任务", exact: true }).click();
  await page
    .locator(".kanban-column[data-status=review]")
    .getByText("Browser <script>test</script>")
    .waitFor();

  await open("#prompts");
  const original = await page.locator("#prompt-editor").inputValue();
  await page
    .locator("#prompt-editor")
    .fill(original + "\nBrowser validation note.");
  await page.getByRole("button", { name: "校验并保存" }).click();
  await page.getByText("全部 Prompt 校验通过并已保存").waitFor();
  await page.reload();
  await page.locator("#prompt-editor").waitFor();
  assert(
    (await page.locator("#prompt-editor").inputValue()).includes(
      "Browser validation note.",
    ),
  );
  await page.getByRole("button", { name: "恢复当前文件" }).click();
  await page.getByRole("button", { name: "校验并保存" }).click();
  await page.getByText("全部 Prompt 校验通过并已保存").waitFor();

  await open("#review");
  await page
    .getByText("创建并运行一次谓词实验后，在这里逐项审核定义。")
    .waitFor();
  await open("#data");
  assert.equal(await page.locator("#data-version,#data-input-set").count(), 0);
  await page.locator("#data-dataset").selectOption("alternative-v2");
  await page
    .locator("#window-detail h2")
    .filter({ hasText: "测试数据集 B v2" })
    .waitFor();
  assert.equal(await page.locator("#window-detail .event").count(), 3);
  await page.getByRole("button", { name: "创建切分实验", exact: true }).click();
  assert.equal(
    await page.locator("#split-dataset").inputValue(),
    "alternative-v2",
  );
  assert.equal(await page.locator("[name=max_window_events]").inputValue(), "");
  assert.deepEqual(await page.locator('#split-preprocess-source option').evaluateAll(nodes => nodes.map(n => n.value)), [preparedAlternative]);
  assert.equal(await page.locator("[name=max_window_tokens]").count(), 0);
  const fillSplit = async (title, events) => {
    await page.locator("[name=title]").fill(title);
    for (const [key, value] of Object.entries({
      max_window_events: events,
      overlap_events: 0,
      max_previous_summary_tokens: 0,
      max_future_summary_tokens: 0,
    })) {
      await page.locator(`[name=${key}]`).fill(String(value));
    }
    await page.locator("#split-preview[data-window-count]").waitFor();
    assert.equal(
      await page.locator("#split-preview").getAttribute("data-window-count"),
      String(Math.ceil(3 / events)),
    );
    await page
      .getByRole("button", { name: "创建切分实验草稿", exact: true })
      .click();
    await page.getByRole("heading", { name: title, exact: true }).waitFor();
    assert.equal(await page.locator(".metric-value .pill.draft").count(), 1);
    await page.getByRole("button", { name: "开始运行", exact: true }).click();
    await page
      .locator(".metric-value .pill.completed")
      .waitFor({ timeout: 20000 });
    return page.url().split("#experiment/")[1];
  };
  const alternativeSplit = await fillSplit("Alternative split", 2);
  assert.equal(await page.locator("[data-action=window-modal]").count(), 2);
  await page.locator("[data-action=window-modal]").first().click();
  await page
    .getByRole("heading", { name: "轨迹证据与阶段结果", exact: true })
    .waitFor();
  assert.equal(await page.locator("#modal .event").count(), 2);
  await page.getByRole("button", { name: "关闭", exact: true }).click();
  await open("#data");
  await page.locator("#data-dataset").selectOption("fixture-v1");
  await page.getByRole("button", { name: "创建切分实验", exact: true }).click();
  const fixtureSplit = await fillSplit("Fixture split", 1);
  assert.equal(await page.locator("[data-action=window-modal]").count(), 3);
  const output = path.join(root, "runs/browser-checks");
  fs.mkdirSync(output, { recursive: true });
  await page.screenshot({
    path: path.join(output, "splitting-result.png"),
    fullPage: true,
  });
  await page
    .getByRole("button", { name: "基于此切分发现谓词", exact: true })
    .click();
  assert.equal(
    await page.locator("#new-source-experiment").inputValue(),
    fixtureSplit,
  );
  assert.equal(await page.locator("#new-dataset").inputValue(), "fixture-v1");
  await page.locator("[name=title]").fill("UI pipeline validation");
  await page.locator("#trajectory-picker input:checked").first().waitFor();
  await page.locator("[name=window_limit]").fill("3");
  await page.locator("[name=batch_size]").fill("2");
  await page.getByRole("button", { name: "创建实验草稿", exact: true }).click();
  await page.getByRole("heading", { name: "UI pipeline validation" }).waitFor();
  const predicateA = page.url().split("#experiment/")[1];
  await page.getByRole("button", { name: "开始运行", exact: true }).click();
  await page
    .getByRole("button", { name: "填写批次反馈" })
    .waitFor({ timeout: 20000 });
  await page.getByRole("button", { name: "审核定义", exact: true }).click();
  await page.locator("[data-action=select-predicate][data-name=USES]").click();
  await page.locator("#review-notes").fill("Rename USES to USES_INFORMATION.");
  await page.getByRole("button", { name: "修订", exact: true }).click();
  await page.getByRole("button", { name: "保存审核", exact: true }).click();
  await page.getByText("审核意见已保存").waitFor();
  await page.reload();
  await page.locator("#review-notes").waitFor();
  // Re-select the edited predicate after reloading the review queue.
  await page.locator("[data-action=select-predicate][data-name=USES]").click();
  assert.equal(
    await page.locator("#review-notes").inputValue(),
    "Rename USES to USES_INFORMATION.",
  );
  await page.locator(".evidence-item button").first().click();
  await page.getByRole("heading", { name: "轨迹证据与阶段结果" }).waitFor();
  assert((await page.locator("#modal .event").count()) > 0);
  await page.getByRole("button", { name: "关闭", exact: true }).click();

  await page.getByRole("button", { name: "提交批次反馈", exact: true }).click();
  assert(
    (await page.locator("[name=feedback]").inputValue()).includes(
      "Rename USES",
    ),
  );
  await page
    .getByRole("button", { name: "提交反馈并继续", exact: true })
    .click();
  await page
    .locator(".metric-value .pill.completed")
    .waitFor({ timeout: 20000 });
  await page
    .getByRole("link", { name: "USES_INFORMATION", exact: true })
    .waitFor();
  await page.getByRole("button", { name: "批次与反馈", exact: true }).click();
  await page
    .getByRole("button", { name: "反馈记录", exact: true })
    .first()
    .click();
  await page.getByRole("heading", { name: "批次 1 · 审核记录" }).waitFor();
  assert(
    (await page.locator("#modal-content").innerText()).includes("Rename USES"),
  );
  await page.getByRole("button", { name: "关闭", exact: true }).click();

  await page.screenshot({
    path: path.join(output, "experiment.png"),
    fullPage: true,
  });
  await open("#experiments");
  await page.getByRole("button", { name: "对比实验", exact: true }).click();
  await page.locator("#compare-a").selectOption(alternativeSplit);
  await page.locator("#compare-b").selectOption(fixtureSplit);
  await page.locator(".change-row").first().waitFor();
  await page.getByText("生成窗口", { exact: true }).waitFor();
  await page.getByRole("button", { name: "关闭", exact: true }).click();
  await page
    .getByRole("link", { name: "Alternative split", exact: false })
    .click();
  await page
    .getByRole("button", { name: "基于此切分发现谓词", exact: true })
    .click();
  await page.locator("[name=title]").fill("Dataset B comparison");
  await page.locator("#trajectory-picker input:checked").first().waitFor();
  await page.getByRole("button", { name: "创建实验草稿", exact: true }).click();
  await page.getByRole("heading", { name: "Dataset B comparison" }).waitFor();
  const predicateB = page.url().split("#experiment/")[1];
  await page.getByRole("button", { name: "窗口与阶段", exact: true }).click();
  await page
    .getByRole("cell", { name: "测试数据集 B v2", exact: true })
    .first()
    .waitFor();
  await open("#experiments");
  await page.locator("#experiment-filter").selectOption("alternative-v2");
  assert.equal(await page.locator("#experiment-list tbody tr").count(), 3);
  await page.getByRole("button", { name: "对比实验", exact: true }).click();
  await page.locator("#compare-a").selectOption(predicateA);
  await page.locator("#compare-b").selectOption(predicateB);
  await page.locator(".change-row").first().waitFor();
  await page.getByRole("button", { name: "关闭", exact: true }).click();
  await open("#data");
  await page.locator("#data-dataset").selectOption("official-fixture-1.0");
  await page
    .locator("#dataset-stats")
    .filter({ hasText: "2 个官方任务" })
    .waitFor();
  await page
    .locator("#window-detail h2")
    .filter({ hasText: "alpha-task" })
    .waitFor();
  assert.equal(await page.locator("#window-list button").count(), 2);
  assert.equal(await page.locator("#window-detail .event").count(), 0);
  assert.equal(await page.locator("#window-detail script").count(), 0);
  assert.equal(await page.evaluate(() => window.injected), undefined);
  assert.equal(
    await page
      .getByRole("button", { name: "创建切分实验", exact: true })
      .isDisabled(),
    false,
  );
  await page.getByText("原版文件清单 · 5 个文件", { exact: true }).click();
  await page.getByText("solution/fixture.txt", { exact: true }).waitFor();
  await page.getByRole("button", { name: "创建切分实验", exact: true }).click();
  assert.equal(await page.locator("[name=max_window_events]").inputValue(), "");
  assert.equal(await page.getByRole('button', { name: '创建切分实验草稿', exact: true }).isDisabled(), true);
  assert.equal(await page.locator('#split-trajectory-picker input').count(), 0);
  await page.getByText('这个数据集需要先完成一次轨迹预处理实验。完成后可在这里选择处理结果。', { exact: true }).waitFor();
  await page.getByRole('button', { name: '关闭', exact: true }).click();
  const catalog = JSON.parse(fs.readFileSync(catalogPath, "utf8"));
  catalog.datasets.find(
    (d) => d.id === "official-fixture-1.0",
  ).normalized_path = "fixture-v1/normalized";
  fs.writeFileSync(catalogPath, JSON.stringify(catalog));
  const officialPrepared = await prepare('official-fixture-1.0');
  await page.getByRole('button', { name: '创建切分实验', exact: true }).click();
  await page.locator('#split-preprocess-source').waitFor();
  assert.equal(await page.locator('#split-preprocess-source').inputValue(), officialPrepared);
  await fillSplit('Official processed split', 1);
  assert.equal(await page.locator('[data-action=window-modal]').count(), 3);
  await open("#data");
  await page.locator("#data-dataset").selectOption("official-fixture-1.0");
  await page.locator("#data-content").selectOption("trajectories");
  await page.locator("#window-detail .event").first().waitFor();
  assert.equal(await page.locator("#window-detail .event").count(), 3);
  await open("#settings");
  const keyInput = page.locator("[name=api_key]");
  assert.equal(await keyInput.getAttribute("type"), "text");
  assert.equal(await keyInput.inputValue(), "test-key-local-only");
  const replacementKey = 'test-key-local-only-2<&"';
  await keyInput.fill(replacementKey);
  await page.getByRole("button", { name: "保存模型设置", exact: true }).click();
  await page.getByText("模型设置已保存", { exact: true }).waitFor();
  assert.equal(await keyInput.inputValue(), replacementKey);
  await page.reload();
  await keyInput.waitFor();
  assert.equal(await keyInput.getAttribute("type"), "text");
  assert.equal(await keyInput.inputValue(), replacementKey);
  await open("#overview");
  await page.screenshot({
    path: path.join(output, "overview.png"),
    fullPage: true,
  });
  await page.setViewportSize({ width: 390, height: 844 });
  for (const hash of [
    "#overview",
    "#experiments",
    "#review",
    "#tasks",
    "#data",
    "#prompts",
    "#settings",
  ]) {
    await open(hash);
    await page.waitForTimeout(150);
    assert.equal(
      await page.evaluate(
        () => document.documentElement.scrollWidth > innerWidth,
      ),
      false,
      "Mobile overflow " + hash,
    );
  }
  await open("#overview");
  await page.screenshot({
    path: path.join(output, "mobile.png"),
    fullPage: true,
  });
  assert.deepEqual(errors, []);
  console.log(
    "PASS: task persistence, prompt snapshots, predicate review, evidence, comparison, real worker + web feedback, batch audit, flat datasets, splitting parameters/results/comparison, explicit split-to-predicate lineage, original task packages and safe rendering, settings, 7 mobile routes.",
  );
}
run()
  .catch((e) => {
    console.error(e);
    process.exitCode = 1;
  })
  .finally(async () => {
    if (browser) await browser.close();
    fixture.kill("SIGINT");
  });
