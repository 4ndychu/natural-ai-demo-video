"""NAVI voice treatment. Gentle on purpose: it should make a take sit well, never make it sound processed.

Chain, in order:
1. De-esser on 5 to 8 kHz (split at 5 kHz, detection centred on 6.3 kHz), acting only in the loudest 12 dB, 3:1.
2. High shelf -2.5 dB above 8 kHz.
3. Light compression: 2:1, soft knee 6 dB, threshold -22 dB with the voice at -20 LUFS, 10 ms attack, 150 ms release.
4. Voice level -16.4 LUFS integrated.
5. Look-ahead peak limiter at -2.5 dBFS.

Room tone is added at mix time (see add_room_tone): about -62 LUFS, band-limited to 90 Hz to 2.5 kHz.

Usage: python3 treat.py in.wav out.wav
"""
import json
import sys

import dsp

VO_LUFS, CEILING = -16.4, -2.5


def treat(x, sr):
    y, cut_max, cut_avg = dsp.deess(x, sr, split=5000, band=(6300, 0.8))
    y = dsp.biquad(y, *dsp.high_shelf(8000, -2.5, sr))
    y = dsp.gain(y, -20.0 - dsp.lufs(y, sr))
    y, comp = dsp.compressor(y, sr, thr_db=-22.0, ratio=2.0)
    y = dsp.gain(y, VO_LUFS - dsp.lufs(y, sr))
    for _ in range(2):
        y = dsp.limiter(y, CEILING, sr)
        y = dsp.gain(y, VO_LUFS - dsp.lufs(y, sr))
    y = dsp.limiter(y, CEILING, sr)
    info = {
        'deess': {'band_hz': [5000, 8000], 'range_db': 12, 'ratio': 3,
                  'max_cut_db': round(cut_max, 1), 'avg_cut_db': round(cut_avg, 1)},
        'high_shelf': {'hz': 8000, 'db': -2.5},
        'compressor': {'ratio': 2, 'threshold_db': -22, 'at_level_lufs': -20, 'attack_ms': 10, 'release_ms': 150,
                       'max_reduction_db': round(comp, 1)},
        'limiter_ceiling_db': CEILING,
        'lufs': round(dsp.lufs(y, sr), 1), 'peak_db': round(dsp.peak_db(y), 1),
    }
    return y, info


def add_room_tone(voice, tone, sr, tone_lufs=-62.0, fade_in=0.4):
    """Mix faint room tone under the whole track so gaps never drop to digital silence.
    `tone` is a recording of a quiet room (any length; it loops). It's band-limited to 90 Hz to 2.5 kHz first."""
    t = dsp.biquad(tone, *dsp.hpf(90, sr))
    t = dsp.biquad(t, *dsp.lpf(2500, sr))
    t = dsp.gain(t, tone_lufs - dsp.lufs(t, sr))
    fi = int(fade_in * sr)
    return [v + t[i % len(t)] * min(1.0, i / fi if fi else 1.0) for i, v in enumerate(voice)]


if __name__ == '__main__':
    x, sr = dsp.read_wav(sys.argv[1])
    y, info = treat(x, sr)
    dsp.write_wav(sys.argv[2], y, sr)
    print(json.dumps(info))
