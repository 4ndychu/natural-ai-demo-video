"""NAVI Phase 2: word timings from the finished voice track, and each action pinned to its cue word.

- Word timestamps come from the finished track itself, locally (faster-whisper, config timing.model), one section at a
  time with that section's talking text as a hint, so fillers and restarts keep their real timing. No API call.
- Each action's "on" word is matched (fuzzy) to its first occurrence in its own section, after the previous action.
  Special cues: "start" = the moment the section's voice begins, "end" = the moment it ends.
- Every action gets a kind: explain, click, hunt or wait (given in the script, else inferred from what it does).
- Checks: every cue mapped; actions in order; waits only at section boundaries ("start" or "end");
  warns where the screen would sit still for more than recording.max_still_s (5 s).

Input:  the script JSON (sections with talk and actions) and the folder generate.py wrote (voice.wav, voice.json).
Output: timing.json (the schedule), timing.md (a table per section), and with --preview a watchable preview.mp4:
        the voice track, the words lighting up as they're spoken, and each action appearing at its word.

Usage: .venv/bin/python scripts/timing/timing.py examples/test-todo-b.json output/test-todo-v4 [--preview]
"""
import argparse
import difflib
import json
import os
import re
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
CONFIG = json.load(open(os.path.join(ROOT, 'config', 'defaults.json')))
KINDS = ('explain', 'click', 'hunt', 'wait')
INFER = {'click': 'click', 'type': 'click', 'press': 'click', 'drag': 'click', 'select': 'click', 'scroll': 'explain',
         'highlight': 'explain', 'hover': 'explain', 'zoom': 'explain', 'goto': 'wait', 'wait': 'wait', 'reload': 'wait'}
HUNT = re.compile(r"where is it|where's the|where's it|hang on|let's see", re.I)
FF = os.path.join(ROOT, '.venv', 'bin', 'ffmpeg')


def norm(w):
    return re.sub(r"[^a-z0-9']", '', w.lower())


def transcribe(wav, script, windows):
    """Word timings from the finished track, locally, one section at a time. Each section's own talking text is
    given to the model as a hint, so it writes what was actually said, fillers and restarts included; without it,
    Whisper drops "uh, book the" and squeezes the words after it (one cue landed a full second early).
    Cached next to the track."""
    cache = os.path.join(os.path.dirname(wav), 'words.local.json')
    if os.path.exists(cache) and os.path.getmtime(cache) > max(os.path.getmtime(wav), os.path.getmtime(__file__)):
        return json.load(open(cache))
    from faster_whisper import WhisperModel
    from faster_whisper.audio import decode_audio
    m = WhisperModel(CONFIG['timing']['model'], device='cpu', compute_type='int8')
    audio, sr = decode_audio(wav, sampling_rate=16000), 16000
    words = []
    for k, (sec, win) in enumerate(zip(script['sections'], windows)):
        a, b = int(max(0.0, win['start'] - 0.1) * sr), int((win['end'] + 0.1) * sr)
        hint = re.sub(r'\[[^\]]+\]', '', sec['talk']).strip()
        segs, _ = m.transcribe(audio[a:b], language='en', word_timestamps=True, initial_prompt=hint,
                               condition_on_previous_text=False)
        # each word keeps the section it was heard in ('sec'): a section's first word often starts right at the edge
        # of its clip, a little before the section's own start, and sorting words into sections by time lost it
        # (12 Nov 2026: a cue on a section's first word, "Pricing", was "not heard")
        words += [{'w': w.word.strip(), 'start': round(w.start + a / sr, 3), 'end': round(w.end + a / sr, 3), 'sec': k}
                  for s_ in segs for w in s_.words]
    json.dump(words, open(cache, 'w'))
    return words


def match(cue, words, i0):
    """First word at or after i0 whose text matches the cue (one or more words), fuzzy. Returns (index, n words)."""
    parts = [norm(p) for p in cue.split() if norm(p)]
    for i in range(i0, len(words) - len(parts) + 1):
        got = [norm(words[i + k]['w']) for k in range(len(parts))]
        if all(g == p or g.startswith(p) or difflib.SequenceMatcher(None, g, p).ratio() >= 0.8 for g, p in zip(got, parts)):
            return i, len(parts)
    # a hyphenated cue ("One-time") is often heard as two words ("One", "-time"): the cue as one string against two
    # or three heard words run together
    whole = norm(cue)
    for i in range(i0, len(words)):
        for n in (2, 3):
            if i + n <= len(words) and ''.join(norm(words[i + k]['w']) for k in range(n)) == whole:
                return i, n
    return None, 0


