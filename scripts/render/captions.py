"""NAVI captions: the clean caption text of each section, timed to the words the voice actually says.

The caption version is not the talking version (voice-rules.md: captions are clean, short, no fillers), so the
two are matched on the meaningful words they share ("type", "box", "Enter"). A caption word with no spoken match
sits right next to the word it belongs with, for about as long as it takes to say: it is never stretched over
speech that says something else.

A caption shows only while its own words are spoken (Andy, Phase 5): it starts just before its first word and ends
0.3 s after its last. Where the voice talks for a while between two caption words, the caption is split there,
so one caption is never left up while the voice has moved on. At most 2 lines of 42 characters; a new caption at
each sentence end; never overlapping. Captions never run across a section boundary.

A caption never covers what the cursor is pointing at or clicking (Andy, 2026-11-10): place() moves it to the top
of the frame while a target sits where the bottom caption would be (and keeps it at the bottom when the top would
cover a target too, whichever covers less).
"""
import difflib
import re

GLUE = {'a', 'an', 'the', 'to', 'of', 'at', 'in', 'on', 'for', 'with', 'by', 'from', 'your', 'my', 'this', 'that', 'its',
        'their', 'our', 'and', 'or', 'but', 'is', 'are', 'it', 'you', 'i'}
JOIN = {'and', 'or', 'then', 'but', 'so'}
LINE = 42
MAX_CHARS = 2 * LINE
LEAD, HOLD, GAP = 0.1, 0.3, 0.06   # caption starts 0.1 s before its first word, ends 0.3 s after its last
MIN_S = 0.9         # shortest caption, only if its words leave room (never more than MIN_OVER past its words)
MIN_OVER = 0.6
SPLIT_GAP = 1.5     # the voice says other things for this long between two caption words: split there
PER_CHAR = 0.065    # seconds per character of speech, for caption words with no spoken match


def key(w):
    return re.sub(r'[^a-z0-9]', '', w.lower())


def _time_words(caption, spoken, start, end):
    """[(word, t0, t1)] for each caption word, using the spoken words' times where the words agree."""
    words = caption.split()
    # anchor only on meaningful words: "and" or "the" would pin a caption to the wrong moment
    ci = [i for i, w in enumerate(words) if key(w) and key(w) not in GLUE]
    si = [j for j, w in enumerate(spoken) if key(w['w']) and key(w['w']) not in GLUE]
    ck, sk = [key(words[i]) for i in ci], [key(spoken[j]['w']) for j in si]
    m = {}
    for a, b, n in difflib.SequenceMatcher(None, ck, sk, autojunk=False).get_matching_blocks():
        for i in range(n):
            m[ci[a + i]] = (spoken[si[b + i]]['start'], spoken[si[b + i]]['end'])
    out, i = [], 0
    while i < len(words):
        if i in m:
            out.append((words[i], *m[i]))
            i += 1
            continue
        j = i
        while j < len(words) and j not in m:
            j += 1
        span = words[i:j]
        prev_end = out[-1][2] if out else None
        next_start = m[j][0] if j < len(words) else None
        # words up to a sentence end belong with the word before them; the rest with the word after them
        ends = [k for k, w in enumerate(span) if re.search(r'[.!?]["\')]*$', w)]
        cut = ends[-1] + 1 if ends and prev_end is not None else (len(span) if next_start is None else 0)
        after, before = span[:cut], span[cut:]
        if after:
            t0 = prev_end if prev_end is not None else start
            out += _place(after, t0, min(end, next_start if next_start is not None else end), forward=True)
        if before:
            t1 = next_start if next_start is not None else end
            lo = out[-1][2] if out else start
            if after or prev_end is None:
                out += _place(before, lo, t1, forward=False)
            else:
                # no sentence end in between: if the gap is about as long as saying the words, spread them over
                # it; if the voice says a lot more in between, keep them next to the word before
                need = PER_CHAR * sum(len(w) + 1 for w in before)
                if (t1 - lo) <= 1.6 * need:
                    out += _place(before, lo, t1, forward=False)
                else:
                    # a long gap: words from a joining word on ("and press") go with the word after them
                    k = next((k for k, w in enumerate(before) if key(w) in JOIN), len(before))
                    out += _place(before[:k], lo, t1, forward=True) if k else []
                    out += _place(before[k:], out[-1][2] if out else lo, t1, forward=False) if k < len(before) else []
        i = j
    # keep times in order
    for k in range(1, len(out)):
        if out[k][1] < out[k - 1][1]:
            out[k] = (out[k][0], out[k - 1][1], max(out[k][2], out[k - 1][1]))
    return out


