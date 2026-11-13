// The blind A/B/C pick screen, pause/resume and the Settings models list against the real engine, in a headless browser.
//
//   NAVI_BLIND_STOP=waiting .venv/bin/python scripts/batch/test_blind.py      leaves a batch waiting for picks and prints
//                                                                              NAVI_DATA=... BATCH=...
//   start the app's server on port 4799 with that NAVI_DATA, NAVI_WORK=output/blind-test and NAVI_NO_LAUNCHD=1, then
//   BATCH=<id> node ui/tests/pick-live-check.js <folder for screenshots>
//   afterwards: scripts/batch/runner.py stop <id>, and stop the server
const path = require('path');
const { chromium } = require(process.env.PLAYWRIGHT || path.join(__dirname, '..', '..', 'recorder', 'agent-screenplay', 'node_modules', 'playwright-core'));
const out = process.argv[2]; const bid = process.env.BATCH;
const log = (n, ok, d) => console.log(`| ${n} | ${ok ? 'pass' : '**FAIL**'} | ${d || ''} |`);
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1280, height: 900 } });
  const errs = []; p.on('pageerror', (e) => errs.push(String(e))); p.on('console', (m) => { if (m.type() === 'error') errs.push(m.text()); });
  await p.goto('http://127.0.0.1:4799/'); await p.waitForTimeout(2500);
  const st = await (await p.request.get('http://127.0.0.1:4799/api/state')).json();
  const B = st.batches.find((x) => x.id === bid);
  log('engine state: 5 jobs with model and effort', st.jobs.length === 5 && st.jobs[0].model === 'claude-fable-5-2', st.jobs.map((j) => j.label + ' ' + j.model + '/' + j.effort).join('; '));
  log('engine state never names a model inside the picks', !/claude|effort|model/.test(JSON.stringify(B.blind_view.lessons)));
  await p.evaluate((id) => navi.openBatch(id), bid); await p.waitForTimeout(800);
  log('home → batch: head says there are picks to make', /2 to pick/.test(await p.locator('.bsub').innerText()), (await p.locator('.bsub').innerText()).slice(0, 80));
  log('primary button offers the first pick', /Listen to #1/.test(await p.locator('.bprimary').innerText()));
  await p.locator('.bprimary').click(); await p.waitForTimeout(500);
  const cards = await p.locator('.pickcard').count();
  log('pick panel: three versions by letter', cards === 3 && (await p.locator('.pickletter').allInnerTexts()).join('') === 'ABC', (await p.locator('.pickhead').allInnerTexts()).join(' | ').replace(/\n/g, ' '));
  const a = B.blind_view.lessons[0];
  const r = await p.request.get(`http://127.0.0.1:4799/media/${a.demo}/blind/A.mp3`);
  log('each version\'s audio is served', r.status() === 200 && (await r.body()).length > 20000, r.headers()['content-type'] + ', ' + (await r.body()).length + ' bytes');
  const k = await p.request.get(`http://127.0.0.1:4799/media/${a.demo}/blind/arm1/script.json`);
  log('the drafts and the key are not served', k.status() === 404);
  await p.locator('.pickcard').nth(0).locator('button', { hasText: 'Play' }).click(); await p.waitForTimeout(1500);
  log('Play starts that version (button turns to Pause, bar moves)', (await p.locator('.pickcard').nth(0).locator('.pickplay button').innerText()) === 'Pause' && parseInt(await p.locator('.pickcard').nth(0).locator('.pickbar span').evaluate((e) => e.style.width)) > 0);
  await p.locator('.pickcard').nth(1).locator('.link').click(); await p.waitForTimeout(300);
  log('Read the script opens the whole script', (await p.locator('.pickcard').nth(1).locator('.picklines p').count()) >= 3);
  await p.screenshot({ path: out + '/live-pick.png', fullPage: false });
  await p.locator('.pickcard').nth(1).locator('.pickbtn').click(); await p.waitForTimeout(2500);
  const st2 = await (await p.request.get('http://127.0.0.1:4799/api/state')).json(); const B2 = st2.batches.find((x) => x.id === bid);
  log('Pick B: recorded by the engine, the panel moves to the next video', B2.blind_view.lessons[0].status === 'picked' && B2.blind_view.lessons[0].picked === 'B' && /#2/.test(await p.locator('#bpick-h').innerText()), await p.locator('#bpick-h').innerText());
  log('arms still hidden while a pick is open', !B2.blind_view.revealed && !/claude/.test(await p.locator('main').innerText()));
  await p.locator('.pickcard').nth(0).locator('.pickbtn').click(); await p.waitForTimeout(6000);
  const st3 = await (await p.request.get('http://127.0.0.1:4799/api/state')).json(); const B3 = st3.batches.find((x) => x.id === bid);
  log('second pick, made while video 1 records: taken as the answer straight away', B3.blind_view.lessons[1].status === 'picked' && B3.blind_view.lessons[1].picked === 'A' && (await p.locator('.pickcard').count()) === 0);
  log('the batch records by itself after a pick', B3.runner && B3.runner.alive && B3.runner.phase === 'recording', JSON.stringify({ phase: B3.runner && B3.runner.phase, awake: B3.runner && B3.runner.awake }));
  await p.locator('button', { hasText: 'Pause recording' }).click(); await p.waitForTimeout(5000);
  const st4 = await (await p.request.get('http://127.0.0.1:4799/api/state')).json(); const B4 = st4.batches.find((x) => x.id === bid);
  const sub = await p.locator('.bsub').innerText();
  log('Pause: the engine stops and the screen asks to resume', B4.state === 'paused' && !B4.runner.alive && /Paused at video 1 of 2\. Resume\?/.test(sub) && (await p.locator('button', { hasText: 'Resume recording' }).count()) === 1, sub);
  await p.screenshot({ path: out + '/live-paused.png' });
  await p.evaluate(() => navi.setState({ screen: 'settings' })); await p.waitForTimeout(600);
  const rows = await p.locator('.jobrow').allInnerTexts();
  log('Settings: each job\'s model and effort, read only', rows.length === 5 && /claude-fable-5-2 · high/.test(rows[0]) && (await p.locator('.jobrow button, .jobrow input').count()) === 0, rows.map((x) => x.replace(/\n/g, ' ')).join(' | ').slice(0, 200));
  log('no page errors', errs.length === 0, errs.slice(0, 2).join(' ; ').slice(0, 200));
  await b.close();
})();
