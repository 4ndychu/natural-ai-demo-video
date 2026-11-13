"""Measure casual vs scripted demo narration from CrisperWhisper verbatim transcripts plus the audio.

Per video: words/min, fillers (uh, um) per 100 words and per min, repeats, fragments (cut-off words),
unsure moments (self-talk phrases and long mid-clause pauses), pause distribution, breaths and clicks
(acoustic, inside pauses), phrase-to-phrase pace and pitch variation, and action phrasings.

Usage: analyse.py <transcripts dir> <wav dir> <out json> [extra.json: {"name": [json, wav]} to also measure]
"""
import glob
import json
import os
import re
import sys

import numpy as np
import soundfile as sf

SR = 16000
TAG = re.compile(r'^\[([A-Z_ ]+)\]$')
FILL = {'UH': 'uh', 'UM': 'um'}
SELF_TALK = re.compile(r"\b(where (is|was|did|are|'s) (it|that|the)|where'?s (it|that|the)|let'?s see|let me see|"
                       r"hang on|hold on|wait|i think|i guess|i'm not sure|not sure|maybe|probably|"
                       r"i don'?t know|i forget|what (is|was) it|how do (i|you)|oops|whoops|there we go|"
                       r"actually|or something)\b", re.I)
ACTION = re.compile(r"\b(click|clicking|clicked|select|choose|hit|press|type|drag|scroll|open|go (to|into|over|back)|"
                    r"head (to|over)|navigate|tap|toggle|check|uncheck|paste|copy|upload|save)\b", re.I)
ACTION_FRAMES = [
    ('imperative ("click X", "go to X")', re.compile(r"(^|[.!?,]\s*)(now |so |and |then |just |simply )*(click|select|choose|hit|press|type|drag|scroll|open|go|head|navigate|tap|paste|upload|save)\b", re.I)),
    ('"you (can/just/'"'"'ll/want to) X"', re.compile(r"\byou(('ll| will| can| could| just| simply| want to| need to| have to| would| should| 're going to| are going to| gonna)\s*)+(\w+ )?(click|select|choose|hit|press|type|drag|scroll|open|go|head|navigate|tap|see)\b", re.I)),
    ('"I\'m going to / I\'ll / let me X"', re.compile(r"\b(i'm going to|i'm gonna|i am going to|i'll|i will|let me|i want to|i'm just going to)\s+(just\s+)?(\w+\s+)?(click|select|choose|hit|press|type|drag|scroll|open|go|head|show|grab|pull|put|add|copy|paste|run)\b", re.I)),
    ('"let\'s X"', re.compile(r"\blet's\s+(just\s+)?(\w+\s+)?(click|select|choose|hit|press|type|drag|scroll|open|go|head|take|look|see|start|try|add|create|jump|move|check)\b", re.I)),
    ('"we (can/\'ll/\'re going to) X"', re.compile(r"\bwe(('ll| will| can| could| just| want to| need to| 're going to| are going to| 're gonna)\s*)+(\w+ )?(click|select|choose|hit|press|type|drag|scroll|open|go|head|navigate|see|add|create)\b", re.I)),
    ('narrating the result ("and there it is", "now it\'s", "it opens")', re.compile(r"\b(there it is|there we go|here it is|and now (it|we|you)|it'?s (now )?(open|opened|loading|saved|there|done)|that opens|this opens|pops up|shows up)\b", re.I)),
]


def norm(w):
    return re.sub(r"[^a-z0-9'-]", '', w.lower())


