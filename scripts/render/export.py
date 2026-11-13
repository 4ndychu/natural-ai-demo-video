"""NAVI Phase 5: render and export a finished demo.

Takes a finished recording (record.py: the video with the voice and room tone already laid in) and makes the files
the user gets, named after the demo title, in the folder they named (default ~/Movies/NAVI), never inside this repo:

  <title>.mp4                 1080p. Captions burned in when the caption mode is "burn"; corner label if set.
  <title>.srt                 captions as a separate file, unless captions are "off"
  <title> transcript.txt      the clean caption text, one paragraph per section, with its start time
  <title> (720p preview).mp4  only with --preview (or export.preview_720p in the settings)
  <title> (1.35x).mp4 + .srt  only with --speed 1.35 (or "speed_copy" in the script / export.speed_copy in the
                              settings): a sped-up copy as well as the normal one. The voice keeps its natural pitch
                              (ffmpeg atempo); captions and the corner label are sped up with the picture.

Caption mode (burn / file / off) and the corner label (off / tl / tr / bl / br + text) come from the command line,
else the demo's script ("captions", "corner_label", "corner_text"), else config/defaults.json "on_screen". Changing
them only re-renders: no voice is generated and nothing is recorded again. With captions "file" or "off" and no
corner label, the video isn't even re-encoded.

No other overlays: no watermark, brand name or tag (SKILL.md, recording-rules.md).

Usage: .venv/bin/python scripts/render/export.py examples/test-todo-b.json output/test-todo-v4
       [--recording recording] [--captions burn|file|off] [--corner off|tl|tr|bl|br] [--corner-text "..."]
       [--preview] [--speed 1.35] [--to ~/Movies/NAVI] [--video recording.mp4]
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
CONFIG = json.load(open(os.path.join(ROOT, 'config', 'defaults.json')))
FF = os.path.join(ROOT, '.venv', 'bin', 'ffmpeg')
sys.path.insert(0, HERE)
import captions as cap  # noqa: E402

FONTS = '/System/Library/Fonts'
# Captions: white, medium weight, on a soft dark box so they read on any page; bottom centre.
# Corner label: the same look, smaller. Sizes are for 1080p.
STYLES = ("Style: Caption,Helvetica Neue Medium,44,&H00FFFFFF,&H00FFFFFF,&H40141414,&H00000000,0,0,0,0,100,100,0,0,3,12,0,2,160,160,64,1\n"
          "Style: Label,Helvetica Neue Medium,28,&H00FFFFFF,&H00FFFFFF,&H40141414,&H00000000,0,0,0,0,100,100,0,0,3,9,0,{align},44,44,40,1\n")
CORNER = {'tl': 7, 'tr': 9, 'bl': 1, 'br': 3}
CAPTION_V, LINE_STEP = 64, 74   # bottom line's distance from the bottom edge; distance between the two lines' boxes


def safe_name(title):
    name = re.sub(r'[\\/:*?"<>|\x00-\x1f]', '-', title).strip(' .')
    return name or 'NAVI demo'


def folder(path):
    p = os.path.abspath(os.path.expanduser(path))
    if p == ROOT or p.startswith(ROOT + os.sep):
        sys.exit(f"Exports never go inside NAVI's own folder ({ROOT}). Pick another folder, for example ~/Movies/NAVI.")
    os.makedirs(p, exist_ok=True)
    return p


def fmt(t):
    return f'{int(t // 60)}:{int(t % 60):02d}'


def transcript(script, timing, offset):
    out = [script.get('title', 'Demo'), '']
    for sec, win in zip(script['sections'], timing['sections']):
        text = (sec.get('caption') or '').strip()
        if text:
            out += [f"{fmt(win['start'] + offset)}  {text}", '']
    return '\n'.join(out)


def ass(cues, corner, corner_text):
    hdr = ('[Script Info]\nScriptType: v4.00+\nPlayResX: 1920\nPlayResY: 1080\nWrapStyle: 2\nScaledBorderAndShadow: yes\n\n'
           '[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, '
           'Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n'
           + STYLES.format(align=CORNER.get(corner, 3)) + '\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n')
    ev = []
    for c in cues:
        # one event per line, each with its own box, stacked with a small gap (boxes never overlap); a cue moved to
        # the top (captions.place: the bottom would cover what's being pointed at) is anchored to the top edge
        top = c.get('pos') == 'top'
        for k, line in enumerate(c['lines'] if top else reversed(c['lines'])):
            ev.append(f"Dialogue: 0,{cap.ass_time(c['start'])},{cap.ass_time(c['end'])},Caption,,0,0,{CAPTION_V + k * LINE_STEP},,"
                      + ('{\\an8}' if top else '') + cap.ass_text(line))
    if corner != 'off' and corner_text:
        ev.append(f"Dialogue: 1,0:00:00.00,9:59:59.00,Label,,0,0,0,,{cap.ass_text(corner_text)}")
    return hdr + '\n'.join(ev) + '\n'


# Caption looks (on_screen.caption_look). "helvetica-square" is drawn by ffmpeg's subtitle renderer (STYLES above);
# "mona-rounded" by the browser (caption_png.mjs), which can use Mona Sans and round the boxes. Same size and box colour.
MONA = {'family': "'Mona Sans'", 'weight': 520, 'size': 39, 'gap': 6, 'bottom': 64, 'box': 'rgba(20,20,20,0.75)', 'padY': 8,
        'padX': 14, 'radius': 10, 'labelSize': 25, 'labelPadY': 6, 'labelPadX': 11, 'labelMargin': 36}


def burn_browser(src, mp4, cues, corner, corner_text, tmp):
    """Captions and label as browser-drawn transparent pictures, laid over the video at their times."""
    items = [{'name': f'c{i:04d}', 'lines': c['lines'], 'pos': c.get('pos', 'bottom')} for i, c in enumerate(cues)]
    if corner != 'off':
        items.append({'name': 'label', 'kind': 'label', 'corner': corner, 'lines': [corner_text]})
    r = subprocess.run(['node', os.path.join(HERE, 'caption_png.mjs')], input=json.dumps({'out': tmp, 'look': MONA, 'items': items}),
                       capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit('Drawing the captions failed:\n' + (r.stdout + r.stderr)[-1500:])
    blank = os.path.join(tmp, 'blank.png')
    run([FF, '-loglevel', 'error', '-y', '-f', 'lavfi', '-i', 'color=c=black@0.0:s=1920x1080,format=rgba', '-frames:v', '1', blank])
    lines, t = ['ffconcat version 1.0'], 0.0
    for i, c in enumerate(cues):        # blank until each caption, the caption for its time, blank after the last
        if c['start'] > t:
            lines += [f"file '{blank}'", f"duration {c['start'] - t:.3f}"]
        lines += [f"file '{os.path.join(tmp, f'c{i:04d}.png')}'", f"duration {c['end'] - c['start']:.3f}"]
        t = c['end']
    lines += [f"file '{blank}'", 'duration 1', f"file '{blank}'"]
    lst = os.path.join(tmp, 'captions.ffconcat')
    open(lst, 'w').write('\n'.join(lines) + '\n')
    cmd = [FF, '-loglevel', 'error', '-y', '-i', src, '-f', 'concat', '-safe', '0', '-i', lst]
    graph = '[0:v][1:v]overlay=eof_action=pass:format=auto[v]'
    if corner != 'off':
        cmd += ['-loop', '1', '-i', os.path.join(tmp, 'label.png')]
        graph = '[0:v][1:v]overlay=eof_action=pass:format=auto[c];[c][2:v]overlay=shortest=1:format=auto[v]'
    run(cmd + ['-filter_complex', graph, '-map', '[v]', '-map', '0:a', '-c:v', 'libx264', '-preset', 'medium', '-crf', '16',
               '-pix_fmt', 'yuv420p', '-c:a', 'copy', '-movflags', '+faststart', mp4])


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit('ffmpeg failed:\n' + r.stderr[-1500:])


def speed_label(x):
    return f'{x:g}x'


def export(script, voice_dir, rec_name='recording', captions=None, corner=None, corner_text=None, preview=None, to=None, video=None,
           speed=None, look=None):
    rec = os.path.join(voice_dir, rec_name)
    report = json.load(open(os.path.join(rec, 'report.json')))
    timing = json.load(open(os.path.join(voice_dir, 'timing.json')))
    src = os.path.join(rec, video or 'recording.mp4')
    on = CONFIG['on_screen']
    captions = captions or script.get('captions') or on['captions']
    corner = corner or script.get('corner_label') or on['corner_label']
    corner_text = (corner_text if corner_text is not None else script.get('corner_text', on['corner_text'])) or ''
    look = look or script.get('caption_look') or on['caption_look']
    if look not in on['caption_look_options']:
        sys.exit(f'The caption look must be one of {on["caption_look_options"]}.')
    if captions not in on['captions_options']:
        sys.exit(f'Captions must be one of {on["captions_options"]}.')
    if corner not in on['corner_options']:
        sys.exit(f'The corner label must be one of {on["corner_options"]}.')
    if corner != 'off' and not corner_text.strip():
        sys.exit('A corner label needs its text (--corner-text).')
    preview = CONFIG['export'].get('preview_720p', False) if preview is None else preview
    sc = CONFIG['export']['speed_copy']
    if speed is None:
        speed = script.get('speed_copy') or (sc['speed'] if sc['on'] else None)
    if speed is not None and not sc['range'][0] <= speed <= sc['range'][1]:
        sys.exit(f"The sped-up copy's speed must be between {sc['range'][0]} and {sc['range'][1]}.")
    out = folder(to or script.get('export_to') or CONFIG['export'].get('folder', '~/Movies/NAVI'))
    name = safe_name(script.get('title', 'NAVI demo'))
    cues = cap.build(script, timing, report['voice_offset_s'])
    take_file = os.path.join(rec, 'take', 'take.json')
    scen_file = os.path.join(rec, 'scenario.json')
    if os.path.exists(take_file) and os.path.exists(scen_file):
        vp = json.load(open(scen_file))['viewport']
        cap.place(cues, json.load(open(take_file)), (vp['width'], vp['height']))
    moved = [c for c in cues if c.get('pos') == 'top']
    files = {}

    mp4 = os.path.join(out, name + '.mp4')
    burn = captions == 'burn' or corner != 'off'
    with tempfile.TemporaryDirectory() as tmp:
        if burn and look == 'mona-rounded':
            burn_browser(src, mp4, cues if captions == 'burn' else [], corner, corner_text, tmp)
        elif burn:
            sub = os.path.join(tmp, 'overlay.ass')
            open(sub, 'w').write(ass(cues if captions == 'burn' else [], corner, corner_text))
            run([FF, '-loglevel', 'error', '-y', '-i', src, '-vf', f'ass={sub}:fontsdir={FONTS}', '-c:v', 'libx264', '-preset', 'medium',
                 '-crf', '16', '-pix_fmt', 'yuv420p', '-c:a', 'copy', '-movflags', '+faststart', mp4])
        else:
            run([FF, '-loglevel', 'error', '-y', '-i', src, '-c', 'copy', '-movflags', '+faststart', mp4])
    files['video'] = mp4
    srt = os.path.join(out, name + '.srt')
    if captions != 'off':
        open(srt, 'w').write(cap.srt(cues))
        files['captions'] = srt
    elif os.path.exists(srt):
        os.remove(srt)                       # an earlier export's captions would no longer match
    txt = os.path.join(out, name + ' transcript.txt')
    open(txt, 'w').write(transcript(script, timing, report['voice_offset_s']))
    files['transcript'] = txt
    pv = os.path.join(out, name + ' (720p preview).mp4')
    if preview:
        run([FF, '-loglevel', 'error', '-y', '-i', mp4, '-vf', 'scale=1280:720:flags=lanczos', '-c:v', 'libx264', '-preset', 'medium',
             '-crf', '23', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', pv])
        files['preview'] = pv
    if speed:
        # the finished picture (captions and label included) and the voice, faster; atempo keeps the pitch
        fast = os.path.join(out, f'{name} ({speed_label(speed)}).mp4')
        run([FF, '-loglevel', 'error', '-y', '-i', mp4, '-filter_complex', f'[0:v]setpts=PTS/{speed}[v];[0:a]atempo={speed}[a]',
             '-map', '[v]', '-map', '[a]', '-r', str(CONFIG['recording'].get('fps', 60)), '-c:v', 'libx264', '-preset', 'medium',
             '-crf', '16', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', fast])
        files['speed_video'] = fast
        if captions != 'off':
            fast_srt = os.path.join(out, f'{name} ({speed_label(speed)}).srt')
            open(fast_srt, 'w').write(cap.srt([{**c, 'start': c['start'] / speed, 'end': c['end'] / speed} for c in cues]))
            files['speed_captions'] = fast_srt
    return {'folder': out, 'files': files, 'captions': captions, 'corner': corner, 'cues': len(cues), 'cues_at_top': len(moved), 're_encoded': burn, 'speed': speed,
            'look': look, 'cue_list': cues}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('script')
    ap.add_argument('voice_dir')
    ap.add_argument('--recording', default='recording', help='recording folder inside voice_dir')
    ap.add_argument('--video', help='which video in it (default recording.mp4; e.g. recording-recordly.mp4)')
    ap.add_argument('--captions', choices=CONFIG['on_screen']['captions_options'])
    ap.add_argument('--corner', choices=CONFIG['on_screen']['corner_options'])
    ap.add_argument('--corner-text')
    ap.add_argument('--preview', action='store_true', default=None, help='also make a 720p preview')
    ap.add_argument('--look', choices=CONFIG['on_screen']['caption_look_options'], help='caption look')
    ap.add_argument('--speed', type=float, help='also make a sped-up copy at this speed, e.g. 1.35 (natural pitch)')
    ap.add_argument('--to', help='folder for the files (default ~/Movies/NAVI)')
    a = ap.parse_args()
    r = export(json.load(open(a.script)), a.voice_dir, a.recording, a.captions, a.corner, a.corner_text, a.preview, a.to, a.video, a.speed, a.look)
    print(f"Exported to {r['folder']} (captions {r['captions']}, corner label {r['corner']}; "
          f"{r['cues_at_top']} of {r['cues']} captions moved to the top so they don't cover what's being pointed at):")
    for k, f in r['files'].items():
        print(f'  {k}: {os.path.basename(f)} ({os.path.getsize(f) / 1e6:.1f} MB)' if f.endswith('.mp4') else f'  {k}: {os.path.basename(f)}')


if __name__ == '__main__':
    main()