def _place(span, lo, hi, forward):
    """Times for words with no spoken match, between lo and hi: next to lo (forward) or next to hi, about as long
    as it takes to say them; spread evenly if the room is shorter than that."""
    total = sum(len(w) + 1 for w in span)
    need = min(PER_CHAR * total, max(0.0, hi - lo))
    t0 = lo if forward else hi - need
    out, acc = [], 0
    for w in span:
        a = t0 + need * acc / total
        acc += len(w) + 1
        out.append((w, a, t0 + need * acc / total))
    return out


def _lines(text):
    """One line, or two balanced lines that don't end a line on a little word ("the", "at", "to")."""
    if len(text) <= LINE:
        return [text]
    spaces = [i for i, c in enumerate(text) if c == ' ']

    def cost(i):
        before = key(text[:i].split()[-1])
        too_long = max(i, len(text) - i - 1) > LINE
        return (too_long, abs(i - len(text) / 2) + (12 if before in GLUE else 0) - (10 if text[i - 1] in ',;:' else 0))
    best = min(spaces, key=cost)
    return [text[:best], text[best + 1:]]


def _chunks(timed):
    cues, cur = [], []
    for w in timed:
        if cur and w[1] - cur[-1][2] > SPLIT_GAP:   # the voice has moved on between these two words
            cues.append(cur)
            cur = []
        text = ' '.join(x[0] for x in cur + [w])
        if cur and len(text) > MAX_CHARS:
            # break at the last comma in the cue if there is one, else before this word
            commas = [k for k, x in enumerate(cur[:-1]) if x[0].endswith(',')]
            if commas and commas[-1] >= 2:
                k = commas[-1] + 1
                cues.append(cur[:k])
                cur = cur[k:]
            else:
                cues.append(cur)
                cur = []
        cur.append(w)
        if re.search(r'[.!?]["\')]*$', w[0]):
            cues.append(cur)
            cur = []
    if cur:
        cues.append(cur)
    return cues


def build(script, timing, offset):
    """Caption cues on the video's clock: [{'start', 'end', 'lines', 'section'}]."""
    words = timing['words']
    cues = []
    for sec, win in zip(script['sections'], timing['sections']):
        assert sec['name'] == win['section'], (sec['name'], win['section'])
        text = (sec.get('caption') or '').strip()
        if not text:
            continue
        spoken = [w for w in words if win['start'] - 0.05 <= w['start'] <= win['end'] + 0.05]
        timed = _time_words(text, spoken, win['start'], win['end'])
        sec_cues = []
        for ch in _chunks(timed):
            sec_cues.append({'section': sec['name'], 'start': ch[0][1] - LEAD, 'end': ch[-1][2] + HOLD,
                             'words_end': ch[-1][2], 'words_start': ch[0][1], 'lines': _lines(' '.join(x[0] for x in ch))})
        for k, c in enumerate(sec_cues):
            nxt = sec_cues[k + 1]['start'] - GAP if k + 1 < len(sec_cues) else win['end'] + HOLD
            c['end'] = min(max(c['end'], min(c['start'] + MIN_S, c['words_end'] + MIN_OVER)), max(nxt, c['words_end']))
        cues += sec_cues
    for k in range(1, len(cues)):  # never overlap, across sections too
        cues[k]['start'] = max(cues[k]['start'], cues[k - 1]['end'] + GAP)
    for c in cues:
        for k in ('start', 'end', 'words_start', 'words_end'):
            c[k] = round(max(0.0, c[k] + offset), 3)
        c['end'] = max(c['end'], c['start'] + 0.5)
    return cues


