"""Phase 4 check (docs/BUILD_BRIEF.md): a page seeded with fake emails, money figures and fake API keys.
Tier 1 must always be blurred, tier 2 blurred by default, and nothing may leak when the camera zooms or scrolls.

Records examples/privacy-test/ live (no voice, no credits): hover the avatar, click "Reveal key" (a key appears),
type an email, scroll to the invoice image and the customer table, scroll back. Runs the frame scan, renders
Casual and Recordly style (Recordly zooms on the clicks), then reads the finished videos with Apple's text
recognition, independently of the blur code, and checks that:
  - none of the fake private values can be read in any frame of either video, and
  - the things that should stay visible (headings, the public price, usage, the date) can be read.

Usage: .venv/bin/python scripts/privacy/test_privacy.py [output/privacy-test]
"""
import json
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'scripts', 'record'))
sys.path.insert(0, HERE)
import privacy  # noqa: E402
import record  # noqa: E402

PAGE = os.path.join(ROOT, 'examples', 'privacy-test', 'index.html')


def fake():
    src = open(os.path.join(ROOT, 'examples', 'privacy-test', 'fake.js')).read()
    d = json.loads(src[src.index('{'):src.index('};') + 1])
    b = d['blur']
    secret = {
        'account name': [b['account_name']], 'emails': b['emails'], 'typed email': [b['typed_email']],
        'start of the typed email': [b['typed_email'].split('@')[0]],
        'phones': b['phones'], 'addresses': b['addresses'], 'customer names': b['customer_names'], 'money': b['money'],
        'counts': b['counts'], 'API keys': [k[0] + k[1] if k[0] == 'AKIA' else '_'.join(k) for k in b['keys']],
        'card number': [' '.join(b['card'])], 'recovery codes': b['codes'], 'tax ID': [b['gov_id']],
        'login link token': [b['login_link'][1]], 'hide word': [b['hide_word']], 'text inside the image': b['in_image'],
    }
    return secret, d['show']


def norm(t):
    return re.sub(r'[^a-z0-9@$£.]', '', t.lower())


def readable(value, texts):
    """True if the value (or, for long ones, any 10-character piece of it) can be read in some frame."""
    v = norm(value)
    pieces = [v] if len(v) <= 14 else [v[i:i + 10] for i in range(0, len(v) - 9, 3)]
    return [i for i, t in enumerate(texts) if any(p in t for p in pieces)]


def video_text(video, work, fps=6):
    d = os.path.join(work, os.path.basename(video) + '-frames')
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d)
    subprocess.run([record.FF, '-loglevel', 'error', '-i', video, '-vf', f'fps={fps}', os.path.join(d, 'f%05d.png')], check=True)
    files = sorted(os.path.join(d, f) for f in os.listdir(d))
    res = privacy.ocr(files)
    texts = [norm(' '.join(l['text'] for l in res[f]['lines'])) for f in files]
    shutil.rmtree(d)
    return texts


def main():
    out = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'output', 'privacy-test'))
    shutil.rmtree(out, ignore_errors=True)
    os.makedirs(out)
    secret, show = fake()
    s = privacy.settings({'privacy': {'preset': 'standard', 'hide_words': ['Northwind']}})
    s['typed'], _ = privacy.typed([('invite', secret['typed email'][0])], s)
    url = 'file://' + PAGE
    check = privacy.check_page(url, s, os.path.join(out, 'privacy-check.png'), [1440, 810])
    steps = [{'pause': 0.05}, {'hover': 'css=#avatar'}, {'click': 'text=Reveal key'},
             {'type': secret['typed email'][0], 'into': 'placeholder=Their email'},
             {'hover': 'css=#inv'}, {'hover': 'css=#customers'}, {'hover': 'text=Acme Dashboard'}, {'pause': 1.5}]
    scenario = {'name': 'privacy-test', 'url': url, 'viewport': {'width': 1440, 'height': 810}, 'realtime': True,
                'startAt': [0, 1.0, 3.0, 5.5, 10.0, 13.0, 17.0, 20.0], 'typingSpeed': 1.3, 'scale': 2,
                'style': {**record.STYLE, 'maxZoom': 1.0}, 'initScript': privacy.init_script(s),
                'output': {'width': 1920, 'height': 1080, 'fps': 60, 'path': 'silent.mp4'}, 'steps': steps}
    take, take_dir, _ = record.record(scenario, out)
    shutil.move(take_dir, os.path.join(out, 'take'))
    take_dir = os.path.join(out, 'take')
    if os.path.exists(os.path.join(out, 'silent.mp4')):   # the recorder's own draft, no longer made (--take-only)
        os.remove(os.path.join(out, 'silent.mp4'))
    shutil.rmtree(os.path.join(out, '.screenplay'), ignore_errors=True)
    scan = privacy.scan_take(take_dir, s)
    priv = privacy.review(out, take, scan, s, {'blurred': len(check['hits'])})
    videos = {}
    for style in ('casual', 'recordly'):
        videos[style] = os.path.join(out, f'{style}.mp4')
        info = record.polish(take_dir, style, videos[style])
        print(f'{style}: {len(info["zoomRegions"])} zooms, {info["post_blur_boxes"]} frame-scan blur boxes', flush=True)

    rows, ok = [], True
    for style, v in videos.items():
        texts = video_text(v, out)
        for what, values in secret.items():
            leaks = [(val, readable(val, texts)) for val in values]
            leaks = [(val, fr) for val, fr in leaks if fr]
            ok &= not leaks
            rows.append(f"| {style} | must be blurred | {what} | " + ('**LEAK** at ' + ', '.join(f'{fr[0] / 6:.1f} s' for _, fr in leaks) if leaks else 'not readable') + ' |')
        for val in show:
            seen = readable(val, texts)
            ok &= bool(seen)
            rows.append(f"| {style} | must stay visible | {val} | " + ('readable' if seen else '**OVER-BLURRED**') + ' |')
    page = privacy.in_page(take)
    cats = sorted({h['cat'] for h in page})
    has_photo = 'photo' in cats
    ok &= has_photo
    lines = ['# Phase 4 privacy check', '', f'Page: `examples/privacy-test/` (fake data). Preset: Standard, hide word "Northwind".', '',
             f"Blurred inside the page during the take: {len(page)} things ({', '.join(cats)}). Avatar blurred: {'yes' if has_photo else '**NO**'}.",
             f"Frame scan: {scan['frames_read']} frames read, {len(scan['hits'])} readable matches blurred afterwards "
             f"({sum(h['unsure'] for h in scan['hits'])} unsure).", '',
             'Read back from the finished videos with Apple text recognition, 6 frames a second:', '',
             '| Video | Rule | What | Result |', '|---|---|---|---|'] + rows + ['', f"**{'PASS' if ok else 'FAIL'}**"]
    open(os.path.join(out, 'check.md'), 'w').write('\n'.join(lines) + '\n')
    print('\n'.join(lines))
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
