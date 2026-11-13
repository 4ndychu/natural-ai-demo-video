"""Phase 7 engine check, app side: the local server, "wait for the app", real state, Keychain/logins/"Your data".

Runs a server on a spare port against throwaway folders (NAVI_DATA, NAVI_WORK) and a throwaway Keychain entry
(NAVI_KEY_SERVICE), so the user's real key, logins and settings are never touched.

Usage: .venv/bin/python scripts/app/test_app.py
"""
import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
PY = os.path.join(ROOT, '.venv', 'bin', 'python')

tmp = tempfile.mkdtemp(prefix='navi-app-test-')
env = {**os.environ, 'NAVI_DATA': os.path.join(tmp, 'data'), 'NAVI_WORK': os.path.join(tmp, 'work'),
       'NAVI_KEY_SERVICE': f'navi-test-{os.getpid()}'}
env.pop('NAVI_ELEVENLABS_KEY', None)
s = socket.socket()
s.bind(('127.0.0.1', 0))
port = s.getsockname()[1]
s.close()
srv = subprocess.Popen([PY, os.path.join(HERE, 'server.py'), '--port', str(port)], env=env, stdout=subprocess.PIPE, text=True)
srv.stdout.readline()
base = f'http://127.0.0.1:{port}'
ORIGIN = base
rows, ok = [], True


def check(name, cond, detail=''):
    global ok
    ok &= bool(cond)
    rows.append(f"| {name} | {'pass' if cond else '**FAIL**'} | {detail} |")


def call(path, body=None, origin=ORIGIN, host=None):
    h = {'Content-Type': 'application/json'}
    if origin:
        h['Origin'] = origin
    if host:
        h['Host'] = host
    req = urllib.request.Request(base + path, data=json.dumps(body).encode() if body is not None else None, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            ctype = r.headers.get('Content-Type', '')
            raw = r.read()
            return r.status, (json.loads(raw) if 'json' in ctype else raw)
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b'{}')


