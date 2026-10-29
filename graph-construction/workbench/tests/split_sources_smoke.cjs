// Completed upstream artifacts are the only selectable inputs for splitting.
const { chromium } = require('playwright');
const { spawn } = require('node:child_process');
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const root = path.resolve(__dirname, '..');
const fixture = spawn(process.env.PYTHON_BIN || 'python3', [path.join(__dirname, 'browser_fixture.py'), '--selection'],
  { cwd: root, stdio: ['ignore', 'pipe', 'inherit'] });
let browser;
async function run() {
  const { url, catalog_path: catalogPath } = await new Promise((resolve, reject) => {
    let output = '';
    fixture.stdout.on('data', data => { output += data; if (output.includes('\n')) resolve(JSON.parse(output.split('\n')[0])); });
    fixture.on('exit', code => reject(new Error('Fixture exited ' + code)));
  });
  browser = await chromium.launch({ executablePath: process.env.CHROME_BIN || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless: true });
  const page = await browser.newPage({ viewport: { width: 1440, height: 1100 } });
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  const token = (await (await page.request.get(url + '/api/bootstrap')).json()).token;
  const get = async route => (await page.request.get(url + '/api/' + route)).json();
  const post = async (route, body) => {
    const response = await page.request.post(url + '/api/' + route, { headers: { 'X-Workspace-Token': token }, data: body });
    assert(response.ok(), await response.text());
    return response.json();
  };
  const prepare = async (title, ids, complete = true) => {
    const e = await post('experiment/create', { kind: 'preprocess', title, dataset_id: 'fixture-v1',
      ...(ids ? { trajectory_ids: ids } : {}), config: { deduplicate_observation: false, remove_source_lines: false } });
    if (!complete) return e;
    await post('experiment/start', { id: e.id });
    for (let i = 0; i < 100; i++) {
      const current = await get('experiment?id=' + e.id);
      if (current.status === 'completed') return current;
      assert.notEqual(current.status, 'failed');
      await new Promise(resolve => setTimeout(resolve, 100));
    }
    throw new Error('Preprocessing did not complete');
  };
  const all = await prepare('全部处理结果');
  const single = await prepare('单条处理结果', ['test-trajectory']);
  await prepare('预处理草稿', undefined, false);
  await page.goto(url + '/#experiments');
  await page.getByRole('button', { name: '新建实验', exact: true }).click();
  await page.locator('[data-action=new-split]').click();
  const source = page.locator('#split-preprocess-source');
  await source.waitFor();
  assert.deepEqual((await source.locator('option').evaluateAll(nodes => nodes.map(n => n.value))).sort(), [all.id, single.id].sort());
  assert((await source.textContent()).includes('全部处理结果 · 3 条轨迹'));
  assert((await source.textContent()).includes('单条处理结果 · 1 条轨迹'));
  await source.selectOption(all.id);
  await page.locator('#split-selection-summary').getByText('已选 3 条执行轨迹 · 展开选择', { exact: true }).waitFor();
  await page.locator('#split-dataset').selectOption('alternative-v2');
  await page.getByText('这个数据集需要先完成一次轨迹预处理实验。完成后可在这里选择处理结果。', { exact: true }).waitFor();
  assert.equal(await page.locator('#split-trajectory-picker input').count(), 0);
  assert.equal(await page.locator('[form=new-split-form][type=submit]').isDisabled(), true);
  await page.locator('#split-dataset').selectOption('fixture-v1');
  await source.selectOption(single.id);
  await page.locator('#split-selection-summary').getByText('已选 1 条执行轨迹 · 展开选择', { exact: true }).waitFor();
  await page.locator('#split-selection-summary').click();
  await page.locator('#split-trajectory-picker input').uncheck();
  assert.equal(await page.locator('[form=new-split-form][type=submit]').isDisabled(), true);
  await page.locator('#split-trajectory-picker input').check();
  await page.locator('#new-split-form [name=title]').fill('从单条处理结果切分');
  for (const [name, value] of Object.entries({ max_window_events: 2, overlap_events: 1, max_previous_summary_tokens: 0, max_future_summary_tokens: 0 }))
    await page.locator(`#new-split-form [name=${name}]`).fill(String(value));
  await page.locator('#split-preview[data-window-count="2"]').waitFor();
  const output = path.join(root, 'runs/browser-checks'); fs.mkdirSync(output, { recursive: true });
  await page.screenshot({ path: path.join(output, 'split-preprocessed-sources.png') });
  await page.setViewportSize({ width: 390, height: 844 });
  assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false);
  await page.screenshot({ path: path.join(output, 'split-preprocessed-sources-mobile.png') });
  await page.getByRole('button', { name: '创建切分实验草稿', exact: true }).click();
  await page.getByRole('heading', { name: '从单条处理结果切分', exact: true }).waitFor();
  const splitId = page.url().split('#experiment/')[1];
  const split = await get('experiment?id=' + splitId);
  assert.equal(split.preprocess_experiment_id, single.id);
  assert.deepEqual(split.trajectory_ids, ['test-trajectory']);
  // Reproduce a historical empty draft in this disposable workspace.
  const directory = path.join(path.dirname(path.dirname(catalogPath)), 'workspace/experiments', splitId);
  const meta = JSON.parse(fs.readFileSync(path.join(directory, 'experiment.json'), 'utf8'));
  Object.keys(meta).filter(key => key.startsWith('preprocess_')).forEach(key => delete meta[key]);
  Object.assign(meta, { input_state: 'awaiting_input', input_hash: '', trajectory_ids: [], trajectory_count: 0 });
  fs.writeFileSync(path.join(directory, 'experiment.json'), JSON.stringify(meta));
  for (const name of fs.readdirSync(path.join(directory, 'inputs'))) fs.unlinkSync(path.join(directory, 'inputs', name));
  await page.reload();
  await page.getByRole('button', { name: '接入预处理结果', exact: true }).click();
  await page.locator('#attach-preprocess-source').waitFor();
  assert.deepEqual((await page.locator('#attach-preprocess-source option').evaluateAll(nodes => nodes.map(n => n.value))).sort(), [all.id, single.id].sort());
  await page.locator('#attach-preprocess-source').selectOption(single.id);
  await page.locator('#attach-trajectory-picker[data-ready=true]').waitFor();
  assert.equal(await page.locator('#attach-trajectory-picker input').count(), 1);
  await page.getByRole('button', { name: '保存轨迹快照', exact: true }).click();
  await page.getByRole('button', { name: '开始运行', exact: true }).waitFor();
  assert.equal((await get('experiment?id=' + splitId)).preprocess_experiment_id, single.id);
  assert.deepEqual(errors, []);
  console.log('PASS completed-only source options, counts, source/dataset changes, empty/unchecked states, preview, frozen creation, legacy attachment and mobile layout');
}
run().catch(error => { console.error(error); process.exitCode = 1; }).finally(async () => { if (browser) await browser.close(); fixture.kill('SIGTERM'); });
