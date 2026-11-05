"""NAVI Phase 3: record the browser live to the voice.

The voice leads (reference/recording-rules.md). From Phase 2's timing.json, every action gets a wall-clock start
time so that its click (or the first typed key) lands on its cue word. The recorder (agent-screenplay with NAVI's
patch) waits live for each step; the footage plays at normal speed ("realtime"), and nothing is retimed afterwards.
The recorder never gets the voice: if it did, it would hold frames to fit the audio. NAVI lays the voice track
over the finished recording at the moment the browser was told it started.

Calibration: the drawn cursor travels 0.42 to 1.05 s before a click, depending on distance. The first take uses a
default lead per kind of step; if any action lands more than 0.25 s off its word, the measured lead is used and the
take is recorded again (local, no credits), up to --passes times.

Join checks (recording-rules.md 7): no still screen over max_still_s (5 s); no frozen frame over 1.5 s while the
voice is silent; no cut within 1.5 s of a click (a live take has no cuts); every action within 0.5 s of its word.

Usage: .venv/bin/python scripts/record/record.py examples/test-todo-b.json output/test-todo-v4 [--passes 3]
Output (in <voice_dir>/recording/): scenario.json, <name>.mp4 (silent recorder output), take files,
recording.mp4 (with the voice and room tone), report.md.
"""
import argparse
import json
import math
import os
import re
import shutil
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
CONFIG = json.load(open(os.path.join(ROOT, 'config', 'defaults.json')))
REC = os.path.join(ROOT, 'recorder', 'agent-screenplay')
FF = os.path.join(ROOT, '.venv', 'bin', 'ffmpeg')
sys.path.insert(0, os.path.join(ROOT, 'scripts', 'audio'))

VOICE_START = 0.6      # seconds after the first step before the voice starts (the page has already loaded and settled)
LEAD = {'click': 0.75, 'hover': 0.75, 'type_into': 0.75, 'type': 0.05, 'press': 0.05}
TOLERANCE = 0.25       # re-record when an action lands further than this from its word
MAX_DRIFT = 0.5        # recording-rules.md: every action within 0.5 s of its word
STYLE = {'cursor': 'macos', 'accent': '#1d1d1f', 'click': 'ripple', 'captions': False, 'padding': 0, 'radius': 0,
         'shadow': False, 'maxZoom': 1.6, 'cards': False, 'background': '#ffffff'}


def target(t):
    """NAVI targets to the recorder's: placeholder=/text=/role=/label= pass through, anything else is CSS."""
    if re.match(r'^(placeholder|text|role|label|testid|css|at)=', t):
        return t
    return 'css=' + t.replace(' >> ', ' ').replace("'", '"')


def build(script, timing, leads):
    url = next((a['target'] for a in timing['actions'] if a['do'] == 'goto'), None)
    if not url:
        sys.exit('The script needs a goto action at the start of the first section (the page the video opens on).')
    vw, vh = CONFIG['recording']['viewport']
    steps, start_at, plan = [{'pause': 0.05}], [0.0], []  # the patch starts its clock only when step 1 has a time
    for a in timing['actions']:
        if a['do'] == 'goto':
            continue
        if a['do'] == 'click':
            st, kind = {'click': target(a['target'])}, 'click'
        elif a['do'] == 'type':
            st = {'type': a['text']}
            kind = 'type'
            if a.get('into'):
                st['into'], kind = target(a['into']), 'type_into'
            if a.get('then') == 'Enter':
                st['submit'] = True
        elif a['do'] == 'press':
            st, kind = {'press': a['key']}, 'press'
        elif a['do'] in ('hover', 'highlight'):
            # NAVI never adds a spotlight overlay (recording-rules.md 9): "highlight" means the cursor goes there
            st, kind = {'hover': target(a['target'])}, 'hover'
        else:
            sys.exit(f"Don't know how to record '{a['do']}'.")
        lead = leads.get(len(steps), LEAD[kind])
        steps.append(st)
        start_at.append(round(VOICE_START + a['t'] - lead, 3))
        plan.append({'step': len(steps) - 1, 'cue': a['on'], 'cue_t': a['t'], 'kind': kind, 'lead': lead, 'do': a['do']})
    scenario = {'name': script.get('title', 'demo'), 'url': url, 'viewport': {'width': vw, 'height': vh},
                'realtime': True, 'startAt': start_at, 'typingSpeed': 1.3, 'style': STYLE,
                'output': {'width': 1920, 'height': 1080, 'fps': 30, 'path': 'silent.mp4'}, 'steps': steps}
    return scenario, plan


def record(scenario, out):
    path = os.path.join(out, 'scenario.json')
    json.dump(scenario, open(path, 'w'), indent=1)
    r = subprocess.run(['node', os.path.join(REC, 'dist', 'cli.js'), 'record', path], cwd=out, capture_output=True, text=True)
    log = r.stdout + r.stderr
    open(os.path.join(out, 'recorder.log'), 'a').write(log + '\n----\n')
    if r.returncode != 0:
        sys.exit('The recorder failed:\n' + log[-2000:])
    takes = [os.path.join(dp, f) for dp, _, fs in os.walk(out) for f in fs if f == 'take.json']
    return json.load(open(max(takes, key=os.path.getmtime))), log


def drift(take, plan):
    steps = {s['index']: s for s in take['steps']}
    zero = steps[0]['start']
    rows = []
    for p in plan:
        s = steps[p['step']]
        at = s.get('actionAt', s['start'])
        landed = at - zero - VOICE_START          # on the voice track's clock
        rows.append({**p, 'landed': round(landed, 3), 'off': round(landed - p['cue_t'], 3),
                     'measured_lead': round(at - s['start'], 3), 'late_start': round(s['start'] - zero - (VOICE_START + p['cue_t'] - p['lead']), 3)})
    return zero, rows


