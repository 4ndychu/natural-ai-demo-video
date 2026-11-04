"""Small pure-Python audio toolkit: WAV I/O, biquads, BS.1770 loudness, de-esser, limiter.
Mono float lists at 44.1 kHz unless stated."""
import array, math, wave
from collections import deque

SR = 44100


def read_wav(path):
    w = wave.open(path)
    sr, ch, n = w.getframerate(), w.getnchannels(), w.getnframes()
    a = array.array('h', w.readframes(n)); w.close()
    if ch > 1:
        a = [sum(a[i:i + ch]) / ch for i in range(0, len(a), ch)]
    return [v / 32768 for v in a], sr


def write_wav(path, x, sr=SR):
    o = wave.open(path, 'wb'); o.setnchannels(1); o.setsampwidth(2); o.setframerate(sr)
    o.writeframes(array.array('h', (max(-32768, min(32767, round(v * 32767))) for v in x)).tobytes()); o.close()


def biquad(x, b, a):
    b0, b1, b2 = (v / a[0] for v in b); a1, a2 = a[1] / a[0], a[2] / a[0]
    y, x1, x2, y1, y2 = [0.0] * len(x), 0.0, 0.0, 0.0, 0.0
    for i, v in enumerate(x):
        o = b0 * v + b1 * x1 + b2 * x2 - a1 * y1 - a2 * y2
        x2, x1, y2, y1 = x1, v, y1, o
        y[i] = o
    return y


def _w(fc, sr, q):
    w0 = 2 * math.pi * fc / sr
    return math.cos(w0), math.sin(w0) / (2 * q)


def hpf(fc, sr=SR, q=0.7071):
    c, al = _w(fc, sr, q)
    return [(1 + c) / 2, -(1 + c), (1 + c) / 2], [1 + al, -2 * c, 1 - al]


def lpf(fc, sr=SR, q=0.7071):
    c, al = _w(fc, sr, q)
    return [(1 - c) / 2, 1 - c, (1 - c) / 2], [1 + al, -2 * c, 1 - al]


def bpf(fc, sr=SR, q=1.0):
    c, al = _w(fc, sr, q)
    return [al, 0, -al], [1 + al, -2 * c, 1 - al]


def high_shelf(fc, gain_db, sr=SR, q=0.7071):
    A = 10 ** (gain_db / 40); c, al = _w(fc, sr, q); s = 2 * math.sqrt(A) * al
    return ([A * ((A + 1) + (A - 1) * c + s), -2 * A * ((A - 1) + (A + 1) * c), A * ((A + 1) + (A - 1) * c - s)],
            [(A + 1) - (A - 1) * c + s, 2 * ((A - 1) - (A + 1) * c), (A + 1) - (A - 1) * c - s])


# ---- ITU-R BS.1770 loudness (K-weighting, 400 ms blocks, gating) ----
def _kweight(x, sr):
    x = biquad(x, *high_shelf(1681.9744509555319, 3.99984385397, sr, 0.7071752369554193))
    return biquad(x, *hpf(38.13547087613982, sr, 0.5003270373253953))


def _blocks(x, sr, win=0.4, hop=0.1):
    k = _kweight(x, sr); n, h = int(win * sr), int(hop * sr)
    sq = [v * v for v in k]; out, s = [], sum(sq[:n])
    for st in range(0, len(sq) - n + 1, h):
        if st: s = s - sum(sq[st - h:st]) + sum(sq[st + n - h:st + n])
        out.append(s / n)
    return out


def lufs(x, sr=SR):
    """Integrated loudness (mono; a stereo mix of identical channels reads +3 dB as stereo)."""
    z = _blocks(x, sr)
    L = lambda m: -0.691 + 10 * math.log10(m) if m > 0 else -200
    g = [m for m in z if L(m) > -70]
    if not g: return -200
    rel = L(sum(g) / len(g)) - 10
    g2 = [m for m in g if L(m) > rel]
    return L(sum(g2) / len(g2))


def momentary_max(x, sr=SR):
    z = _blocks(x, sr)
    return max((-0.691 + 10 * math.log10(m)) for m in z if m > 0) if z else -200


def peak_db(x):
    p = max(abs(v) for v in x)
    return 20 * math.log10(p) if p else -200


def true_peak_db(x):
    """4x oversampled peak (linear interpolation of a windowed-sinc would be closer; cubic is close enough here)."""
    p = 0.0
    for i in range(1, len(x) - 2):
        a, b, c, d = x[i - 1], x[i], x[i + 1], x[i + 2]
        for t in (0.25, 0.5, 0.75):
            v = b + 0.5 * t * (c - a + t * (2 * a - 5 * b + 4 * c - d + t * (3 * (b - c) + d - a)))
            if abs(v) > p: p = abs(v)
        if abs(b) > p: p = abs(b)
    return 20 * math.log10(p) if p else -200


def gain(x, db):
    g = 10 ** (db / 20)
    return [v * g for v in x]


def envelope(x, sr, attack, release):
    ca, cr = math.exp(-1 / (attack * sr)), math.exp(-1 / (release * sr))
    e, out = 0.0, [0.0] * len(x)
    for i, v in enumerate(x):
        a = abs(v); c = ca if a > e else cr
        e = c * e + (1 - c) * a; out[i] = e
    return out


