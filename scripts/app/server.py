"""NAVI's local app server (Phase 7). Serves the app in ui/ and its engine API on this Mac only.

  http://127.0.0.1:4747/             the app (ui/, served as it is)
  GET  /api/state                    everything the app shows: settings, key status (never the key), logins, demos,
                                     batches (store.state())
  GET  /api/demo/<id>                one demo
  GET  /media/<id>/<file>            a demo's recording, for Review's player (mp4/png/jpg only, inside that demo's folder)
  GET  /api/live/<id>                Watch live: the newest frame of that demo's recording in progress (204 when none)
  POST /api/action                   something the user did: {"type": ..., ...}. Simple changes are applied here
                                     (settings, marks, blur decisions, approvals, forgetting a login); every action
                                     is also queued for Claude.
  GET  /api/wait?after=N&timeout=S   blocks until the user does something (scripts/app/wait.py)
  POST /api/progress                 the engine reports progress ({"demo": id, "text": "Recording 4 of 9"})

Safety: listens on 127.0.0.1 only; refuses other Host names (DNS rebinding) and POSTs from other web pages (Origin
must be this server); destructive actions ("Your data", removing the key) take two steps, look then confirm with a
token. The key is accepted only by POST from the app, piped to the Keychain, and never written to the log or queue.

Usage: .venv/bin/python scripts/app/server.py [--port 4747] [--open]
"""
import argparse
import json
import mimetypes
import os
import re
import subprocess
import sys
import threading
import time
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
UI = os.path.join(ROOT, 'ui')
sys.path.insert(0, HERE)
import store  # noqa: E402

LOCK = threading.Condition()
QUEUE = []          # [{'seq', 't', 'type', ...}] what the user did, for Claude
SECRET_FIELDS = {'key'}


def queue(action):
    with LOCK:
        a = {k: v for k, v in action.items() if k not in SECRET_FIELDS}
        a.update(seq=len(QUEUE) + 1, t=time.time())
        QUEUE.append(a)
        LOCK.notify_all()
        return a['seq']


