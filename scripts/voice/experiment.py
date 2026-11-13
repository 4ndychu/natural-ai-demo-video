"""Small voice experiments: several wordings or settings, N takes each, ranked by measure_speech.py, best take per
variant copied out under a blind label for listening.

Input JSON: {"name": "...", "takes": 2, "voice_id": "...",
             "experiments": {"E1": {"about": "...", "variants": [{"id": "a", "text": "[relaxed] ...",
                                     "model": "eleven_v3", "stability": 0.7, "speed": 1.0, "reuse": "<path to take>"}]}}}
"speed" is left out for eleven_v4 (no speed setting). "reuse" points at existing take files (<base>_take1.mp3...)
instead of generating, for comparing against takes made earlier with the same text and settings.

Usage: experiment.py exp.json --out output/experiments/<name> [--yes]
Without --yes it prints the character count and stops. Takes are cached by model, text and settings, so re-running
never pays twice. Ranking runs locally (CrisperWhisper verbatim transcript + measure_speech.py).
"""
import argparse
import base64
import difflib
import hashlib
import json
import os
import random
import re
import shutil
import subprocess
import sys
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'research'))
os.environ['PATH'] = os.path.dirname(sys.executable) + os.pathsep + os.environ.get('PATH', '')
TAG_RE = re.compile(r'\[[^\]]+\]')


def get_key():
    r = subprocess.run(['security', 'find-generic-password', '-s', 'navi-elevenlabs', '-w'], capture_output=True, text=True)
    key = os.environ.get('NAVI_ELEVENLABS_KEY') or (r.stdout.strip() if r.returncode == 0 else '')
    if not key:
        sys.exit('No ElevenLabs key in the Keychain (service "navi-elevenlabs").')
    return key


def settings_for(v):
    s = {'stability': v.get('stability', 0.7), 'similarity_boost': 0.75}
    if not v.get('model', 'eleven_v3').startswith('eleven_v4'):
        s.update({'style': 0.0, 'use_speaker_boost': True, 'speed': v.get('speed', 1.0)})
    return s


def take_base(out, v, k):
    h = hashlib.sha1(json.dumps([v.get('model', 'eleven_v3'), v['text'], settings_for(v)], sort_keys=True).encode()).hexdigest()[:10]
    return os.path.join(out, 'takes', f'{h}_take{k}')


def fetch(base, voice_id, v, key):
    if os.path.exists(base + '.mp3'):
        return 'cached'
    body = {'text': v['text'], 'model_id': v.get('model', 'eleven_v3'), 'voice_settings': settings_for(v)}
    url = f'https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/with-timestamps?output_format=mp3_44100_128'
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers={'xi-api-key': key, 'Content-Type': 'application/json'})
    try:
        res = json.load(urllib.request.urlopen(req, timeout=240))
        audio = base64.b64decode(res['audio_base64'])
    except urllib.error.HTTPError as e:
        msg = e.read()[:400].decode(errors='replace')
        if e.code in (400, 422) and 'timestamp' in msg.lower():  # model without timestamps: plain endpoint
            req = urllib.request.Request(url.replace('/with-timestamps', ''), data=json.dumps(body).encode(),
                                         headers={'xi-api-key': key, 'Content-Type': 'application/json'})
            audio = urllib.request.urlopen(req, timeout=240).read()
        else:
            raise SystemExit(f'ElevenLabs refused {v.get("model")} (HTTP {e.code}): {msg}')
    open(base + '.mp3', 'wb').write(audio)
    return 'new'


def words_of(text):
    t = TAG_RE.sub(' ', text).lower().replace('-', ' ')
    t = re.sub(r'\b(uh|um)\b', lambda m: ' ' + m.group(1) + ' ', t)
    return re.sub(r"[^a-z' ]", ' ', t).split()


def heard_words(tr):
    out = []
    for w in tr['words']:
        m = re.fullmatch(r'\[(UH|UM)\]', w['w'].strip())
        out += [m.group(1).lower()] if m else words_of(w['w'])
    return out


