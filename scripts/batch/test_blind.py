"""Check for the blind A/B/C tests (scripts/batch/blind.py), with no model and no credits spent: the model jobs are
stood in for (each "arm" hands back the approved to-do script, marked with its arm), and the voice reuses the saved
takes of that script, as test_batch.py does. The recording at the end is real.

  plans: one per arm, shown by letter only; nothing is written until one is picked; the pick is recorded
  scripts: one draft per arm for the first videos, each voiced once (one take), shown as A/B/C with the arm hidden
  an arm that fails is left out, never swapped; the pick's script and its one take are what gets recorded
  the arms are revealed only when every pick of the batch is made; the picks add up in blind-picks.jsonl

Usage: .venv/bin/python scripts/batch/test_blind.py
"""
import glob
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
SRC = os.path.join(ROOT, 'output', 'test-todo-v4')
work = os.path.join(ROOT, 'output', 'blind-test')
shutil.rmtree(work, ignore_errors=True)
os.environ.update({'NAVI_WORK': work, 'NAVI_DATA': tempfile.mkdtemp(prefix='navi-blind-data-'), 'NAVI_NO_QUIET_WAIT': '1', 'NAVI_VARIETY_OFF': '1',
                   'NAVI_NO_QA': '1', 'NAVI_FAKE_CREDITS': '50000', 'NAVI_NO_REHEARSAL': '1', 'NAVI_NO_SITE_MEMORY': '1'})
os.environ.pop('NAVI_NO_BLIND', None)
sys.path.insert(0, HERE)
import batch  # noqa: E402
import blind  # noqa: E402
import jobs  # noqa: E402
import store  # noqa: E402

ok, rows, calls = True, [], []
APPROVED = json.load(open(os.path.join(ROOT, 'examples', 'test-todo-b.json')))
# as in test_batch.py: the approved script's "down at the bottom" is said as the position check wants it
APPROVED['sections'] = json.loads(json.dumps(APPROVED['sections']).replace('down at the bottom', 'down at the bottom of the list')
                                  .replace('At the bottom', 'At the bottom of the list'))


def check(name, cond, detail=''):
    global ok
    ok &= bool(cond)
    rows.append(f"| {name} | {'pass' if cond else '**FAIL**'} | {detail} |")
    print(rows[-1], flush=True)


def fake_job(b, name, did=None, arm=None, prompt=None, **fill):
    calls.append({'job': name, 'demo': did, 'arm': arm, 'prompt': prompt})
    cfg = jobs.config()[name]
    e = {'job': name, 'model': (arm or cfg)['model'], 'effort': (arm or cfg)['effort'], 'seconds': 1, 'tokens_out': 1, 'text': 'PASS', 'ok': True}
    if name == 'planning':
        e['data'] = {'videos': [{'id': x, 'goal': f"made by {e['model']} {e['effort']}", 'start_url': 'https://demo.playwright.dev/todomvc', 'sections': []} for x in b['items']]}
    elif name == 'explore':
        ex = os.path.join(ROOT, fill['demo_dir'], 'explore')
        shutil.copy(os.path.join(ROOT, 'examples', 'explore-test-todo', 'explore.json'), ex)
        open(os.path.join(ex, 'notes.md'), 'w').write('notes')
    elif name == 'writing':
        ad = os.path.join(ROOT, fill['demo_dir'])
        if arm and arm['model'] == 'claude-opus-4-6' and did == b['items'][1]:
            raise jobs.JobError('claude-opus-4-6 was unavailable')       # one arm drops out of the second video
        sc = dict(json.load(open(os.path.join(ad, 'draft1.json'))), sections=APPROVED['sections'], _arm=f"{e['model']} {e['effort']}")
        json.dump(sc, open(os.path.join(ad, 'script.json'), 'w'))
        for f in glob.glob(os.path.join(SRC, '*_take*')):           # saved takes: the voice step costs nothing
            shutil.copy2(f, ad)
    return e