try:
    code, st = call('/api/state')
    check('state', code == 200 and st['key']['stored'] is False and st['demos'] == [] and 'settings' in st,
          f"settings, key (stored: {st['key']['stored']}), {len(st['demos'])} demos, logins, batches")
    code, html = call('/')
    check('serves the app as it is', code == 200 and html == open(os.path.join(ROOT, 'ui', 'index.html'), 'rb').read(), 'ui/index.html, read only')
    check('no files outside ui/', call('/../config/defaults.json')[0] == 404 and call('/%2e%2e/config/defaults.json')[0] == 404)
    check('other host names refused', call('/api/state', host='evil.example')[0] == 403, 'DNS rebinding')
    check('POSTs from other web pages refused', call('/api/action', {'type': 'settings.set', 'patch': {}}, origin='https://evil.example')[0] == 403
          and call('/api/action', {'type': 'settings.set', 'patch': {}}, origin=None)[0] == 403)

    # batches that just work (Andy, 11 Nov 2026): the spending limit and the Go click are settings; Watch live; Go
    code, r = call('/api/action', {'type': 'settings.set', 'patch': {'credit_limit': 5000, 'auto_go': True}})
    bad = call('/api/action', {'type': 'settings.set', 'patch': {'credit_limit': 'lots'}})[0]
    check('spending limit and "start without the Go click" are settings', code == 200 and r['settings']['credit_limit'] == 5000
          and r['settings']['auto_go'] is True and bad == 400, 'credit_limit 5000, auto_go on; a non-number refused')
    call('/api/action', {'type': 'settings.set', 'patch': {'credit_limit': 10000, 'auto_go': False}})
    code, body = call('/api/live/no-such-demo')
    check('Watch live: nothing recording gives an empty answer', code == 204 and body == b'', 'GET /api/live/<demo>: 204')
    check('Go on an unknown batch is refused', call('/api/action', {'type': 'batch.go', 'batch': 'nope-1'})[0] == 400)
    code, r = call('/api/action', {'type': 'logins.check'})
    code2, st2 = call('/api/state')
    check('logins checked live, in the background', code == 200 and 'logins_checking' in st2, 'logins.check, then logins_checking in the state')

    # wait for the app: an action reaches a waiting Claude
    got = {}
    t = threading.Thread(target=lambda: got.update(r=subprocess.run([PY, os.path.join(HERE, 'wait.py'), '--port', str(port), '--timeout', '30'],
                                                                     capture_output=True, text=True)))
    t.start()
    time.sleep(1.0)
    code, r = call('/api/action', {'type': 'demo.new', 'title': 'Connect payouts', 'site': 'whop.com', 'kind': 'course'})
    did = r['demo']['id']
    t.join(40)
    w = json.loads(got['r'].stdout)
    check('"wait for the app" returns the click', got['r'].returncode == 0 and w['actions'][0]['type'] == 'demo.new'
          and w['actions'][0]['result']['demo']['id'] == did, f"type demo.new, demo {did}, step {r['demo']['step_name']}")
    code, st = call('/api/state')
    check('real state has the demo', any(d['id'] == did and d['status'] == 'Writing script' for d in st['demos']))

    # settings
    code, r = call('/api/action', {'type': 'settings.set', 'patch': {'captions': 'file', 'speed_copy': 1.35, 'hide_words': ['Acme']}})
    check('settings saved', code == 200 and r['settings']['captions'] == 'file' and call('/api/state')[1]['settings']['speed_copy'] == 1.35)
    check('bad settings refused', call('/api/action', {'type': 'settings.set', 'patch': {'export_to': ROOT + '/output'}})[0] == 400
          and call('/api/action', {'type': 'settings.set', 'patch': {'captions': 'loud'}})[0] == 400)

    # demo actions
    check('script approval refused while the script has problems', call('/api/action', {'type': 'demo.approve_script', 'demo': did})[0] == 400)
    code, r = call('/api/action', {'type': 'demo.mark', 'demo': did, 't': 12.5, 'text': 'Sounds like AI'})
    check('review marks saved', code == 200 and call(f'/api/demo/{did}')[1]['marks'][0]['text'] == 'Sounds like AI')

    # logins
    os.makedirs(os.path.join(tmp, 'data', 'logins'))
    open(os.path.join(tmp, 'data', 'logins', 'whop.com.json'), 'w').write('{}')
    check('saved logins listed', [l['site'] for l in call('/api/state')[1]['logins']] == ['whop.com'])
    code, r = call('/api/action', {'type': 'login.forget', 'site': 'whop.com'})
    check('forget a login', r['forgot'] and r['logins'] == [])
    open(os.path.join(tmp, 'data', 'logins', 'whop.com.json'), 'w').write('{}')

    # the key: stored in the (throwaway) Keychain entry, never echoed anywhere
    fake = 'sk_' + 'f' * 48
    code, r = call('/api/action', {'type': 'key.store', 'key': fake})
    stored = subprocess.run(['security', 'find-generic-password', '-s', env['NAVI_KEY_SERVICE'], '-w'], capture_output=True, text=True).stdout.strip()
    w = json.loads(subprocess.run([PY, os.path.join(HERE, 'wait.py'), '--port', str(port), '--after', '0', '--timeout', '1'],
                                  capture_output=True, text=True).stdout)
    leaked = fake in json.dumps(w) or fake in json.dumps(call('/api/state')[1]) or fake in json.dumps(r)
    check('key goes to the Keychain only', stored == fake and not leaked, f"stored: {stored == fake}; in the queue, state or reply: {leaked}; "
          f"ElevenLabs said: {r.get('key', {}).get('problem') or 'works'}")

    # Your data: look, then confirm; finished videos untouched
    exports = os.path.join(tmp, 'Movies', 'NAVI')
    os.makedirs(exports)
    open(os.path.join(exports, 'Connect payouts.mp4'), 'wb').write(b'video')
    code, plan = call('/api/action', {'type': 'data.plan_delete', 'what': 'everything'})
    kinds = sorted({i['what'] for i in plan['items']})
    check('"delete everything" shows the list first', code == 200 and kinds == ['demo', 'key', 'login', 'settings']
          and os.path.exists(os.path.join(tmp, 'data', 'settings.json')), ', '.join(kinds) + ' (nothing deleted yet)')
    check('a wrong token deletes nothing', call('/api/action', {'type': 'data.confirm_delete', 'token': 'nope'})[0] == 400)
    code, r = call('/api/action', {'type': 'data.confirm_delete', 'token': plan['token']})
    gone = subprocess.run(['security', 'find-generic-password', '-s', env['NAVI_KEY_SERVICE']], capture_output=True).returncode != 0
    st = call('/api/state')[1]
    check('confirmed: key, logins, settings, drafts gone', code == 200 and gone and st['logins'] == [] and st['demos'] == []
          and not os.path.exists(os.path.join(tmp, 'data', 'settings.json')), f"{len(r['deleted'])} things deleted")
    check('finished videos never touched', os.path.exists(os.path.join(exports, 'Connect payouts.mp4')))
    check('the token works once', call('/api/action', {'type': 'data.confirm_delete', 'token': plan['token']})[0] == 400)
finally:
    srv.terminate()
    subprocess.run(['security', 'delete-generic-password', '-s', env['NAVI_KEY_SERVICE']], capture_output=True)
    shutil.rmtree(tmp, ignore_errors=True)

print('\n'.join(['| Check | Result | Detail |', '|---|---|---|'] + rows + ['', f"**{'PASS' if ok else 'FAIL'}**"]))
sys.exit(0 if ok else 1)
