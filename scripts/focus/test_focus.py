"""Check that NAVI never takes over the Mac (reference/recording-rules.md rule 22).

Runs a real explore and a real recording (the saved to-do demo: no credits) with the focus watcher on, and passes
only if none of NAVI's browsers came to the front or showed a window. Keep using other apps while it runs.

With --login it also opens the visible login window on two local test pages (it comes to the front once, that's
expected), puts the app that was in front back after 5 s, and fails if the login window jumps in front again while
it keeps saving the session.

Usage: .venv/bin/python scripts/focus/test_focus.py [--login]
"""
import http.server
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'scripts', 'setup'))
import assets  # noqa: E402
assets.need_todo_takes()          # the saved to-do takes (not in the repo); exits 77, skipped, when missing
PY = os.path.join(ROOT, '.venv', 'bin', 'python')
WATCH = os.path.join(ROOT, '.venv', 'bin', 'navi-focuswatch')
rows, ok = [], True


def check(name, cond, detail=''):
    global ok
    ok &= bool(cond)
    rows.append(f"| {name} | {'pass' if cond else '**FAIL**'} | {detail} |")
    print(rows[-1], flush=True)


def build():
    src = os.path.join(HERE, 'focuswatch.swift')
    if not os.path.exists(WATCH) or os.path.getmtime(WATCH) < os.path.getmtime(src):
        subprocess.run(['swiftc', '-O', src, '-o', WATCH], check=True, capture_output=True)


def watched(cmd, seconds, give_back=None, **kw):
    """Run cmd with the watcher on; return (exit code, watcher events)."""
    args = [WATCH, str(seconds)] + (['--give-back-at', str(give_back)] if give_back else [])
    w = subprocess.Popen(args, stdout=subprocess.PIPE, text=True)
    time.sleep(0.5)
    if callable(cmd):
        code = cmd()
    else:
        r = subprocess.run(cmd, capture_output=True, text=True, **kw)
        code = r.returncode
        if code:
            print((r.stdout + r.stderr)[-1500:], flush=True)
    w.terminate()
    out = w.communicate()[0]
    return code, [json.loads(l) for l in out.splitlines() if l.strip()]


def navi(events):
    return [e for e in events if e.get('navi') or e['event'] == 'window']


def what(events):
    return '; '.join(f"{e['event']} {e.get('app') or e.get('owner')} ({e.get('path', '')}) at {e['t']} s" for e in navi(events))


def apps(events):
    return sorted({e['app'] for e in events if e['event'] == 'activate' and not e.get('navi')})


build()
tmp = tempfile.mkdtemp(prefix='navi-focus-')
try:
    steps = os.path.join(tmp, 'steps.json')
    json.dump([{'fill': ['What needs to be done?', 'Call the dentist']}, {'press': 'Enter'},
               {'click': {'css': '.todo-list li .toggle'}}, {'click': 'Completed'}], open(steps, 'w'))
    out = os.path.join(ROOT, 'output', 'focus-test-explore')
    code, ev = watched(['node', os.path.join(ROOT, 'scripts', 'explore', 'explore.mjs'), '--url', 'https://demo.playwright.dev/todomvc',
                        '--out', out, '--steps', steps], 120)
    check('explore stays in the background', code == 0 and not navi(ev),
          f"{len(navi(ev))} NAVI windows or activations {what(ev)}; meanwhile in front: {', '.join(apps(ev)) or 'no change'}")
    shutil.rmtree(out, ignore_errors=True)

    code, ev = watched([PY, os.path.join(ROOT, 'scripts', 'record', 'record.py'), os.path.join(ROOT, 'examples', 'test-todo-b.json'),
                        os.path.join(ROOT, 'output', 'test-todo-v4'), '--name', 'focus-test'], 1200)
    check('recording and polish stay in the background', code == 0 and not navi(ev),
          f"{len(navi(ev))} NAVI windows or activations {what(ev)}; meanwhile in front: {', '.join(apps(ev)) or 'no change'}")
    shutil.rmtree(os.path.join(ROOT, 'output', 'test-todo-v4', 'focus-test'), ignore_errors=True)

    if '--login' in sys.argv:
        pages = os.path.join(tmp, 'pages')
        os.makedirs(pages)
        open(os.path.join(pages, 'a.html'), 'w').write("<!doctype html><title>A</title><p>origin A</p><script>localStorage.setItem('a','1');"
                                                       "setTimeout(()=>location.href='http://localhost:'+location.port+'/b.html',1500)</script>")
        open(os.path.join(pages, 'b.html'), 'w').write("<!doctype html><title>B</title><p>origin B: close this window</p><script>localStorage.setItem('b','2')</script>")
        class Quiet(http.server.SimpleHTTPRequestHandler):
            def __init__(self, *a, **k):
                super().__init__(*a, directory=pages, **k)

            def log_message(self, *a):
                pass
        srv = http.server.ThreadingHTTPServer(('127.0.0.1', 0), Quiet)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        sess = os.path.join(tmp, 'session.json')

        def login():
            p = subprocess.Popen(['node', os.path.join(ROOT, 'recorder', 'agent-screenplay', 'dist', 'cli.js'), 'login',
                                  f'http://127.0.0.1:{srv.server_address[1]}/a.html', '--out', sess],
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(20)
            p.terminate()
            p.wait(10)
            return 0
        code, ev = watched(login, 25, give_back=5)
        gb = next((e['t'] for e in ev if e['event'] == 'give-back'), '999')
        jumps = [e for e in ev if e.get('navi') and e['event'] == 'activate' and float(e['t']) > float(gb)]
        saved = json.load(open(sess)) if os.path.exists(sess) else {'origins': []}
        check('login: in front once, never jumps back', not jumps and any(e.get('navi') for e in ev),
              f"{len(jumps)} jumps back in front after the user's app was put back at {gb} s")
        check('login: session still saved', len(saved['origins']) == 2, f"storage of {len(saved['origins'])} of 2 sites, cookies: {len(saved.get('cookies', []))}")
        srv.shutdown()
finally:
    shutil.rmtree(tmp, ignore_errors=True)

print('\n'.join(['', '| Check | Result | Detail |', '|---|---|---|'] + rows + ['', f"**{'PASS' if ok else 'FAIL'}**"]))
sys.exit(0 if ok else 1)