def deess(x, sr=SR, split=5500, band=(7000, 1.2), range_db=12, ratio=3.0, max_cut=8.0):
    """Split-band de-esser: only the highs above `split` are turned down, and only while
    sibilant energy (band around 7 kHz) sits in its top `range_db` dB. Returns (out, max_cut, avg_cut_when_active)."""
    hi = biquad(x, *hpf(split, sr))
    det = envelope(biquad(x, *bpf(band[0], sr, band[1])), sr, 0.001, 0.06)
    top = max(det) or 1e-9; thr = 20 * math.log10(top) - range_db
    out, cuts = [0.0] * len(x), []
    for i, v in enumerate(x):
        d = 20 * math.log10(det[i]) if det[i] > 0 else -200
        cut = min(max_cut, max(0.0, (d - thr) * (1 - 1 / ratio)))
        if cut > 0.05: cuts.append(cut)
        out[i] = v + hi[i] * (10 ** (-cut / 20) - 1)
    return out, (max(cuts) if cuts else 0), (sum(cuts) / len(cuts) if cuts else 0)


def limiter(x, ceiling_db=-3.0, sr=SR, look=0.005):
    """Look-ahead peak limiter: per-sample required gain, sliding minimum over +-look, then a moving average."""
    c = 10 ** (ceiling_db / 20); L = max(1, int(look * sr)); n = len(x)
    req = [min(1.0, c / abs(v)) if v else 1.0 for v in x]
    mn, dq = [1.0] * n, deque()
    for i in range(n + L):  # sliding min over window [i-2L, i] assigned to centre i-L
        if i < n:
            while dq and req[dq[-1]] >= req[i]: dq.pop()
            dq.append(i)
        while dq and dq[0] < i - 2 * L: dq.popleft()
        j = i - L
        if 0 <= j < n and dq: mn[j] = req[dq[0]]
    # Centred moving average of the minimum: smooth, and still <= the required gain at each peak.
    out, half, pre = [0.0] * n, L // 2, [0.0]
    for v in mn: pre.append(pre[-1] + v)
    for i in range(n):
        a, b = max(0, i - half), min(n, i + half + 1)
        out[i] = x[i] * min(mn[i] if b - a <= 1 else (pre[b] - pre[a]) / (b - a), 1.0)
    return out


def yin(x, sr=SR, fmin=70, fmax=320, hop=0.01, frame=0.04, thresh=0.15):
    """F0 track via YIN on an 8 kHz copy. Returns [(time_s, f0_hz or None)]."""
    y = biquad(biquad(x, *lpf(3000, sr)), *lpf(3000, sr))
    step = sr / 8000.0
    d8 = [y[int(i * step)] for i in range(int(len(y) / step))]
    fs, n, h = 8000, int(frame * 8000), int(hop * 8000)
    tmin, tmax = int(fs / fmax), int(fs / fmin) + 1
    peak = max((abs(v) for v in d8), default=0) or 1e-9
    out = []
    for st in range(0, len(d8) - n - tmax, h):
        seg = d8[st:st + n + tmax]
        if max(abs(v) for v in seg[:n]) < 0.03 * peak:
            out.append((st / fs + frame / 2, None)); continue
        d = [0.0] * (tmax + 1); run = 0.0
        for tau in range(1, tmax + 1):
            s = 0.0
            for j in range(n):
                e = seg[j] - seg[j + tau]; s += e * e
            run += s
            d[tau] = s * tau / run if run else 1.0
        # first local minimum under the threshold within range, else the global minimum
        cand = None
        for tau in range(tmin, tmax):
            if d[tau] < thresh and d[tau] <= d[tau + 1]:
                cand = tau; break
        if cand is None:
            cand = min(range(tmin, tmax + 1), key=lambda k: d[k])
            if d[cand] > 0.35:
                out.append((st / fs + frame / 2, None)); continue
        # parabolic interpolation
        if 1 <= cand < tmax:
            a, b, c = d[cand - 1], d[cand], d[cand + 1]
            den = a - 2 * b + c
            cand = cand + (0.5 * (a - c) / den if den else 0)
        out.append((st / fs + frame / 2, fs / cand))
    return out


def compressor(x, sr=SR, thr_db=-22.0, ratio=2.0, attack=0.010, release=0.150, knee_db=6.0):
    """Gentle feed-forward compressor (soft knee). Returns (out, max_reduction_db)."""
    env = envelope(x, sr, attack, release)
    out, most = [0.0] * len(x), 0.0
    for i, v in enumerate(x):
        lvl = 20 * math.log10(env[i]) if env[i] > 1e-9 else -200
        over = lvl - thr_db
        if over <= -knee_db / 2: red = 0.0
        elif over >= knee_db / 2: red = over * (1 - 1 / ratio)
        else: red = (1 - 1 / ratio) * (over + knee_db / 2) ** 2 / (2 * knee_db)
        most = max(most, red)
        out[i] = v * 10 ** (-red / 20)
    return out, most
