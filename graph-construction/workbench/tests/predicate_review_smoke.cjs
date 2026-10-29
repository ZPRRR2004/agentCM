// Isolated model fixture: English definitions, review persistence, no translation calls.
const { chromium } = require('playwright');
const { spawn } = require('node:child_process');
const assert = require('node:assert/strict');
const path = require('node:path');
const fs = require('node:fs');
const root = path.resolve(__dirname, '..');
const fixture = spawn(process.env.PYTHON_BIN || 'python3',
  [path.join(__dirname, 'browser_fixture.py')], { cwd: root, stdio: ['ignore', 'pipe', 'inherit'] });
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
  const errors = [], requests = [];
  page.on('pageerror', error => errors.push(error.message));
  page.on('request', request => {
    if (request.url().endsWith('/api/review/translation')) requests.push(request.postDataJSON());
  });
  const get = async route => (await page.request.get(url + '/api/' + route)).json();
  const { token } = await get('bootstrap');
  const post = async (route, data) => {
    const response = await page.request.post(url + '/api/' + route,
      { headers: { 'X-Workspace-Token': token }, data });
    assert(response.ok(), await response.text());
    return response.json();
  };
  const complete = async data => {
    const e = await post('experiment/create', data);
    await post('experiment/start', { id: e.id });
    for (let i = 0; i < 100; i++) {
      const result = await get('experiment?id=' + e.id);
      if (result.status === 'completed') return result;
      assert.notEqual(result.status, 'failed', result.log);
      await new Promise(resolve => setTimeout(resolve, 100));
    }
    throw new Error('Experiment did not finish');
  };
  const pre = await complete({ kind: 'preprocess', title: 'Prepare', dataset_id: 'fixture-v1',
    config: { deduplicate_observation: false, remove_source_lines: false } });
  const split = await complete({ kind: 'split', title: 'Split', dataset_id: 'fixture-v1',
    preprocess_experiment_id: pre.id, config: { max_window_events: 1, overlap_events: 0,
      max_previous_summary_tokens: 0, max_future_summary_tokens: 0 } });
  const e = await complete({ title: '谓词审核检查', dataset_id: 'fixture-v1',
    source_experiment_id: split.id, window_limit: 1, batch_size: 1, max_retries: 0 });
  await page.goto(url + '/#review/' + e.id);
  const notes = page.locator('#review-notes');
  await notes.fill('正在输入的审核意见需要保留。');
  assert.equal(await page.locator('#predicate-definition .definition-name').innerText(), 'IS_PLAN');
  const definition = e.registry.find(p => p.name === 'IS_PLAN');
  assert.equal(await page.locator('#predicate-definition .definition-text').first().innerText(), definition.definition);
  assert.deepEqual(await page.locator('.parameter p').allTextContents(), definition.parameters.map(p => p.description));
  assert.deepEqual(await page.locator('.condition li').allTextContents(),
    [...definition.assertion_conditions, ...definition.exclusion_conditions]);
  assert.equal(await page.locator('#translation-status').count(), 0);
  assert.equal(requests.length, 0);
  assert(!('review_translations' in e));
  await page.getByRole('button', { name: '保存审核', exact: true }).click();
  await page.waitForFunction(() => document.querySelector('#toast')?.textContent.includes('已保存'));
  await page.reload();
  assert.equal(await notes.inputValue(), '正在输入的审核意见需要保留。');
  const search = page.locator('#predicate-search');
  await search.fill('USES');
  assert.equal(await page.locator('#predicate-list .list-item').count(), 1);
  await page.locator('#predicate-list .list-item').click();
  assert.equal(await page.locator('.definition-name').innerText(), 'USES');
  await search.fill('');
  const screenshots = path.join(root, 'runs/browser-checks');
  fs.mkdirSync(screenshots, { recursive: true });
  await page.screenshot({ path: path.join(screenshots, 'predicate-review.png'), fullPage: true });
  await page.setViewportSize({ width: 390, height: 844 });
  await page.locator('#predicate-definition').scrollIntoViewIfNeeded();
  assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1));
  await page.screenshot({ path: path.join(screenshots, 'predicate-review-mobile.png'), fullPage: true });
  await page.reload();
  await page.locator('.definition-name').waitFor();
  assert.deepEqual(await get('export?id=' + e.id), e.registry);
  await page.goto(url + '/#experiment/' + e.id);
  await page.getByRole('heading', { name: '当前谓词库', exact: true }).waitFor();
  assert.deepEqual(await page.locator('.registry-definition .definition-text').allTextContents(), e.registry.map(p => p.definition));
  assert.equal(e.schema, 'predicate-definition/v2');
  await page.setViewportSize({ width: 1440, height: 1000 });
  await page.getByRole('button', { name: '窗口与阶段', exact: true }).click();
  await page.getByRole('button', { name: '打开证据', exact: true }).click();
  await page.getByRole('heading', { name: '本次发现使用的节点', exact: true }).waitFor();
  const evidence = await get(`window?dataset=fixture-v1&experiment=${e.id}&id=${e.windows[0].id}`);
  const nodes = evidence.nodes.core.nodes;
  assert.equal(await page.locator('.trajectory-node').count(), nodes.length);
  for (let i = 0; i < nodes.length; i++) {
    const card = page.locator('.trajectory-node').nth(i);
    assert.equal(await card.getAttribute('data-node-id'), nodes[i].id);
    assert.equal(await card.locator('.node-type').innerText(), nodes[i].type);
    const shown = await card.locator('pre').textContent();
    assert.deepEqual(typeof nodes[i].content === 'string' ? shown : JSON.parse(shown), nodes[i].content);
  }
  assert.equal(await page.locator('.node-connection').count(), 1);
  assert.equal(await page.locator('.trajectory-node script').count(), 0);
  await page.screenshot({ path: path.join(screenshots, 'typed-nodes-desktop.png'), fullPage: true });
  await page.setViewportSize({ width: 390, height: 844 });
  assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1));
  await page.screenshot({ path: path.join(screenshots, 'typed-nodes-mobile.png'), fullPage: true });
  assert.equal(requests.length, 0, 'Reviewing, searching and reloading must not call translation');
  const removedEndpoint = await page.request.post(url + '/api/review/translation',
    { headers: { 'X-Workspace-Token': token }, data: { id: e.id, name: 'USES' } });
  assert.equal(removedEndpoint.status(), 404);
  assert.deepEqual(errors, []);
  console.log(JSON.stringify({ ok: true, checks: [
    'English fields unchanged', 'saved review survives reload', 'English search',
    'no translation requests', 'translation endpoint removed', 'English export unchanged',
    'registry list', 'mobile', 'typed node identities and exact content',
    'call-result edges', 'tool output escaped', 'typed nodes mobile'] }));
}
run().catch(error => { console.error(error); process.exitCode = 1; }).finally(async () => {
  if (browser) await browser.close();
  fixture.kill('SIGINT');
});
