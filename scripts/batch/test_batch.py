"""Batch check: a batch of 3 videos runs from the list to export, with no real credits spent and no question asked
mid-run (Phase 7, and Andy's 11 Nov 2026 "batch this just works" rules).

The three scripts are the approved to-do demo under three titles. Videos 1 and 3 reuse its saved voice takes, so they
cost nothing. Video 2 starts without takes, so it really needs about 1,400 credits. With a simulated 1,500 left
(NAVI keeps 1,000 spare): Go is refused up front, before anything is spent, saying why; and a run started anyway
never asks: it skips video 2 with the reason, records 1 and 3, and writes the morning report. Then the "top-up": its
takes are copied in (still no real credits) and the batch finishes. "go --auto" waits on the Go screen while the
"start without the Go click" setting is off. Then the review queue, approval and export with the list file.

Usage: .venv/bin/python scripts/batch/test_batch.py <export folder outside the repo>
"""
import csv
import glob
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
PY = os.path.join(ROOT, '.venv', 'bin', 'python')
EXPORT = os.path.abspath(sys.argv[1])
SRC = os.path.join(ROOT, 'output', 'test-todo-v4')
work = os.path.join(ROOT, 'output', 'batch-test')
shutil.rmtree(work, ignore_errors=True)
shutil.rmtree(EXPORT, ignore_errors=True)
# NAVI_VARIETY_OFF: the three videos reuse one recorded script on purpose (no credits), which the variety check
# would rightly refuse; variety is tested on its own (scripts/script/test_variety.py)
env = {**os.environ, 'NAVI_WORK': work, 'NAVI_DATA': tempfile.mkdtemp(prefix='navi-batch-data-'), 'NAVI_NO_QUIET_WAIT': '1',
       'NAVI_VARIETY_OFF': '1', 'NAVI_NO_QA': '1'}   # NAVI_NO_QA: the last check is a model job (scripts/jobs/test_jobs.py)
rows, ok = [], True


def check(name, cond, detail=''):
    global ok
    ok &= bool(cond)
    rows.append(f"| {name} | {'pass' if cond else '**FAIL**'} | {detail} |")
    print(rows[-1], flush=True)


def batch(*args, credits=None):
    e = dict(env)
    if credits is not None:
        e['NAVI_FAKE_CREDITS'] = str(credits)
    r = subprocess.run([PY, os.path.join(HERE, 'batch.py'), *args], capture_output=True, text=True, env=e)
    return r.returncode, r.stdout + r.stderr


def copy_takes(folder):
    for f in glob.glob(os.path.join(SRC, '*_take*')):
        shutil.copy2(f, folder)


lst = os.path.join(tempfile.mkdtemp(), 'videos.txt')
open(lst, 'w').write('1. Adding your first task\n2. Adding a few more | three tasks and ticking one off\n- Filtering and clearing\n')
code, out = batch('new', '--name', 'To-do course', '--list', lst, '--site', 'https://demo.playwright.dev/todomvc', '--export-to', EXPORT)
bid = out.split()[1].rstrip(':')
b = json.load(open(os.path.join(work, 'batches', bid, 'batch.json')))
folders = [os.path.join(work, d) for d in b['items']]
check('a list in', code == 0 and len(folders) == 3 and all(os.path.exists(os.path.join(f, 'script.template.json')) for f in folders),
      '3 videos from a 3-line list (numbers, bullets and "| what to show" handled)')
code, out = batch('approve', bid)
check('approval refused while no script exists', code != 0 and 'No script is ready yet' in out)

approved = json.load(open(os.path.join(ROOT, 'examples', 'test-todo-b.json')))
# The approved to-do script says "down at the bottom" for the bottom of the list, which the position check now
# (rightly) refuses; the batch scripts say which, and carry the to-do explore data the check needs.
sections = json.loads(json.dumps(approved['sections']).replace('down at the bottom', 'down at the bottom of the list')
                      .replace('At the bottom', 'At the bottom of the list'))
for f in folders:
    t = json.load(open(os.path.join(f, 'script.template.json')))
    json.dump({**t, 'sections': sections, 'explore': os.path.join(ROOT, 'examples', 'explore-test-todo')},
              open(os.path.join(f, 'script.json'), 'w'), indent=1)
NEW_CREDITS = 2 * sum(len(s['talk']) for s in sections)   # video 2 needs both takes of every section
copy_takes(folders[0])
copy_takes(folders[2])
code, out = batch('sheet', bid, credits=1500)
sheet = open(os.path.join(work, 'batches', bid, 'batch-scripts.md')).read()
check('every script in one list', code == 0 and sheet.count('Talking version') == 3 and f'about {NEW_CREDITS:,}' in sheet,
      f'batch-scripts.md: 3 scripts side by side; about {NEW_CREDITS:,} credits (only video 2 needs new takes)')
