"""Bounded run: first CAP seconds of each remaining demo; worker k of 2 takes every other file."""
import glob, json, os, subprocess, sys, time
from crisperwhisper import CrisperWhisperModel
CAP, K = int(sys.argv[1]), int(sys.argv[2])
ROOT = os.path.expanduser('~/Documents/natural-ai-demo-video/output/research')
FF = os.path.expanduser('~/Documents/natural-ai-demo-video/.venv/bin/ffmpeg')
files = sorted(glob.glob(f'{ROOT}/demos/casual/*.m4a')) + sorted(glob.glob(f'{ROOT}/demos/polished/*.m4a'))
todo = [p for p in files if not os.path.exists(f"{ROOT}/transcripts/{p.split('/')[-2]}__{os.path.basename(p)[:-4]}.json")]
mine = todo[K::2]
print(f'worker {K}: {len(mine)} files', flush=True)
m = CrisperWhisperModel('nyralabs/CrisperWhisper2.0_medium', backend='transformers', device='cpu', compute_type='float32')
for p in mine:
    style = p.split('/')[-2]; vid = os.path.basename(p)[:-4]
    out = f'{ROOT}/transcripts/{style}__{vid}.json'
    wav = f'{ROOT}/wav/{vid}.wav'
    subprocess.run([FF, '-loglevel', 'error', '-y', '-i', p, '-t', str(CAP), '-ac', '1', '-ar', '16000', wav], check=True)
    t = time.time()
    r = m.transcribe(wav, language='en', word_timestamps=True)
    json.dump({'id': vid, 'style': style, 'duration': r.duration, 'cap_s': CAP, 'text': r.text,
               'words': [{'w': w.word, 's': w.start, 'e': w.end} for w in r.words]}, open(out, 'w'))
    print(f'{style} {vid}: {r.duration:.0f}s audio in {time.time()-t:.0f}s', flush=True)
print(f'worker {K} DONE', flush=True)
