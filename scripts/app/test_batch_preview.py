"""The batch list's line under an opened video is the first sentence of that video's real script.json "talk", and
nothing when there's no script yet (14 Nov 2026: it was a made-up line, "Okay so… in this one we're gonna <title>.
It's, um, quicker than it looks.", that read like a real script).

Runs the real app server on a spare port against throwaway folders (NAVI_DATA, NAVI_WORK, a throwaway Keychain
entry) and opens the real page in a headless browser (Playwright from the recorder's install).

  .venv/bin/python scripts/app/test_batch_preview.py     (exit 1 on any failure)
"""
import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
PY = os.path.join(ROOT, '.venv', 'bin', 'python')
FAILS = []


def check(label, good, extra=''):
    print(('ok    ' if good else 'FAIL  ') + label + (f'  ({extra})' if extra else ''), flush=True)
    if not good:
        FAILS.append(label)


tmp = tempfile.mkdtemp(prefix='navi-preview-test-')
env = {**os.environ, 'NAVI_DATA': os.path.join(tmp, 'data'), 'NAVI_WORK': os.path.join(tmp, 'work'),
       'NAVI_KEY_SERVICE': f'navi-test-{os.getpid()}', 'NAVI_VARIETY_OFF': '1'}
env.pop('NAVI_ELEVENLABS_KEY', None)

# a batch of two videos: the first has a script (the approved to-do script, which passes the checker), the second none
lst = os.path.join(tmp, 'videos.txt')
open(lst, 'w').write('1. Adding your first task\n2. Filtering and clearing\n')
r = subprocess.run([PY, os.path.join(ROOT, 'scripts', 'batch', 'batch.py'), 'new', '--name', 'Preview check', '--list', lst,
                    '--site', 'https://demo.playwright.dev/todomvc'], capture_output=True, text=True, env=env)
bid = r.stdout.split()[1].rstrip(':')
b = json.load(open(os.path.join(env['NAVI_WORK'], 'batches', bid, 'batch.json')))
first, second = b['items']
approved = json.load(open(os.path.join(ROOT, 'examples', 'test-todo-b.json')))
folder = os.path.join(env['NAVI_WORK'], first)
t = json.load(open(os.path.join(folder, 'script.template.json')))
json.dump({**t, 'sections': approved['sections'], 'explore': os.path.join(ROOT, 'examples', 'explore-test-todo')},
          open(os.path.join(folder, 'script.json'), 'w'), indent=1)
talk = approved['sections'][0]['talk']           # "[relaxed] So this is a pretty basic to-do list. I'm gonna type ..."
WANT = 'So this is a pretty basic to-do list.'
check('the to-do script starts as this check expects', talk.startswith('[relaxed] ' + WANT), talk[:60])

s = socket.socket()
s.bind(('127.0.0.1', 0))
port = s.getsockname()[1]
s.close()
srv = subprocess.Popen([PY, os.path.join(HERE, 'server.py'), '--port', str(port)], env=env, stdout=subprocess.PIPE, text=True)
srv.stdout.readline()
base = f'http://127.0.0.1:{port}'
try:
    st = json.load(urllib.request.urlopen(base + '/api/state', timeout=60))
    d1 = next(d for d in st['demos'] if d['id'] == first)
    check('the server counts the first video as written (its script passes the checker)', d1['written'], d1.get('script_check'))
    js = r"""
const { chromium } = require(process.argv[1]);
(async () => {
  const [base, bid] = [process.argv[2], process.argv[3]];
  const b = await chromium.launch();
  const p = await b.newPage();
  await p.goto(base + '/');
  await p.waitForFunction((bid) => window.navi && (navi.state.batches || []).some((x) => x.id === bid && x.engine), bid, { timeout: 30000 });
  const items = await p.evaluate((bid) => navi.state.batches.find((x) => x.id === bid).items.map((x) => ({ st: x.st, preview: x.preview })), bid);
  const shown = [];
  for (let i = 0; i < items.length; i++) {
    await p.evaluate(([bid, i]) => navi.setState({ screen: 'batch', curBatch: bid, btOpen: i, help: false }), [bid, i]);
    await p.waitForTimeout(300);
    shown.push(await p.evaluate(() => document.body.innerText));
  }
  console.log(JSON.stringify({ items, shown }));
  await b.close();
})().catch((e) => { console.error(e); process.exit(1); });
"""
    pw = os.path.join(ROOT, 'recorder', 'agent-screenplay', 'node_modules', 'playwright-core')
    r = subprocess.run(['node', '-e', js, pw, base, bid], capture_output=True, text=True, timeout=120)
    out = json.loads(r.stdout.strip().splitlines()[-1]) if r.returncode == 0 else None
    check('the real page loaded the batch from the server', out is not None, r.stderr[-400:])
    if out:
        items, shown = out['items'], out['shown']
        check('video 1 (has a script): its line is the script\'s first sentence, voice tag taken out',
              items[0]['preview'] == WANT, items[0])
        check('video 1, opened: the page shows that sentence in quotes', f'“{WANT}”' in shown[0])
        check('video 2 (no script yet): no line at all', items[1]['preview'] == '', items[1])
        check('video 2, opened: no quote is shown', '“' not in shown[1].split('Want changes?')[0].split('Filtering and clearing')[-1])
        made_up = ['in this one we’re gonna', 'quicker than it looks']
        check('the made-up line is gone from the page', not any(m in x for x in shown for m in made_up))
finally:
    srv.terminate()
    srv.wait(timeout=10)
    subprocess.run(['security', 'delete-generic-password', '-s', env['NAVI_KEY_SERVICE']], capture_output=True)
    shutil.rmtree(tmp, ignore_errors=True)

print(f'\n{len(FAILS)} FAILED' if FAILS else '\nall batch preview checks passed')
sys.exit(1 if FAILS else 0)
