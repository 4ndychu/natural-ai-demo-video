"""A started batch is its own background process (Andy, 12 Nov 2026: batches that survive).

  runner.py start <batch> [--go]   hand the batch to macOS and return at once. --go: the user's Go click.
  runner.py stop <batch>           pause it (it stays where it is; nothing is lost)
  runner.py resume <batch>         carry on from where it stopped
  runner.py status <batch>         is it alive, what is it doing, where is it ("video 7 of 30")
  runner.py run <batch>            the process itself (macOS starts this; not for hand use)

- **It outlives the session.** `start` installs a per-batch job with macOS's own launcher (a LaunchAgent,
  ~/Library/LaunchAgents/com.navi.batch.<id>.plist). The batch then belongs to macOS, not to T3 Code, Claude Code or a
  terminal: closing them, or a session timing out, doesn't touch it.
- **It keeps the Mac awake itself**, with macOS's own `caffeinate` tied to the runner, for as long as it is working
  (writing, voicing, recording). While it only waits for the user (a plan or A/B/C pick, the Go click) it lets the
  Mac sleep. On battery with the lid shut a Mac sleeps whatever anyone asks: leave it on power.
- **It resumes.** The job is marked "run when I log in" and "start again if it dies", so after a restart, a crash or
  a power cut it starts again at the next login and carries on: written scripts, voiced takes and recorded videos are
  all kept; the video that was mid-recording is recorded again. When the batch is finished (or paused) the job
  removes itself.

What it does, in order, each step picking up where it stopped: write every script (`batch.write`; stopping for the plan
pick when the blind test is on), the list of scripts (`sheet`), Go (straight away with --go or the "start without the
Go click" setting, otherwise it waits on the Go screen), then record (`batch.run`), waiting for A/B/C picks and
recording each as it is picked. One runner per batch (a lock); a second start is a no-op.

NAVI_NO_LAUNCHD=1: a plain detached process instead of a LaunchAgent (other systems; no resume after a restart).
"""
import argparse
import fcntl
import json
import os
import plistlib
import signal
import subprocess
import sys
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
PY = os.path.join(ROOT, '.venv', 'bin', 'python')
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, 'scripts', 'app'))
import store  # noqa: E402

POLL = float(os.environ.get('NAVI_RUNNER_POLL', '5'))
BEAT = 5
ALIVE_S = 30


def label(bid):
    return f'com.navi.batch.{bid}'


def plist_path(bid):
    return os.path.expanduser(f'~/Library/LaunchAgents/{label(bid)}.plist')


def bfile(bid, name):
    import batch
    return os.path.join(batch.bdir(bid), name)


def use_launchd():
    return sys.platform == 'darwin' and not os.environ.get('NAVI_NO_LAUNCHD')


def _pid_alive(pid):
    try:
        os.kill(int(pid), 0)
        return True
    except (OSError, TypeError, ValueError):
        return False


def status(bid):
    """{alive, pid, phase, doing, waiting_for, awake, paused, installed, position: {done, total, at}}."""
    import batch
    b = batch.load(bid)
    r = store._read(bfile(bid, 'runner.json'), {}) or {}
    alive = bool(r.get('pid')) and _pid_alive(r['pid']) and time.time() - r.get('beat', 0) < ALIVE_S
    done = sum(1 for d in b['items'] if store.demo(d)['recorded'] or (b.get('results', {}).get(d, {}).get('status') == 'skipped'))
    total = len(b['items'])
    stopped = not alive and b['state'] in ('running', 'paused', 'writing') and bool(r) and r.get('phase') != 'done'
    return {'alive': alive, 'pid': r.get('pid') if alive else None, 'phase': r.get('phase'), 'doing': r.get('doing') if alive else None,
            'waiting_for': r.get('waiting_for') if alive else None, 'awake': bool(r.get('awake')) and alive,
            'paused': b['state'] == 'paused' or stopped, 'installed': os.path.exists(plist_path(bid)),
            'position': {'done': done, 'total': total, 'at': min(done + 1, total)},
            'line': (f"paused at video {min(done + 1, total)} of {total}" if (b['state'] == 'paused' or stopped) and r.get('phase') == 'recording'
                     else 'paused' if b['state'] == 'paused' or stopped else None)}


