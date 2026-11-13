"""Wait for the app: blocks until the user does something in the NAVI app, then prints what they did as JSON and
exits. This is how clicks in the app reach Claude (Phase 7).

  .venv/bin/python scripts/app/wait.py                 wait for the next action
  .venv/bin/python scripts/app/wait.py --after 12      everything after action 12 (no action is missed between waits)
  .venv/bin/python scripts/app/wait.py --timeout 600   give up after 10 minutes (exit code 2)

Prints {"actions": [...], "last": N}. Pass "last" as --after next time. Each action has its type, what the server
already did with it ("ok", "result"), and anything Claude still has to do (record, redo, export, run a batch).
The key is never in it.
"""
import argparse
import json
import os
import sys
import urllib.request

ap = argparse.ArgumentParser()
ap.add_argument('--after', type=int, default=None)
ap.add_argument('--timeout', type=float, default=3600)
ap.add_argument('--port', type=int, default=int(os.environ.get('NAVI_PORT', 4747)))
a = ap.parse_args()
base = f'http://127.0.0.1:{a.port}'
after = a.after
try:
    if after is None:   # start from now: only what the user does next
        after = json.load(urllib.request.urlopen(f'{base}/api/wait?after=999999999&timeout=0', timeout=10))['last']
    r = json.load(urllib.request.urlopen(f'{base}/api/wait?after={after}&timeout={a.timeout}', timeout=a.timeout + 30))
except OSError:
    sys.exit("The NAVI app isn't running. Start it with: .venv/bin/python scripts/app/server.py --open")
print(json.dumps(r, indent=1, ensure_ascii=False))
sys.exit(0 if r['actions'] else 2)