def schedule(script, voice_dir):
    vj = json.load(open(os.path.join(voice_dir, 'voice.json')))
    words = transcribe(os.path.join(voice_dir, 'voice.wav'), script, vj['sections'])
    ref = vj.get('words', [])
    out, problems, warnings = [], [], []
    max_still = CONFIG['recording']['max_still_s']
    for k, (sec, win) in enumerate(zip(script['sections'], vj['sections'])):
        sw = [w for w in words if (w['sec'] == k if 'sec' in w else win['start'] - 0.05 <= w['start'] < win['end'])]
        speech0 = sw[0]['start'] if sw else win['start']
        speech1 = sw[-1]['end'] if sw else win['end']
        cursor, rows = 0, []
        for a in sec.get('actions', []):
            kind = a.get('kind') or INFER.get(a['do'], 'explain')
            if kind not in KINDS:
                problems.append(f"{sec['name']}: action on '{a['on']}' has unknown kind '{kind}'")
            row = {'section': sec['name'], 'on': a['on'], 'do': a['do'], 'kind': kind,
                   'target': a.get('target'), 'text': a.get('text'), 'key': a.get('key'),
                   'into': a.get('into'), 'then': a.get('then')}
            if a['on'] in ('start', 'end'):
                row['t'] = round(speech0 if a['on'] == 'start' else speech1, 3)
                row['heard'] = f"<section {a['on']}>"
            else:
                i, n = match(a['on'], sw, cursor)
                if i is None:
                    problems.append(f"{sec['name']}: cue '{a['on']}' not heard in this section")
                    continue
                row['t'] = sw[i]['start']
                row['heard'] = ' '.join(w['w'] for w in sw[i:i + n])
                # agreement with the timings generate.py stored, when it has the same word nearby
                near = [r for r in ref if r.get('section') == sec['name'] and norm(r['w']).startswith(norm(a['on'].split()[0]))]
                if near:
                    row['other_timing_diff_ms'] = round(min(abs(r['start'] - row['t']) for r in near) * 1000)
                cursor = i + n
                if kind == 'wait':
                    problems.append(f"{sec['name']}: wait on '{a['on']}' is mid-section; waits go at a section boundary ('start' or 'end')")
            row['t_in_section'] = round(row['t'] - win['start'], 3)
            rows.append(row)
        ts = [r['t'] for r in rows]
        if ts != sorted(ts):
            problems.append(f"{sec['name']}: actions are out of order")
        # typing keeps the screen changing for about 0.09 s per character
        busy = [r['t'] + (0.09 * len(r['text']) if r['do'] == 'type' and r.get('text') else 0) for r in rows]
        marks = [speech0] + sorted(ts + busy) + [speech1]
        for a, b in zip(marks, marks[1:]):
            if b - a > max_still:
                warnings.append(f"{sec['name']}: nothing happens on screen from {a:.1f} s to {b:.1f} s ({b - a:.1f} s)")
        out += rows
    # still screen across section boundaries too: from one action to the next, anywhere in the video
    ts = sorted([r['t'] for r in out] + [r['t'] + 0.09 * len(r['text']) for r in out if r['do'] == 'type' and r.get('text')])
    for a, b in zip(ts, ts[1:]):
        if b - a > max_still:
            msg = f"nothing happens on screen from {a:.1f} s to {b:.1f} s ({b - a:.1f} s)"
            if not any(msg in x for x in warnings):
                warnings.append(f'across sections: {msg}')
    return {'track': os.path.join(voice_dir, 'voice.wav'), 'duration': vj['duration'], 'sections': vj['sections'],
            'words': words, 'actions': out, 'problems': problems, 'warnings': warnings}


def table(sch):
    lines = []
    for win in sch['sections']:
        lines += [f"### {win['section']}  ({win['start']:.2f} to {win['end']:.2f} s)", '',
                  '| Time | In section | Cue | Heard | Does | Kind | Target |', '|---|---|---|---|---|---|---|']
        for r in [r for r in sch['actions'] if r['section'] == win['section']]:
            tgt = r.get('target') or r.get('text') or r.get('key') or ''
            lines.append(f"| {r['t']:.2f} s | {r['t_in_section']:.2f} s | {r['on']} | {r['heard']} | {r['do']} | {r['kind']} | `{tgt}` |")
        lines.append('')
    lines.append('**Problems:** ' + ('; '.join(sch['problems']) if sch['problems'] else 'none'))
    lines.append('')
    lines.append('**Warnings:** ' + ('; '.join(sch['warnings']) if sch['warnings'] else 'none'))
    return '\n'.join(lines)


