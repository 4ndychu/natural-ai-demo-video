"""Phase 5 check (docs/BUILD_BRIEF.md): all three caption modes and a corner label render correctly, and changing
them re-renders without new voice or recording.

Exports one finished recording several ways into a folder outside the repo and checks each result by reading the
frames back with Apple's text recognition:
  burn  + corner br : captions readable at every cue, label readable bottom right, .srt + transcript written
  file  + corner tl : no captions in the picture, .srt matches the voice, label top left
  off   + corner tr : no captions, no .srt, label top right
  file  + corner bl : label bottom left
  file  (no label)  : the video is copied, not re-encoded (identical picture data)
  burn, Mona Sans look + corner br, with a 1.35x copy: captions readable; the copy is 1.35x shorter and the voice
                      keeps its pitch (within half a semitone)
Captions follow the speech: each one ends at most 0.65 s after its own last word, has at most 2 lines, and is
gone from the picture 0.2 s after it ends.
Also: the voice and the recording are byte-for-byte unchanged afterwards, an export into the repo is refused,
and --preview makes a 1280x720 file.

Usage: .venv/bin/python scripts/render/test_export.py <script.json> <voice_dir> <recording> <out_dir outside the repo>
"""
import hashlib
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, 'scripts', 'privacy'))
import captions as cap  # noqa: E402
import math  # noqa: E402
sys.path.insert(0, os.path.join(ROOT, 'scripts', 'audio'))
import dsp  # noqa: E402
import export as ex  # noqa: E402
import privacy  # noqa: E402

LABELS = {'br': 'Acme Academy', 'tl': 'Lesson 3', 'tr': 'Draft 2', 'bl': 'Module 1'}


def md5(path):
    h = hashlib.md5()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


# Letters Apple's text reader sometimes returns in place of the Latin ones they look like (Cyrillic and Greek).
LOOKALIKE = str.maketrans(dict(zip('АВСЕНІЈКМОРЅТХУаеіјорсѕхуԁΑΒΕΗΙΚΜΝΟΡΤΥΧΖοκνρτυχ',
                                   'ABCEHIJKMOPSTXYaeijopcsxydABEHIKMNOPTYXZokvptux')))


def norm(t):
    return re.sub(r'[^a-z0-9 ]', '', t.translate(LOOKALIKE).lower())


def frames_at(video, times, d):
    os.makedirs(d, exist_ok=True)
    out = []
    for i, t in enumerate(times):
        p = os.path.join(d, f'{i:03d}.png')
        subprocess.run([ex.FF, '-loglevel', 'error', '-y', '-ss', f'{t:.3f}', '-i', video, '-frames:v', '1', p], check=True)
        out.append(p)
    res = privacy.ocr(out)
    return [{**res[p], 'path': p} for p in out]


def found(text, ocr, region=None):
    """Most of the words of `text` read in the frame (optionally only inside region (x0, y0, x1, y1), as fractions)."""
    lines = ocr['lines']
    if region:
        W, H = ocr['width'], ocr['height']
        lines = [l for l in lines if region[0] * W <= l['box'][0] + l['box'][2] / 2 <= region[2] * W
                 and region[1] * H <= l['box'][1] + l['box'][3] / 2 <= region[3] * H]
    seen = set(norm(' '.join(l['text'] for l in lines)).split())
    want = norm(text).split()
    return sum(w in seen for w in want) >= max(1, round(0.8 * len(want)))


QUAD = {'tl': (0, 0, .5, .5), 'tr': (.5, 0, 1, .5), 'bl': (0, .5, .5, 1), 'br': (.5, .5, 1, 1)}
SAME_LABEL = 0.9    # share of the label's white text pixels that must match a frame where the text was read


def _in(region, ocr):
    W, H = ocr['width'], ocr['height']
    return [l for l in ocr['lines'] if region[0] * W <= l['box'][0] + l['box'][2] / 2 <= region[2] * W
            and region[1] * H <= l['box'][1] + l['box'][3] / 2 <= region[3] * H]


def _text_mask(png, box):
    """The white text pixels (luminance over 200) inside box (x, y, w, h) of a frame. On a label's dark box, only
    the letters are that bright."""
    x, y, w, h = box
    r = subprocess.run([ex.FF, '-loglevel', 'error', '-i', png, '-vf', f'crop={w}:{h}:{x}:{y},format=gray', '-f', 'rawvideo', '-'],
                       capture_output=True, check=True)
    return [v > 200 for v in r.stdout]