def apply(a):
    """Apply what can be applied straight away. Returns a result for the app (and for Claude)."""
    t = a.get('type')
    if t == 'settings.set':
        return {'settings': store.set_settings(a['patch'])}
    if t == 'demo.new':
        for k, v in (a.get('settings') or {}).items():
            store.check_setting(k, v)
        extra = {'settings': a['settings']} if a.get('settings') else {}
        if a.get('voice'):
            store.check_setting('voice', a['voice'])
        d = store.new_demo(**{k: a[k] for k in ('title', 'site', 'kind', 'length_min', 'audience', 'what') if k in a}, **extra)
        if a.get('voice'):
            d = store.update_demo(d['id'], {'voice': a['voice']})
        return {'demo': d}
    if t == 'demo.update':                     # the app's own edits: voice, kind, brief fields, settings, hidden (delete with Undo)
        bad = set(a['patch']) - store.APP_EDITABLE
        if bad:
            raise ValueError(f'Not editable from the app: {sorted(bad)}')
        patch = dict(a['patch'])
        if 'settings' in patch:
            cur = store._read(os.path.join(store.demo_dir(a['demo']), 'demo.json'), {}).get('settings', {})
            patch['settings'] = {**cur, **patch['settings']}
        if 'voice' in patch:
            store.check_setting('voice', patch['voice'])
        return {'demo': store.update_demo(a['demo'], patch)}
    if t == 'demo.mark':                       # Review: a mark at a time ("Sounds like AI", "Needs a blur", a note)
        d = store.demo(a['demo'])
        marks = d['marks'] + [{'t': float(a['t']), 'section': a.get('section'), 'text': str(a['text'])[:300]}]
        return {'demo': store.update_demo(a['demo'], {'marks': marks})}
    if t == 'demo.unmark':
        d = store.demo(a['demo'])
        return {'demo': store.update_demo(a['demo'], {'marks': [m for i, m in enumerate(d['marks']) if i != int(a['index'])]})}
    if t == 'demo.blur':                       # Review: keep blurred / show it / undo
        if a['s'] not in ('keep', 'show', ''):
            raise ValueError('s must be keep, show or empty.')
        d = store.demo(a['demo'])
        return {'demo': store.update_demo(a['demo'], {'blur_decisions': {**d['blur_decisions'], a['id']: a['s']}})}
    if t == 'demo.approve_script':
        d = store.demo(a['demo'])
        if not d['written']:
            raise ValueError('The script has problems to fix first.')
        return {'demo': store.update_demo(a['demo'], {'script_approved': True})}
    if t == 'demo.approve_review':
        d = store.demo(a['demo'])
        unsure = d['unsure_blurs']
        if unsure and not a.get('anyway'):
            raise ValueError(f'{unsure} unsure blur{"s" if unsure != 1 else ""} not sorted yet.')
        return {'demo': store.update_demo(a['demo'], {'review': 'approved'})}
    if t == 'demo.settings':                   # per-demo captions, corner label, style...
        d = store.demo(a['demo'])
        cur = store._read(os.path.join(store.demo_dir(a['demo']), 'demo.json'), {}).get('settings', {})
        return {'demo': store.update_demo(a['demo'], {'settings': {**cur, **a['patch']}})}
    if t == 'batch.hide':                      # All demos: delete a batch with Undo (its videos and files stay)
        import importlib
        batch = importlib.import_module('batch')
        path = os.path.join(batch.bdir(a['batch']), 'batch.json')
        b = store._read(path, None)
        if b is None:
            raise ValueError('No such batch.')
        b['hidden'] = bool(a.get('hidden', True))
        store._write(path, b)
        return {'batch': {k: b[k] for k in ('id', 'name', 'state')}}
    if t == 'batch.go':                        # the Go click: preflight, then the whole batch, in the background, never asking
        import importlib
        batch = importlib.import_module('batch')
        b = store._read(os.path.join(batch.bdir(a['batch']), 'batch.json'), None)
        if b is None:
            raise ValueError('No such batch.')
        runner = importlib.import_module('runner')
        if b['state'] == 'running' and runner.status(a['batch'])['alive']:
            raise ValueError('That batch is already running.')
        # the batch becomes its own background job, owned by macOS: it outlives this app and the session, keeps the
        # Mac awake while it works, and carries on after a restart (scripts/batch/runner.py)
        runner.start(a['batch'], go=True)
        return {'batch': {'id': b['id'], 'name': b['name'], 'state': 'starting'}}
    if t in ('batch.pause', 'batch.resume'):   # "paused at video 7 of 30, resume?"
        import importlib
        runner = importlib.import_module('runner')
        st = runner.stop(a['batch']) if t == 'batch.pause' else (runner.start(a['batch']) and runner.status(a['batch']))
        return {'runner': st}
    if t in ('blind.pick', 'blind.pick_plan'):   # a blind A/B/C pick; the batch then carries on by itself, in the background
        import importlib
        batch, blind = importlib.import_module('batch'), importlib.import_module('blind')
        if t == 'blind.pick_plan':
            res = blind.pick_plan(batch, a['batch'], a.get('letter'))
        else:
            res = blind.pick(batch, a['batch'], a['demo'], a.get('letter'))
        b = batch.load(a['batch'])
        importlib.import_module('runner').start(a['batch'])     # the batch's own runner carries on (a no-op if it is alive)
        return {'batch': {'id': b['id'], 'name': b['name'], 'state': b['state']}, **res}
    if t == 'batch.approve_all':
        import importlib
        batch = importlib.import_module('batch')
        return {'batch': batch.approve(a['batch'])}
    if t == 'login.start':
        return store.start_login(a['url'], a.get('seat'))
    if t == 'logins.check':
        return store.check_logins(a.get('site'), a.get('seat'))
    if t == 'login.forget':
        return {'forgot': store.forget_login(a['site'], a.get('seat')), 'logins': store.logins()}
    if t == 'key.store':
        return {'key': store.store_key(a['key'])}
    if t == 'key.test':                        # Welcome and Settings: check with ElevenLabs, save to the Keychain only if it works
        return store.test_and_store_key(a['key'])
    if t == 'app.open_folder':                 # Finder on the export folder (only a folder that exists in the user's home)
        folder = os.path.abspath(os.path.expanduser(a.get('folder') or store.settings()['export_to']))
        home = os.path.expanduser('~')
        if not (folder.startswith(home + os.sep) and os.path.isdir(folder)):
            raise ValueError("That folder doesn't exist yet.")
        import subprocess
        subprocess.Popen(['open', folder])
        return {'opened': folder}
    if t == 'data.plan_delete':
        return store.plan_delete(a['what'])
    if t == 'data.confirm_delete':
        return store.confirm_delete(a['token'])
    if t in FOR_CLAUDE:
        return {}                              # Claude does these (they take time or credits): redo, export, run a batch...
    raise ValueError(f'Unknown action "{t}".')


