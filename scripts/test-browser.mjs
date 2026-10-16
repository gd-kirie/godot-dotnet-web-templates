import assert from 'node:assert/strict';
import { chromium } from 'playwright-core';

const browser = await chromium.launch({
  executablePath: process.env.CHROMIUM_PATH,
  headless: true,
  args: ['--enable-unsafe-swiftshader'],
});
try {
  const page = await browser.newPage({ viewport: { width: 960, height: 540 } });
  const messages = [];
  const errors = [];
  page.on('console', message => {
    messages.push(message.text());
    console.log(message.text());
  });
  page.on('pageerror', error => errors.push(error.message));
  const waitForLog = async (text, start = 0) => {
    const deadline = Date.now() + 60000;
    while (!messages.slice(start).some(message => message.includes(text))) {
      assert(Date.now() < deadline, `Timed out waiting for ${text}`);
      assert.equal(errors.length, 0, errors.join('\n'));
      assert(!messages.some(message => /(?:PROBE|DEMO)_FAIL/.test(message)), messages.join('\n'));
      await page.waitForTimeout(100);
    }
  };
  await page.goto(process.argv[2]);
  assert(await page.evaluate(() => crossOriginIsolated));
  for (let pass = 0; pass < 2; pass++) {
    const start = messages.length;
    if (pass) await page.reload();
    await waitForLog('THREAD_PROBE_PASS', pass ? start : 0);
    await waitForLog('BROWSER_CRYPTO_PASS', pass ? start : 0);
    await waitForLog('DEMO_READY', pass ? start : 0);
    let checkpoint = messages.length;
    await page.mouse.click(170, 410);
    await waitForLog('DEMO_STARTED', checkpoint);
    await page.mouse.click(670, 410);
    await waitForLog('running=True', checkpoint);
    await waitForLog('DEMO_COMPLETE', checkpoint);
    checkpoint = messages.length;
    await page.mouse.click(170, 410);
    await waitForLog('DEMO_STARTED', checkpoint);
    await page.mouse.click(400, 410);
    await waitForLog('DEMO_STOPPED', checkpoint);
    checkpoint = messages.length;
    await page.mouse.click(170, 410);
    await waitForLog('DEMO_COMPLETE', checkpoint);
  }
  assert.equal(errors.length, 0, errors.join('\n'));
  console.log('BROWSER_ACCEPTANCE_PASS');
} finally {
  await browser.close();
}
