"""NAVI readiness check: is this computer ready to make a video?

Run from anywhere:   python3 scripts/setup/check.py
It changes nothing except creating two empty folders (output/ in the repo and NAVI's settings folder).
It never installs anything, never spends ElevenLabs credits and never prints the key.

Each line is OK, MISSING or WARN. Every MISSING line says what's needed. Exit code 0 only when all pass.
Written for any python3 (3.9+), so it can run before NAVI's own Python environment exists.
"""
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
VENV_PY = os.path.join(ROOT, '.venv', 'bin', 'python')
RECORDER = os.path.join(ROOT, 'recorder', 'agent-screenplay')
SETTINGS = os.path.expanduser(os.environ.get('NAVI_DATA') or '~/Library/Application Support/NAVI')   # as scripts/app/store.py
KEY_SERVICE = os.environ.get('NAVI_KEY_SERVICE') or 'navi-elevenlabs'
POLISH = os.path.join(ROOT, 'recorder', 'polish')
SKILL_LINK = os.path.join(os.path.expanduser(os.environ.get('NAVI_SKILL_DIR') or '~/.claude/skills'), 'natural-ai-demo-video')
INSTALL = 'Run: sh scripts/setup/install.sh  (installs everything NAVI needs inside this folder; ask the user first)'
_pin = re.search(r'^RECORDER_REV=([0-9a-f]{40})', open(os.path.join(ROOT, 'scripts', 'setup', 'install.sh')).read(), re.M)
RECORDER_REV = _pin.group(1) if _pin else None
CONFIG = json.load(open(os.path.join(ROOT, 'config', 'defaults.json')))
TIMING = CONFIG.get('timing', {'engine': 'faster-whisper', 'model': 'small.en'})

results = []


def report(status, name, detail, fix=None):
    results.append(status)
    mark = {'OK': 'OK     ', 'MISSING': 'MISSING', 'WARN': 'WARN   '}[status]
    print(f'  {mark}  {name}: {detail}')
    if fix:
        print(f'           -> {fix}')


def run(cmd, timeout=60, **kw):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, **kw)
        return r.returncode, r.stdout, r.stderr
    except FileNotFoundError:
        return 127, '', 'not found'
    except subprocess.TimeoutExpired:
        return 124, '', 'timed out'


def check_system():
    mac = platform.mac_ver()[0]
    report('OK', 'Computer', f'macOS {mac}, {platform.machine()}' if mac else platform.platform())
    free_gb = shutil.disk_usage(os.path.expanduser('~')).free / 1e9
    if free_gb < 5:
        report('WARN', 'Disk space', f'{free_gb:.0f} GB free', 'Recording and rendering need a few GB. Free up space first.')
    else:
        report('OK', 'Disk space', f'{free_gb:.0f} GB free')


def check_node():
    code, out, _ = run(['node', '--version'])
    if code != 0:
        return report('MISSING', 'Node.js', 'not found', 'Install Node.js 20 or newer (nodejs.org).')
    major = int(re.findall(r'\d+', out)[0])
    if major < 20:
        return report('MISSING', 'Node.js', f'{out.strip()} is too old', 'Install Node.js 20 or newer.')
    report('OK', 'Node.js', out.strip())


def check_python():
    if not os.path.exists(VENV_PY):
        return report('MISSING', 'Python for NAVI', 'no .venv in the repo (the Mac\'s own python3 is '
                      f'{platform.python_version()}, NAVI needs 3.10+)',
                      INSTALL)
    code, out, _ = run([VENV_PY, '-c', 'import sys; print("%d.%d.%d" % sys.version_info[:3])'])
    ver = out.strip()
    if code != 0 or tuple(int(x) for x in ver.split('.')[:2]) < (3, 10):
        return report('MISSING', 'Python for NAVI', f'.venv has Python {ver or "?"}, needs 3.10+',
                      INSTALL)
    report('OK', 'Python for NAVI', f'{ver} in .venv')


def find_tool(name):
    """NAVI's own copy in .venv/bin comes first (linked from the recorder's ffmpeg-static), then the PATH."""
    own = os.path.join(ROOT, '.venv', 'bin', name)
    return own if os.path.exists(own) else shutil.which(name)


