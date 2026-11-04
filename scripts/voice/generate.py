"""NAVI voice generation: one continuous read per section on ElevenLabs eleven_v3.

The method that won every listening test (see reference/voice-rules.md):
- Each section is ONE request and ONE continuous read. Sentences are never generated separately and stitched,
  and `next_text` is never passed: both make every sentence sound like it's about to carry on.
- 2 takes per section. The take whose last sentence ends lowest in the speaker's range and quietest is ranked
  first (audio/finality.py). The user can still overrule it by ear.
- Nothing inside a read is cut, stretched or rejoined, except a pause longer than MAX_PAUSE at punctuation,
  shortened from its middle with a 30 ms equal-power crossfade. Never trim right after a sentence.
- Edges only: start 40 ms before the first word with a 10 ms fade-in. The real end of speech is found from the
  audio (the last 10 ms window above -30 dB of the take's peak), because v3's timing data runs the last word to
  the end of the file. The word's own decay is kept while it is still falling (up to 0.25 s, 0.45 s for the last
  section). If the file stops mid-word, the tail fades over 150 ms. Never add reverb to fake a decay.

Input: a JSON file {"voice_id": "...", "sections": [{"name": "open", "talk": "[relaxed] ..."}, ...]}
Output (in --out): <name>_take<k>.mp3/.json/.wav per take, voice_dry.wav, voice.wav (treated, with room tone), voice.json
(chosen takes, words with times, per-section windows).

The key is read from the macOS Keychain (service "navi-elevenlabs") or the NAVI_ELEVENLABS_KEY environment
variable. It is never printed or written anywhere.

Usage: python3 generate.py script.json --out output/demo1 [--takes 2] [--stability 0.7] [--speed 1.0] [--yes]
Without --yes it only prints the character count and estimated credits, and stops.
"""
import argparse
import base64
import json
import math
import os
import re
import subprocess
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'audio'))
import dsp  # noqa: E402
from finality import finality, words_from  # noqa: E402
from treat import add_room_tone, synth_room_tone, treat  # noqa: E402

MODEL, SR = 'eleven_v3', 44100
MAX_PAUSE = 0.8          # walkthroughs: only silences over 0.8 s are shortened (voice-rules.md, section 4)
FINAL_MAX, SECTION_MAX = 0.45, 0.25
FADE_END, FADE_CUT, XF = 0.08, 0.15, 0.03
SECTION_GAP = 0.40       # last word to next section's first word (0.35 to 0.45 s)
TAG_RE = re.compile(r'\[[^\]]+\]')
CONFIG_REF_PACE = json.load(open(os.path.join(HERE, '..', '..', 'config', 'defaults.json')))['voice'].get('reference_pace_wps')
# NAVI's ffmpeg lives next to its Python in .venv/bin (see scripts/setup/check.py); find it there first.
os.environ['PATH'] = os.path.dirname(sys.executable) + os.pathsep + os.environ.get('PATH', '')


def get_key():
    key = os.environ.get('NAVI_ELEVENLABS_KEY')
    if not key and sys.platform == 'darwin':
        r = subprocess.run(['security', 'find-generic-password', '-s', 'navi-elevenlabs', '-w'],
                           capture_output=True, text=True)
        key = r.stdout.strip() if r.returncode == 0 else None
    if not key:
        sys.exit('No ElevenLabs key. Run the setup step to store it in the Keychain (service "navi-elevenlabs").')
    return key


ROOM_TONE = os.path.expanduser('~/Library/Application Support/NAVI/room_tone.wav')


def room_tone():
    """A real recording of a quiet room if one is saved in NAVI's settings folder, else steady synthetic noise.
    Either way it goes under the voice at about -62 LUFS, band-limited to 90 Hz to 2.5 kHz (voice-rules.md, 4)."""
    if os.path.exists(ROOM_TONE):
        x, sr = dsp.read_wav(ROOM_TONE)
        if sr == SR:
            return x, 'recorded'
    return synth_room_tone(SR), 'synthetic'


def pace(words):
    """Words per second, first word start to last word start (v3's last-word end runs to the end of the file)."""
    return (len(words) - 1) / max(0.1, words[-1]['start'] - words[0]['start']) if len(words) > 1 else 0.0


