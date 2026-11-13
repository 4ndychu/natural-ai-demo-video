"""Check for batches that survive (scripts/batch/runner.py), for real: the batch is handed to macOS's own launcher,
killed in the middle to stand in for a crash or a restart, paused and resumed. No model and no credits: the scripts
are the approved to-do script with its saved takes (as in test_batch.py). The recordings are real.

  - start returns at once; the batch is a macOS background job, not a child of this process
  - while it waits for Go the Mac may sleep; once it works it keeps the Mac awake itself (caffeinate tied to it)
  - a video with no script is skipped with its reason and doesn't block Go for the others
  - killed mid-batch: macOS starts it again and it carries on; the finished video is not recorded again
  - pause says where it stopped ("paused at video 2 of 3"); resume finishes; the job then removes itself

Usage: .venv/bin/python scripts/batch/test_runner.py
"""
import glob
import json
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'scripts', 'setup'))
import assets  # noqa: E402
assets.need_todo_takes()          # the saved to-do takes (not in the repo); exits 77, skipped, when missing
SRC = os.path.join(ROOT, 'output', 'test-todo-v4')
work = os.path.join(ROOT, 'output', 'runner-test')
shutil.rmtree(work, ignore_errors=True)
os.environ.update({'NAVI_WORK': work, 'NAVI_DATA': tempfile.mkdtemp(prefix='navi-runner-data-'), 'NAVI_NO_QUIET_WAIT': '1', 'NAVI_VARIETY_OFF': '1',
                   'NAVI_NO_QA': '1', 'NAVI_NO_BLIND': '1', 'NAVI_FAKE_CREDITS': '50000', 'NAVI_RUNNER_POLL': '1'})
os.environ.pop('NAVI_NO_LAUNCHD', None)
sys.path.insert(0, HERE)
import batch  # noqa: E402
import runner  # noqa: E402
import store  # noqa: E402

ok, rows = True, []


def check(name, cond, detail=''):
    global ok
    ok &= bool(cond)
    rows.append(f"| {name} | {'pass' if cond else '**FAIL**'} | {detail} |")
    print(rows[-1], flush=True)


def wait(cond, secs, every=2):
    end = time.time() + secs
    while time.time() < end:
        if cond():
            return True
        time.sleep(every)
    return False


def caffeinated(pid):
    # anchored at the start of the command, so a shell whose own command line mentions caffeinate is never counted
    return subprocess.run(['pgrep', '-f', f'^/usr/bin/caffeinate -i -m -s -w {pid}'], capture_output=True).returncode == 0


def loaded(bid):
    return subprocess.run(['launchctl', 'print', f'gui/{os.getuid()}/{runner.label(bid)}'], capture_output=True).returncode == 0


b = batch.new('Runner check', 'Adding your first task\nAdding a few more\nA page that is not there\n', 'https://demo.playwright.dev/todomvc', export_to=tempfile.mkdtemp())
bid = b['id']
d1, d2, d3 = b['items']
approved = json.load(open(os.path.join(ROOT, 'examples', 'test-todo-b.json')))
sections = json.loads(json.dumps(approved['sections']))
for d in (d1, d2):
    f = store.demo_dir(d)
    t = json.load(open(os.path.join(f, 'script.template.json')))
    json.dump({**t, 'sections': sections, 'explore': os.path.join(ROOT, 'examples', 'explore-test-todo')}, open(os.path.join(f, 'script.json'), 'w'), indent=1)
    for x in glob.glob(os.path.join(SRC, '*_take*')):
        shutil.copy2(x, f)
b = batch.load(bid)
b['written'] = {d1: {'checked': True}, d2: {'checked': True}, d3: {'checked': False, 'why': "the pages couldn't be explored (the page didn't open)"}}
batch.save(b)