def check_ffmpeg():
    ff = find_tool('ffmpeg')
    if not ff:
        return report('MISSING', 'ffmpeg', 'not found in .venv/bin or on the PATH',
                      INSTALL)
    _, ver, _ = run([ff, '-hide_banner', '-version'])
    _, enc, _ = run([ff, '-hide_banner', '-encoders'])
    _, dec, _ = run([ff, '-hide_banner', '-decoders'])
    _, flt, _ = run([ff, '-hide_banner', '-filters'])
    need = {'H.264 encoder (libx264)': re.search(r'\blibx264\b', enc) is not None,
            'AAC encoder': re.search(r'\baac\b', enc) is not None,
            'MP3 decoder': re.search(r'\bmp3\b', dec) is not None,
            'burned-in captions (subtitles filter, libass)': re.search(r'\bsubtitles\b', flt) is not None,
            'corner label (drawtext filter)': re.search(r'\bdrawtext\b', flt) is not None}
    lacking = [k for k, v in need.items() if not v]
    name = ver.split('\n')[0].replace('ffmpeg version ', '').split(' ')[0]
    if lacking:
        return report('MISSING', 'ffmpeg', f'{name} lacks: {", ".join(lacking)}',
                      'Install a full ffmpeg build (Homebrew\'s has all of these).')
    where = '.venv/bin' if ff.startswith(ROOT) else os.path.dirname(ff)
    report('OK', 'ffmpeg', f'{name} in {where} (H.264, AAC, MP3, captions, drawtext)')


PW_TEST = r"""
const path = require('path');
const dir = process.argv[1];
let pw = null, name = null;
for (const n of ['playwright', 'playwright-core', '@playwright/test']) {
  try { pw = require(require.resolve(n, { paths: [dir] })); name = n; break; } catch (e) {}
}
if (!pw) { console.log(JSON.stringify({ ok: false, why: 'no-package' })); process.exit(0); }
const version = require(require.resolve(name + '/package.json', { paths: [dir] })).version;
(async () => {
  try {
    const b = await pw.chromium.launch({ headless: true });
    const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
    await p.setContent('<h1>NAVI</h1>');
    const ok = (await p.textContent('h1')) === 'NAVI';
    await b.close();
    console.log(JSON.stringify({ ok, version, chromium: b.version ? 'yes' : '' }));
  } catch (e) {
    console.log(JSON.stringify({ ok: false, version, why: 'launch', msg: String(e.message).split('\n')[0] }));
  }
})();
"""


def check_recorder():
    if not os.path.isdir(RECORDER):
        report('MISSING', 'Recorder', 'agent-screenplay is not set up in recorder/agent-screenplay', INSTALL)
        return report('MISSING', 'Playwright + Chromium', 'comes with the recorder', None)
    code, _, _ = run(['git', '-C', RECORDER, 'diff', '--quiet', '--', 'src/drivers/web.ts'])
    if code == 0:
        report('MISSING', 'Recorder', 'agent-screenplay is there but NAVI\'s patch is not applied',
               INSTALL)
    elif not os.path.exists(os.path.join(RECORDER, 'dist', 'cli.js')):
        report('MISSING', 'Recorder', 'patched but not built', INSTALL)
    else:
        _, rev, _ = run(['git', '-C', RECORDER, 'rev-parse', 'HEAD'])
        rev = rev.strip()
        if RECORDER_REV and rev != RECORDER_REV:
            report('MISSING', 'Recorder', f'agent-screenplay is at {rev[:7]}, but NAVI\'s patch is made for {RECORDER_REV[:7]}',
                   'Move recorder/agent-screenplay aside, then ' + INSTALL[0].lower() + INSTALL[1:])
        else:
            report('OK', 'Recorder', f'agent-screenplay {rev[:7]} with NAVI\'s patch, built')
    code, out, err = run(['node', '-e', PW_TEST, RECORDER], timeout=90)
    try:
        r = json.loads(out.strip().splitlines()[-1])
    except Exception:
        return report('MISSING', 'Playwright + Chromium', f'test failed to run ({err.strip()[:120]})')
    if r.get('why') == 'no-package':
        return report('MISSING', 'Playwright + Chromium', 'Playwright not installed',
                      INSTALL)
    if not r.get('ok'):
        return report('MISSING', 'Playwright + Chromium', f'Playwright {r.get("version")} could not start Chromium '
                      f'({r.get("msg", "")[:100]})', INSTALL)
    report('OK', 'Playwright + Chromium', f'Playwright {r["version"]}, Chromium opened a 1920x1080 page')