code, out = batch('approve', bid)
check('all approved at once', code == 0 and "'approved'" in out)

code, out = batch('plan', bid, credits=1500)
p = json.loads(out[out.index('{'):])
check('the Go screen: every video, its cost, the total against the credits', len(p['videos']) == 3 and p['total'] == NEW_CREDITS
      and p['short'] and [v['cost'] for v in p['videos']] == [0, NEW_CREDITS, 0] and p['logins'] == [],
      f"costs {[v['cost'] for v in p['videos']]}, total {p['total']:,}, {p['left']:,} left: short; no login needed (a public site)")

code, out = batch('go', bid, '--auto', credits=100000)
b = json.load(open(os.path.join(work, 'batches', bid, 'batch.json')))
check('go --auto waits for Go while the setting is off', code == 2 and b['state'] == 'ready' and not glob.glob(os.path.join(folders[0], 'recording')),
      f"state {b['state']}: {b['reason']}")

code, out = batch('go', bid, credits=1500)
b = json.load(open(os.path.join(work, 'batches', bid, 'batch.json')))
nothing = not glob.glob(os.path.join(folders[1], '*_take*')) and not glob.glob(os.path.join(folders[0], 'recording'))
check('Go refused up front when the credits are short, nothing spent', code == 2 and b['state'] == 'needs you' and nothing
      and 'credits' in b['reason'], b['reason'])

code, out = batch('run', bid, credits=1500)
b = json.load(open(os.path.join(work, 'batches', bid, 'batch.json')))
nothing = not glob.glob(os.path.join(folders[1], '*_take*'))
report = open(os.path.join(work, 'batches', bid, 'batch-report.md')).read() if os.path.exists(os.path.join(work, 'batches', bid, 'batch-report.md')) else ''
check('mid-run, never a question: the video it can\'t pay for is skipped, the rest recorded', code == 0 and b['state'] == 'review' and nothing
      and os.path.exists(os.path.join(folders[0], 'recording', 'recording.mp4')) and os.path.exists(os.path.join(folders[2], 'recording', 'recording.mp4')),
      f"videos 1 and 3 recorded; video 2 skipped, nothing of it generated: {nothing}")
check('the morning report says what was done and what was skipped, and why', '2 done, 1 skipped' in report and 'not enough credits' in report
      and len(b['report']['skipped']) == 1, report.splitlines()[2] if report else 'no batch-report.md')

copy_takes(folders[1])               # the "top-up", without spending real credits
code, out = batch('run', bid, credits=100000)
b = json.load(open(os.path.join(work, 'batches', bid, 'batch.json')))
recs = [json.load(open(os.path.join(f, 'recording', 'report.json'))) for f in folders if os.path.exists(os.path.join(f, 'recording', 'report.json'))]
check('finishes after the top-up', code == 0 and b['state'] == 'review' and len(recs) == 3 and not b['report']['skipped'],
      f"3 recorded; join checks: {', '.join('pass' if r['checks']['pass'] else 'FAIL' for r in recs)}")

code, out = batch('queue', bid)
check('review queue', code == 0 and out.count(' s), ') == 3, '3 videos waiting, with length, unsure blurs and marks')
code, out = batch('export', bid)
check('nothing exported before review', 'Nothing approved' in out)
for d in b['items']:
    batch('review', bid, d, 'approve')
code, out = batch('export', bid)
folder = os.path.join(EXPORT, 'To-do course')
lst_csv = os.path.join(folder, 'To-do course - list.csv')
videos = sorted(x for x in os.listdir(folder) if x.endswith('.mp4')) if os.path.isdir(folder) else []
listed = list(csv.reader(open(lst_csv)))[1:] if os.path.exists(lst_csv) else []
check('export plus a list file', code == 0 and len(videos) == 3 and len(listed) == 3 and os.path.exists(os.path.join(folder, 'To-do course - list.md')),
      f"{len(videos)} videos, {len(listed)} rows in \"To-do course - list.csv\" and .md, in {folder}")
check('never published', 'upload' not in open(os.path.join(HERE, 'batch.py')).read().replace('Nothing is ever uploaded', '').replace('Nothing was uploaded', '').lower(),
      'the batch code has no upload or publish step at all')
print('\n'.join(['', '| Check | Result | Detail |', '|---|---|---|'] + rows + ['', f"**{'PASS' if ok else 'FAIL'}**"]))
sys.exit(0 if ok else 1)
