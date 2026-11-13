"""NAVI voice generation: one continuous read per section on ElevenLabs eleven_v3.

The method that won every listening test (see reference/voice-rules.md):
- Each section is ONE request and ONE continuous read. Sentences are never generated separately and stitched,
  and `next_text` is never passed: both make every sentence sound like it's about to carry on.
- 2 takes per section. Pace is a gate (within 15% of the reference pace); among the takes that pass, the one whose last
  sentence ends lowest in the speaker's range and quietest is ranked
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

SR = 44100
CONFIG = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'config', 'defaults.json')))
MODEL = CONFIG['voice']['model']  # eleven_v4 by default; --model eleven_v3 for speed control
HUNT_WORDS = CONFIG['audio_edit'].get('hunt_words', []) if CONFIG['audio_edit'].get('keep_hunt_pauses') else []
MAX_PAUSE = 0.8          # walkthroughs: only silences over 0.8 s are shortened (voice-rules.md, section 4)
FINAL_MAX, SECTION_MAX = 0.45, 0.45  # every section keeps its last word's natural decay
FADE_END, FADE_CUT, XF = 0.08, 0.15, 0.03
SECTION_GAP = 0.40       # the old fixed gap; now one gap per boundary, drawn with the style (0.25 to 0.70 s): gaps()
PACE_GATE = 0.15         # a take is eligible when its pace is within 15% of the reference (pace no longer ranks)
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
    """One take. Reuses an existing take: <base>.json (ElevenLabs alignment) or, for a take made elsewhere,
    <base>.words.json (local word timings, e.g. from scripts/research/transcribe_verbatim.py) next to <base>.mp3."""
    local = os.path.exists(path_base + '.mp3') and os.path.exists(path_base + '.words.json')
    if not local and not os.path.exists(path_base + '.json'):
        key = key or get_key()
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
    if local:
        words = []
        for w in json.load(open(path_base + '.words.json')):
            m = re.fullmatch(r'\[(UH|UM)\]', w['w'].strip())
            word = m.group(1).lower() + ',' if m else w['w']
            if not TAG_RE.fullmatch(word):
                words.append({'w': word, 'start': w['s'], 'end': w['e']})
        return x, words
    words = [w for w in words_from(json.load(open(path_base + '.json'))) if not TAG_RE.fullmatch(w['w'])]
    return x, words


def level(x, t, w=0.01):
    n = int(w * SR)
    i = int(t * SR)
    return math.sqrt(sum(v * v for v in x[i:i + n]) / n) if i + n < len(x) else 0.0


def peak_level(x):
    return max(level(x, k * 0.01) for k in range(int(len(x) / SR / 0.01) - 1))


RELEASE_GRACE = 0.25  # final consonants ("left", "list") release a burst after the vowel: not a breath


def decay_stop(x, end, limit, top):
    """Where the last word's decay reaches silence (-60 dB of the take's peak), or stops falling because a breath
    starts (a 3 dB rise). Rises in the first RELEASE_GRACE seconds are the word's own consonant release, kept."""
    t, low = end, level(x, end)
    while t < end + limit:
        nl = level(x, t + 0.01)
        if nl < top * 10 ** (-60 / 20) or (t > end + RELEASE_GRACE and nl > low * 10 ** (3 / 20)):
            break
        low = min(low, nl)
        t += 0.01
    return max(t, end + 0.05)


def start_breath(x, words):
    """How long the breath after a section's first word is (s), measured from the audio (the alignment stretches
    "Okay," over it): from the first word's voiced end until the next word comes in. 0 when there isn't one.
    Andy, 11 Nov 2026: every section began "Okay" + the same 0.4 s inhale + "so"."""
    if len(words) < 2:
        return 0.0
    top = peak_level(x)
    db = lambda t: 20 * math.log10(max(level(x, t), 1e-9) / max(top, 1e-9))
    # 20 ms frames from the first word to just past where the second word is aligned to start; the breath is the
    # longest run quieter than 14 dB under the peak but louder than 45 dB under it (silence isn't a breath). A dip
    # between the syllables of "O-kay" is far shorter, so the longest run is the breath.
    t0, t1 = words[0]['start'] + 0.1, min(words[1]['start'] + 0.15, words[0]['start'] + 2.0)
    best = run = 0.0
    loud = False
    t = t0
    while t < t1:
        d = db(t)
        if d < -14:
            run += 0.02
            loud = loud or d > -45
        else:
            if loud and run > best:
                best = run
            run, loud = 0.0, False
        t += 0.02
    return round(best, 2) if best >= 0.2 else 0.0


def gaps(script, n):
    """One gap per section boundary: the style's, or drawn from the script (0.25 to 0.70 s, most between 0.3 and 0.5,
    neighbours at least 0.08 s apart). The fixed 0.40 s was the tidy scripted pattern; real pauses are uneven."""
    drawn = list(((script.get('style') or {}).get('gaps')) or [])
    import random
    rnd = random.Random(json.dumps([script.get('title'), [x.get('name') for x in script.get('sections', [])]]))
    while len(drawn) < n:
        for _ in range(20):
            g = round(min(0.70, max(0.25, rnd.triangular(0.25, 0.70, 0.40))), 2)
            if not drawn or abs(g - drawn[-1]) >= 0.08:
                break
        drawn.append(g)
    return drawn[:n]