def start(bid, go=False):
    """Hand the batch to macOS. Returns straight away."""
    import batch
    b = batch.load(bid)
    if go:      # its own small file: the runner may be holding the batch file
        open(bfile(bid, 'go.clicked'), 'w').write(str(time.time()))
    st = status(bid)
    if st['alive']:
        return {'started': False, 'already': True, **st}
    if b['state'] == 'paused':
        b['state'], b['reason'] = b.get('state_before_pause') or 'running', None
        batch.save(b)
    env = {k: v for k, v in os.environ.items() if k.startswith('NAVI_') or k in ('PATH', 'HOME', 'LANG', 'TMPDIR', 'USER')}
    log = bfile(bid, 'runner.log')
    if not use_launchd():
        subprocess.Popen([PY, os.path.abspath(__file__), 'run', bid], stdout=open(log, 'a'), stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
                         start_new_session=True, env=env, cwd=ROOT)
        return {'started': True, 'how': 'detached process (no resume after a restart)'}
    pl = {'Label': label(bid), 'ProgramArguments': [PY, os.path.abspath(__file__), 'run', bid], 'WorkingDirectory': ROOT,
          'EnvironmentVariables': env, 'RunAtLoad': True, 'KeepAlive': {'SuccessfulExit': False}, 'ThrottleInterval': 15,
          'ProcessType': 'Interactive', 'StandardOutPath': log, 'StandardErrorPath': log}
    os.makedirs(os.path.dirname(plist_path(bid)), exist_ok=True)
    dom = f'gui/{os.getuid()}'
    subprocess.run(['launchctl', 'bootout', f'{dom}/{label(bid)}'], capture_output=True)
    with open(plist_path(bid), 'wb') as f:
        plistlib.dump(pl, f)
    r = subprocess.run(['launchctl', 'bootstrap', dom, plist_path(bid)], capture_output=True, text=True)
    if r.returncode != 0:
        os.remove(plist_path(bid))
        raise ValueError('macOS did not take the batch job: ' + (r.stderr or r.stdout).strip()[:200])
    return {'started': True, 'how': 'macOS background job (survives closing the app; resumes after a restart)'}


def stop(bid):
    """Pause: the job is taken off macOS's list and the runner stopped. Everything made so far is kept."""
    import batch
    b = batch.load(bid)
    r = store._read(bfile(bid, 'runner.json'), {}) or {}
    if os.path.exists(plist_path(bid)):
        os.remove(plist_path(bid))
    subprocess.run(['launchctl', 'bootout', f'gui/{os.getuid()}/{label(bid)}'], capture_output=True)
    pid = int(r['pid']) if r.get('pid') else None
    try:
        pg = os.getpgid(pid) if pid else None
    except OSError:
        pg = None
    for sig in (signal.SIGTERM, signal.SIGKILL):     # the runner and everything it started (voice, browser, renderer)
        if pg and pg != os.getpgid(0):
            try:
                os.killpg(pg, sig)
            except OSError:
                break
            end = time.time() + 6
            while time.time() < end and _pid_alive(pid):
                try:
                    os.waitpid(pid, os.WNOHANG)      # ours to clear when this process started it (no launchd)
                except OSError:
                    pass
                time.sleep(0.3)
    if r:      # it is stopped now, whatever the process table still lists (a finished child isn't cleared at once)
        store._write(bfile(bid, 'runner.json'), dict(r, pid=None, awake=False, doing=None, waiting_for=None))
    b = batch.load(bid)
    if b['state'] != 'paused':
        b['state_before_pause'] = b['state']
    b['state'], b['reason'] = 'paused', 'paused by you'
    batch.log(b, 'Paused. Everything made so far is kept; resume carries on from here.')
    batch.save(b)
    return status(bid)


