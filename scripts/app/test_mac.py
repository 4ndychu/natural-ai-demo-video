"""NAVI busy-Mac check (store.mac_load), on a made-up Mac: a fake process list and a fake clock, so it runs the same
anywhere. Runs on a temporary $NAVI_DATA; touches nothing of the user's.

Checks (Andy, 14 Nov 2026): Google Chrome and Wispr Flow are never named and can be edited in Settings (keep_apps);
NAVI's own processes (Chrome for Testing, the renderer, ffmpeg, the app and what it starts) are not load; the number is
a 30-second average, so the line doesn't change with every refresh; only apps really using a lot are named.

  .venv/bin/python scripts/app/test_mac.py     (exit 1 on any failure)
"""
import os
import random
import sys
import tempfile
import types

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.environ['NAVI_DATA'] = tempfile.mkdtemp(prefix='navi-mac-')
import store  # noqa: E402

FAILS = []


def check(label, ok, extra=''):
    print(('ok    ' if ok else 'FAIL  ') + label + (f'  ({extra})' if extra else ''))
    if not ok:
        FAILS.append(label)


R = store.ROOT
APP = '/Applications'
# pid: (ppid, command, % of a core it uses)
MAC = {
    100: (1, '.venv/bin/python scripts/app/server.py --port 4747', 5),               # the app, started with a relative path
    101: (100, f'{R}/.venv/bin/ffmpeg -i take.mp4 out.mp4', 300),                      # its ffmpeg
    102: (1, '/Users/a/Library/Caches/ms-playwright/chromium-1248/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing', 150),
    103: (1, f'node {R}/recorder/polish/render.mjs --style casual', 100),              # the renderer
    104: (100, 'claude -p --model claude-sonnet-5-5', 40),                            # a job the app started
    200: (1, f'{APP}/Google Chrome.app/Contents/MacOS/Google Chrome', 120),
    201: (200, f'{APP}/Google Chrome.app/Contents/Frameworks/Google Chrome Framework.framework/Helpers/Google Chrome Helper (Renderer).app/Contents/MacOS/Google Chrome Helper (Renderer) --type=renderer', 90),
    202: (1, f'{APP}/Wispr Flow.app/Contents/MacOS/Wispr Flow', 60),
    300: (1, f'{APP}/Roblox.app/Contents/MacOS/RobloxPlayer', 180),
    301: (1, f'{APP}/Spotify.app/Contents/Frameworks/Spotify Helper (Renderer).app/Contents/MacOS/Spotify Helper (Renderer) --type=renderer', 70),
    302: (1, f'{APP}/Slack.app/Contents/MacOS/Slack', 20),
    303: (1, f'{APP}/T3 Code (Beta).app/Contents/MacOS/T3 Code (Beta)', 60),
    400: (1, '/usr/sbin/coreaudiod', 10),
    401: (1, '/System/Library/PrivateFrameworks/FileProvider.framework/Support/fileproviderd', 5),
}


class FakeMac:
    def __init__(self):
        self.t, self.used, self.rate = 1_000_000.0, {}, {pid: p[2] for pid, p in MAC.items()}
        self.jitter = 0.0

    def advance(self, secs):
        for pid, r in self.rate.items():
            r = max(r * (1 + random.uniform(-self.jitter, self.jitter)), 0)
            self.used[pid] = self.used.get(pid, 0.0) + r / 100 * secs
        self.t += secs

    def processes(self):
        return {pid: (MAC[pid][0], self.used.get(pid, 0.0), MAC[pid][1]) for pid in self.rate}


mac = FakeMac()
store._processes = mac.processes
store.time = types.SimpleNamespace(time=lambda: mac.t, sleep=mac.advance)
os.getloadavg = lambda: (9.9, 9.9, 9.9)


def watch(secs, every=5):
    """The app's background reading every few seconds, for `secs`."""
    for _ in range(int(secs / every)):
        mac.advance(every)
        store.mac_sample()