batch.job = fake_job
lst = os.path.join(tempfile.mkdtemp(), 'v.txt')
open(lst, 'w').write('Adding your first task\nAdding a few more\n')
b = batch.new('Blind check', open(lst).read(), 'https://demo.playwright.dev/todomvc', export_to=tempfile.mkdtemp())
bid = b['id']
plan_arms, write_arms = blind.cfg('planning')['arms'], blind.cfg('writing')['arms']
check('config: writing test off, claude-opus-5-5 medium locked in (13 Nov 2026: it won 2 of 2 picks); the arms stay for when it is turned back on',
      not blind.cfg('writing').get('enabled') and (jobs.config()['writing']['model'], jobs.config()['writing']['effort']) == ('claude-opus-5-5', 'medium')
      and blind.cfg('writing')['lessons'] == 2 and [(a['model'], a['effort']) for a in write_arms] == [('claude-opus-5-5', 'medium'), ('claude-opus-5-5', 'low')])
# the rest checks the mechanics with three arms, one of which drops out of the second video
write_arms = write_arms + [{'model': 'claude-opus-4-6', 'effort': 'medium'}]
_cfg = blind.cfg
blind.cfg = lambda job: dict(_cfg(job), arms=write_arms, enabled=True) if job == 'writing' else _cfg(job)   # turned on for the mechanics
check('config: planning arms as asked', [(a['model'], a['effort']) for a in plan_arms] == [('claude-fable-5-2', 'high'), ('claude-opus-5-5', 'high'), ('claude-opus-5-5', 'medium')])

r = batch.write(bid)
b = batch.load(bid)
check('planning: one plan per arm, then it waits for the pick', r.get('waiting') == 'plan' and [c['arm'] for c in calls] == plan_arms and b['state'] == 'needs you', b.get('reason', ''))
check('nothing explored or written before the plan is picked', not any(c['job'] in ('explore', 'writing') for c in calls))
v = blind.view(b)
shown = json.dumps(v) + json.dumps({k: x for k, x in b.items() if k != 'log'})
check('plans shown by letter; the letters are not in arm order by rule (shuffled key kept apart)', [o['letter'] for o in v['plan']['options']] == ['A', 'B', 'C']
      and os.path.exists(os.path.join(blind.bdir(b), 'key.json')) and 'key' not in b.get('blind', {}))
check('the batch and the app view never name an arm before the picks', 'effort' not in json.dumps(b.get('blind')) and '"model"' not in json.dumps(v).replace('made by', ''))
key = json.load(open(os.path.join(blind.bdir(b), 'key.json')))
try:
    blind.pick_plan(batch, bid, 'D')
    check('a letter that is not on offer is refused', False)
except ValueError:
    check('a letter that is not on offer is refused', True)
blind.pick_plan(batch, bid, 'B')
plan = json.load(open(os.path.join(batch.bdir(bid), 'plan.json')))
arm = plan_arms[key['plan']['B']]
check('the picked plan is the one used', plan['videos'][0]['goal'] == f"made by {arm['model']} {arm['effort']}", plan['videos'][0]['goal'])

r = batch.write(bid)
b = batch.load(bid)
d1, d2 = b['items']
w = [c for c in calls if c['job'] == 'writing']
check('writing: one draft per arm for each of the first videos, each on its own model and effort',
      [c['arm'] for c in w if c['demo'] == d1] == write_arms and all(c['prompt'] == 'writing_one' for c in w), f"{len(w)} writer runs")
check('each draft goes through the checks job', sum(1 for c in calls if c['job'] == 'checks') == 5)
check('an arm that fails is left out, not swapped', blind.lesson(b, d1)['letters'] == ['A', 'B', 'C'] and blind.lesson(b, d2)['letters'] == ['A', 'B'])
check('both scripts count as written', r['ready'] == 2)
chars = sum(len(s['talk']) for s in APPROVED['sections'])
for f in glob.glob(os.path.join(blind.arm_dir(d2, 0), '*_take1*')):      # video 2, one version: no takes yet
    os.remove(f)