def srt_time(t):
    ms = int(round(t * 1000))
    return f'{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}'


def srt(cues):
    return '\n'.join(f"{i}\n{srt_time(c['start'])} --> {srt_time(c['end'])}\n" + '\n'.join(c['lines']) + '\n'
                     for i, c in enumerate(cues, 1))


def ass_time(t):
    cs = int(round(t * 100))
    return f'{cs // 360000}:{cs // 6000 % 60:02d}:{cs // 100 % 60:02d}.{cs % 100:02d}'


def ass_text(t):
    return t.replace('\\', '/').replace('{', '(').replace('}', ')')


# ---- where a caption sits: bottom unless that covers what's being pointed at -----------------------------------
FRAME_W, FRAME_H = 1920, 1080
BAND = {'margin': 64, 'line_h': 62, 'gap': 6, 'char_w': 21, 'pad': 28}   # the caption boxes' size on a 1080p frame
MIN_SHARED = 0.2    # a target pointed at for less of the caption's time than this doesn't move it
POINT_AFTER = 3.0   # the cursor still points at a target this long after its click, unless it sets off sooner


def _band(lines, where):
    """The caption's box on the 1080p frame: (x0, y0, x1, y1)."""
    h = len(lines) * BAND['line_h'] + (len(lines) - 1) * BAND['gap']
    w = max(len(l) for l in lines) * BAND['char_w'] + BAND['pad']
    x0 = (FRAME_W - w) / 2
    y0 = FRAME_H - BAND['margin'] - h if where == 'bottom' else BAND['margin']
    return (x0, y0, x0 + w, y0 + h)


def _pointed(take, viewport):
    """[(t0, t1, box on the 1080p frame)]: each target from when the cursor sets off toward it until it leaves."""
    k = FRAME_W / viewport[0]
    steps = [s for s in take['steps'] if s.get('box') and ('travelStart' in s or 'actionAt' in s)]
    out = []
    for i, s in enumerate(steps):
        t0 = s.get('travelStart', s.get('actionAt'))
        # a click that opened another page or a pop-up leaves nothing there to cover
        t1 = s.get('actionEnd', s.get('actionAt', t0)) + (0.3 if s.get('navigated') else POINT_AFTER)
        if i + 1 < len(steps):
            t1 = min(t1, steps[i + 1].get('travelStart', steps[i + 1].get('actionAt', t1)))
        b = s['box']
        out.append((t0, t1, (b['x'] * k, b['y'] * k, (b['x'] + b['width']) * k, (b['y'] + b['height']) * k)))
    return out


def _cover(a, b):
    w = min(a[2], b[2]) - max(a[0], b[0])
    h = min(a[3], b[3]) - max(a[1], b[1])
    return max(0, w) * max(0, h)


def place(cues, take, viewport):
    """Set each cue's 'pos' to 'bottom' or 'top' (see the module notes). take: the recording's take.json (its clock
    is the video's). viewport: the page size the take was recorded at."""
    pointed = _pointed(take, viewport) if take else []
    for c in cues:
        live = [box for t0, t1, box in pointed if min(t1, c['end']) - max(t0, c['start']) > MIN_SHARED]
        bottom = sum(_cover(_band(c['lines'], 'bottom'), b) for b in live)
        top = sum(_cover(_band(c['lines'], 'top'), b) for b in live)
        c['pos'] = 'top' if bottom > 0 and top < bottom else 'bottom'
    return cues
