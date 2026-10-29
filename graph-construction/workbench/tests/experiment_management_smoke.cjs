// Exercise navigation and reversible deletion in a disposable local workspace.
const { chromium } = require('playwright');
const { spawn } = require('node:child_process');
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const root = path.resolve(__dirname, '..');
const fixture = spawn(process.env.PYTHON_BIN || 'python3', [path.join(__dirname, 'browser_fixture.py'), '--preprocess'], { cwd: root, stdio: ['ignore', 'pipe', 'inherit'] });
let browser;
async function run() {
  const url = await new Promise((resolve, reject) => {
    let output = '';
    fixture.stdout.on('data', data => { output += data; if (output.includes('\n')) resolve(JSON.parse(output.split('\n')[0]).url); });
    fixture.on('exit', code => reject(new Error('Fixture exited ' + code)));
  });
  browser = await chromium.launch({ executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless: true });
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  const bootstrap = await (await page.request.get(url + '/api/bootstrap')).json();
  async function post(action, body) {
    const response = await page.request.post(url + '/api/' + action, { data: body, headers: { 'X-Workspace-Token': bootstrap.token } });
    assert(response.ok(), await response.text());
    return response.json();
  }
  async function waitState(id, status) {
    for (let i = 0; i < 150; i++) {
      const e = await (await page.request.get(url + '/api/experiment?id=' + id)).json();
      if (e.status === status) return e;
      assert.notEqual(e.status, 'failed', JSON.stringify(e.lifecycle));
      await new Promise(resolve => setTimeout(resolve, 100));
    }
    throw new Error('Experiment did not reach ' + status);
  }
  const pre = await post('experiment/create', { kind: 'preprocess', title: '预处理 <script>样例</script>', dataset_id: 'fixture-v1', config: { deduplicate_observation: true, remove_source_lines: true, simplify_call_ids: true } });
  await post('experiment/start', { id: pre.id });
  await waitState(pre.id, 'completed');
  const split = await post('experiment/create', { kind: 'split', title: '切分样例', dataset_id: 'fixture-v1', preprocess_experiment_id: pre.id, config: { max_window_events: 1, overlap_events: 0, max_previous_summary_tokens: 0, max_future_summary_tokens: 0 } });
  await post('experiment/start', { id: split.id });
  await waitState(split.id, 'completed');
  const pred = await post('experiment/create', { kind: 'predicate', title: '谓词样例', dataset_id: 'fixture-v1', source_experiment_id: split.id, batch_size: 1 });
  const output = path.join(root, 'runs/browser-checks');
  fs.mkdirSync(output, { recursive: true });
  await page.goto(url + '/#experiments');
  await page.locator('#experiment-list [data-experiment-id]').first().waitFor();
  assert.equal(await page.locator('#experiment-list [data-action=delete-experiment]').count(), 3);
  await page.screenshot({ path: path.join(output, 'experiment-management-desktop.png') });

  // List filters survive a detail/back round trip; all experiment kinds have a back link.
  await page.getByRole('textbox', { name: '搜索实验', exact: true }).fill('预处理');
  await page.locator('#experiment-filter').selectOption('fixture-v1');
  await page.locator(`[data-experiment-id="${pre.id}"] .experiment-name`).click();
  await page.locator('#preprocess-after').waitFor();
  await page.getByRole('link', { name: '返回实验管理', exact: true }).click();
  assert.equal(await page.locator('#experiment-search').inputValue(), '预处理');
  assert.equal(await page.locator('#experiment-filter').inputValue(), 'fixture-v1');
  await page.locator('#experiment-search').fill('');
  for (const e of [split, pred, pre]) {
    await page.locator(`[data-experiment-id="${e.id}"] .experiment-name`).click();
    await page.getByRole('link', { name: '返回实验管理', exact: true }).waitFor();
    assert.equal(await page.locator('.experiment-navigation [data-action=delete-experiment]').count(), 1);
    await page.getByRole('link', { name: '返回实验管理', exact: true }).click();
    await page.locator('#experiment-search').waitFor();
  }
  const row = page.locator(`[data-experiment-id="${pre.id}"]`);
  await row.locator('[data-action=delete-experiment]').click();
  assert((await page.locator('#modal-content').textContent()).includes(pre.title));
  assert.equal(await page.locator('#modal-content script').count(), 0);
  await page.getByRole('button', { name: '取消', exact: true }).click();
  assert.equal(await row.count(), 1);

  await row.locator('.experiment-name').click();
  await page.locator('#preprocess-after').waitFor();
  await page.screenshot({ path: path.join(output, 'experiment-detail-back.png') });
  await page.setViewportSize({ width: 390, height: 844 });
  assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false);
  await page.locator('.experiment-navigation').scrollIntoViewIfNeeded();
  await page.screenshot({ path: path.join(output, 'experiment-detail-back-mobile.png') });
  await page.locator('.experiment-navigation [data-action=delete-experiment]').click();
  await page.getByRole('button', { name: '移至回收站', exact: true }).click();
  await page.waitForURL('**/#experiments');
  await page.locator('#experiment-list').waitFor();
  assert.equal(await page.locator(`[data-experiment-id="${pre.id}"]`).count(), 0);
  await page.reload();
  await page.locator('#experiment-list').waitFor();
  assert.equal(await page.locator(`[data-experiment-id="${pre.id}"]`).count(), 0);
  assert.equal(await page.locator('#navigation .nav-count').textContent(), '2');
  await page.getByRole('button', { name: '回收站', exact: true }).click();
  await page.locator(`[data-deleted-id="${pre.id}"]`).waitFor();
  assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false);
  await page.screenshot({ path: path.join(output, 'experiment-trash-mobile.png') });
  await page.locator(`[data-deleted-id="${pre.id}"] [data-action=restore-experiment]`).click();
  await page.getByText('回收站为空。', { exact: true }).waitFor();
  await page.locator('#modal .modal-footer [data-action=close-modal]').click();
  await page.locator(`[data-experiment-id="${pre.id}"] .experiment-name`).click();
  await page.locator('#preprocess-after').waitFor();
  assert.equal(JSON.parse(await page.locator('#preprocess-after').textContent()).tool_calls[0].tool_call_id, 'call-0001');

  // Waiting model processes must be stopped before deletion; use the fixture's local model.
  await page.setViewportSize({ width: 1440, height: 1000 });
  await post('experiment/start', { id: pred.id });
  await waitState(pred.id, 'waiting');
  await page.goto(url + '/#experiment/' + pred.id);
  await page.getByRole('button', { name: '停止运行', exact: true }).waitFor();
  assert.equal(await page.locator('.experiment-navigation [data-action=delete-experiment]').isDisabled(), true);
  await page.getByRole('button', { name: '停止运行', exact: true }).click();
  await page.getByRole('button', { name: '恢复实验', exact: true }).waitFor();
  await page.locator('.experiment-navigation [data-action=delete-experiment]').click();
  await page.getByRole('button', { name: '移至回收站', exact: true }).click();
  await page.waitForURL('**/#experiments');
  await page.locator('#experiment-list').waitFor();
  await page.locator(`[data-experiment-id="${split.id}"] [data-action=delete-experiment]`).click();
  await page.getByRole('button', { name: '移至回收站', exact: true }).click();
  await page.waitForFunction(id => !document.querySelector(`[data-experiment-id="${id}"]`), split.id);
  assert.equal(await page.locator('#experiment-list [data-experiment-id]').count(), 1);
  await page.getByRole('button', { name: '回收站', exact: true }).click();
  await page.locator(`[data-deleted-id="${pred.id}"]`).waitFor();
  assert.equal(await page.locator('[data-deleted-id]').count(), 2);
  assert.deepEqual(errors, []);
  console.log('PASS: back links for all experiment kinds, persistent filters, delete/cancel/restore, reload, mobile layout, waiting-worker guard and stopped experiment deletion.');
}
run().catch(error => { console.error(error); process.exitCode = 1; }).finally(async () => { if (browser) await browser.close(); fixture.kill('SIGINT'); });