m = store.mac_load()
check('the very first look takes a short reading of its own', m['seconds'] >= 2, m['seconds'])
watch(40)
m = store.mac_load()
names = [h['app'] for h in m['heavy']]
check('averaged over about 30 seconds', 28 <= m['seconds'] <= 36, m['seconds'])
check("NAVI's own processes are not load (app, ffmpeg, Chrome for Testing, renderer, its jobs)", abs(m['navi'] - 5.95) < 0.15, m['navi'])
check('other apps: Roblox, Spotify, Slack, T3 Code, coreaudiod = 3.4 cores', abs(m['others'] - 3.4) < 0.1, m['others'])
check('busy at 3.4 cores (quiet under 2)', m['busy'], m['line'])
check('names Roblox and Spotify, biggest first', names == ['Roblox', 'Spotify'], names)
check('never names Google Chrome or Wispr Flow', 'Google Chrome' not in m['line'] and 'Wispr' not in m['line'], m['line'])
check('never names Slack (20%), T3 Code or a system process', not {'Slack', 'T3 Code (Beta)', 'coreaudiod'} & set(names), names)
check('kept apps are reported, not counted', {k['app'] for k in m['kept']} == {'Google Chrome', 'Wispr Flow'}, m['kept'])
check('the line says what to quit', m['line'].endswith('Quit Roblox and Spotify before Go.'), m['line'])
check('iCloud syncing at 5% is not mentioned', not m['icloud_syncing'])

# the same Mac, measured at every refresh with ±25% noise each second: the line stays the same
mac.jitter = 0.25
lines = set()
for _ in range(12):
    for _ in range(5):
        mac.advance(1)
    store.mac_sample()
    lines.add(store.mac_load()['line'])
check('the line stays the same across a minute of refreshes', len(lines) == 1, lines)
mac.jitter = 0.0

# a moment's spike that a one-moment check would have named (Slack at 300% for 2 s) changes nothing
mac.rate[302] = 300
mac.advance(2)
store.mac_sample()
mac.rate[302] = 20
watch(5)
m = store.mac_load()
check('a 2-second spike to 300% does not name an app', [h['app'] for h in m['heavy']] == ['Roblox', 'Spotify'], m['heavy'])

# Settings: Google Chrome taken off the keep list is counted and named; an app added is never named
store.set_settings({'keep_apps': ['Wispr Flow', 'roblox']})
watch(35)
m = store.mac_load()
check('Chrome off the keep list: named (210% of a core)', [h['app'] for h in m['heavy']] == ['Google Chrome', 'Spotify'], m['heavy'])
check('"roblox" added (any case, part of the name): never named, not counted', 'Roblox' not in m['line'] and abs(m['others'] - 3.7) < 0.1, m)
store.set_settings({'keep_apps': ['Google Chrome', 'Wispr Flow']})
for bad in ('Google Chrome', [''], [3], ['x' * 81]):
    try:
        store.set_settings({'keep_apps': bad})
        check(f'keep_apps refuses {bad!r}', False)
    except ValueError:
        check(f'keep_apps refuses {str(bad)[:20]!r}', True)

# quiet again once Roblox goes; near the line it doesn't flicker
mac.rate[300] = 0
watch(35)
m = store.mac_load()
check('without Roblox (1.6 cores) it stays busy: a quarter under the line is needed', m['busy'] and abs(m['others'] - 1.6) < 0.1, m['others'])
mac.rate[301] = 20
watch(35)
m = store.mac_load()
check('at 1.1 cores it is quiet', not m['busy'], m['line'])
check('quiet and nothing heavy: a short, steady line', m['line'] == 'Your Mac is quiet.', m['line'])
mac.rate[303] = 180
watch(35)
m = store.mac_load()
check('just over the line (2.3 cores) it turns busy, naming nothing it may not', m['busy'] and m['heavy'] == [], m['line'])
check('with nothing to name, it asks nothing', 'Quit' not in m['line'] and 'Close' not in m['line'], m['line'])

print(f'\n{len(FAILS)} FAILED' if FAILS else '\nall busy-Mac checks passed')
sys.exit(1 if FAILS else 0)
