"""Compare two recordings of the same clip: frame timing, smoothness, cursor and click timing.

Made for the focus check (recording-rules.md rule 22): the same clip recorded with the browser in front and in the
background must come out the same. Reads each recording folder's report.json, take/take.json and silent.mp4.

Usage: .venv/bin/python scripts/focus/compare_takes.py <recording A> <recording B> [--labels "In front" "Background"]
Prints a markdown table; exits 1 if B is worse than A beyond the noise allowances below.
"""
import json
import re
import os
import statistics as st
import subprocess
import sys

# How much worse B may measure before it counts as worse: run-to-run noise, measured between two takes made the same
# way. Anything beyond these fails.
FF = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '.venv', 'bin', 'ffmpeg')
ALLOW = {'fps': 2.0, 'gap_p95_ms': 8, 'gap_max_ms': 50, 'long_gaps': 2, 'late_start_ms': 15, 'off_ms': 40,
         'repaint_ms': 40, 'dup_frames': 3, 'travel_ms': 30}


def load(d):
    rep = json.load(open(os.path.join(d, 'report.json')))
    take = json.load(open(os.path.join(d, 'take', 'take.json')))
    return rep, take


def pct(xs, p):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(round(p / 100 * (len(xs) - 1))))] if xs else 0


def moving_spans(take):
    """When something on screen moves: cursor travel up to the action, and 0.6 s after it (the page reacting)."""
    out = []
    for s in take['steps']:
        if 'travelStart' in s:
            out.append((s['travelStart'], s.get('actionAt', s['end']) + 0.6))
        elif 'actionAt' in s:
            out.append((s['actionAt'], s['end'] + 0.6))
    return out


def frame_stats(take):
    ts = [t for t, _ in take['source']['frames']]
    gaps = [(b - a) * 1000 for a, b in zip(ts, ts[1:])]
    spans = moving_spans(take)
    mg = [(b - a) * 1000 for a, b in zip(ts, ts[1:]) if any(s <= a and b <= e for s, e in spans)]
    dur = ts[-1] - ts[0]
    moving_s = sum(e - s for s, e in spans)
    moving_frames = sum(1 for t in ts if any(s <= t <= e for s, e in spans))
    return {'frames': len(ts), 'fps_moving': moving_frames / moving_s if moving_s else 0,
            'gap_p50_ms': pct(mg, 50), 'gap_p95_ms': pct(mg, 95), 'gap_max_ms': max(mg) if mg else 0,
            'long_gaps': sum(1 for g in mg if g > 50), 'dur': dur}


def repaint(take):
    """After each click, type or press: how long until the page's next new frame (how fast the page responded)."""
    ts = [t for t, _ in take['source']['frames']]
    out = []
    for s in take['steps']:
        a = s.get('actionAt')
        if a is None:
            continue
        nxt = [t for t in ts if t > a]
        if nxt:
            out.append((nxt[0] - a) * 1000)
    return out


def dup_frames(video, spans):
    """Frames of the finished video identical to the one before while something should be moving (stutter)."""
    r = subprocess.run([FF, '-v', 'info', '-i', video, '-f', 'framemd5', '-'], capture_output=True, text=True)
    md5 = [l.split(',')[-1].strip() for l in r.stdout.splitlines() if l and not l.startswith('#')]
    m = re.search(r'([\d.]+) fps', r.stderr)
    fps = float(m.group(1)) if m else 60.0
    dups = 0
    for i in range(1, len(md5)):
        t = i / fps
        if md5[i] == md5[i - 1] and any(s <= t <= e for s, e in spans):
            dups += 1
    return dups, len(md5), fps