def check_tags(text):
    """Only [relaxed] at the very start is allowed (voice-rules.md, section 2)."""
    tags = TAG_RE.findall(text)
    bad = [t for t in tags if t != '[relaxed]'] + (['[relaxed] not at start'] if '[relaxed]' in tags and not text.lstrip().startswith('[relaxed]') else [])
    if bad:
        sys.exit(f'Banned or misplaced tags: {bad}. Only [relaxed] at the start of a section is allowed.')


def fetch(path_base, voice_id, text, settings, key):
    if not os.path.exists(path_base + '.json'):
        req = urllib.request.Request(
            f'https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/with-timestamps?output_format=mp3_44100_128',
            data=json.dumps({'text': text, 'model_id': MODEL, 'voice_settings': settings}).encode(),
            headers={'xi-api-key': key, 'Content-Type': 'application/json'})
        res = json.load(urllib.request.urlopen(req, timeout=240))
        open(path_base + '.mp3', 'wb').write(base64.b64decode(res['audio_base64']))
        json.dump(res['alignment'], open(path_base + '.json', 'w'))
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', path_base + '.mp3', '-ac', '1', '-ar', str(SR),
                    path_base + '.wav'], check=True)
    x, _ = dsp.read_wav(path_base + '.wav')
    words = [w for w in words_from(json.load(open(path_base + '.json'))) if not TAG_RE.fullmatch(w['w'])]
    return x, words


def level(x, t, w=0.01):
    n = int(w * SR)
    i = int(t * SR)
    return math.sqrt(sum(v * v for v in x[i:i + n]) / n) if i + n < len(x) else 0.0


def peak_level(x):
    return max(level(x, k * 0.01) for k in range(int(len(x) / SR / 0.01) - 1))


def decay_stop(x, end, limit, top):
    """Where the last word's decay stops falling (a breath would rise 3 dB) or reaches silence."""
    t, low = end, level(x, end)
    while t < end + limit:
        nl = level(x, t + 0.01)
        if nl < top * 10 ** (-60 / 20) or nl > low * 10 ** (3 / 20):
            break
        low = min(low, nl)
        t += 0.01
    return max(t, end + 0.05)