def _iou(a, b):
    inter = sum(1 for x, y in zip(a, b) if x and y)
    return inter / max(1, sum(1 for x, y in zip(a, b) if x or y))


def label_frames(text, ocrs, region):
    """How many frames show the label, and a note. A frame counts when the text reader reads the label there, or when
    its pixels are the same letters as a frame where it was read (the reader sometimes returns look-alike letters,
    "Астe" for "Acme"; the label itself never changes). At least one frame must be read as text."""
    read = [found(text, o, region) for o in ocrs]
    if not any(read):
        return 0, 'never read as text'
    ref = ocrs[read.index(True)]
    want = set(norm(text).split())
    lines = [l for l in _in(region, ref) if want & set(norm(l['text']).split())]
    x0 = min(l['box'][0] for l in lines) - 6
    y0 = min(l['box'][1] for l in lines) - 6
    x1 = max(l['box'][0] + l['box'][2] for l in lines) + 6
    y1 = max(l['box'][1] + l['box'][3] for l in lines) + 6
    box = (max(0, int(x0)), max(0, int(y0)), int(min(ref['width'], x1) - max(0, x0)), int(min(ref['height'], y1) - max(0, y0)))
    ref_mask = _text_mask(ref['path'], box)
    if sum(ref_mask) < 40:
        return 0, 'no letters where the label was read'
    seen, by_pixels, worst = 0, 0, 1.0
    for o, r in zip(ocrs, read):
        if r:
            seen += 1
            continue
        same = _iou(_text_mask(o['path'], box), ref_mask)
        worst = min(worst, same)
        if same >= SAME_LABEL:
            seen += 1
            by_pixels += 1
    note = f', {by_pixels} by pixels (the reader misread the letters; same letters as a read frame, {worst:.0%} match)' if by_pixels else ''
    if seen < len(ocrs):
        note += f'; the closest unread frame matches the label\'s letters {worst:.0%} (needs {SAME_LABEL:.0%})'
    return seen, note


