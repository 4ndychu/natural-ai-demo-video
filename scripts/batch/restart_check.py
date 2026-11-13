"""The real-restart test (do it once before the first overnight batch): docs/before-first-overnight-batch.md.

  .venv/bin/python scripts/batch/restart_check.py start    starts a small practice batch (2 short videos, no credits,
                                                           nothing published) as a real background job
  ... restart the Mac, log in ...
  .venv/bin/python scripts/batch/restart_check.py check    says whether the batch carried on by itself, then tidies up

The practice batch is the approved to-do test video twice, with its saved voice takes (output/test-todo-v4), in its
own folder (output/restart-check), away from your real demos and settings.
"""
import glob
import json
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
WORK = os.path.join(ROOT, 'output', 'restart-check')
SRC = os.path.join(ROOT, 'output', 'test-todo-v4')
os.environ.update({'NAVI_WORK': WORK, 'NAVI_DATA': os.path.join(WORK, 'data'), 'NAVI_NO_QUIET_WAIT': '1', 'NAVI_VARIETY_OFF': '1', 'NAVI_NO_QA': '1',
                   'NAVI_NO_BLIND': '1', 'NAVI_FAKE_CREDITS': '50000'})
os.environ.pop('NAVI_NO_LAUNCHD', None)
sys.path.insert(0, HERE)
import batch  # noqa: E402
import runner  # noqa: E402
import store  # noqa: E402


def the_batch():
    ids = sorted(os.listdir(os.path.join(WORK, 'batches'))) if os.path.isdir(os.path.join(WORK, 'batches')) else []
    return ids[-1] if ids else None


def start():
    old = the_batch()
    if old:
        runner.stop(old)
    shutil.rmtree(WORK, ignore_errors=True)
    if not glob.glob(os.path.join(SRC, '*_take1*')):
        sys.exit("The saved test takes aren't here (output/test-todo-v4), so the practice batch can't be made without spending credits.")
    b = batch.new('Restart check', 'Practice video one\nPractice video two\n', 'https://demo.playwright.dev/todomvc', export_to=os.path.expanduser('~/Movies/NAVI/Restart check'))   # never used: the practice batch exports nothing
    approved = json.load(open(os.path.join(ROOT, 'examples', 'test-todo-b.json')))
    sections = json.loads(json.dumps(approved['sections']))
    for d in b['items']:
        f = store.demo_dir(d)
        t = json.load(open(os.path.join(f, 'script.template.json')))
        json.dump({**t, 'sections': sections, 'explore': os.path.join(ROOT, 'examples', 'explore-test-todo')}, open(os.path.join(f, 'script.json'), 'w'), indent=1)
        for x in glob.glob(os.path.join(SRC, '*_take*')):
            shutil.copy2(x, f)
    b = batch.load(b['id'])
    b['written'] = {d: {'checked': True} for d in b['items']}
    batch.save(b)
    runner.start(b['id'], go=True)
    print('The practice batch is running in the background (2 short videos, about 8 minutes, no credits, nothing published).')
    print('Now restart the Mac: Apple menu > Restart. Log in again, wait a minute, then run:')
    print('  .venv/bin/python scripts/batch/restart_check.py check')


def check():
    bid = the_batch()
    if not bid:
        sys.exit('No practice batch here. Run "restart_check.py start" first.')
    b = batch.load(bid)
    st = runner.status(bid)
    import re
    import subprocess
    m = re.search(r'sec = (\d+)', subprocess.run(['sysctl', '-n', 'kern.boottime'], capture_output=True, text=True).stdout)
    booted = float(m.group(1)) if m else 0          # when the Mac last started
    boot = time.time() - booted
    carried = any('Carrying on from where it stopped' in x['text'] for x in b['log'])
    started_before_boot = bool(booted) and (b.get('started') or b.get('created') or 0) < booted
    done = sum(1 for d in b['items'] if store.demo(d)['recorded'])
    print(f"The Mac started {boot / 60:.0f} min ago. The practice batch: {b['state']}, {done} of {len(b['items'])} recorded; "
          f"its background job is {'running' if st['alive'] else 'not running'}.")
    if not started_before_boot:
        print("NOT TESTED: the Mac hasn't been restarted since the practice batch started. Restart it, log in, and run this again.")
        return 2
    if carried and (st['alive'] or b['state'] == 'review'):
        print('PASS: after the restart the batch started again by itself and carried on.' + ('' if b['state'] == 'review' else ' It is still recording; it will finish and remove itself.'))
        if b['state'] == 'review':
            shutil.rmtree(WORK, ignore_errors=True)
            print('Tidied up: the practice batch is gone.')
        return 0
    print('FAIL: the batch did not carry on after the restart. Tell Claude, and send the last lines of ' + os.path.join(batch.bdir(bid), 'runner.log'))
    return 1


if __name__ == '__main__':
    sys.exit(start() if sys.argv[1:] == ['start'] else check() if sys.argv[1:] == ['check'] else print(__doc__))