def room_tone_track(seconds, sr=44100):
    import dsp
    from treat import add_room_tone, synth_room_tone
    tone = synth_room_tone(sr)
    return add_room_tone([0.0] * int(seconds * sr), tone, sr, tone_lufs=CONFIG['audio_edit']['room_tone_lufs'], fade_in=0.0)


def duration(video):
    m = re.search(r'Duration: (\d+):(\d+):([\d.]+)', subprocess.run([FF, '-i', video], capture_output=True, text=True).stderr)
    return int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))


def mux(out, silent, voice_wav, offset):
    import dsp
    dur = duration(silent)
    tone = os.path.join(out, 'roomtone.wav')
    dsp.write_wav(tone, room_tone_track(dur + 1), 44100)
    final = os.path.join(out, 'recording.mp4')
    ms = int(round(offset * 1000))
    subprocess.run([FF, '-loglevel', 'error', '-y', '-i', silent, '-i', voice_wav, '-i', tone, '-filter_complex',
                    f'[1:a]adelay={ms}|{ms}[v];[v][2:a]amix=inputs=2:normalize=0:duration=longest,atrim=0:{dur:.3f}[a]',
                    '-map', '0:v', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', final], check=True)
    return final, dur


def freezes(video, noise_db=-60, min_s=1.5):
    r = subprocess.run([FF, '-i', video, '-vf', f'freezedetect=n={noise_db}dB:d={min_s}', '-map', '0:v', '-f', 'null', '-'],
                       capture_output=True, text=True)
    starts = [float(x) for x in re.findall(r'freeze_start: ([\d.]+)', r.stderr)]
    ends = [float(x) for x in re.findall(r'freeze_end: ([\d.]+)', r.stderr)]
    return list(zip(starts, ends + [None] * (len(starts) - len(ends))))


def checks(final, dur, offset, timing, rows):
    words = [(w['start'] + offset, w['end'] + offset) for w in timing['words']]
    def voiced(a, b):
        return sum(max(0, min(b, e) - max(a, s)) for s, e in words) / max(b - a, 1e-6)
    fr = [(a, b if b is not None else dur) for a, b in freezes(final)]
    still = [(a, b) for a, b in fr if b - a > CONFIG['recording']['max_still_s']]
    frozen_silent = [(a, b) for a, b in fr if b - a > CONFIG['recording']['max_frozen_frame_s'] and voiced(a, b) < 0.5]
    late = [r for r in rows if abs(r['off']) > MAX_DRIFT]
    return {'freezes': fr, 'still_over_5s': still, 'frozen_while_silent': frozen_silent, 'cuts': [], 'actions_off_by_over_0.5s': late,
            'pass': not still and not frozen_silent and not late}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('script')
    ap.add_argument('voice_dir')
    ap.add_argument('--passes', type=int, default=3)
    a = ap.parse_args()
    script = json.load(open(a.script))
    timing = json.load(open(os.path.join(a.voice_dir, 'timing.json')))
    if timing['problems']:
        sys.exit('Fix the timing problems first (scripts/timing/timing.py).')
    out = os.path.abspath(os.path.join(a.voice_dir, 'recording'))
    shutil.rmtree(out, ignore_errors=True)
    os.makedirs(out)
    leads, history = {}, []
    for n in range(1, a.passes + 1):
        scenario, plan = build(script, timing, leads)
        take, log = record(scenario, out)
        zero, rows = drift(take, plan)
        worst = max(abs(r['off']) for r in rows)
        history.append({'pass': n, 'worst_off_s': worst, 'rows': rows})
        print(f'pass {n}: worst action {worst:.2f} s from its word', flush=True)
        if worst <= TOLERANCE:
            break
        for r in rows:
            # only re-time a step that started on time; a late start means the step before it ran long (a script
            # problem: cue too close to the previous action), and starting it earlier can't help
            if abs(r['off']) > TOLERANCE and r['late_start'] < 0.05:
                leads[r['step']] = round(r['lead'] + r['off'], 3)
    silent = os.path.join(out, 'silent.mp4')
    offset = zero + VOICE_START
    final, dur = mux(out, silent, os.path.join(a.voice_dir, 'voice.wav'), offset)
    res = checks(final, dur, offset, timing, rows)
    report = {'passes': history, 'voice_offset_s': round(offset, 3), 'duration_s': round(dur, 2), 'checks': res, 'video': final}
    json.dump(report, open(os.path.join(out, 'report.json'), 'w'), indent=1)
    lines = [f"# Recording report", '', f"Video: `{final}` ({dur:.1f} s). Voice starts at {offset:.2f} s. Passes: {len(history)}.", '',
             '| Cue | Word at | Action landed | Off by | Kind |', '|---|---|---|---|---|']
    lines += [f"| {r['cue']} | {r['cue_t']:.2f} s | {r['landed']:.2f} s | {r['off']:+.2f} s | {r['do']} |" for r in rows]
    lines += ['', f"Still screen over 5 s: {res['still_over_5s'] or 'none'}",
              f"Frozen over 1.5 s while the voice is silent: {res['frozen_while_silent'] or 'none'}",
              f"Cuts: none (one continuous live take)",
              f"Actions more than 0.5 s from their word: {[r['cue'] for r in res['actions_off_by_over_0.5s']] or 'none'}",
              '', '**Join checks: ' + ('PASS' if res['pass'] else 'FAIL') + '**']
    open(os.path.join(out, 'report.md'), 'w').write('\n'.join(lines) + '\n')
    print('\n'.join(lines))
    sys.exit(0 if res['pass'] else 1)


if __name__ == '__main__':
    main()
