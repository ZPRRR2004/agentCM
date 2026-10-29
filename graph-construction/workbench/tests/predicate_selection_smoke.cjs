// Isolated UI check: pick individual, nonconsecutive windows and freeze exactly those inputs.
const { chromium } = require('playwright');
const { spawn } = require('node:child_process');
const assert = require('node:assert/strict');
const path = require('node:path');
const fs = require('node:fs');
const root = path.resolve(__dirname, '..');
const fixture = spawn(process.env.PYTHON_BIN || 'python3', [path.join(__dirname, 'browser_fixture.py')],
  { cwd: root, stdio: ['ignore', 'pipe', 'inherit'] });
let browser;
async function run() {
  const url = await new Promise((resolve, reject) => {
    let output = '';
    fixture.stdout.on('data', chunk => {
      output += chunk;
      if (output.includes('\n')) resolve(JSON.parse(output.split('\n')[0]).url);
    });
    fixture.on('exit', code => reject(new Error('Fixture exited: ' + code)));
  });
  browser = await chromium.launch({ headless: true,
    executablePath: process.env.CHROME_BIN || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' });
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  const get = async route => (await page.request.get(url + '/api/' + route)).json();
  const token = (await get('bootstrap')).token;
  const post = async (route, data) => {
    const response = await page.request.post(url + '/api/' + route,
      { headers: { 'X-Workspace-Token': token }, data });
    assert(response.ok(), await response.text());
    return response.json();
  };
  const complete = async data => {
    const experiment = await post('experiment/create', data);
    await post('experiment/start', { id: experiment.id });
    for (let i = 0; i < 100; i++) {
      const e = await get('experiment?id=' + experiment.id);
      if (e.status === 'completed') return e;
      assert.notEqual(e.status, 'failed');
      await new Promise(resolve => setTimeout(resolve, 100));
    }
    throw new Error('Experiment did not finish');
  };
  const prepare = async (dataset, events) => {
    const pre = await complete({ kind: 'preprocess', title: 'Prepared ' + dataset, dataset_id: dataset,
      config: { deduplicate_observation: false, remove_source_lines: false } });
    return complete({ kind: 'split', title: 'Windows ' + dataset, dataset_id: dataset,
      preprocess_experiment_id: pre.id, config: { max_window_events: events, overlap_events: 0,
        max_previous_summary_tokens: 0, max_future_summary_tokens: 0 } });
  };
  const source = await prepare('fixture-v1', 1);
  const other = await prepare('alternative-v2', 3);
  await page.goto(url + '/#experiment/' + source.id);
  await page.getByRole('button', { name: '基于此切分发现谓词', exact: true }).click();
  const ready = () => page.locator('#trajectory-picker[data-ready=true]').waitFor();
  await ready();
  const master = page.locator('#predicate-select-all');
  const group = page.locator('input[name=predicate_trajectory_group]');
  const windows = page.locator('input[name=window_ids]');
  const selected = () => page.locator('input[name=window_ids]:checked').count();
  const limit = page.locator('#window-limit');
  const submit = page.getByRole('button', { name: '创建实验草稿', exact: true });
  const clear = page.getByRole('button', { name: '取消全选', exact: true });
  assert.equal(await windows.count(), 3);
  assert(await master.isChecked());
  await clear.click();
  assert.equal(await selected(), 0);
  assert(await submit.isDisabled());
  assert.equal(await limit.inputValue(), '');
  await master.check();
  assert.equal(await selected(), 3);
  await master.uncheck();
  assert.equal(await selected(), 0);
  await group.check();
  assert.equal(await selected(), 3);
  await group.uncheck();
  assert.equal(await selected(), 0);
  await page.locator('.predicate-window-group > summary > span').click();
  await windows.nth(0).check();
  assert.equal(await limit.inputValue(), '1');
  await windows.nth(2).check();
  assert.equal(await limit.inputValue(), '2');
  assert.equal(await selected(), 2);
  assert(await master.evaluate(el => el.indeterminate));
  assert(await group.evaluate(el => el.indeterminate));
  assert.equal(await page.locator('#predicate-selection-count').innerText(), '已选 2 个窗口');
  await limit.fill('3');
  assert(await submit.isDisabled());
  await limit.fill('1');
  assert.equal(await page.locator('#predicate-selection-count').innerText(), '已选 2 个窗口，这次处理前 1 个');
  await limit.fill('2');
  const screenshots = path.join(root, 'runs/browser-checks');
  fs.mkdirSync(screenshots, { recursive: true });
  await page.screenshot({ path: path.join(screenshots, 'predicate-window-selection.png') });
  await page.setViewportSize({ width: 390, height: 844 });
  await page.locator('.predicate-window-group').scrollIntoViewIfNeeded();
  assert(await page.locator('.modal-body').evaluate(el => el.scrollWidth <= el.clientWidth + 1));
  assert(await page.locator('#trajectory-picker').evaluate(el => el.scrollWidth <= el.clientWidth + 1), 'Window choices overflow on mobile');
  await page.screenshot({ path: path.join(screenshots, 'predicate-window-selection-mobile.png') });
  await page.setViewportSize({ width: 1440, height: 1000 });
  // Switching source must clear the previous IDs and reset limits.
  await page.locator('#new-dataset').selectOption('alternative-v2');
  await ready();
  assert.equal(await page.locator('#new-source-experiment').inputValue(), other.id);
  assert.equal(await windows.count(), 1);
  assert.equal(await limit.inputValue(), '1');
  await page.locator('#new-dataset').selectOption('fixture-v1');
  await ready();
  assert.equal(await windows.count(), 3);
  await clear.click();
  await page.locator('.predicate-window-group > summary > span').click();
  await windows.nth(0).check();
  await windows.nth(2).check();
  await page.locator('#new-experiment-form [name=title]').fill('Only first and third windows');
  const responsePromise = page.waitForResponse(response => response.url().endsWith('/api/experiment/create'));
  await submit.click();
  const saved = await (await responsePromise).json();
  const expected = [source.windows[0].id, source.windows[2].id];
  assert.deepEqual(saved.window_ids, expected);
  assert.equal(saved.window_count, 2);
  const persisted = await get('experiment?id=' + saved.id);
  assert.deepEqual(persisted.windows.map(w => w.id), expected);
  await page.reload();
  await page.getByRole('heading', { name: saved.title, exact: true }).waitFor();
  assert.deepEqual(errors, []);
  console.log(JSON.stringify({ ok: true, selected_windows: expected.length,
    checks: ['all/none', 'group selection', 'partial selection', 'limit', 'source switch', 'saved inputs', 'mobile'] }));
}
run().catch(error => { console.error(error); process.exitCode = 1; }).finally(async () => {
  if (browser) await browser.close();
  fixture.kill('SIGINT');
});