def shape(x, words, final):
    """Trim to the speech, shorten only pauses over MAX_PAUSE, keep the end's natural decay."""
    top = peak_level(x)
    s0 = max(0.0, words[0]['start'] - 0.04)
    t = min(len(x) / SR, words[-1]['end'] + 0.5) - 0.01
    while t > words[-1]['start'] and level(x, t) < top * 10 ** (-30 / 20):
        t -= 0.01
    words[-1] = {**words[-1], 'end': round(min(words[-1]['end'], t + 0.01), 3)}
    stop = min(decay_stop(x, words[-1]['end'], FINAL_MAX if final else SECTION_MAX, top), len(x) / SR)
    cut_off = len(x) / SR - stop < 0.02
    keep, cuts, pos = [], [], s0
    for k in range(len(words) - 1):
        gap = words[k + 1]['start'] - words[k]['end']
        if re.search(r'[.?!,]$', words[k]['w']) and gap > MAX_PAUSE:
            a = words[k]['end'] + MAX_PAUSE / 2
            b = words[k + 1]['start'] - MAX_PAUSE / 2
            keep.append((pos, a))
            cuts.append((a, b))
            pos = b
    keep.append((pos, min(len(x) / SR, stop + (FADE_END if final else 0))))
    out, xf = [], int(XF * SR)
    for n_, (a, b) in enumerate(keep):
        seg = x[int(a * SR):int(b * SR)]
        if n_:
            for j in range(xf):
                g = j / xf
                out[-xf + j] = out[-xf + j] * math.cos(g * math.pi / 2) + seg[j] * math.sin(g * math.pi / 2)
            seg = seg[xf:]
        out += seg
    f = int(0.01 * SR)
    for j in range(min(f, len(out))):
        out[j] *= j / f

    def remap(tt):
        sh = s0
        for a, b in cuts:
            if tt >= b:
                sh += b - a - XF
        return tt - sh

    ws = [{'w': w['w'], 'start': round(remap(w['start']), 3), 'end': round(remap(w['end']), 3)} for w in words]
    fo = int((FADE_CUT if cut_off else 0.015) * SR)
    for j in range(min(fo, len(out))):
        out[-1 - j] *= (j / fo) ** 2
    return out, ws, stop - words[-1]['end'], [f'{a:.2f}-{b:.2f}' for a, b in cuts]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('script')
    ap.add_argument('--out', required=True)
    ap.add_argument('--takes', type=int, default=2)
    ap.add_argument('--stability', type=float, default=0.7)
    ap.add_argument('--speed', type=float, default=1.0)
    ap.add_argument('--yes', action='store_true', help='actually spend credits')
    ap.add_argument('--pick', default='', help='overrule the ranking by ear, e.g. "open=2,filter-and-clear=1"')
    ap.add_argument('--reference-pace', type=float, default=None,
                    help='words per second of an approved take; picks the take closest to it in pace')
    a = ap.parse_args()
    if not 0.6 <= a.stability <= 0.75:
        sys.exit('Stability must stay within 0.6 to 0.75 (config/defaults.json).')
    if not 0.94 <= a.speed <= 1.08:
        sys.exit('Speed must stay within 0.94 to 1.08 (config/defaults.json).')
    picks = dict((n, int(k)) for n, k in (p.split('=') for p in a.pick.split(',') if p))
    ref = a.reference_pace or CONFIG_REF_PACE
    sc = json.load(open(a.script))
    for s in sc['sections']:
        check_tags(s['talk'])
    chars = sum(len(s['talk']) for s in sc['sections']) * a.takes
    print(f'{len(sc["sections"])} sections x {a.takes} takes = about {chars:,} characters (about {chars:,} credits).')
    if not a.yes:
        print('Nothing generated. Re-run with --yes once the user has agreed to the cost.')
        return
    os.makedirs(a.out, exist_ok=True)
    key = get_key()
    settings = {'stability': a.stability, 'similarity_boost': 0.75, 'style': 0.0, 'use_speaker_boost': True,
                'speed': a.speed}
    out, words_all, windows, report, prev_tail = [], [], [], [], 0.0
    for si, s in enumerate(sc['sections']):
        final = si == len(sc['sections']) - 1
        cands = []
        for k in range(1, a.takes + 1):
            x, w = fetch(os.path.join(a.out, f'{s["name"]}_take{k}'), sc['voice_id'], s['talk'], settings, key)
            f = finality(x, SR, w)
            fin = (f['end_above_floor_st'] + max(0, f['last_word_db_vs_median'])) if f else 99
            wps = pace(w)
            score = (abs(wps - ref), fin) if ref else (fin,)
            cands.append((score, k, x, w, f))
            report.append(f'{s["name"]} take{k}: pace {wps:.2f} words/s, finality {f}')
        if s['name'] in picks:
            k = picks[s['name']]
            _, k, x, w, _ = next(c for c in cands if c[1] == k)
            how = 'picked by ear'
        else:
            _, k, x, w, _ = min(cands, key=lambda c: c[0])
            how = f'closest to reference pace {ref:.2f}' if ref else 'most finished ending'
        seg, ws, tail, cuts = shape(x, w, final)
        if out:
            out += [0.0] * int(max(0.05, SECTION_GAP - prev_tail) * SR)
        off = len(out) / SR
        out += seg
        prev_tail = tail
        windows.append({'section': s['name'], 'take': k, 'start': round(off, 3), 'end': round(len(out) / SR, 3)})
        words_all += [{'section': s['name'], 'w': v['w'], 'start': round(v['start'] + off, 3),
                       'end': round(v['end'] + off, 3)} for v in ws]
        report.append(f'{s["name"]}: using take{k} ({how}); pause edits: {", ".join(cuts) or "none"}')
    dsp.write_wav(os.path.join(a.out, 'voice_dry.wav'), out, SR)
    treated, info = treat(out, SR)
    tone, info['room_tone'] = room_tone()
    treated = add_room_tone(treated, tone, SR, tone_lufs=-62.0)
    dsp.write_wav(os.path.join(a.out, 'voice.wav'), treated, SR)
    json.dump({'model': MODEL, 'voice_id': sc['voice_id'], 'settings': settings, 'treatment': info,
               'sections': windows, 'words': words_all, 'duration': round(len(out) / SR, 3)},
              open(os.path.join(a.out, 'voice.json'), 'w'), indent=1)
    print('\n'.join(report))


if __name__ == '__main__':
    main()