def yin_track(x, sr, hop=0.01, win=0.04, fmin=60, fmax=400):
    """Vectorised YIN-ish pitch: returns times and f0 (nan where unvoiced)."""
    n, h = int(win * sr), int(hop * sr)
    tmin, tmax = int(sr / fmax), int(sr / fmin)
    if len(x) < n + tmax:
        return np.array([]), np.array([])
    starts = np.arange(0, len(x) - n - tmax, h)
    f0 = np.full(len(starts), np.nan)
    frames = np.lib.stride_tricks.sliding_window_view(x, n + tmax)[starts]
    energy = (frames[:, :n] ** 2).mean(1)
    gate = np.percentile(energy, 30) * 3
    for i, fr in enumerate(frames):
        if energy[i] < gate:
            continue
        a = fr[:n]
        d = np.array([np.sum((a - fr[t:t + n]) ** 2) for t in range(tmin, tmax)])
        cm = d * np.arange(1, len(d) + 1) / np.maximum(np.cumsum(d), 1e-12)
        k = np.argmin(cm)
        if cm[k] < 0.15:
            f0[i] = sr / (k + tmin)
    return starts / sr + win / 2, f0


def gap_events(x, sr, gaps):
    """Breaths and pre-speech clicks inside silent gaps between words. Measured against the whole file's
    noise floor. Breath: 120-800 ms of aperiodic noise (centroid 0.9-5 kHz, high zero-crossing rate) that is
    above the floor but well below speech. Click: a 2 ms transient > 10x floor that dies within 30 ms, counted
    only in the last 0.6 s before speech resumes (where tongue clicks sit; mouse and keyboard clicks land
    anywhere). Rough: music beds and keyboard noise still leak in."""
    frame = int(0.01 * sr)
    n = len(x) // frame
    fr_all = np.sqrt((x[:n * frame].reshape(n, frame) ** 2).mean(1))
    floor = np.percentile(fr_all, 5) + 1e-6
    speech = np.percentile(fr_all, 80)
    breaths, clicks = [], []
    def periodicity(c):
        c = c - c.mean()
        ac = np.correlate(c, c, 'full')[len(c) - 1:]
        ac = ac / (ac[0] + 1e-12)
        return ac[int(sr / 400):int(sr / 70)].max()
    for s, e in gaps:
        a, b = int(s * sr), int(e * sr)
        seg = x[a:b]
        # breath: trim 60 ms after the word and 40 ms before the next so word tails don't count
        inner = x[int((s + 0.06) * sr):int((e - 0.04) * sr)]
        m = len(inner) // frame
        if m >= 12:
            fr = np.sqrt((inner[:m * frame].reshape(m, frame) ** 2).mean(1))
            hot = (fr > floor * 3) & (fr < speech * 0.5)
            dur = hot.sum() * 0.01
            if 0.12 <= dur <= 0.8:
                idx = np.where(hot)[0]
                chunk = inner[idx[0] * frame:(idx[-1] + 1) * frame][:int(0.5 * sr)]
                spec = np.abs(np.fft.rfft(chunk * np.hanning(len(chunk))))
                freqs = np.fft.rfftfreq(len(chunk), 1 / sr)
                cen = (spec * freqs).sum() / max(spec.sum(), 1e-9)
                if 500 <= cen <= 5000 and len(chunk) > int(0.08 * sr) and periodicity(chunk[:int(0.08 * sr)]) < 0.4:
                    breaths.append(round(s + 0.06 + idx[0] * 0.01, 2))
        if len(seg) < int(0.1 * sr):
            continue
        tail = seg[-int(0.6 * sr):]
        w2 = int(0.002 * sr)
        r2 = np.sqrt(np.convolve(tail ** 2, np.ones(w2) / w2, mode='same'))
        for p in np.where(r2 > floor * 10)[0]:
            after = r2[p + int(0.03 * sr): p + int(0.06 * sr)]
            before = r2[max(0, p - int(0.03 * sr)): max(1, p - int(0.005 * sr))]
            if len(after) and after.mean() < floor * 3 and before.mean() < floor * 3:
                clicks.append(round(e - 0.6 + p / sr, 2))
                break
    return breaths, clicks


