"""Does a sentence sound finished? Two cues listeners use:
1. Pitch lands near the bottom of the speaker's range: the back of the last word vs the 10th percentile of the
   whole sentence's pitch (semitones above the floor). A continuation tone stays up in the middle.
2. Energy drains: the last word's loudness vs the sentence's median word (dB).
Usage: python3 finality.py <take.wav> [...]  (alignment .json next to each .wav; break tags ignored)"""
import json, math, sys
import dsp


def words_from(al, n_chars=None):
    keys = ('characters', 'character_start_times_seconds', 'character_end_times_seconds')
    chars, st, en = (al[k][:n_chars] if n_chars else al[k] for k in keys)
    if n_chars is None:  # drop a trailing break tag if present
        txt = ''.join(chars); cut = txt.find(' <break')
        if cut > 0: chars, st, en = chars[:cut], st[:cut], en[:cut]
    words, cur = [], None
    for ch, s, e in zip(chars, st, en):
        if ch.isspace():
            if cur: words.append(cur); cur = None
            continue
        if cur is None: cur = {'w': ch, 'start': s, 'end': e}
        else: cur['w'] += ch; cur['end'] = e
    if cur: words.append(cur)
    return words


def median(v):
    v = sorted(v); n = len(v)
    return (v[n // 2] + v[(n - 1) // 2]) / 2 if n else None


def clean(track):
    out = []
    for i, (t, f) in enumerate(track):
        m = median([g for _, g in track[max(0, i - 3):i + 4]])
        if abs(12 * math.log2(f / m)) <= 4: out.append((t, f))
    return out


def finality(x, sr, words):
    a, b = max(0, int((words[0]['start'] - 0.02) * sr)), min(len(x), int((words[-1]['end'] + 0.12) * sr))
    tr = clean([(t + a / sr, f) for t, f in dsp.yin(x[a:b], sr, fmin=50) if f])
    if len(tr) < 8: return None
    fs = sorted(f for _, f in tr); floor = fs[len(fs) // 10]
    last = words[-1]
    lw = [(t, f) for t, f in tr if last['start'] <= t <= last['end'] + 0.08]
    if len(lw) < 3:
        # eleven_v3's timings drift late at the end of a take, so the reported last word can sit on silence.
        # Fall back to the last unbroken voiced run in the audio (3+ frames, gaps under 30 ms).
        runs, run = [], tr[:1]
        for p, q in zip(tr, tr[1:]):
            if q[0] - p[0] <= 0.03: run.append(q)
            else: runs.append(run); run = [q]
        runs.append(run)
        runs = [r for r in runs if len(r) >= 3]
        if not runs: return None
        lw = runs[-1]
    back = median([f for _, f in lw[len(lw) * 3 // 5:]])
    rms = lambda w: math.sqrt(sum(v * v for v in x[int(w['start'] * sr):int(w['end'] * sr)]) / max(1, int((w['end'] - w['start']) * sr)))
    word_db = [20 * math.log10(max(1e-9, rms(w))) for w in words]
    return {'end_above_floor_st': round(12 * math.log2(back / floor), 1), 'floor_hz': round(floor), 'end_hz': round(back),
            'last_word_db_vs_median': round(word_db[-1] - median(word_db), 1)}


if __name__ == '__main__':
    for p in sys.argv[1:]:
        x, sr = dsp.read_wav(p)
        print(p.split('/')[-1], finality(x, sr, words_from(json.load(open(p[:-4] + '.json')))))