WHISPER_TEST = r"""
import json, sys
from faster_whisper import WhisperModel
m = WhisperModel(sys.argv[2], device='cpu', compute_type='int8', local_files_only=True)
segs, _ = m.transcribe(sys.argv[1], word_timestamps=True, language='en')
words = [{'w': w.word.strip(), 's': round(w.start, 2), 'e': round(w.end, 2)} for s in segs for w in s.words]
print(json.dumps(words))
"""


def check_whisper():
    label = f'{TIMING["engine"]} ({TIMING["model"]})'
    if not os.path.exists(VENV_PY):
        return report('MISSING', 'Word timings', f'{label} needs the .venv first')
    code, _, _ = run([VENV_PY, '-c', 'import faster_whisper'])
    if code != 0:
        return report('MISSING', 'Word timings', f'{label} is not installed',
                      INSTALL)
    if sys.platform != 'darwin' or not shutil.which('say'):
        return report('WARN', 'Word timings', f'{label} installed; skipped the spoken test (needs macOS "say")')
    tmp = tempfile.mkdtemp(prefix='navi-check-')
    wav = os.path.join(tmp, 'test.wav')
    phrase = 'Open the settings page and click save.'
    run(['say', '-o', wav, '--data-format=LEI16@16000', phrase])
    t0 = time.time()
    code, out, err = run([VENV_PY, '-c', WHISPER_TEST, wav, TIMING['model']], timeout=300)
    shutil.rmtree(tmp, ignore_errors=True)
    if code != 0:
        if 'local_files_only' in err or 'snapshot' in err.lower() or 'LocalEntryNotFound' in err:
            return report('MISSING', 'Word timings', f'the {TIMING["model"]} model is not downloaded yet',
                          INSTALL)
        return report('MISSING', 'Word timings', f'test failed: {err.strip().splitlines()[-1][:140] if err.strip() else code}')
    words = json.loads(out.strip().splitlines()[-1])
    heard = ' '.join(w['w'] for w in words).lower()
    found = [w for w in ('settings', 'click', 'save') if w in heard]
    if len(found) < 3 or not all(w['e'] >= w['s'] for w in words):
        return report('MISSING', 'Word timings', f'heard "{heard}", expected the words settings/click/save')
    s = next(w for w in words if 'settings' in w['w'].lower())
    report('OK', 'Word timings', f'{label} runs locally; test phrase heard, "settings" at {s["s"]:.2f} s '
           f'({time.time() - t0:.0f} s)')


def get_key():
    key = os.environ.get('NAVI_ELEVENLABS_KEY')
    if key and KEY_SERVICE == 'navi-elevenlabs':
        return key.strip(), 'NAVI_ELEVENLABS_KEY'
    if sys.platform == 'darwin':
        code, out, _ = run(['security', 'find-generic-password', '-s', KEY_SERVICE, '-w'])
        if code == 0 and out.strip():
            return out.strip(), 'Keychain'
    return None, None


def api(path, key):
    req = urllib.request.Request('https://api.elevenlabs.io' + path, headers={'xi-api-key': key})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, json.load(r)
    except urllib.error.HTTPError as e:
        try:
            body = json.load(e)
        except Exception:
            body = {}
        return e.code, body
    except Exception as e:  # network down etc. Never include the key in what we return.
        return 0, {'error': type(e).__name__}


def check_key():
    key, where = get_key()
    if not key:
        return report('MISSING', 'ElevenLabs key', 'not in the Keychain' + (f' (service "{KEY_SERVICE}")' if KEY_SERVICE != 'navi-elevenlabs' else ''),
                      'Run: sh scripts/setup/store-key.sh  (you paste the key there, hidden; never in chat)')
    code, sub = api('/v1/user/subscription', key)
    if code == 200:
        used, limit = sub.get('character_count', 0), sub.get('character_limit', 0)
        reset = sub.get('next_character_count_reset_unix')
        when = f', resets {time.strftime("%d %b %Y", time.localtime(reset))}' if reset else ''
        tier = sub.get('tier', '?')
        detail = f'works ({where}); {limit - used:,} credits left of {limit:,}, plan "{tier}"{when}'
        if tier == 'free':
            return report('WARN', 'ElevenLabs key', detail, 'NAVI needs the Starter plan or above.')
        return report('OK', 'ElevenLabs key', detail)
    status = (sub.get('detail') or {}).get('status', '') if isinstance(sub.get('detail'), dict) else ''
    if code == 401 and status == 'missing_permissions':
        # The key is valid but can't read the plan. Confirm it works with a free call that lists voices.
        c2, _ = api('/v2/voices?page_size=1', key)
        if c2 == 200:
            return report('WARN', 'ElevenLabs key', f'works ({where}), but it isn\'t allowed to read your credits',
                          'Optional: give the key "User: read" access at elevenlabs.io so NAVI can show credits left.')
    if status == 'api_key_id_used_as_api_key':
        return report('MISSING', 'ElevenLabs key', 'the Keychain holds the key\'s ID, not the key itself',
                      'The key starts with "sk_" and is shown only once, when you create it at elevenlabs.io. '
                      'Make a new key, copy it straight away, then run: sh scripts/setup/store-key.sh')
    if code == 0:
        return report('MISSING', 'ElevenLabs key', f'couldn\'t reach ElevenLabs ({sub.get("error")})',
                      'Check the internet connection and run the check again.')
    report('MISSING', 'ElevenLabs key', f'ElevenLabs refused it (HTTP {code} {status})'.rstrip(),
           'Make a new key at elevenlabs.io (text to speech access), then run: sh scripts/setup/store-key.sh')


