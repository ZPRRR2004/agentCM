// Real background browser pages control a disposable workbench's lifetime.
const { chromium } = require('playwright');
const { spawn } = require('node:child_process');
const path = require('node:path');
const assert = require('node:assert/strict');
const root = path.resolve(__dirname, '..');
const fixture = spawn(process.env.PYTHON_BIN || 'python3', [path.join(__dirname, 'browser_fixture.py'), '--on-demand'],
  { cwd: root, stdio: ['ignore', 'pipe', 'inherit'] });
const exited = new Promise(resolve => fixture.on('exit', resolve));
let browser;
const delay = ms => new Promise(resolve => setTimeout(resolve, ms));
async function run() {
  const { url } = await new Promise((resolve, reject) => {
    let output = '';
    fixture.stdout.on('data', data => { output += data; if (output.includes('\n')) resolve(JSON.parse(output.split('\n')[0])); });
    fixture.on('exit', code => reject(new Error('Fixture exited before ready: ' + code)));
  });
  browser = await chromium.launch({ executablePath: process.env.CHROME_BIN || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless: true });
  const context = await browser.newContext();
  const errors = [];
  context.on('page', page => page.on('pageerror', e => errors.push(e.message)));
  const count = async expected => {
    let health;
    for (let n = 0; n < 60; n++) {
      health = await (await context.request.get(url + '/api/health')).json();
      if (health.open_pages === expected) return;
      await delay(50);
    }
    const views = await Promise.all(context.pages().map(page => page.locator('#main').innerText()));
    throw new Error('Page count did not reach ' + expected + ': ' + JSON.stringify({ health, errors, views }));
  };
  const first = await context.newPage();
  await first.goto(url + '/#experiments');
  await count(1);
  const second = await context.newPage();
  await second.goto(url + '/#overview');
  await count(2);
  await first.close();
  await count(1);
  await delay(1500);
  assert.equal(fixture.exitCode, null, 'Another open page must keep the service alive');
  await second.reload();
  await count(1);
  await delay(1500);
  assert.equal(fixture.exitCode, null, 'Refresh must keep the service alive');
  // Block the optional close notification: socket disconnection must still stop it.
  await second.route('**/api/session/close', route => route.abort());
  await second.close();
  const code = await Promise.race([exited, delay(6000).then(() => 'timeout')]);
  assert.equal(code, 0, 'The last closed page must stop the server');
  assert.deepEqual(errors, []);
  console.log('PASS two pages, closing one, refresh, missing close notification, last-page shutdown, no page errors');
}
run().catch(error => { console.error(error); process.exitCode = 1; }).finally(async () => {
  if (browser) await browser.close();
  if (fixture.exitCode === null) fixture.kill('SIGTERM');
});
