"""Check for the per-job models (scripts/jobs/jobs.py), with a stand-in `claude` so nothing is spent:

- every job runs on the model and effort config/defaults.json names, by full ID, never an alias;
- an unavailable model falls back to the next one, with a visible warning; another kind of failure doesn't;
- a headless run never falls back to Fable, an attended one may;
- claude-opus-4-6 is flagged after 2027-01-15 and not before;
- model, effort, time and tokens of every run land in the log and in the batch report's Models table.

Usage: .venv/bin/python scripts/jobs/test_jobs.py        (add --live to also ask each real model for one word)
"""
import json
import os
import stat
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import jobs  # noqa: E402

tmp = tempfile.mkdtemp(prefix='navi-jobs-')
fake = os.path.join(tmp, 'claude')
calls = os.path.join(tmp, 'calls.jsonl')
# The stand-in: logs what it was asked, is "unavailable" for the models in $FAKE_DOWN, breaks for those in $FAKE_BROKEN.
open(fake, 'w').write(f'''#!{sys.executable}
import json, os, sys
a = sys.argv[1:]
m, e = a[a.index('--model') + 1], a[a.index('--effort') + 1]
open({calls!r}, 'a').write(json.dumps({{'model': m, 'effort': e, 'args': a, 'prompt': sys.stdin.read()[:80]}}) + '\\n')
base = {{'type': 'result', 'num_turns': 1, 'total_cost_usd': 0.01}}
if m in os.environ.get('FAKE_DOWN', '').split(','):
    sys.stderr.write('[claude-code:unrecognized_model] ' + m + '\\n')
    print(json.dumps(base | {{'is_error': True, 'subtype': 'error', 'api_error_status': 404, 'result': 'model not found', 'modelUsage': {{}}}}))
elif m in os.environ.get('FAKE_BROKEN', '').split(','):
    print(json.dumps(base | {{'is_error': True, 'subtype': 'error', 'api_error_status': 401, 'result': 'Invalid credentials', 'modelUsage': {{}}}}))
else:
    print(json.dumps(base | {{'is_error': False, 'subtype': 'success', 'result': 'done by ' + m,
          'modelUsage': {{m: {{'inputTokens': 100, 'cacheReadInputTokens': 20, 'cacheCreationInputTokens': 5, 'outputTokens': 7}}}}}}))
''')
os.chmod(fake, os.stat(fake).st_mode | stat.S_IEXEC)
os.environ['NAVI_CLAUDE_BIN'] = fake
os.environ.pop('NAVI_JOBS_LOG', None)
ok, rows = True, []


def check(name, cond, detail=''):
    global ok
    ok &= bool(cond)
    rows.append(f"| {name} | {'pass' if cond else '**FAIL**'} | {detail} |")
    print(rows[-1], flush=True)


def last_calls(n):
    return [json.loads(x) for x in open(calls).read().splitlines()][-n:]


cfg = jobs.config()
want = {'planning': ('claude-fable-5-2', 'high', ['claude-opus-5-5']), 'explore': ('claude-haiku-5-5', 'medium', ['claude-sonnet-5-5']),
        'writing': ('claude-opus-5-5', 'medium', ['claude-sonnet-5-5']), 'checks': ('claude-sonnet-5-5', 'medium', ['claude-opus-5-5']),
        'batch_qa': ('claude-opus-5-5', 'high', ['claude-sonnet-5-5'])}
check('config holds the five jobs as asked', all((cfg[j]['model'], cfg[j]['effort'], cfg[j]['fallback']) == want[j] for j in want))
log = os.path.join(tmp, 'jobs.jsonl')
for j in jobs.JOBS:
    e = jobs.run(j, 'hello', log=log, demo='video-1')
    c = last_calls(1)[0]
    check(f'{j} runs on its own model and effort', (c['model'], c['effort']) == want[j][:2] and e['model'] == want[j][0], f"{c['model']} / {c['effort']}")
check('every call names a full model ID', all(jobs.FULL_ID.match(c['model']) for c in last_calls(5)))
def arg(c, flag):
    return c['args'][c['args'].index(flag) + 1]


five = last_calls(5)
check('lean: own short instructions, none of the user\'s settings, skills off',
      all('--system-prompt' in c['args'] and arg(c, '--setting-sources') == '' and '--disable-slash-commands' in c['args'] for c in five))
check('lean: each job gets only its own few tools (planning none)',
      [arg(c, '--tools') for c in five] == ['', 'Read,Write,Bash', 'Read,Write,Edit,Bash', 'Read,Edit,Bash', 'Read,Bash'], str([arg(c, '--tools') for c in five]))
