"""Checks for videos on two or more logins, and the house rules (never_name, spelling, a seat per section).
No browser, no credits: a scratch $NAVI_DATA with two fake saved logins.

  .venv/bin/python scripts/seats/test_multi.py
"""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
data = tempfile.mkdtemp(prefix='navi-multi-')
os.environ['NAVI_DATA'] = data
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, 'scripts', 'script'))
import seats  # noqa: E402
import house_rules  # noqa: E402

fails = []


def ok(cond, what, got=''):
    print(('ok    ' if cond else 'FAIL  ') + what + (f'  ({got})' if got != '' else ''))
    if not cond:
        fails.append(what)


json.dump({'x.com': {'seats': {'owner': {'home': 'https://x.com/home'}}},
           'google.com': {'covers': ['docs.google.com', 'mail.google.com'], 'seats': {'owner': {'home': 'https://docs.google.com/spreadsheets/'}}}},
          open(os.path.join(data, 'seats.json'), 'w'))
for site, cookie in (('x.com', {'name': 'auth_token', 'value': 'X', 'domain': '.x.com', 'path': '/'}),
                     ('google.com', {'name': 'SID', 'value': 'G', 'domain': '.google.com', 'path': '/'})):
    os.makedirs(os.path.join(data, 'logins', site), exist_ok=True)
    json.dump({'cookies': [cookie], 'origins': [{'origin': f'https://{site}', 'localStorage': []}]},
              open(os.path.join(data, 'logins', site, 'owner.json'), 'w'))

ok(seats.login_site('docs.google.com') == 'google.com', 'docs.google.com uses the google.com login')
ok(seats.login_file('docs.google.com').endswith('logins/google.com/owner.json'), 'its saved login is google.com/owner')

script = {'site': 'x.com', 'seats': [{'site': 'x.com', 'seat': 'owner'}, {'site': 'google.com', 'seat': 'owner'}],
          'sections': [{'name': 'a', 'seat': 'x.com', 'talk': 'x', 'caption': 'x', 'actions': [{'do': 'goto', 'on': 'start', 'target': 'https://x.com/home'}]},
                       {'name': 'b', 'seat': 'google.com', 'talk': 'x', 'caption': 'x', 'actions': [{'do': 'goto', 'on': 'start', 'target': 'https://docs.google.com/spreadsheets/'}]}]}
fs = seats.for_script(script)
ok([x['site'] for x in fs['seats']] == ['x.com', 'google.com'], 'both logins listed, main first', [x['site'] for x in fs['seats']])
joined = json.load(open(fs['login']))
ok(sorted(c['name'] for c in joined['cookies']) == ['SID', 'auth_token'], 'the joined session holds both logins')
ok(oct(os.stat(fs['login']).st_mode & 0o777) == '0o600', 'the joined session is readable only by the user')
ok(fs['login'].startswith(os.path.join(data, 'logins', '_joined')), 'kept with the logins, not in a video folder')
ok(seats.for_script(script)['login'] == fs['login'], 'the same logins give the same joined file')
d = seats.describe(script)
ok('x.com (owner)' in d['label'] and 'google.com (owner)' in d['label'] and d['login_saved'], 'the preview names both logins', d['label'])
g = seats.guard_config(script, '/dev/null')
ok(g['sites'] == ['x.com', 'google.com'], 'the guard gets both sites', g['sites'])

# a missing second login is reported, not hidden
os.remove(os.path.join(data, 'logins', 'google.com', 'owner.json'))
d2 = seats.describe(script)
ok(not d2['login_saved'] and 'not logged in' in d2['label'], 'a missing login shows on the preview', d2['label'])

# house rules
codes = lambda sc: [c for _, c, _, _ in house_rules.check(sc)]
ok(codes(script) == [], 'a seat per section, each opening its own site: no issues', codes(script))
bad = json.loads(json.dumps(script))
del bad['sections'][1]['seat']
ok('seat' in codes(bad), 'a section with no seat in a two-login video is an error')
bad = json.loads(json.dumps(script))
bad['sections'][0]['actions'][0]['target'] = 'https://docs.google.com/x'
ok('seat' in codes(bad), 'a section opening the other login\'s site is an error')
tool = {'never_name': ['NAVI', 'ElevenLabs'], 'sections': [{'name': 'a', 'talk': 'I made this with Eleven Labs.', 'caption': 'Fine.'}]}
ok(codes(tool) == ['never-name'], 'a never_name word in the voice is an error (also with a space inside)', codes(tool))
ok(codes({'never_name': ['NAVI'], 'sections': [{'name': 'a', 'talk': 'navigate to it', 'caption': 'Navigation'}]}) == [],
   'whole words only ("navigate" is not "NAVI")')
us = {'spelling': 'US', 'sections': [{'name': 'a', 'talk': 'x', 'caption': 'Pick your favourite colour and organise it.'}]}
ok(codes(us) == ['spelling'] * 3, 'British spellings in a US caption are errors', codes(us))
uk = {'spelling': 'UK', 'sections': [{'name': 'a', 'talk': 'x', 'caption': 'Enroll in the program, then optimize it.'}]}
ok(codes(uk) == ['spelling'] * 2, 'American spellings in a UK caption are errors ("program" is fine)', codes(uk))

# the guard: each request against its own site's pack; a logged-in site with no pack has its changes blocked
r = subprocess.run(['node', '--input-type=module', '-e', '''
import { classify } from "./scripts/guard/guard.mjs";
const pack = {own_hosts: "(^|\\\\.)x\\\\.com$", dangerous: [{category: "post", reason: "posting", match: [{op: "CreateTweet"}]}]};
const req = {method: "POST", host: "x.com", path: "/i/api/graphql/abc/CreateTweet", query: "", ops: [{kind: "mutation", name: "CreateTweet"}], body: ""};
console.log(JSON.stringify(classify(req, pack, {business: {name: "your own account", real: true}})));
'''], cwd=ROOT, capture_output=True, text=True)
ok('"block"' in r.stdout and 'posting' in r.stdout, 'a post on X is blocked by its pack', (r.stdout or r.stderr).strip()[:120])

print('\nall multi-login checks passed' if not fails else f'\n{len(fails)} FAILED')
sys.exit(1 if fails else 0)
