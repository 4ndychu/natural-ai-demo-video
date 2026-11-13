"""Settings > Logins, end to end, on a local site where logging in needs no password (Andy, 13 Nov 2026: "I log in,
close it, click Check now, and it still says Not checked yet; Log in again opens a fresh logged-out page").
A throwaway $NAVI_DATA, the app server on a spare port, the real login command (headless, and its page closes by
itself after 4 s, as if the person closed the window: NAVI_LOGIN_HEADLESS / NAVI_LOGIN_CLOSE_AFTER), the real check.
Nothing of the user's is touched; no window opens; no credits.

  .venv/bin/python scripts/app/test_logins.py
"""
import json, os, socket, subprocess, sys, tempfile, threading, time, urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
def port():
    s = socket.socket(); s.bind(('127.0.0.1', 0)); p = s.getsockname()[1]; s.close(); return p
SITE_LOG = []
class Site(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def do_GET(self):
        ok = 'sid=ok' in (self.headers.get('Cookie') or '')
        SITE_LOG.append((self.path, ok))
        if self.path.startswith('/login'):
            if 'auto=1' in self.path:      # "logging in": one click, no password
                self.send_response(302); self.send_header('Set-Cookie', 'sid=ok; Max-Age=2592000; Path=/'); self.send_header('Location', '/'); self.end_headers(); return
            self.send_response(200); self.end_headers(); self.wfile.write(b'<form>Sign in <input type=password></form>'); return
        if self.path == '/?autologin=1' and not ok:     # a site added from "Add a site": opening it logs in
            self.send_response(200); self.send_header('Set-Cookie', 'sid=ok; Max-Age=2592000; Path=/'); self.end_headers(); self.wfile.write(b'<h1>hi</h1>'); return
        if self.path == '/' and not ok:
            self.send_response(302); self.send_header('Location', '/login?next=/'); self.end_headers(); return
        self.send_response(200); self.send_header('Content-Type', 'text/html'); self.end_headers()
        self.wfile.write(b'<h1>Welcome back</h1>' if ok else b'<h1>hi</h1>')
SP = port(); threading.Thread(target=ThreadingHTTPServer(('127.0.0.1', SP), Site).serve_forever, daemon=True).start()
data = tempfile.mkdtemp(prefix='navi-login-repro-')
json.dump({'127.0.0.1': {'seats': {'owner': {'label': 'Owner', 'home': f'http://127.0.0.1:{SP}/'}}}}, open(os.path.join(data, 'seats.json'), 'w'))
AP = port()
env = dict(os.environ, NAVI_DATA=data, NAVI_WORK=tempfile.mkdtemp(prefix='navi-work-'), NAVI_LOGIN_HEADLESS='1', NAVI_LOGIN_CLOSE_AFTER='4000')
srv = subprocess.Popen([os.path.join(REPO, '.venv/bin/python'), os.path.join(REPO, 'scripts/app/server.py'), '--port', str(AP)], env=env, cwd=REPO, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
O = f'http://127.0.0.1:{AP}'
def call(path, body=None):
    r = urllib.request.Request(O + path, data=json.dumps(body).encode() if body is not None else None, headers={'Origin': O, 'Content-Type': 'application/json'})
    with urllib.request.urlopen(r, timeout=120) as f: return json.loads(f.read() or b'{}')
def status(site):
    st = call('/api/state')
    return next(({k: l.get(k) for k in ('status', 'saved')} for l in st['logins'] if l['site'] == site), None), st.get('logins_checking')
def wait_for(site, want, secs=60):
    t = time.time()
    while time.time() - t < secs:
        s, _ = status(site)
        if s and s['status'] == want: return True, round(time.time() - t, 1)
        time.sleep(0.5)
    return False, status(site)
res = []
def check(name, ok, info=''):
    res.append(ok); print(('PASS ' if ok else 'FAIL ') + name, info, flush=True)
try:
    for _ in range(50):
        try: call('/api/state'); break
        except Exception: time.sleep(0.2)
    check('before: needs login', status('127.0.0.1')[0]['status'] == 'needs login', status('127.0.0.1'))
    r = call('/api/action', {'type': 'login.start', 'url': f'http://127.0.0.1:{SP}/login?auto=1', 'seat': 'owner'})
    time.sleep(1.5)
    check('window open shows', status('127.0.0.1')[0]['status'] == 'window open', status('127.0.0.1'))
    r2 = call('/api/action', {'type': 'login.start', 'url': f'http://127.0.0.1:{SP}/', 'seat': 'owner'})
    check('second click while open opens nothing', bool(r2.get('result', r2).get('already_open') if isinstance(r2.get('result', r2), dict) else False), json.dumps(r2)[:200])
    ok, info = wait_for('127.0.0.1', 'working', 60)
    check('after close: Working, without Check now', ok, info)
    call('/api/action', {'type': 'logins.check'})
    t = time.time()
    while status('127.0.0.1')[1] and time.time() - t < 60:
        time.sleep(0.5)
    check('Check now: Working once the check ends', status('127.0.0.1') == ({'status': 'working', 'saved': status('127.0.0.1')[0]['saved']}, False), status('127.0.0.1'))
    SITE_LOG.clear()
    call('/api/action', {'type': 'login.start', 'url': f'http://127.0.0.1:{SP}/', 'seat': 'owner'})
    time.sleep(3)
    first = SITE_LOG[0] if SITE_LOG else None
    check('Log in again opens logged in', first == ('/', True), SITE_LOG[:3])
    wait_for('127.0.0.1', 'working', 60)
    # a site that isn't in seats.json (added from "Add a site")
    r = call('/api/action', {'type': 'login.start', 'url': f'http://localhost:{SP}/?autologin=1'})
    ok, info = wait_for('localhost', 'working', 60)
    check('a site added from "Add a site": Working after its window closes', ok, info)
    call('/api/action', {'type': 'logins.check'})
    t = time.time()
    while status('localhost')[1] and time.time() - t < 60:
        time.sleep(0.5)
    check('a site added from "Add a site": Working after Check now', status('localhost')[0]['status'] == 'working', status('localhost'))
    # a login saved with no seats.json entry at all (by hand, or before seats): Check now still checks it
    os.makedirs(os.path.join(data, 'logins', 'example.invalid'), exist_ok=True)
    json.dump({'cookies': [], 'origins': []}, open(os.path.join(data, 'logins', 'example.invalid', 'owner.json'), 'w'))
    call('/api/action', {'type': 'logins.check'}); time.sleep(1)
    t = time.time()
    while status('example.invalid')[1] and time.time() - t < 90:
        time.sleep(0.5)
    check('a saved login outside seats.json is checked too', status('example.invalid')[0]['status'] != 'unchecked', status('example.invalid'))
finally:
    srv.terminate()
print('\n**PASS**' if all(res) else f'\n**FAIL**: {res.count(False)} failed')
sys.exit(0 if all(res) else 1)
