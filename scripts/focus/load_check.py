"""Does a recording come out the same when something else is going on? (Andy, 12 Nov 2026: record in parallel, and draw
one video while the next records, only if the output stays identical.)

The approved to-do clip is recorded live several times, from the same voice:

  alone         twice: the second against the first is the Mac's own run-to-run noise today
  with-render   while Recordly's renderer is drawing another video
  with-timing   while the word-timing model is working through another video's voice
  two           two recordings at the same time
  three         three recordings at the same time

Every take is then finished the normal way and compared with the first "alone" take by scripts/focus/compare_takes.py
(page frames a second, frame gaps, repeated frames, how fast the page answers, cursor travel, scheduler lateness,
each action against its word, cursor shapes, join checks), with that script's own noise allowances. A way of working
is only switched on in config/defaults.json (app.batch) when every take made that way is no worse on any measure.

Usage: .venv/bin/python scripts/focus/load_check.py [alone with-render with-timing two three]
Writes output/load-check/summary.md. About 40 minutes for all of it; no credits.
"""
import json
import os
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
PY = os.path.join(ROOT, '.venv', 'bin', 'python')
SRC = os.path.join(ROOT, 'output', 'test-todo-v4')
SCRIPT = os.path.join(ROOT, 'examples', 'test-todo-b.json')
WORK = os.path.join(ROOT, 'output', 'load-check')
REC = os.path.join(ROOT, 'scripts', 'record', 'record.py')


def rec(name, *flags, wait=True):
    cmd = [PY, REC, SCRIPT, WORK, '--name', name, *flags]
    if not wait:
        return subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return subprocess.run(cmd, capture_output=True, text=True).returncode


def capture(names, alongside=None):
    """Capture these takes at the same time; `alongside()` starts something else first and returns its process."""
    other = alongside() if alongside else None
    if other:
        time.sleep(4)                       # let it get going
    procs = [rec(n, '--capture-only', wait=False) for n in names]
    for p in procs:
        p.wait()
    busy = other is not None and other.poll() is None      # was the other thing still working when the take ended?
    if other:
        other.wait()
    return busy


def compare(name):
    r = subprocess.run([PY, os.path.join(HERE, 'compare_takes.py'), os.path.join(WORK, 'alone-1'), os.path.join(WORK, name),
                        '--labels', 'Alone', name], capture_output=True, text=True)
    return r.returncode == 0, r.stdout.strip()


def main():
    want = sys.argv[1:] or ['alone', 'with-render', 'with-timing', 'two', 'three']
    if 'alone' in want or not os.path.exists(os.path.join(WORK, 'alone-1', 'report.json')):
        shutil.rmtree(WORK, ignore_errors=True)
        os.makedirs(WORK)
        for f in os.listdir(SRC):       # the voice, its timing and what earlier takes learned about slow targets
            if os.path.isfile(os.path.join(SRC, f)) and (f.startswith('voice') or f in ('timing.json', 'record-leads.json', 'words.local.json')):
                shutil.copy2(os.path.join(SRC, f), WORK)
        want = ['alone'] + [w for w in want if w != 'alone']
    groups, notes = {}, {}
    load0 = os.getloadavg()[0]
    for w in want:
        print(f'[{w}] load {os.getloadavg()[0]:.0f}', flush=True)
        if w == 'alone':
            for n in ('alone-1', 'alone-2'):
                capture([n])
                rec(n, '--finish')
            groups[w] = ['alone-2']
        elif w == 'with-render':
            capture(['render-source'])
            busy = capture(['with-render'], lambda: rec('render-source', '--finish', wait=False))
            rec('with-render', '--finish')
            groups[w], notes[w] = ['with-render'], '' if busy else 'the render finished before the take did, so only part of the take was under it'
        elif w == 'with-timing':
            td = os.path.join(WORK, 'timing-job')
            shutil.rmtree(td, ignore_errors=True)
            os.makedirs(td)
            big = sorted((d for d in os.listdir(os.path.join(ROOT, 'output', 'demos')) if os.path.exists(os.path.join(ROOT, 'output', 'demos', d, 'voice.wav'))),
                         key=lambda d: -os.path.getsize(os.path.join(ROOT, 'output', 'demos', d, 'voice.wav')))
            src = os.path.join(ROOT, 'output', 'demos', big[0]) if big else SRC
            for f in ('voice.wav', 'voice.json', 'script.json'):
                if os.path.exists(os.path.join(src, f)):
                    shutil.copy2(os.path.join(src, f), td)
            sc = os.path.join(td, 'script.json') if os.path.exists(os.path.join(td, 'script.json')) else SCRIPT

            def timing():
                return subprocess.Popen([PY, os.path.join(ROOT, 'scripts', 'timing', 'timing.py'), sc, td], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            busy = capture(['with-timing'], timing)
            rec('with-timing', '--finish')
            groups[w], notes[w] = ['with-timing'], '' if busy else 'the timing finished before the take did, so only part of the take was under it'
        elif w in ('two', 'three'):
            names = [f'{w}-{i}' for i in range(1, 3 if w == 'two' else 4)]
            capture(names)
            for n in names:
                rec(n, '--finish')
            groups[w] = names
    lines = ['# Does a recording stay the same under load?', '',
             f"The approved to-do clip, recorded live from the same voice, {time.strftime('%d %b %Y %H:%M')}. The Mac's load when it started: {load0:.0f}"
             f" (other apps running); at the end: {os.getloadavg()[0]:.0f}.", '']
    verdict = {}
    for w, names in groups.items():
        oks = []
        for n in names:
            if not os.path.exists(os.path.join(WORK, n, 'report.json')):
                oks.append(False)
                lines += [f'## {n}', '', 'This take did not finish.', '']
                continue
            ok, table = compare(n)
            oks.append(ok)
            lines += [f'## {n}' + (f' ({notes[w]})' if notes.get(w) else ''), '', table, '']
        verdict[w] = all(oks)
    names = {'alone': 'Recorded alone, a second time (the noise)', 'with-render': 'While another video is being drawn', 'with-timing': 'While another voice is being timed',
             'two': 'Two recordings at once', 'three': 'Three recordings at once'}
    head = ['## Result', ''] + [f"- {names[w]}: **{'the same' if ok else 'NOT the same'}**" for w, ok in verdict.items()] + ['']
    lines[4:4] = head
    open(os.path.join(WORK, 'summary.md'), 'w').write('\n'.join(lines) + '\n')
    json.dump(verdict, open(os.path.join(WORK, 'verdict.json'), 'w'))
    print('\n'.join(head))
    print(os.path.join(WORK, 'summary.md'))


if __name__ == '__main__':
    main()