FOR_CLAUDE = {'demo.redo', 'demo.export', 'demo.record', 'demo.voice', 'batch.new', 'batch.run', 'batch.export', 'batch.review',
              'app.message', 'demo.line', 'demo.brief', 'demo.sample', 'demo.pause', 'demo.resume', 'demo.stop'}


class H(BaseHTTPRequestHandler):
    server_version = 'NAVI'

    def log_message(self, fmt, *args):         # quiet, and never logs bodies (the key arrives in one)
        pass

    def _send(self, code, body, ctype='application/json'):
        data = body if isinstance(body, bytes) else json.dumps(body, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header('Content-Type', ctype)
        self.send_header('Content-Length', str(len(data)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.end_headers()
        self.wfile.write(data)

    def _host_ok(self):
        host = (self.headers.get('Host') or '').split(':')[0]
        return host in ('127.0.0.1', 'localhost')

    def _origin_ok(self):
        o = self.headers.get('Origin')
        port = self.server.server_address[1]
        return o in (f'http://127.0.0.1:{port}', f'http://localhost:{port}')

    def do_GET(self):
        if not self._host_ok():
            return self._send(403, {'error': 'NAVI only answers on this Mac.'})
        u = urllib.parse.urlparse(self.path)
        q = urllib.parse.parse_qs(u.query)
        try:
            if u.path == '/api/state':
                return self._send(200, store.state())
            if u.path.startswith('/api/demo/'):
                return self._send(200, store.demo(u.path.split('/')[-1]))
            if u.path.startswith('/media/'):
                return self._media(urllib.parse.unquote(u.path[len('/media/'):]))
            if u.path.startswith('/api/live/'):              # Watch live: the newest frame of a recording in progress
                f = store.live_frame(u.path.split('/')[-1])
                if not f:
                    return self._send(204, b'', 'text/plain')
                return self._send(200, open(f, 'rb').read(), 'image/jpeg')
            if u.path == '/api/wait':
                after, timeout = int(q.get('after', ['0'])[0]), float(q.get('timeout', ['3600'])[0])
                end = time.time() + timeout
                with LOCK:
                    while len(QUEUE) <= after and time.time() < end:
                        LOCK.wait(min(5, end - time.time()))
                    return self._send(200, {'actions': QUEUE[after:], 'last': len(QUEUE)})
        except ValueError as e:
            return self._send(400, {'error': str(e)})
        # the app's files, read only
        rel = urllib.parse.unquote(u.path).lstrip('/') or 'index.html'
        p = os.path.realpath(os.path.join(UI, rel))
        if not p.startswith(os.path.realpath(UI) + os.sep) or not os.path.isfile(p):
            return self._send(404, {'error': 'Not found.'})
        return self._send(200, open(p, 'rb').read(), mimetypes.guess_type(p)[0] or 'application/octet-stream')

    def _media(self, rel):
        """A demo's video or picture, read only, with byte ranges so the player can seek."""
        did, _, rest = rel.partition('/')
        folder = os.path.realpath(store.demo_dir(did))
        p = os.path.realpath(os.path.join(folder, rest))
        if not p.startswith(folder + os.sep) or not os.path.isfile(p) or not (os.path.splitext(p)[1].lower() in ('.mp4', '.png', '.jpg')
                                                                                    or re.fullmatch(r'blind/[A-E]\.mp3', rest)):   # a blind test's versions, by letter
            return self._send(404, {'error': 'Not found.'})
        size = os.path.getsize(p)
        ctype = mimetypes.guess_type(p)[0] or 'application/octet-stream'
        rng = self.headers.get('Range')
        start, end = 0, size - 1
        if rng and rng.startswith('bytes='):
            a, _, b = rng[6:].split(',')[0].partition('-')
            start = int(a) if a else max(0, size - int(b))
            end = min(size - 1, int(b)) if a and b else end
        length = end - start + 1
        self.send_response(206 if rng else 200)
        self.send_header('Content-Type', ctype)
        self.send_header('Accept-Ranges', 'bytes')
        self.send_header('Content-Length', str(length))
        if rng:
            self.send_header('Content-Range', f'bytes {start}-{end}/{size}')
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        with open(p, 'rb') as fh:
            fh.seek(start)
            left = length
            try:
                while left > 0:
                    chunk = fh.read(min(1 << 16, left))
                    if not chunk:
                        break
                    self.wfile.write(chunk)
                    left -= len(chunk)
            except (BrokenPipeError, ConnectionResetError):
                pass

    def do_POST(self):
        if not self._host_ok() or not self._origin_ok():
            return self._send(403, {'error': 'Only the NAVI app on this Mac can do that.'})
        if 'application/json' not in (self.headers.get('Content-Type') or ''):
            return self._send(415, {'error': 'Send JSON.'})
        try:
            body = json.loads(self.rfile.read(int(self.headers.get('Content-Length') or 0)) or b'{}')
        except ValueError:
            return self._send(400, {'error': 'Bad JSON.'})
        u = urllib.parse.urlparse(self.path).path
        if u == '/api/progress':
            try:
                store.update_demo(body['demo'], {'progress': body.get('text')})
            except (KeyError, ValueError) as e:
                return self._send(400, {'error': str(e)})
            return self._send(200, {'ok': True})
        if u != '/api/action' or not body.get('type'):
            return self._send(404, {'error': 'Not found.'})
        try:
            result = apply(body)
            ok = True
        except (KeyError, ValueError, TypeError) as e:
            result, ok = {'error': str(e) if not isinstance(e, KeyError) else f'Missing {e}.'}, False
        seq = queue({**body, 'ok': ok, 'result': _brief(result)})
        return self._send(200 if ok else 400, {'seq': seq, **result})


def _brief(r):
    """What Claude sees of a result: no whole state dumps, and never the key."""
    if not isinstance(r, dict):
        return r
    out = {}
    for k, v in r.items():
        if k == 'demo' and isinstance(v, dict):
            out[k] = {x: v.get(x) for x in ('id', 'title', 'status', 'step_name')}
        elif k in ('settings', 'logins', 'items', 'deleted', 'error', 'forgot', 'site', 'token', 'key', 'batch', 'result', 'opened'):
            out[k] = v
    return out


def serve(port=4747, open_browser=False):
    sys.path.insert(0, os.path.join(ROOT, 'scripts', 'batch'))
    httpd = ThreadingHTTPServer(('127.0.0.1', port), H)
    url = f'http://127.0.0.1:{httpd.server_address[1]}/'
    print(f'NAVI is running at {url} (this Mac only). Stop it with Ctrl+C.', flush=True)
    if open_browser:
        import webbrowser
        webbrowser.open(url)
    httpd.serve_forever()


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--port', type=int, default=int(os.environ.get('NAVI_PORT', 4747)))
    ap.add_argument('--open', action='store_true')
    a = ap.parse_args()
    serve(a.port, a.open)