def shape(x, words, final, protect=(), shorten_start=False):
    """Trim to the speech, shorten only pauses over MAX_PAUSE, keep the end's natural decay. protect: word indexes
    whose pauses are never shortened (a hunt). shorten_start: cut the breath after the first word down to a catch."""
    top = peak_level(x)
    s0 = max(0.0, words[0]['start'] - 0.04)
    t = min(len(x) / SR, words[-1]['end'] + 0.5) - 0.01
    while t > words[-1]['start'] and level(x, t) < top * 10 ** (-45 / 20):  # -45 dB keeps quiet final f, s, t
        t -= 0.01
    words[-1] = {**words[-1], 'end': round(min(words[-1]['end'], t + 0.01), 3)}
    stop = min(decay_stop(x, words[-1]['end'], FINAL_MAX if final else SECTION_MAX, top), len(x) / SR)
    cut_off = len(x) / SR - stop < 0.02
    keep, cuts, pos = [], [], s0
    for k in range(len(words) - 1):
        gap = words[k + 1]['start'] - words[k]['end']
        near = ' '.join(w['w'] for w in words[max(0, k - 2):k + 3]).lower()
        if any(h in near for h in HUNT_WORDS) or any(abs(k - p) <= 3 for p in protect):
            continue  # never shorten a pause at a hunt moment (voice-rules.md, section 4), whatever its wording
        if re.search(r'[.?!,]$', words[k]['w']) and gap > MAX_PAUSE:
            a = words[k]['end'] + MAX_PAUSE / 2
            b = words[k + 1]['start'] - MAX_PAUSE / 2
            keep.append((pos, a))
            cuts.append((a, b))
            pos = b
    if shorten_start and len(words) > 1 and re.search(r',$', words[0]['w']) and not cuts:
        # the one narrow new edit (docs/variety-spec.md 6.3): a section planned to start clean that still breathed after
        # its first word ("Okay, [breath] so"): keep 60 ms each side, cut the middle. Never after a full stop.
        b = start_breath(x, words)
        if b >= 0.2:
            vend = words[1]['start'] - b
            a, bb = vend + 0.06, words[1]['start'] - 0.06
            if bb - a > 0.1 and a > pos:
                keep.append((pos, a))
                cuts.append((a, bb))
                pos = bb
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
    global MODEL
    ap = argparse.ArgumentParser()
    ap.add_argument('script')
    ap.add_argument('--out', required=True)
    ap.add_argument('--takes', type=int, default=2)
    ap.add_argument('--stability', type=float, default=0.7)
    ap.add_argument('--model', default=MODEL, choices=list(CONFIG['voice']['models']))
    ap.add_argument('--speed', type=float, default=None, help='eleven_v3 only (eleven_v4 has no speed setting)')
    ap.add_argument('--yes', action='store_true', help='actually spend credits')
    ap.add_argument('--pick', default='', help='overrule the ranking by ear, e.g. "open=2,filter-and-clear=1"')
    ap.add_argument('--reference-pace', type=float, default=None,
                    help='words per second of an approved take; takes within 15%% of it are eligible, and the most finished ending wins among them')
    a = ap.parse_args()
    if not 0.6 <= a.stability <= 0.75:
        sys.exit('Stability must stay within 0.6 to 0.75 (config/defaults.json).')
    MODEL = a.model
    if not CONFIG['voice']['models'][MODEL]['speed'] and a.speed is not None:
        sys.exit(f'{MODEL} has no speed setting. Leave --speed out, or use --model eleven_v3.')
    if a.speed is None:
        a.speed = 1.0
    if not 0.94 <= a.speed <= 1.08:
        sys.exit('Speed must stay within 0.94 to 1.08 (config/defaults.json).')
    picks = dict((n, int(k)) for n, k in (p.split('=') for p in a.pick.split(',') if p))
    ref = a.reference_pace or CONFIG_REF_PACE
    sc = json.load(open(a.script))
    for s in sc['sections']:
        check_tags(s['talk'])
    # the script checker (Phase 6): no credits are spent on a script with errors
    sys.path.insert(0, os.path.join(HERE, '..', 'script'))
    from check_script import check as check_script
    errors = [i for i in check_script(sc, os.path.dirname(os.path.abspath(a.script))) if i['level'] == 'error']
    if errors:
        sys.exit('The script has problems to fix first (scripts/script/check_script.py):\n'
                 + '\n'.join(f"- {i['section'] or 'script'}: {i['message']}" for i in errors))
    def have(n, k):
        b = os.path.join(a.out, f'{n}_take{k}')
        return os.path.exists(b + '.json') or (os.path.exists(b + '.mp3') and os.path.exists(b + '.words.json'))
    chars = sum(len(s['talk']) for s in sc['sections'] for k in range(1, a.takes + 1) if not have(s['name'], k))
    print(f'{len(sc["sections"])} sections x {a.takes} takes = about {chars:,} characters (about {chars:,} credits).')
    if not a.yes:
        print('Nothing generated. Re-run with --yes once the user has agreed to the cost.')
        return
    os.makedirs(a.out, exist_ok=True)
    key = None
    settings = {'stability': a.stability, 'similarity_boost': 0.75}
    if CONFIG['voice']['models'][MODEL]['speed']:
        settings.update({'style': 0.0, 'use_speaker_boost': True, 'speed': a.speed})
    out, words_all, windows, report, prev_tail = [], [], [], [], 0.0
    style = sc.get('style') or {}
    breathy = set(style.get('breath_sections') or [])         # sections the style lets start with a breath
    boundary = gaps(sc, max(0, len(sc['sections']) - 1))
    prev_breath, breaths = None, []
    for si, s in enumerate(sc['sections']):
        final = si == len(sc['sections']) - 1
        cands = []
        for k in range(1, a.takes + 1):
            x, w = fetch(os.path.join(a.out, f'{s["name"]}_take{k}'), sc['voice_id'], s['talk'], settings, key)
            f = finality(x, SR, w)
            fin = (f['end_above_floor_st'] + max(0, f['last_word_db_vs_median'])) if f else 99
            wps = pace(w)
            br = start_breath(x, w)
            cands.append({'k': k, 'x': x, 'w': w, 'fin': fin, 'wps': wps, 'breath': br})
            report.append(f'{s["name"]} take{k}: pace {wps:.2f} words/s, finality {f}, start breath {br:.2f} s')
        if s['name'] in picks:
            c = next(c for c in cands if c['k'] == picks[s['name']])
            how = 'picked by ear'
        else:
            # pace is a gate, not the ranking (ranking by distance to one approved take made every take alike);
            # among the eligible takes the most finished ending wins; near-ties go to the start that differs
            ok = [c for c in cands if not ref or abs(c['wps'] - ref) <= PACE_GATE * ref] or \
                 [min(cands, key=lambda c: abs(c['wps'] - ref))]
            best = min(ok, key=lambda c: c['fin'])
            want_breath = s['name'] in breathy
            near = [c for c in ok if c['fin'] - best['fin'] <= 1.5]
            pref = lambda c: (0 if (c['breath'] >= 0.2) == want_breath else 1,
                              0 if prev_breath is None or (c['breath'] >= 0.2) != prev_breath else 1, c['fin'])
            c = min(near, key=pref)
            how = (f'pace within {int(PACE_GATE * 100)}% of {ref:.2f}, ' if ref else '') + 'most finished ending' + \
                  (', start chosen for variety' if c is not best else '')
        k, x, w = c['k'], c['x'], c['w']
        clean = s['name'] not in breathy
        trims = sum(1 for b in breaths if b.get('trimmed'))
        seg, ws, tail, cuts = shape(x, w, final, protect=hunt_indexes(s, w),
                                    shorten_start=clean and c['breath'] >= 0.2 and trims < len(sc['sections']) / 2)
        after = start_breath(seg, ws) if c['breath'] >= 0.2 else 0.0
        breaths.append({'section': s['name'], 'breath': c['breath'], 'trimmed': bool(c['breath'] >= 0.2 and after < c['breath'])})
        prev_breath = (after if c['breath'] >= 0.2 else 0.0) >= 0.2
        if out:
            out += [0.0] * int(max(0.05, boundary[si - 1] - prev_tail) * SR)
        off = len(out) / SR
        out += seg
        prev_tail = tail
        windows.append({'section': s['name'], 'take': k, 'start': round(off, 3), 'end': round(len(out) / SR, 3),
                        'start_breath_s': breaths[-1]['breath'], 'start_breath_trimmed': breaths[-1]['trimmed'],
                        'gap_before_s': boundary[si - 1] if si else None})
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
    # the history of finished scripts, so the next video can't repeat this one (scripts/script/variety.py)
    import variety
    variety.record(sc, extra={'start_breath': [b['breath'] for b in breaths], 'gaps': boundary})
    many = [b['section'] for b in breaths if b['breath'] >= 0.2 and not b['trimmed']]
    if len(many) > (1 if len(breaths) <= 4 else len(breaths) // 3):
        report.append(f'start-breath (warning): {len(many)} sections still start with a breath ({", ".join(many)}): reword their first words.')
    print('\n'.join(report))


def hunt_indexes(section, words):
    """Word indexes of the cue words of the section's hunt actions: their pauses are never shortened, whatever the
    hunt's wording (the old hunt_words list only protected the exact phrases in it)."""
    out = []
    norm = lambda t: re.sub(r"[^\w']", '', t.lower())
    for a in section.get('actions', []):
        if a.get('kind') != 'hunt' or not a.get('on'):
            continue
        cue = norm(a['on'].split()[0])
        out += [i for i, w in enumerate(words) if norm(w['w']) == cue]
    return out


if __name__ == '__main__':
    main()