try:
    t0 = time.time()
    r = runner.start(bid)
    check('start returns at once', r['started'] and time.time() - t0 < 5, r.get('how', ''))
    check('the batch is a macOS background job', loaded(bid) and os.path.exists(runner.plist_path(bid)), runner.label(bid))
    ok_wait = wait(lambda: runner.status(bid)['waiting_for'] == 'Go', 60)
    st = runner.status(bid)
    check('it is not a child of this process', st['alive'] and st['pid'] != os.getpid() and os.getppid() != st['pid']
          and subprocess.run(['ps', '-o', 'ppid=', '-p', str(st['pid'])], capture_output=True, text=True).stdout.strip() == '1', f"pid {st['pid']}, parent 1 (macOS)")
    check('it waits on the Go screen, and lets the Mac sleep meanwhile', ok_wait and batch.load(bid)['state'] == 'ready' and not st['awake'] and not caffeinated(st['pid']))
    p = batch.plan(bid)
    check('the Go screen: two videos ready, the one without a script listed as skipped, not blocking',
          p['ready'] and p['skipping'] == ['A page that is not there'], str(p['skipping']))

    runner.start(bid, go=True)                    # the Go click
    ok_rec = wait(lambda: runner.status(bid)['phase'] == 'recording', 120)
    st = runner.status(bid)
    check('Go: it starts, and keeps the Mac awake itself', ok_rec and st['awake'] and caffeinated(st['pid']), f"caffeinate -i -m -s -w {st['pid']}")
    ok1 = wait(lambda: store.demo(d1)['recorded'], 900, 5)
    rec1 = os.path.join(store.demo_dir(d1), 'recording', 'recording.mp4')
    m1 = os.path.getmtime(rec1) if ok1 else 0
    check('video 1 recorded', ok1)
    wait(lambda: 'Recording' in (store.demo(d2).get('status') or '') or 'Timing' in (store.demo(d2).get('status') or ''), 120)
    time.sleep(8)

    pid = runner.status(bid)['pid']               # a crash / power cut / restart: everything of the batch dies at once
    os.killpg(os.getpgid(pid), signal.SIGKILL)
    back = wait(lambda: runner.status(bid)['alive'] and runner.status(bid)['pid'] != pid, 90)
    check('killed mid-batch: macOS starts it again by itself', back, f"pid {pid} -> {runner.status(bid)['pid']}")
    check('it carries on from where it stopped', wait(lambda: any('Carrying on from where it stopped (recording)' in x['text'] for x in batch.load(bid)['log']), 60)
          and wait(lambda: runner.status(bid)['phase'] == 'recording', 60))
    check('and keeps the Mac awake again', wait(lambda: caffeinated(runner.status(bid)['pid'] or 0), 30))
    wait(lambda: 'Recording' in (store.demo(d2).get('status') or ''), 180)
    time.sleep(5)

    st = runner.stop(bid)                         # pause
    time.sleep(3)
    check('pause: stopped, off macOS\'s list, and it says where', not runner.status(bid)['alive'] and not loaded(bid) and not os.path.exists(runner.plist_path(bid))
          and batch.load(bid)['state'] == 'paused' and runner.status(bid)['line'] == 'paused at video 2 of 3', str(runner.status(bid)['line']))
    check('paused: the Mac is let go', wait(lambda: not caffeinated(''), 20))
    check('paused: nothing of the batch is left running', wait(lambda: subprocess.run(['pgrep', '-f', work], capture_output=True).returncode != 0, 20))
    check('the state the app reads carries it', any(x['id'] == bid and x.get('runner', {}).get('line') == 'paused at video 2 of 3' for x in store.batches()))

    runner.start(bid)                             # resume
    done = wait(lambda: batch.load(bid)['state'] == 'review' and not runner.status(bid)['alive'], 1200, 5)
    b = batch.load(bid)
    check('resume: the batch finishes', done and store.demo(d1)['recorded'] and store.demo(d2)['recorded'], b['state'])
    check('the finished video was not recorded again', os.path.getmtime(rec1) == m1)
    check('the video without a script was skipped with its reason', b['results'][d3]['status'] == 'skipped' and "couldn't be explored" in b['results'][d3]['why'], b['results'][d3]['why'])
    report = open(os.path.join(batch.bdir(bid), 'batch-report.md')).read()
    check('the report says so', '2 done, 1 skipped' in report and "couldn't be explored" in report)
    check('finished: the job removed itself', wait(lambda: not loaded(bid), 30) and not os.path.exists(runner.plist_path(bid)))
finally:
    if os.path.exists(runner.plist_path(bid)):
        os.remove(runner.plist_path(bid))
    subprocess.run(['launchctl', 'bootout', f'gui/{os.getuid()}/{runner.label(bid)}'], capture_output=True)
print('\n**PASS**' if ok else '\n**FAIL**')
sys.exit(0 if ok else 1)