def summarize(d):
    rep, take = load(d)
    p = min(rep['passes'], key=lambda x: x['worst_off_s'])  # the pass record.py kept as take/
    rows = p['rows']
    fs = frame_stats(take)
    rp = repaint(take)
    spans = moving_spans(take)  # the video runs on the take's clock
    dups, nframes, vfps = dup_frames(os.path.join(d, 'silent.mp4'), spans)
    travel = [(s['actionAt'] - s['travelStart']) * 1000 for s in take['steps'] if 'travelStart' in s and 'actionAt' in s]
    shapes = [tuple(c for _, c in s.get('cursorShapes', [])) for s in take['steps']]
    return {
        'passes': len(rep['passes']), 'checks': rep['checks']['pass'],
        'fps_moving': fs['fps_moving'], 'frames': fs['frames'], 'gap_p50_ms': fs['gap_p50_ms'], 'gap_p95_ms': fs['gap_p95_ms'],
        'gap_max_ms': fs['gap_max_ms'], 'long_gaps': fs['long_gaps'],
        'late_start_ms': max(abs(r.get('late_start', 0)) for r in rows) * 1000,
        'off_mean_ms': st.mean(abs(r['off']) for r in rows) * 1000, 'off_worst_ms': max(abs(r['off']) for r in rows) * 1000,
        'repaint_p50_ms': pct(rp, 50), 'repaint_max_ms': max(rp) if rp else 0,
        'dup_frames': dups, 'video_frames': nframes, 'video_fps': vfps,
        'travel_mean_ms': st.mean(travel) if travel else 0, 'shapes': shapes,
        'source': rep.get('polish', {}).get('source'),
    }


def main():
    a, b = sys.argv[1], sys.argv[2]
    la, lb = (sys.argv[sys.argv.index('--labels') + 1], sys.argv[sys.argv.index('--labels') + 2]) if '--labels' in sys.argv else ('A', 'B')
    A, B = summarize(a), summarize(b)
    lines = [f'| | {la} | {lb} | B worse? |', '|---|---|---|---|']
    worse = []

    def row(name, k, fmt, higher_bad, allow):
        va, vb = A[k], B[k]
        bad = (vb - va > allow) if higher_bad else (va - vb > allow)
        if bad:
            worse.append(name)
        lines.append(f"| {name} | {fmt.format(va)} | {fmt.format(vb)} | {'**yes**' if bad else 'no'} |")

    row('Page frames per second while moving', 'fps_moving', '{:.1f}', False, ALLOW['fps'])
    row('Frame gap while moving, typical (ms)', 'gap_p50_ms', '{:.1f}', True, ALLOW['gap_p95_ms'])
    row('Frame gap while moving, 95th pct (ms)', 'gap_p95_ms', '{:.1f}', True, ALLOW['gap_p95_ms'])
    row('Longest frame gap while moving (ms)', 'gap_max_ms', '{:.0f}', True, ALLOW['gap_max_ms'])
    row('Frame gaps over 50 ms while moving', 'long_gaps', '{}', True, ALLOW['long_gaps'])
    row('Repeated frames in the video while moving', 'dup_frames', '{}', True, ALLOW['dup_frames'])
    row('Page response after an action, typical (ms)', 'repaint_p50_ms', '{:.0f}', True, ALLOW['repaint_ms'])
    row('Page response after an action, slowest (ms)', 'repaint_max_ms', '{:.0f}', True, ALLOW['repaint_ms'] * 2)
    row('Cursor travel time, average (ms)', 'travel_mean_ms', '{:.0f}', True, ALLOW['travel_ms'])
    row('Scheduler lateness, worst (ms)', 'late_start_ms', '{:.0f}', True, ALLOW['late_start_ms'])
    row('Action vs its word, average (ms)', 'off_mean_ms', '{:.0f}', True, ALLOW['off_ms'])
    row('Action vs its word, worst (ms)', 'off_worst_ms', '{:.0f}', True, ALLOW['off_ms'] * 2)
    same_shapes = A['shapes'] == B['shapes']
    if not same_shapes:
        worse.append('cursor shapes')
    lines.append(f"| Cursor shapes along every move | {len(A['shapes'])} steps | {'identical' if same_shapes else 'different'} | {'no' if same_shapes else '**yes**'} |")
    lines.append(f"| Passes needed / join checks | {A['passes']} / {'pass' if A['checks'] else 'FAIL'} | {B['passes']} / {'pass' if B['checks'] else 'FAIL'} | "
                 f"{'**yes**' if A['checks'] and not B['checks'] else 'no'} |")
    if A['checks'] and not B['checks']:
        worse.append('join checks')
    lines.append(f"| Browser frames / video | {A['source']} / {A['video_frames']} at {A['video_fps']:.0f} fps | {B['source']} / {B['video_frames']} at {B['video_fps']:.0f} fps | |")
    print('\n'.join(lines))
    print(f"\n**{'B is worse: ' + ', '.join(worse) if worse else 'B is no worse than A on any measure'}**")
    sys.exit(1 if worse else 0)


if __name__ == '__main__':
    main()