check('subagents get no MCP servers and never prompt', all('--strict-mcp-config' in c['args'] and 'dontAsk' in c['args'] for c in last_calls(5)))
e = jobs.read_log(log)[-1]
check('the log has model, effort, time and tokens', e['model'] and e['effort'] and 'seconds' in e and e['tokens_in'] == 125 and e['tokens_out'] == 7, json.dumps({k: e[k] for k in ('model', 'effort', 'seconds', 'tokens_in', 'tokens_out')}))
for bad in ('opus', 'sonnet', 'claude-opus-latest', 'opus-5-5'):
    try:
        jobs.check_id(bad)
        check(f'alias "{bad}" refused', False)
    except jobs.JobError:
        check(f'alias "{bad}" refused', True)

os.environ['FAKE_DOWN'] = 'claude-opus-5-5'
e = jobs.run('writing', 'hello', log=log)
check('unavailable model: the fallback runs', e['model'] == 'claude-sonnet-5-5' and e['effort'] == 'medium', e['model'])
check('...with a visible warning', 'claude-opus-5-5 was unavailable' in e.get('warning', ''), e.get('warning', ''))
os.environ['FAKE_DOWN'] = 'claude-sonnet-5-5'
e = jobs.run('checks', 'hello', log=log)
check('checks falls back to its own list', e['model'] == 'claude-opus-5-5')

# never Fable as a fallback when nobody is watching
os.environ['FAKE_DOWN'] = 'claude-haiku-5-5'
fb = ['claude-fable-5-2', 'claude-sonnet-5-5']
e = jobs.run('explore', 'hello', fallback=fb)
check('headless: Fable in a fallback list is passed over', e['model'] == 'claude-sonnet-5-5', e['model'])
e = jobs.run('explore', 'hello', fallback=fb, headless=False)
check('attended: Fable may be the fallback', e['model'] == 'claude-fable-5-2', e['model'])
try:
    jobs.run('explore', 'hello', fallback=['claude-fable-5-2'])
    check('headless with only Fable left: the job stops, saying why', False)
except jobs.JobError as err:
    check('headless with only Fable left: the job stops, saying why', 'never a fallback' in str(err) or 'no model was available' in str(err), str(err)[:90])
os.environ['FAKE_DOWN'] = ''
e = jobs.run('planning', 'hello')
check("planning's own model is Fable, headless too", e['model'] == 'claude-fable-5-2')
os.environ['FAKE_DOWN'] = 'claude-fable-5-2'
e = jobs.run('planning', 'hello')
check('planning falls back to Opus 5.5', e['model'] == 'claude-opus-5-5' and e.get('warning'))

os.environ['FAKE_DOWN'], os.environ['FAKE_BROKEN'] = '', 'claude-opus-5-5'
n = len(open(calls).read().splitlines())
try:
    jobs.run('writing', 'hello')
    check('a failure that is not "unavailable" does not fall back', False)
except jobs.JobError as err:
    check('a failure that is not "unavailable" does not fall back', len(open(calls).read().splitlines()) == n + 1, str(err)[:80])
os.environ['FAKE_BROKEN'] = ''

# the date warning
old = json.loads(json.dumps(cfg))
old['writing']['blind_test'] = {'arms': [{'model': 'claude-opus-5-5', 'effort': 'low'}, {'model': 'claude-opus-4-6', 'effort': 'medium'}]}
import datetime  # noqa: E402
check('claude-opus-4-6: no warning on 2027-01-15', not jobs.warnings(old, datetime.date(2027, 1, 15)))
w = jobs.warnings(old, datetime.date(2027, 1, 16))
check('claude-opus-4-6: warning from 2027-01-16', len(w) == 1 and 'claude-opus-4-6' in w[0] and 'writing' in w[0], w[0] if w else '')
plain = {k: ({x: y for x, y in v.items() if x != 'blind_test'} if isinstance(v, dict) else v) for k, v in cfg.items()}
check('no warning while nothing uses it', not jobs.warnings(plain, datetime.date(2027, 6, 1)))
check('the real config no longer uses claude-opus-4-6 (dropped 13 Nov 2026), so it is quiet after the date too',
      not jobs.warnings(cfg, datetime.date(2026, 11, 12)) and not jobs.warnings(cfg, datetime.date(2027, 1, 16)))

# the batch report's Models part
lines = jobs.report_lines(jobs.read_log(log), {'video-1': 'Adding a task'}, cfg)
txt = '\n'.join(lines)
check('report: one row per run with model, effort, time and tokens', '| Writing | Adding a task | claude-opus-5-5 | medium |' in txt and '| 105 | 7 | 20 |' in txt)
check('report: real cost per video, cache re-reads left out', 'Per video (1): about' in txt and 'new tokens in' in txt)
check('report: the fallback warning is shown', '**Warning:** Writing: claude-opus-5-5 was unavailable, so claude-sonnet-5-5 did it instead.' in txt)

if '--live' in sys.argv:
    del os.environ['NAVI_CLAUDE_BIN']
    r = subprocess.run([sys.executable, os.path.join(HERE, 'jobs.py'), 'ping'], capture_output=True, text=True)
    check('live: every configured model answers', r.returncode == 0, r.stdout.strip().replace('\n', '; '))

print('\nPASS' if ok else '\nFAIL')
sys.exit(0 if ok else 1)