def score(m, fidelity, kind):
    """Lower is better. Fidelity first (did it say what was written, fillers and repeats included), then the
    research targets: flatter inside a phrase, slower instruction lines, more phrase-to-phrase variation,
    breaths and clicks kept."""
    s = (1 - fidelity) * 10
    sw = m.get('phrase_pitch_range_st_median')
    if sw is not None and sw > 5.3:
        s += (sw - 5.3) / 2
    r = m.get('phrase_rate_median_wps')
    if r is not None and r > 3.8:
        s += (r - 3.8)
    if kind == 'section':
        cv = m.get('phrase_rate_cv')
        if cv is not None and cv < 0.25:
            s += (0.25 - cv) * 10
        pv = m.get('phrase_to_phrase_pitch_sd_st')
        if pv is not None and pv < 2.35:
            s += (2.35 - pv)
    s -= 0.2 * min(3, m.get('breaths_per_min', 0) * m['minutes']) + 0.2 * min(2, m.get('clicks_per_min', 0) * m['minutes'])
    return round(s, 2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('spec')
    ap.add_argument('--out', required=True)
    ap.add_argument('--yes', action='store_true')
    a = ap.parse_args()
    spec = json.load(open(a.spec))
    takes = spec.get('takes', 2)
    os.makedirs(os.path.join(a.out, 'takes'), exist_ok=True)
    todo, chars = [], 0
    for eid, e in spec['experiments'].items():
        for v in e['variants']:
            for k in range(1, takes + 1):
                base = v['reuse'] + f'_take{k}' if v.get('reuse') else take_base(a.out, v, k)
                if not v.get('reuse') and not os.path.exists(base + '.mp3'):
                    chars += len(v['text'])
                todo.append((eid, v, k, base))
    print(f'{len(todo)} takes, {chars:,} characters still to generate (about {chars:,} credits at most).')
    if not a.yes:
        print('Nothing generated. Re-run with --yes once the user has agreed to the cost.')
        return
    key = get_key() if chars else None
    for eid, v, k, base in todo:
        if not v.get('reuse'):
            print(eid, v['id'], f'take{k}', fetch(base, spec['voice_id'], v, key), flush=True)
    # local ranking: verbatim transcript + measurements
    from measure_speech import measure
    from crisperwhisper import CrisperWhisperModel
    model = CrisperWhisperModel('nyralabs/CrisperWhisper2.0_medium', backend='transformers', device='cpu', compute_type='float32')
    results = {}
    for eid, v, k, base in todo:
        wav16 = os.path.join(a.out, 'takes', os.path.basename(base) + '.16k.wav')
        trj = wav16[:-4] + '.verbatim.json'
        if not os.path.exists(wav16):
            subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', base + '.mp3', '-ac', '1', '-ar', '16000', wav16], check=True)
        if not os.path.exists(trj):
            r = model.transcribe(wav16, language='en', word_timestamps=True)
            json.dump({'id': os.path.basename(base), 'duration': r.duration, 'text': r.text,
                       'words': [{'w': w.word, 's': w.start, 'e': w.end} for w in r.words]}, open(trj, 'w'))
        tr = json.load(open(trj))
        m = measure(tr, wav16)
        fid = difflib.SequenceMatcher(None, words_of(v['text']), heard_words(tr)).ratio()
        results.setdefault(eid, {}).setdefault(v['id'], []).append(
            {'take': k, 'file': base + '.mp3', 'heard': tr['text'], 'fidelity': round(fid, 3),
             'score': score(m, fid, spec['experiments'][eid].get('kind', 'line')),
             'metrics': {x: m[x] for x in ('minutes', 'wpm', 'phrase_rate_median_wps', 'phrase_rate_cv',
                                           'phrase_pitch_range_st_median', 'phrase_to_phrase_pitch_sd_st',
                                           'pause_share_gt200ms', 'long_mid_pauses_per_min', 'breaths_per_min',
                                           'clicks_per_min', 'fillers_per_100w', 'repeats_per_min')}})
        print(eid, v['id'], f'take{k}', 'score', results[eid][v['id']][-1]['score'], '| heard:', tr['text'][:90], flush=True)
    # best take per variant, blind labels per experiment
    listen = os.path.join(a.out, 'listen')
    shutil.rmtree(listen, ignore_errors=True)
    os.makedirs(listen)
    key_map = {}
    rnd = random.Random(hash(a.out) & 0xffff)
    for eid, vs in results.items():
        ids = list(vs)
        labels = [chr(ord('A') + i) for i in range(len(ids))]
        rnd.shuffle(labels)
        for vid, lab in zip(ids, labels):
            best = min(vs[vid], key=lambda t: t['score'])
            dst = os.path.join(listen, f'{eid}-{lab}.mp3')
            shutil.copy(best['file'], dst)
            key_map[f'{eid}-{lab}'] = {'variant': vid, 'take': best['take'], 'score': best['score']}
    json.dump(results, open(os.path.join(a.out, 'results.json'), 'w'), indent=1)
    json.dump(key_map, open(os.path.join(a.out, 'blind_key.json'), 'w'), indent=1)
    print('Blind files in', listen)


if __name__ == '__main__':
    main()
