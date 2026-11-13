"""Redo only the sections marked in Review (docs/BUILD_BRIEF.md, Phase 5).

Only the marked sections get a new voice. Every other section keeps exactly the take it had (passed to the voice
step as a pick). Then the timing is redone and the whole video is recorded again: recording is local and free,
and one continuous take keeps the "no cuts" rule (recording-rules.md). Then export as usual (export.py).

Two ways to redo a section's voice:
  (default)     new takes for the marked sections. Costs credits: the estimate is shown, and nothing is
                generated without --yes.
  --other-take  switch each marked section to the other take NAVI already made. Free.

The previous voice, timing and video are kept in <voice_dir>/replaced/<time>/ so they can be compared.

Usage: .venv/bin/python scripts/render/redo.py script.json voice_dir --sections open,filter-and-clear
       [--other-take] [--yes] [--recording recording] [--style casual|recordly]
"""
import argparse
import glob
import json
import os
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
PY = os.path.join(ROOT, '.venv', 'bin', 'python')


def step(name, cmd):
    print(f'{name}...', flush=True)
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f'{name} failed:\n' + (r.stdout + r.stderr)[-2000:])
    return r.stdout


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('script')
    ap.add_argument('voice_dir')
    ap.add_argument('--sections', required=True, help='the marked sections, e.g. "open,filter-and-clear"')
    ap.add_argument('--other-take', action='store_true', help="use each marked section's other saved take (free)")
    ap.add_argument('--yes', action='store_true', help='spend the credits for new takes')
    ap.add_argument('--recording', default='recording')
    ap.add_argument('--style', help='video style (default: the one the recording used)')
    a = ap.parse_args()
    script = json.load(open(a.script))
    vd = a.voice_dir
    voice = json.load(open(os.path.join(vd, 'voice.json')))
    used = {s['section']: s['take'] for s in voice['sections']}
    names = [s['name'] for s in script['sections']]
    marked = [s.strip() for s in a.sections.split(',') if s.strip()]
    bad = [s for s in marked if s not in names]
    if bad:
        sys.exit(f'No section called {", ".join(bad)}. Sections: {", ".join(names)}.')
    takes = max(int(os.path.basename(p).rsplit('_take', 1)[1].split('.')[0])
                for p in glob.glob(os.path.join(vd, '*_take*.mp3')))
    picks = {n: used[n] for n in names if n not in marked}

    if a.other_take:
        for n in marked:
            others = [k for k in range(1, takes + 1) if k != used[n] and os.path.exists(os.path.join(vd, f'{n}_take{k}.mp3'))]
            if not others:
                sys.exit(f'"{n}" has no other saved take. Redo it with new takes instead (costs credits).')
            picks[n] = others[0]
        print(f"Free redo: {', '.join(f'{n} take {used[n]} -> {picks[n]}' for n in marked)}. No credits.")
    else:
        text = {s['name']: s['talk'] for s in script['sections']}
        chars = sum(len(text[n]) for n in marked) * takes
        print(f'New voice for {len(marked)} section(s) ({", ".join(marked)}), {takes} takes each: '
              f'about {chars:,} characters (about {chars:,} credits). Every other section keeps its take.')
        if not a.yes:
            print('Nothing changed. Re-run with --yes once the user has agreed to the cost, or use --other-take (free).')
            return

    keep = os.path.join(vd, 'replaced', time.strftime('%Y%m%d-%H%M%S'))
    os.makedirs(keep)
    for f in ('voice.wav', 'voice_dry.wav', 'voice.json', 'timing.json', 'timing.md'):
        if os.path.exists(os.path.join(vd, f)):
            shutil.copy2(os.path.join(vd, f), keep)
    rec = os.path.join(vd, a.recording)
    for f in ('recording.mp4', 'report.json', 'report.md', 'privacy.json'):
        if os.path.exists(os.path.join(rec, f)):
            shutil.copy2(os.path.join(rec, f), os.path.join(keep, 'recording-' + f))
    if not a.other_take:
        for n in marked:
            for p in glob.glob(os.path.join(vd, f'{n}_take*')):
                shutil.move(p, keep)                  # the generator makes only what's missing: these sections

    style = a.style
    if not style and os.path.exists(os.path.join(keep, 'recording-report.json')):
        style = json.load(open(os.path.join(keep, 'recording-report.json'))).get('style')
    gen = [PY, os.path.join(ROOT, 'scripts', 'voice', 'generate.py'), a.script, '--out', vd, '--takes', str(takes),
           '--model', voice['model'], '--stability', str(voice['settings']['stability']), '--yes',
           '--pick', ','.join(f'{n}={k}' for n, k in picks.items())]
    print(step('Voice', gen))
    print(step('Timing', [PY, os.path.join(ROOT, 'scripts', 'timing', 'timing.py'), a.script, vd]).strip().splitlines()[-1])
    rec_cmd = [PY, os.path.join(ROOT, 'scripts', 'record', 'record.py'), a.script, vd, '--name', a.recording]
    if style:
        rec_cmd += ['--style', style]
    r = subprocess.run(rec_cmd, capture_output=True, text=True)
    print(r.stdout[-2500:])
    if r.returncode != 0:
        sys.exit('The recording did not pass its checks; see the report above. The previous version is in ' + keep)
    print(f'Done. Only {", ".join(marked)} changed in the voice. The previous voice and video are in {keep}.')
    print(f'Export it as usual: .venv/bin/python scripts/render/export.py {a.script} {vd} --recording {a.recording}')


if __name__ == '__main__':
    main()
