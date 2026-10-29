// Headless, isolated fixture: delayed requests, retry, human review, and live log scrolling.
const { chromium } = require('playwright');
const { spawn } = require('node:child_process');
const assert = require('node:assert/strict');
const path = require('node:path');
const fs = require('node:fs');
const root = path.resolve(__dirname, '..');
const fixture = spawn(process.env.PYTHON_BIN || 'python3',
  [path.join(__dirname, 'browser_fixture.py'), '--progress'], { cwd: root, stdio: ['ignore', 'pipe', 'inherit'] });
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
  const page = await browser.newPage({ viewport: { width: 1440, height: 1100 } });
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  const get = async route => (await page.request.get(url + '/api/' + route)).json();
  const { token } = await get('bootstrap');
  const post = async (route, data) => {
    const response = await page.request.post(url + '/api/' + route,
      { headers: { 'X-Workspace-Token': token }, data });
    assert(response.ok(), await response.text());
    return response.json();
  };
  const waitState = async (id, status) => {
    for (let i = 0; i < 200; i++) {
      const e = await get('experiment?id=' + id);
      if (e.status === status) return e;
      assert.notEqual(e.status, 'failed', e.log);
      await new Promise(resolve => setTimeout(resolve, 100));
    }
    throw new Error('Did not reach ' + status);
  };
  const complete = async data => {
    const e = await post('experiment/create', data);
    await post('experiment/start', { id: e.id });
    return waitState(e.id, 'completed');
  };
  const pre = await complete({ kind: 'preprocess', title: 'Prepare inputs', dataset_id: 'fixture-v1',
    config: { deduplicate_observation: false, remove_source_lines: false } });
  const split = await complete({ kind: 'split', title: 'Split inputs', dataset_id: 'fixture-v1',
    preprocess_experiment_id: pre.id, config: { max_window_events: 1, overlap_events: 0,
      max_previous_summary_tokens: 0, max_future_summary_tokens: 0 } });
  const e = await post('experiment/create', { title: '谓词发现 · 执行过程检查', dataset_id: 'fixture-v1',
    source_experiment_id: split.id, window_limit: 2, batch_size: 1, max_retries: 1 });
  await page.goto(url + '/#experiment/' + e.id);
  await page.getByRole('button', { name: '开始运行', exact: true }).click();
  await page.waitForFunction(() => document.querySelector('.execution-current strong')?.textContent.includes('等待模型返回'));
  await page.locator('#execution-follow').focus();
  await page.waitForFunction(() => document.querySelector('#execution-clock')?.textContent.includes('已等待'));
  const screenshots = path.join(root, 'runs/browser-checks');
  fs.mkdirSync(screenshots, { recursive: true });
  await page.screenshot({ path: path.join(screenshots, 'execution-progress-running.png'), fullPage: true });
  await page.waitForFunction(() => document.querySelector('.execution-current strong')?.textContent.includes('等待你提交审核意见'));
  let waiting = await get('experiment?id=' + e.id);
  assert.equal(waiting.status, 'waiting');
  assert((await page.locator('#execution-output').innerText()).includes('即将重试'));
  assert((await page.locator('.execution-current > span').innerText()).startsWith('第 1/2 个窗口'));
  await page.locator('#execution-follow').uncheck();
  await page.locator('#execution-output').evaluate(el => { el.scrollTop = 20; });
  const oldScroll = await page.locator('#execution-output').evaluate(el => el.scrollTop);
  await page.waitForTimeout(2300);
  assert.equal(await page.locator('#execution-output').evaluate(el => el.scrollTop), oldScroll);
  assert(!(await page.locator('#execution-follow').isChecked()));
  await page.locator('#execution-follow').check();
  assert(await page.locator('#execution-output').evaluate(el => el.scrollHeight - el.scrollTop - el.clientHeight < 16));
  await page.reload();
  await page.locator('#execution-console').waitFor();
  assert((await page.locator('#execution-output').innerText()).includes('即将重试'));
  await page.setViewportSize({ width: 390, height: 844 });
  assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1));
  await page.locator('#execution-console').screenshot({ path: path.join(screenshots, 'execution-progress-mobile.png') });
  await page.setViewportSize({ width: 1440, height: 1100 });
  await post('experiment/feedback', { id: e.id, token: waiting.pending.token, feedback: '' });
  await page.waitForFunction(() => document.querySelector('.execution-current strong')?.textContent === '实验已完成，结果已保存');
  assert((await page.locator('#execution-output').innerText()).includes('第 2/2 个窗口已保存'));
  assert.equal(await page.locator('#execution-clock').innerText(), '');
  // A stopped process can leave its last request in execution.json; status takes precedence.
  const done = await get('experiment?id=' + e.id);
  await page.route('**/api/experiment?*', async route => {
    await route.fulfill({ json: { ...done, status: 'stopped', execution: {
      ...done.execution, event: 'model_wait', message: '等待模型返回', waiting_since: new Date().toISOString() } } });
  });
  await page.reload();
  await page.waitForFunction(() => document.querySelector('.execution-current strong')?.textContent === '实验已停止');
  assert.equal(await page.locator('#execution-clock').innerText(), '');
  await page.unroute('**/api/experiment?*');
  for (const local of [pre, split]) {
    await page.goto(url + '/#experiment/' + local.id);
    await page.waitForFunction(id => document.querySelector('#execution-console')?.dataset.experiment === id, local.id);
    assert((await page.locator('#execution-output').innerText()).includes('已保存'));
  }
  assert.deepEqual(errors, []);
  console.log(JSON.stringify({ ok: true, checks: [
    'live request status', 'waiting timer', 'retry', 'human feedback', 'scroll preserved',
    'follow latest', 'reload', 'mobile', 'completion', 'stopped status', 'all experiment kinds'] }));
}
run().catch(error => { console.error(error); process.exitCode = 1; }).finally(async () => {
  if (browser) await browser.close();
  fixture.kill('SIGINT');
});