def measure(tr, wav):
    words = [w for w in tr['words'] if w['w'].strip()]
    x, sr = sf.read(wav, dtype='float32')
    if x.ndim > 1:
        x = x.mean(1)
    toks = []
    for w in words:
        m = TAG.match(w['w'].strip())
        toks.append({'tag': m.group(1) if m else None, 'w': norm(w['w']), 'raw': w['w'], 's': w['s'], 'e': w['e']})
    lex = [t for t in toks if not t['tag']]
    n = len(lex)
    t0, t1 = toks[0]['s'], toks[-1]['e']
    mins = (t1 - t0) / 60
    tags = {}
    for t in toks:
        if t['tag']:
            tags[t['tag']] = tags.get(t['tag'], 0) + 1
    uh, um = tags.get('UH', 0), tags.get('UM', 0)
    # repeats: the same 1-3 words said twice in a row ("the the", "I'm going I'm going"), fillers ignored
    reps, rep_words, rep_pos = 0, {}, {'clause-start': 0, 'mid': 0}
    i = 0
    while i < len(lex) - 1:
        hit = 0
        for L in (3, 2, 1):
            A, B = [t['w'] for t in lex[i:i + L]], [t['w'] for t in lex[i + L:i + 2 * L]]
            if len(B) == L and A == B and all(A):
                hit = L
                break
        if hit:
            reps += 1
            rep_words[lex[i]['w']] = rep_words.get(lex[i]['w'], 0) + 1
            j = toks.index(lex[i])
            prev = toks[j - 1] if j else None
            start = (prev is None or prev['tag'] or re.search(r'[.,!?;:]$', prev['raw'].strip())
                     or lex[i]['s'] - prev['e'] > 0.25 or prev['w'] in ('and', 'so', 'but', 'then', 'because', 'or'))
            rep_pos['clause-start' if start else 'mid'] += 1
            i += 2 * hit
        else:
            i += 1
    frags = sum(1 for t in lex if t['raw'].strip().rstrip(',.').endswith('-'))
    # pauses between consecutive tokens
    gaps = [(a['e'], b['s']) for a, b in zip(toks, toks[1:]) if b['s'] - a['e'] > 0.0]
    g = np.array([b - a for a, b in gaps]) if gaps else np.array([0.0])
    allg = np.array([max(0.0, b['s'] - a['e']) for a, b in zip(toks, toks[1:])])
    after_punct = [max(0.0, b['s'] - a['e']) for a, b in zip(toks, toks[1:]) if re.search(r'[.!?]$', a['raw'].strip())]
    mid = [max(0.0, b['s'] - a['e']) for a, b in zip(toks, toks[1:]) if not re.search(r'[.,!?;:]$', a['raw'].strip()) and not a['tag'] and not b['tag']]
    filler_gaps = {'uh': [], 'um': []}
    for i, t in enumerate(toks):
        if t['tag'] in FILL and i + 1 < len(toks):
            filler_gaps[FILL[t['tag']]].append(max(0.0, toks[i + 1]['s'] - t['e']))
    long_mid = sum(1 for v in mid if v > 1.0)
    text = ' '.join(t['raw'] for t in lex)
    self_talk = SELF_TALK.findall(text)
    # phrases: split at gaps > 0.3 s; pace and pitch per phrase
    phrases, cur = [], [toks[0]]
    for a, b in zip(toks, toks[1:]):
        if b['s'] - a['e'] > 0.3:
            phrases.append(cur)
            cur = []
        cur.append(b)
    phrases.append(cur)
    rates, med_f0, ranges = [], [], []
    times, f0 = yin_track(x, sr)
    for p in phrases:
        lw = [t for t in p if not t['tag']]
        dur = p[-1]['e'] - p[0]['s']
        if len(lw) >= 4 and dur > 0.6:
            rates.append(len(lw) / dur)
            if len(times):
                sel = f0[(times >= p[0]['s']) & (times <= p[-1]['e'])]
                sel = sel[~np.isnan(sel)]
                if len(sel) >= 10:
                    med_f0.append(np.median(sel))
                    ranges.append(12 * np.log2(np.percentile(sel, 90) / np.percentile(sel, 10)))
    rates = np.array(rates)
    allf = f0[~np.isnan(f0)] if len(times) else np.array([])
    breaths, clicks = gap_events(x, sr, [(a, b) for a, b in gaps if b - a >= 0.15])
    frames = {name: len(rx.findall(text)) for name, rx in ACTION_FRAMES}
    act_sents = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if ACTION.search(s)]
    return {
        'minutes': round(mins, 2), 'words': n, 'wpm': round(n / mins, 1),
        'fillers_per_100w': round((uh + um) / n * 100, 2), 'uh_per_100w': round(uh / n * 100, 2), 'um_per_100w': round(um / n * 100, 2),
        'fillers_per_min': round((uh + um) / mins, 2), 'other_tags': {k: v for k, v in tags.items() if k not in FILL},
        'repeats_per_100w': round(reps / n * 100, 2), 'repeats_per_min': round(reps / mins, 2), 'repeat_words': rep_words, 'repeat_position': rep_pos,
        'fragments_per_100w': round(frags / n * 100, 2),
        'restarts_per_min': round((reps + frags) / mins, 2),
        'self_talk_per_min': round(len(self_talk) / mins, 2), 'self_talk': [s[0].lower() for s in self_talk],
        'long_mid_pauses_per_min': round(long_mid / mins, 2),
        'pause_share_gt200ms': round(float((allg > 0.2).mean()), 3), 'pause_share_gt500ms': round(float((allg > 0.5).mean()), 3),
        'pause_after_sentence_median_s': round(float(np.median(after_punct)), 2) if after_punct else None,
        'sentence_pauses_under_150ms': round(float(np.mean(np.array(after_punct) < 0.15)), 2) if after_punct else None,
        'pause_after_sentence_cv': round(float(np.std(after_punct) / max(np.mean(after_punct), 1e-6)), 2) if len(after_punct) > 2 else None,
        'pause_after_uh_median_s': round(float(np.median(filler_gaps['uh'])), 2) if filler_gaps['uh'] else None,
        'pause_after_um_median_s': round(float(np.median(filler_gaps['um'])), 2) if filler_gaps['um'] else None,
        'phrases': len(rates), 'phrase_rate_median_wps': round(float(np.median(rates)), 2) if len(rates) else None,
        'phrase_rate_cv': round(float(rates.std() / rates.mean()), 3) if len(rates) > 2 else None,
        'phrase_rate_p10_p90': [round(float(np.percentile(rates, 10)), 2), round(float(np.percentile(rates, 90)), 2)] if len(rates) > 2 else None,
        'pitch_range_st_p10_p90': round(float(12 * np.log2(np.percentile(allf, 90) / np.percentile(allf, 10))), 1) if len(allf) > 50 else None,
        'phrase_pitch_range_st_median': round(float(np.median(ranges)), 1) if ranges else None,
        'phrase_to_phrase_pitch_sd_st': round(float(np.std(12 * np.log2(np.array(med_f0) / np.median(med_f0)))), 2) if len(med_f0) > 2 else None,
        'breaths_per_min': round(len(breaths) / mins, 2), 'clicks_per_min': round(len(clicks) / mins, 2),
        'action_frames': frames, 'action_sentences': act_sents[:40],
    }


def main():
    tdir, wdir, out = sys.argv[1:4]
    res = {}
    for p in sorted(glob.glob(os.path.join(tdir, '*.json'))):
        tr = json.load(open(p))
        res[os.path.basename(p)[:-5]] = measure(tr, os.path.join(wdir, tr['id'] + '.wav'))
        print(os.path.basename(p), {k: res[os.path.basename(p)[:-5]][k] for k in ('wpm', 'fillers_per_100w', 'repeats_per_min', 'phrase_rate_cv', 'breaths_per_min', 'clicks_per_min')}, flush=True)
    if len(sys.argv) > 4:
        for name, (tj, wv) in json.load(open(sys.argv[4])).items():
            res[name] = measure(json.load(open(tj)), wv)
            print(name, {k: res[name][k] for k in ('wpm', 'fillers_per_100w', 'repeats_per_min', 'phrase_rate_cv', 'breaths_per_min', 'clicks_per_min')}, flush=True)
    json.dump(res, open(out, 'w'), indent=1)


if __name__ == '__main__':
    main()