# ---- the process itself ----------------------------------------------------------------------------------------------
class Runner:
    def __init__(self, bid):
        self.bid, self.state, self.caf = bid, {'pid': os.getpid(), 'started': time.time(), 'phase': None, 'awake': False}, None
        self.lock = open(bfile(bid, 'runner.lock'), 'w')

    def beat(self, **kw):
        self.state.update(kw, beat=time.time())
        store._write(bfile(self.bid, 'runner.json'), self.state)

    def _beats(self):
        while True:
            time.sleep(BEAT)
            self.beat()

    def awake(self, on):
        """Keep the Mac awake while there is work (macOS's own caffeinate, tied to this process); let it sleep while
        only the user is being waited for."""
        if on and not self.caf and sys.platform == 'darwin':
            self.caf = subprocess.Popen(['/usr/bin/caffeinate', '-i', '-m', '-s', '-w', str(os.getpid())])
        elif not on and self.caf:
            self.caf.terminate()
            self.caf = None
        self.beat(awake=bool(self.caf))

    def wait_user(self, what, until):
        import batch
        self.awake(False)
        self.beat(waiting_for=what, doing=None)
        print(f'[runner] waiting for you: {what}', flush=True)
        while not until(batch.load(self.bid)):
            time.sleep(POLL)
        self.beat(waiting_for=None)

    def work(self, phase, doing):
        self.awake(True)
        self.beat(phase=phase, doing=doing, waiting_for=None)
        print(f'[runner] {doing}', flush=True)

    def crash_guard(self):
        """Started again and again without getting anywhere: stop, and say so, rather than loop all night."""
        import batch
        old = store._read(bfile(self.bid, 'runner.json'), {}) or {}
        starts = [t for t in old.get('starts', []) if time.time() - t < 900] + [time.time()]
        self.state['starts'] = starts
        self.state['phase'] = old.get('phase')
        if len(starts) > 6:
            b = batch.load(self.bid)
            b['state'], b['reason'] = 'needs you', 'the batch kept stopping (see runner.log); it was paused instead of trying all night'
            batch.log(b, 'Stopped: ' + b['reason'])
            batch.save(b)
            return False
        return True

    def run(self):
        import batch
        import blind
        bid = self.bid
        try:
            fcntl.flock(self.lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            print('[runner] this batch already has a runner', flush=True)
            return 0
        if not self.crash_guard():
            return self.finish()
        self.beat()
        threading.Thread(target=self._beats, daemon=True).start()
        b = batch.load(bid)
        if self.state.get('phase') in ('writing', 'go', 'recording'):
            batch.log(b, f"Carrying on from where it stopped ({self.state['phase']}).")
            batch.save(b)
        # 1. every script
        # a video counts as written once it has been through the checks and the rehearsals (it has a "written" entry),
        # not just because a script file exists (14 Nov 2026: hand-fixed scripts went straight to Go)
        while any(d not in b.get('written', {}) for d in b['items']):
            if (b.get('blind') or {}).get('plan', {}).get('status') == 'waiting':
                self.wait_user('your pick of a plan (A, B or C)', lambda x: (x.get('blind') or {}).get('plan', {}).get('status') != 'waiting')
            self.work('writing', 'writing the scripts')
            batch.write(bid)
            b = batch.load(bid)
            if (b.get('blind') or {}).get('plan', {}).get('status') != 'waiting' and all(d in b.get('written', {}) for d in b['items']):
                break
        # 2. the list of scripts, and Go
        b = batch.load(bid)
        if not b.get('started'):
            self.work('go', 'getting ready for Go')
            batch.sheet(bid)
            while True:
                b = batch.load(bid)
                clicked = lambda x=None: os.path.exists(bfile(bid, 'go.clicked'))
                if not (clicked() or store.settings()['auto_go']):
                    b['state'], b['reason'] = 'ready', 'waiting for Go'
                    batch.save(b)
                    self.wait_user('Go', clicked)
                self.work('go', 'checking logins, pages and credits')
                r = batch.go(bid)
                if r['started']:
                    break
                if clicked():
                    os.remove(bfile(bid, 'go.clicked'))
                self.wait_user('Go again, once this is sorted: ' + r['reason'], clicked)
        # 3. record, and every A/B/C pick as it comes
        while True:
            self.work('recording', 'voice, timing and recording')
            batch.run(bid)
            b = batch.load(bid)
            n = len(blind.waiting(b))
            if not n:
                break
            self.wait_user(f"your A/B/C pick for {n} video{'s' if n != 1 else ''}", lambda x: blind.apply_requests(batch, bid) or len(blind.waiting(x)) < n)
        self.beat(phase='done', doing=None)
        return self.finish()

    def finish(self):
        """Done (or given up): take the job off macOS's list so it doesn't start again at the next login."""
        self.awake(False)
        if os.path.exists(plist_path(self.bid)):
            os.remove(plist_path(self.bid))
            subprocess.Popen(['/bin/sh', '-c', f'sleep 2; launchctl bootout gui/{os.getuid()}/{label(self.bid)}'], start_new_session=True,
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print('[runner] finished', flush=True)
        return 0


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)
    for c in ('start', 'stop', 'resume', 'status', 'run'):
        p = sub.add_parser(c)
        p.add_argument('batch')
        if c == 'start':
            p.add_argument('--go', action='store_true', help="the user's Go click: start recording once the scripts are ready and the preflight passes")
    a = ap.parse_args()
    try:
        if a.cmd == 'run':
            sys.exit(Runner(a.batch).run())
        elif a.cmd in ('start', 'resume'):
            print(json.dumps(start(a.batch, getattr(a, 'go', False))))
        elif a.cmd == 'stop':
            print(json.dumps(stop(a.batch)))
        else:
            print(json.dumps(status(a.batch), indent=1))
    except ValueError as e:
        sys.exit(str(e))


if __name__ == '__main__':
    main()