check('credits: one take of each version, not two takes of one', batch.credits_needed(d1) == 0 and batch.credits_needed(d2) == chars, f"video 2 needs {batch.credits_needed(d2):,} for its unvoiced version ({chars:,} characters, one take)")
for f in glob.glob(os.path.join(SRC, '*_take1*')):
    shutil.copy2(f, blind.arm_dir(d2, 0))

batch.approve(bid)
batch.run(bid)
b = batch.load(bid)
v = blind.view(b)
check('run: every version voiced once, then the videos wait for the pick; nothing recorded yet',
      b['state'] == 'needs you' and all(l['status'] == 'waiting' for l in v['lessons']) and not any(store.demo(x)['recorded'] for x in b['items']), b.get('reason', ''))
check('each version can be heard by its letter', all(o['audio'] and os.path.getsize(os.path.join(store.demo_dir(l['demo']), o['audio'])) > 20000 for l in v['lessons'] for o in l['options']),
      ', '.join(f"{l['demo'][:12]}: {'/'.join(o['letter'] for o in l['options'])}" for l in v['lessons']))
check('the versions carry no arm', '_arm' not in json.dumps(v['lessons']) and 'claude' not in json.dumps(v['lessons']))
report = open(os.path.join(batch.bdir(bid), 'batch-report.md')).read()
check('report: waiting for your pick; arms not shown yet', 'Waiting for your pick' in report and 'you picked' not in report)

if os.environ.get('NAVI_BLIND_STOP') == 'waiting':      # leave the batch waiting for picks (to try the app's pick screen on it)
    print('NAVI_DATA=' + os.environ['NAVI_DATA'] + ' BATCH=' + bid)
    sys.exit(0 if ok else 1)
key = json.load(open(os.path.join(blind.bdir(b), 'key.json')))
blind.pick(batch, bid, d1, 'C')
b = batch.load(bid)
want = write_arms[key['lessons'][d1]['C']]
sc = json.load(open(os.path.join(store.demo_dir(d1), 'script.json')))
check('pick: that version\'s script becomes the video\'s', sc.get('_arm') == f"{want['model']} {want['effort']}" and 'explore' not in sc, sc.get('_arm'))
check('pick: its one voice take is the video\'s (nothing generated again)', open(os.path.join(store.demo_dir(d1), 'voice.wav'), 'rb').read() ==
      open(os.path.join(blind.arm_dir(d1, key['lessons'][d1]['C']), 'voice.wav'), 'rb').read() and batch.credits_needed(d1) == 0)
check('arms stay hidden while another pick is open', not b['blind'].get('revealed'))
blind.pick(batch, bid, d2, 'a')
b = batch.load(bid)
picks = blind.read_picks()
check('every pick is recorded with what was on offer', len(picks) == 3 and [p['kind'] for p in picks] == ['planning', 'writing', 'writing'] and len(picks[2]['shown']) == 2)
check('all picks made: the arms are revealed', bool(b['blind'].get('revealed')) and len(b['blind']['revealed']['picks']) == 3, json.dumps(b['blind']['revealed']['tally'])[:160])

voice_before = open(os.path.join(store.demo_dir(d1), 'voice.wav'), 'rb').read()
batch.run(bid)
b = batch.load(bid)
recs = [store.demo(x)['recorded'] for x in b['items']]
check('after the picks the videos record', all(recs) and b['state'] == 'review', str(recs))
check('the recording used the picked take', open(os.path.join(store.demo_dir(d1), 'voice.wav'), 'rb').read() == voice_before and not glob.glob(os.path.join(store.demo_dir(d1), '*_take2.*')))
report = open(os.path.join(batch.bdir(bid), 'batch-report.md')).read()
check('report: which arm each letter was, and the tally', 'you picked **C**' in report and 'picked 1 of' in report)
print('\n' + '\n'.join(l for l in report.splitlines() if 'picked' in l))
print('\n**PASS**' if ok else '\n**FAIL**')
sys.exit(0 if ok else 1)