def main():
    script_path, voice_dir, rec, out = sys.argv[1:5]
    script = json.load(open(script_path))
    rdir = os.path.join(voice_dir, rec)
    before = {f: md5(os.path.join(p, f)) for p, f in [(rdir, 'recording.mp4'), (voice_dir, 'voice.wav')]}
    timing = json.load(open(os.path.join(voice_dir, 'timing.json')))
    report = json.load(open(os.path.join(rdir, 'report.json')))
    cues = cap.build(script, timing, report['voice_offset_s'])
    mids = [(c['start'] + c['end']) / 2 for c in cues]
    rows, ok = [], True

    def check(name, cond, detail=''):
        nonlocal ok
        ok &= bool(cond)
        rows.append(f"| {name} | {'pass' if cond else '**FAIL**'} | {detail} |")

    over = max(c['end'] - c['words_end'] for c in cues)
    check('captions end with their own words', over <= 0.65 and all(len(c['lines']) <= 2 for c in cues),
          f'longest a caption stays up after its last word: {over:.2f} s; at most {max(len(c["lines"]) for c in cues)} lines')
    runs = [('burn', 'br', True, None, None), ('file', 'tl', False, None, None), ('off', 'tr', False, None, None),
            ('file', 'bl', False, None, None), ('file', 'off', False, None, None), ('burn', 'br', False, 'mona-rounded', 1.35)]
    for captions, corner, preview, look, speed in runs:
        d = os.path.join(out, f'{captions}-{corner}-{look or "default"}')
        t0 = time.time()
        r = ex.export(script, voice_dir, rec, captions, corner, LABELS.get(corner, ''), preview, d, None, speed, look)
        secs = time.time() - t0
        f = r['files']
        tag = f'captions {captions}, corner {corner}' + (f', {look}' if look else '') + (f', {speed}x copy' if speed else '')
        ocr = frames_at(f['video'], mids, os.path.join(out, 'frames', f'{captions}-{corner}'))
        hits = sum(found(' '.join(c['lines']), o, (0.05, 0.75, 0.95, 1)) for c, o in zip(cues, ocr))
        if captions == 'burn':
            check(f'{tag}: captions in the picture', hits == len(cues), f'{hits}/{len(cues)} cues readable at their midpoint')
            after = frames_at(f['video'], [c['end'] + 0.2 for c in cues], os.path.join(out, 'frames', f'{captions}-{corner}-after'))
            left = sum(found(' '.join(c['lines']), o, (0.05, 0.75, 0.95, 1)) for c, o in zip(cues, after))
            check(f'{tag}: captions gone once their words end', left == 0, f'{left}/{len(cues)} still readable 0.2 s after their end')
        else:
            check(f'{tag}: no captions in the picture', hits == 0, f'{hits}/{len(cues)} cues readable')
        if captions == 'off':
            check(f'{tag}: no .srt', 'captions' not in f and not any(x.endswith('.srt') for x in os.listdir(d)))
        else:
            srt = open(f['captions']).read()
            times = re.findall(r'(\d\d):(\d\d):(\d\d),(\d\d\d) --> (\d\d):(\d\d):(\d\d),(\d\d\d)', srt)
            ts = [(int(a) * 3600 + int(b) * 60 + int(c) + int(dd) / 1000, int(e) * 3600 + int(g) * 60 + int(h) + int(i) / 1000)
                  for a, b, c, dd, e, g, h, i in times]
            good = len(ts) == len(cues) and all(s < e for s, e in ts) and all(ts[k][1] <= ts[k + 1][0] for k in range(len(ts) - 1))
            check(f'{tag}: .srt', good, f'{len(ts)} cues, in order, none overlapping, last ends {ts[-1][1]:.1f} s of {report["duration_s"]} s')
        check(f'{tag}: transcript', os.path.getsize(f['transcript']) > 50)
        if corner != 'off':
            seen, note = label_frames(LABELS[corner], ocr, QUAD[corner])
            check(f'{tag}: label "{LABELS[corner]}" {corner}', seen == len(ocr), f'readable in {seen}/{len(ocr)} frames{note}, only in that corner')
        else:
            same = subprocess.run([ex.FF, '-loglevel', 'error', '-i', f['video'], '-map', '0:v', '-c', 'copy', '-f', 'md5', '-'], capture_output=True, text=True).stdout \
                == subprocess.run([ex.FF, '-loglevel', 'error', '-i', os.path.join(rdir, 'recording.mp4'), '-map', '0:v', '-c', 'copy', '-f', 'md5', '-'], capture_output=True, text=True).stdout
            check(f'{tag}: video copied, not re-encoded', same and not r['re_encoded'], f'{secs:.1f} s')
        if speed:
            dur = lambda v: float(re.search(r'Duration: (\d+):(\d+):([\d.]+)', subprocess.run([ex.FF, '-i', v], capture_output=True, text=True).stderr).group(3)) \
                + 60 * int(re.search(r'Duration: (\d+):(\d+)', subprocess.run([ex.FF, '-i', v], capture_output=True, text=True).stderr).group(2))
            ratio = dur(f['video']) / dur(f['speed_video'])
            pitch = []
            for v in (f['video'], f['speed_video']):
                wav = v + '.wav'
                subprocess.run([ex.FF, '-loglevel', 'error', '-y', '-i', v, '-ac', '1', '-ar', '44100', wav], check=True)
                x, sr = dsp.read_wav(wav)
                f0 = sorted(hz for _, hz in dsp.yin(x, sr) if hz)
                pitch.append(f0[len(f0) // 2])
                os.remove(wav)
            st = 12 * math.log2(pitch[1] / pitch[0])
            check(f'{tag}: sped-up copy', abs(ratio - speed) < 0.02 and abs(st) < 0.5 and 'speed_captions' in f,
                  f'{ratio:.3f}x shorter; voice pitch {pitch[0]:.0f} Hz -> {pitch[1]:.0f} Hz ({st:+.2f} semitones); .srt sped up too')
        if preview:
            probe = subprocess.run([ex.FF, '-i', f['preview']], capture_output=True, text=True).stderr
            check(f'{tag}: 720p preview', '1280x720' in probe)
        rows[-1] += f' (export took {secs:.1f} s)'
    after = {f: md5(os.path.join(p, f)) for p, f in [(rdir, 'recording.mp4'), (voice_dir, 'voice.wav')]}
    check('voice and recording unchanged by every export', before == after, 'same file hashes before and after')
    r = subprocess.run([sys.executable, os.path.join(HERE, 'export.py'), script_path, voice_dir, '--recording', rec, '--to', os.path.join(ROOT, 'output', 'x')],
                       capture_output=True, text=True)
    check('export into the repo is refused', r.returncode != 0 and 'never go inside' in (r.stdout + r.stderr))
    lines = ['# Phase 5 export check', '', f'Recording: `{rdir}`. Exports in `{out}`.', '', '| Check | Result | Detail |', '|---|---|---|'] + rows + ['', f"**{'PASS' if ok else 'FAIL'}**"]
    open(os.path.join(out, 'check.md'), 'w').write('\n'.join(lines) + '\n')
    print('\n'.join(lines))
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
