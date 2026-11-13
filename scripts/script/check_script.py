"""NAVI script checker (Phase 6): catches what reference/voice-rules.md bans before any credits are spent.

Errors (must be fixed before the script is shown to the user):
  cheerful-line      a cheerful one-word line ("Easy.", "There we go.", "There it is!", "Perfect!")
  there-we-go        "there we go" anywhere but inside a sentence (words before and after it)
  catchphrase        a move a casual demo never makes, found by what the line does (moves.py): an aside about it being
                     private or unfinished, a hook, a reveal, selling, framing, written English, a performed slip
  ellipsis           "…" or "..." used as a hesitation (it stretches the word before it)
  tag                any performance tag other than [relaxed] ([inhales], [laughs], [short pause]...)
  restarts           more than one restart or repeated word in a section ("the, uh, the", "I'm, I'm")
  cut-off            a word cut off ("You- you just drag"): it sounds fake
  filler-sentence    a filler written as its own sentence ("Um." "Uh, okay.")
  still-screen       a stretch of talk likely to leave the screen still for over 5 s (words between two
                     actions at the reference pace, less the cursor's travel before a click or hover)
  crowded            pointing actions (clicks, hovers) stacked so close that each starts before the one before it is done
                     and the lateness adds up (Andy, 12 Nov 2026: four hovers in about 4 s on a slow page landed up to
                     0.8 s late and failed the join check). Each one is taken to need about 1.2 s of the cursor's time;
                     an action predicted to land over 1 s late is an error. Spread them out with more words between.
  position           a position ("top right", "at the bottom of the form") that is wrong, reads two ways, or isn't
                     checked against the explored page (scripts/script/positions.py; the script's "explore" folder)
  structure          missing talk or caption, an action whose cue word isn't in the talk (in order), an
                     unknown action kind, captions with fillers, tags or swears
Warnings (rules that need judgement):
  result-line        announcing the result of an action ("and it's on the list", "and it's saved")
  closer             the same closer ("so that's one", "so yeah", "okay.", "all right.") twice in a row or
                     more than twice in a video
  filler-end         a section ending on a filler
  rising-end         a section ending on a question or "and yeah, it's ..."
  if-i-click         "If I click..." framing
  section-length     a section much shorter than 10 s or longer than 35 s of talk
  opening            the first section runs longer than about 12 s
  swear              a swear in a script whose swearing is off

Variety (scripts/script/variety.py; Andy, 11 Nov 2026: "they sound the exact same"): repeats inside the script
(how sections start, filler slots, repair kinds, endings, sentence shape), against the recent videos in
$NAVI_DATA/script-history.jsonl, and across a batch. A script that repeats recent ones fails like any other tell.

Usage: .venv/bin/python scripts/script/check_script.py script.json [--json] [--no-history] [--history PATH]
         [--batch other.json ...] [--record]
(positions are checked against <script folder>/explore, or the folder(s) in the script's "explore")
Exit code 1 if there are errors.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
CONFIG = json.load(open(os.path.join(ROOT, 'config', 'defaults.json')))
WPS = CONFIG['voice'].get('reference_pace_wps') or 3.0     # words per second of the approved voice
MAX_STILL = CONFIG['recording']['max_still_s']
KINDS = {'explain', 'click', 'hunt', 'wait'}
TRAVEL = 0.75   # the cursor starts moving about this long before a click or hover lands on its word (record.py LEAD)
MOVES = {'click', 'hover', 'highlight', 'type_into'}
# when a word is spoken, from the start of its section (fitted on the voice's real word times, 12 Nov 2026: 80 cues):
# about 0.26 s a word, plus 0.30 s for each comma, colon or dash and 0.79 s for each full stop before it
SEC_PER_WORD, SEC_PER_COMMA, SEC_PER_STOP = 0.26, 0.30, 0.79
POINTER_BUSY = 1.2     # how long one click or hover keeps the cursor busy (find, travel, land) on a slow page
CROWDED_LATE = 1.0     # predicted lateness over this is an error: the take would land it more than 0.5 s off


def spoken_at(raw_words, i):
    """Estimated seconds from the start of a section to its i-th word."""
    before = raw_words[:i]
    return (SEC_PER_WORD * i + SEC_PER_COMMA * sum(w.endswith((',', ';', ':', '—', '–')) for w in before)
            + SEC_PER_STOP * sum(w.endswith(('.', '?', '!')) for w in before))
FILLERS = {'uh', 'um', 'er', 'erm', 'uhh', 'umm', 'hmm', 'mm', 'ah'}
CHEERFUL = re.compile(r"^(?:and\s+|so\s+|okay,?\s+)?(?:easy|easy peasy|there we go|there it is|there you go|here we go|done|perfect|"
                      r"nice|great|awesome|boom|voil[aà]|simple|simple as that|that'?s it|ta-?da|sweet|lovely|cool|amazing|"
                      r"bingo|nailed it|all done|job done)[.!]*$", re.I)
RESULT = re.compile(r"\b(?:and|so)\s+(?:it'?s|that'?s|they'?re)\s+(?:on the list|saved|added|done|there|in(?=\s*(?:now\b|[,.!?]|$))|ready|live|"
                    r"created|updated|gone|crossed out)\b(?:\s+now)?", re.I)
# hooks, teasers, selling, knowing asides, performed slips: found by move, not by string (moves.py; Andy, 12 Nov 2026)
from moves import find_moves  # noqa: E402
# "there we go": only inside a sentence (words before it and after it), never its own line or a sentence start
THERE_WE_GO = re.compile(r"\bthere we go\b", re.I)
CLOSERS = [r"so that'?s one", r"so yeah", r"\bokay\.$", r"\ball right\.$"]
SWEARS = re.compile(r"\b(?:damn|hell|sucks?|shit|crap|fuck\w*|oh my god)\b", re.I)
RESTART = re.compile(r"\b((?:\w+'\w+|\w+)(?: (?:\w+'\w+|\w+))?),?\s+(?:(?:uh|um|er),?\s+)?\1\b", re.I)
CUTOFF = re.compile(r"\b(\w+)-\s+\1", re.I)
TAG = re.compile(r'\[([^\]]+)\]')


def sentences(text):
    return [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]


def words(text):
    return re.findall(r"[\w'’-]+", TAG.sub('', text))


def check(script, base=None, history=None, batch=None, variety_checks=True):
    """base: the script's folder, where its explore data is found (positions are an error when it can't be checked).
    history: feature dicts of recent videos (default: the history file); batch: feature dicts of the batch's other
    scripts; variety_checks=False skips the variety checks (only the single-script tells)."""
    issues = []

    def add(level, code, section, msg):
        issues.append({'level': level, 'code': code, 'section': section, 'message': msg})

    sw = (script.get('settings') or {}).get('swear', 0)
    closers_used = []
    secs = script.get('sections') or []
    if not secs:
        add('error', 'structure', None, 'The script has no sections.')
    for si, sec in enumerate(secs):
        name = sec.get('name') or f'section {si + 1}'
        talk, cap = sec.get('talk') or '', sec.get('caption') or ''
        if not talk.strip():
            add('error', 'structure', name, 'No talking version.')
            continue
        if not cap.strip():
            add('error', 'structure', name, 'No caption version.')
        # tags: [relaxed] only, at the start
        for t in TAG.findall(talk):
            if t.strip().lower() != 'relaxed':
                add('error', 'tag', name, f'Performance tag [{t}]: only [relaxed] is allowed (voice-rules.md 2).')
        if not talk.lstrip().lower().startswith('[relaxed]'):
            add('warning', 'tag', name, 'The talking version should start with [relaxed].')
        plain = TAG.sub('', talk).strip()
        if '…' in plain or '...' in plain:
            add('error', 'ellipsis', name, '"…" stretches the word before it instead of pausing. Write the hesitation into the sentence, in a slot this video hasn\'t used (voice-rules.md, Fillers).')
        sents = sentences(plain)
        for s in sents:
            bare = re.sub(r'["“”]', '', s).strip()
            if CHEERFUL.match(bare) or (len(words(bare)) <= 3 and bare.endswith('!')):
                add('error', 'cheerful-line', name, f'"{bare}" reads as fake joy. Use something flatter ("yeah, that\'s it") or just move on.')
            toks = [w.lower() for w in words(bare)]
            if toks and all(t in FILLERS or t in {'okay', 'so'} for t in toks) and any(t in FILLERS for t in toks):
                add('error', 'filler-sentence', name, f'"{bare}" is a filler written as its own sentence. Attach it to the word before, inside a sentence.')
            for m in ([] if CHEERFUL.match(bare) else THERE_WE_GO.finditer(bare)):
                before, after = words(bare[:m.start()]), words(bare[m.end():])
                if len(before) < 2 or len(after) < 3:
                    add('error', 'there-we-go', name, f'"{bare}": "there we go" only goes inside a sentence, with words before it and after it '
                        '("I hit save and there we go, it\'s on the list"), never as its own line or the start of one.')
            for move, why, hit in find_moves(bare):
                add('error', 'catchphrase', name, f'"{hit}" ({move}): {why}. Say what\'s on screen, plainly.')
            if RESULT.search(bare):
                add('warning', 'result-line', name, f'"{RESULT.search(bare).group(0)}" announces the result; the screen already shows it.')
            if re.match(r'^if i (?:click|press|hit|tap)', bare, re.I):
                add('warning', 'if-i-click', name, f'"{bare[:40]}…": "If I click…" framing sounded unnatural.')
        # more than one repair in a section: counted by variety.py (every kind of repair, not only repeats)
        if CUTOFF.search(plain):
            add('error', 'cut-off', name, f'"{CUTOFF.search(plain).group(0)}": never cut a word off; drop the whole word and start the clause again, or use another kind of repair (voice-rules.md, Repairs).')
        last = words(plain)[-1].lower() if words(plain) else ''
        if last in FILLERS:
            add('warning', 'filler-end', name, 'Ends on a filler, which sounds unfinished.')
        if sents and (sents[-1].endswith('?') or re.search(r'and yeah,? it\'?s \w+\W*$', sents[-1], re.I)):
            add('warning', 'rising-end', name, f'The last line ("{sents[-1][-40:]}") invites a rise; the last line of a section should end low.')
        for c in CLOSERS:
            if sents and re.search(c, sents[-1], re.I):
                closers_used.append((name, c))
        if sw == 0 and SWEARS.search(plain):
            add('warning', 'swear', name, f'"{SWEARS.search(plain).group(0)}": swearing is off for this script.')
        if FILLERS & {w.lower() for w in words(cap)} or TAG.search(cap) or SWEARS.search(cap) or '…' in cap or '...' in cap:
            add('error', 'structure', name, 'The caption must be clean: no fillers, tags, "…" or swears.')
        # section length
        secs_long = len(words(plain)) / WPS
        if secs_long > 35 * 1.15 or secs_long < 10 * 0.6:
            add('warning', 'section-length', name, f'About {secs_long:.0f} s of talk; sections work best at 15 to 35 s.')
        if si == 0 and secs_long > 14:
            add('warning', 'opening', name, f'The opening section is about {secs_long:.0f} s; keep the open to about 10 to 12 s.')
        # actions: cue words in order, kinds, and the still-screen estimate
        toks = [re.sub(r"[^\w'’-]", '', w).lower() for w in words(plain)]
        pos, marks, travel = 0, [0], set()
        for a in sec.get('actions', []):
            if a.get('kind') not in KINDS:
                add('error', 'structure', name, f'Action "{a.get("do")}" on "{a.get("on")}" needs a kind: explain, click, hunt or wait.')
            on = (a.get('on') or '').strip()
            if on.lower() in {'start', 'end'}:
                if on.lower() == 'end':
                    marks.append(len(toks))
                continue
            cue = [re.sub(r"[^\w'’-]", '', w).lower() for w in on.split()]
            found = next((i for i in range(pos, len(toks) - len(cue) + 1) if toks[i:i + len(cue)] == cue), None)
            if found is None:
                add('error', 'structure', name, f'The cue "{on}" for {a.get("do")} isn\'t in the talking version (after the previous cue).')
                continue
            pos = found + len(cue)
            marks.append(found)
            if a.get('do') in MOVES or (a.get('do') == 'type' and a.get('into')):
                travel.add(found)
            if a.get('do') == 'type' and a.get('text'):   # typing keeps the screen moving for a while
                marks.append(min(len(toks), found + max(1, round(len(a['text']) / 8))))
        marks.append(len(toks))
        # crowded: pointing actions too close together, so each one starts late and the lateness adds up
        raw = TAG.sub('', sec.get('talk', '')).split()
        rtok = [re.sub(r"[^\w'’-]", '', w).lower() for w in raw]
        rpos, free = 0, None
        for a in sec.get('actions', []):
            on = (a.get('on') or '').strip()
            if on.lower() in {'start', 'end'}:
                continue
            cue = [re.sub(r"[^\w'’-]", '', w).lower() for w in on.split()]
            f = next((i for i in range(rpos, len(rtok) - len(cue) + 1) if rtok[i:i + len(cue)] == cue), None)
            if f is None:
                continue
            rpos = f + len(cue)
            if not (a.get('do') in MOVES or (a.get('do') == 'type' and a.get('into'))):
                continue
            t = spoken_at(raw, f)
            land = t if free is None else max(t, free)
            if land - t > CROWDED_LATE:
                add('error', 'crowded', name, f'The {a.get("do")} on "{on}" comes too soon after the pointing before it: with those '
                    f'stacked up, it would land about {land - t:.1f} s after its word, and the take would fail. Put more words between '
                    'them (a clause, or a comma pause), or drop one of the hovers.')
            free = land + POINTER_BUSY
        marks = sorted(set(marks))
        for a, b in zip(marks, marks[1:]):
            gap = (b - a) / WPS - (TRAVEL if b in travel else 0)
            if gap > MAX_STILL:
                stretch = ' '.join(words(plain)[a:b])
                add('error', 'still-screen', name, f'About {gap:.1f} s of talk with nothing happening on screen: "{stretch[:90]}{"…" if len(stretch) > 90 else ""}". '
                    'Add an action in it (a hover, a scroll), or cut or split it.')
    for (n1, c1), (n2, c2) in zip(closers_used, closers_used[1:]):
        if c1 == c2:
            add('warning', 'closer', n2, 'Same closer as the section before. Most sections should just stop on the action.')
    for c in CLOSERS:
        k = sum(1 for _, x in closers_used if x == c)
        if k > 2:
            add('warning', 'closer', None, f'The closer "{c.strip(chr(92) + "b.$")}" ends {k} sections; at most once or twice a video.')
    sys.path.insert(0, HERE)
    import positions
    for level, sec, msg in positions.check(script, base):
        add(level, 'position', sec, msg)
    # NAVI_VARIETY_OFF: for tests that reuse one recorded script on purpose (test_batch.py) only; variety has its own
    # test (scripts/script/test_variety.py)
    if variety_checks and not os.environ.get('NAVI_VARIETY_OFF'):
        import variety
        issues += variety.check(script, history=history, batch=batch)
    return issues


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('script')
    ap.add_argument('--json', action='store_true')
    ap.add_argument('--no-history', action='store_true', help='skip the check against recent videos')
    ap.add_argument('--history', help='a script-history.jsonl other than $NAVI_DATA\'s')
    ap.add_argument('--batch', nargs='*', default=[], help='the other scripts in this batch')
    ap.add_argument('--record', action='store_true', help='add this script to the history (done by generate.py --yes)')
    a = ap.parse_args()
    sys.path.insert(0, HERE)
    import variety
    script = json.load(open(a.script))
    hist = [] if a.no_history else (variety.load_history(a.history, script.get('voice_id'), variety.script_id(script)) if a.history else None)
    batch = [variety.features(json.load(open(p))) for p in a.batch] or None
    issues = check(script, os.path.dirname(os.path.abspath(a.script)), history=hist, batch=batch)
    if a.record:
        variety.record(script, a.history)
    errors = [i for i in issues if i['level'] == 'error']
    if a.json:
        print(json.dumps(issues, indent=1))
    else:
        for i in issues:
            print(f"{'ERROR' if i['level'] == 'error' else 'warn '}  [{i['code']}] {i['section'] or 'script'}: {i['message']}")
        print(f'{len(errors)} errors, {len(issues) - len(errors)} warnings.' if issues else 'No problems found.')
    sys.exit(1 if errors else 0)


if __name__ == '__main__':
    main()