def ass_time(t):
    t = max(0.0, t)
    return f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"


def preview(sch, script, out_mp4):
    """A plain 1280x720 video: the voice, the words lighting up as they're said, each action at its word."""
    ass = os.path.splitext(out_mp4)[0] + '.ass'
    hdr = ("[Script Info]\nScriptType: v4.00+\nPlayResX: 1280\nPlayResY: 720\n\n[V4+ Styles]\n"
           "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, "
           "StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
           "Style: Words,Arial,34,&H00FFFFFF,&H00666666,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,2,90,90,70,1\n"
           "Style: Action,Arial,44,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,1,0,0,0,100,100,0,0,1,0,0,5,90,90,0,1\n"
           "Style: Kind,Arial,26,&H00A0A0A0,&H00A0A0A0,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,8,90,90,60,1\n"
           "Style: Section,Arial,24,&H00808080,&H00808080,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,7,60,60,40,1\n\n"
           "[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")
    ev = []
    for i, win in enumerate(sch['sections']):
        ev.append(f"Dialogue: 0,{ass_time(win['start'])},{ass_time(win['end'])},Section,,0,0,0,,Section {i + 1}: {win['section']}")
    # words: lines of up to ~9 words with karaoke timing (grey until spoken, then white)
    ws = sch['words']
    for k in range(0, len(ws), 9):
        chunk = ws[k:k + 9]
        s0, e0 = chunk[0]['start'], chunk[-1]['end']
        parts, t = [], s0
        for w in chunk:
            gap = max(0, w['start'] - t)
            if gap > 0.01:
                parts.append(f"{{\\k{int(gap * 100)}}}")
            parts.append(f"{{\\k{max(1, int((w['end'] - w['start']) * 100))}}}{w['w']} ")
            t = w['end']
        ev.append(f"Dialogue: 0,{ass_time(s0 - 0.15)},{ass_time(e0 + 0.35)},Words,,0,0,0,,{''.join(parts).strip()}")
    acts = sch['actions']
    labels = {'click': 'CLICK', 'type': 'TYPE', 'press': 'PRESS', 'highlight': 'HIGHLIGHT', 'hover': 'LOOK AT', 'goto': 'OPEN', 'drag': 'DRAG'}
    for j, a in enumerate(acts):
        end = min(a['t'] + 2.2, acts[j + 1]['t'] - 0.05) if j + 1 < len(acts) else a['t'] + 2.2
        what = a.get('text') or a.get('key') or (a.get('target') or '')
        what = what.replace('placeholder=', '').replace('{', '(').replace('}', ')')[:48]
        ev.append(f"Dialogue: 1,{ass_time(a['t'])},{ass_time(end)},Action,,0,0,0,,{{\\fad(60,200)}}{labels.get(a['do'], a['do'].upper())}  {what}")
        ev.append(f"Dialogue: 1,{ass_time(a['t'])},{ass_time(end)},Kind,,0,0,0,,{{\\fad(60,200)}}on \"{a['on']}\"  ·  {a['kind']}")
    open(ass, 'w').write(hdr + '\n'.join(ev) + '\n')
    subprocess.run([FF, '-loglevel', 'error', '-y', '-f', 'lavfi', '-i', f"color=c=0x141414:s=1280x720:d={sch['duration'] + 0.5}",
                    '-i', sch['track'], '-vf', f"ass={ass}:fontsdir=/System/Library/Fonts/Supplemental",
                    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k', '-shortest', out_mp4], check=True)
    return out_mp4


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('script')
    ap.add_argument('voice_dir')
    ap.add_argument('--preview', action='store_true')
    a = ap.parse_args()
    script = json.load(open(a.script))
    sch = schedule(script, a.voice_dir)
    json.dump(sch, open(os.path.join(a.voice_dir, 'timing.json'), 'w'), indent=1)
    md = table(sch)
    open(os.path.join(a.voice_dir, 'timing.md'), 'w').write(md + '\n')
    print(md)
    if a.preview:
        print('Preview:', preview(sch, script, os.path.join(a.voice_dir, 'timing-preview.mp4')))
    sys.exit(1 if sch['problems'] else 0)


if __name__ == '__main__':
    main()