def check_polish():
    """The renderer (recorder/polish): Recordly's frame renderer on pixi.js, bundled on first use."""
    if not os.path.isdir(os.path.join(POLISH, 'node_modules', 'pixi.js')):
        return report('MISSING', 'Renderer', 'recorder/polish has no packages (pixi.js)', INSTALL)
    if not os.path.isdir(os.path.join(RECORDER, 'node_modules', 'vite')):
        return report('MISSING', 'Renderer', 'needs the recorder installed first (it bundles with its vite)', INSTALL)
    code, out, err = run(['node', os.path.join(POLISH, 'build.mjs')], timeout=180)
    if code != 0:
        return report('MISSING', 'Renderer', 'recorder/polish would not build: ' + (out + err).strip().splitlines()[-1][:120] if (out + err).strip() else 'build failed', INSTALL)
    report('OK', 'Renderer', 'Recordly\'s renderer (recorder/polish) builds')


def check_swift():
    """macOS: the privacy text reader and the focus watcher are small Swift programs built on first use."""
    if sys.platform != 'darwin':
        return
    code, out, _ = run(['swiftc', '--version'])
    if code != 0:
        return report('MISSING', 'Swift', 'not found (builds the privacy text reader on first use)',
                      "Install Apple's free command line tools: xcode-select --install")
    report('OK', 'Swift', (out.strip().splitlines() or ['swiftc'])[0][:60])


def check_skill_link():
    """Claude Code finds NAVI in any session through ~/.claude/skills/natural-ai-demo-video (install.sh makes it)."""
    if os.path.exists(SKILL_LINK) and os.path.realpath(SKILL_LINK) == os.path.realpath(ROOT):
        return report('OK', 'Claude Code skill', SKILL_LINK.replace(os.path.expanduser('~'), '~') + ' is this folder')
    if os.path.exists(SKILL_LINK):
        return report('WARN', 'Claude Code skill', SKILL_LINK.replace(os.path.expanduser('~'), '~') + ' is another folder',
                      'Claude Code uses that copy. Remove it and run install.sh again to use this one.')
    report('WARN', 'Claude Code skill', 'not linked, so Claude Code finds NAVI only when started in this folder', INSTALL)


def check_folders():
    out = os.path.join(ROOT, 'output')
    os.makedirs(out, exist_ok=True)
    code, _, _ = run(['git', '-C', ROOT, 'check-ignore', '-q', 'output/x.mp4'])
    if code != 0:
        report('MISSING', 'Folders', 'output/ is not ignored by git', 'Add output/ to .gitignore.')
    else:
        report('OK', 'Folders', 'output/ (ignored by git)')
    os.makedirs(SETTINGS, mode=0o700, exist_ok=True)
    report('OK', 'Settings folder', SETTINGS.replace(os.path.expanduser('~'), '~') + ' (saved logins go here, outside the repo)')


def main():
    print('NAVI readiness check\n')
    for fn in (check_system, check_node, check_python, check_ffmpeg, check_recorder, check_polish, check_swift, check_whisper,
               check_key, check_folders, check_skill_link):
        try:
            fn()
        except Exception as e:  # one broken check shouldn't hide the others
            report('MISSING', fn.__name__.replace('check_', ''), f'check crashed: {type(e).__name__}: {e}')
    missing = results.count('MISSING')
    print()
    if missing:
        print(f'Not ready yet: {missing} thing(s) missing.')
        sys.exit(1)
    print('Ready.' + (' (with warnings above)' if 'WARN' in results else ''))


if __name__ == '__main__':
    main()
