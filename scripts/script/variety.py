"""NAVI variety: every video must sound like the same person on a different day, not the same recipe.

Andy, 11 Nov 2026 (reference/listening/2026-11-11-everything-sounds-the-same.md): every video opened with a breath
and "Okay, so", every step started "Right, so", the fillers all sat before the thing named and every restart was
"word, uh, same word". The rules had turned single A/B winners into templates. This module measures repetition the
way the checker measures any other tell (design: docs/variety-spec.md, sections 3, 5 and 7):

  features(script)            what a script does at each slot: how each section starts (M0 no marker, M1 run-in
                              marker, M2 marker + comma: the model breathes there, M3 marker + full stop), the
                              opening family, fillers and their slot, repairs and their kind, hunts, hedges, how
                              each section ends, who acts, sentence lengths, 4- to 6-word runs
  check_within(f, script)     repeats inside one script
  check_history(f, window)    repeats against recent videos (the last 12 for this voice)
  check_history(f, batch, batch=True)
                              repeats inside a batch: tighter between neighbours (the 8 nearest videos), looser
                              across the whole batch, so a 30-lesson course doesn't run out of ways to start
  narrator(voice_id)          the narrator card (config/narrators/*.json): the few habits this voice keeps across
                              videos (his filler, his hedge, how he hunts). Habits may repeat across videos at about
                              their rate; nothing else may. One recognisable person on different days.
  history / record            $NAVI_DATA/script-history.jsonl: one line per finished script. $NAVI_DATA is outside
                              the repo (~/Library/Application Support/NAVI by default); record() refuses a path
                              inside the repo, so the history can never be committed.
  mark_real                   only real videos count: a line is compared against once its video is approved or
                              exported (store.update_demo marks it). Test and dev runs (the to-do clip, the whop
                              experiments) are voiced too, but never approved, so they don't restrict real lessons
                              (Andy, 13 Nov 2026). Inside one batch the lessons are still held apart from each other.

Thresholds marked "guess" in the spec are kept as named constants here, to tune after the first batches.
"""
import glob
import hashlib
import json
import os
import re
import time
from collections import Counter

TAG = re.compile(r'\[([^\]]+)\]')
MARKERS = {'okay', 'ok', 'right', 'so', 'now', 'then', 'and', 'well', 'anyway', 'next', 'alright'}
MARKER2 = {('all', 'right'), ('after', 'that'), ('from', 'here'), ('next', 'up')}
FILLER = {'uh', 'um', 'er', 'erm'}
CONJ = {'and', 'but', 'so', 'then', 'because', 'cause', 'or', 'which', 'though'}
DET = {'the', 'a', 'an', 'this', 'that', 'these', 'those', 'your', 'my', 'its', 'to', 'into', 'in', 'on', 'under',
       'about', 'for', 'from', 'with', 'at', 'of'}
SUBJ = {'i', 'you', 'we', 'it', 'they', 'he', 'she', "i'm", "i'll", "i'd", "you're", "you'll", "it's", "we'll", 'can',
        "can't", 'just', 'gonna', 'will', "won't", 'could', 'should'}
HEDGES = ['actually', 'i think', 'probably', 'maybe', 'kind of', 'sort of', 'basically', 'pretty much', 'honestly',
          'to be fair', 'you know', 'go ahead and']
HUNT = re.compile(r"\b(?:where (?:is|did|was|has)\b[^,.?!]*|where's\b[^,.?!]*|where've they put it|which one is it|what's it called|let's see(?=\s*[,.?!])|"
                  r"hang on|one sec|somewhere (?:down|up|over) here|not that one|bear with me|it was here[^,.?!]*|i always lose[^,.?!]*)", re.I)
REPEAT = re.compile(r"\b((?:\w+'\w+|\w+)(?: (?:\w+'\w+|\w+))?),?\s+(?:((?:uh|um|er),?)\s+)?\1\b", re.I)
REPEAT_OK = {'very', 'really', 'so', 'no', 'bye', 'okay', 'one', 'two', 'three', 'four', 'five', 'six'}
SUB = re.compile(r"\b(\w+),\s+(sorry|or rather|no|wait|well),\s+(\w+)", re.I)
REPH = re.compile(r",\s+(?:or,?\s+)?(i mean|or rather),\s+", re.I)
FRESH = re.compile(r"(?:^|[.?!]\s+|,\s+)((?:and|but|so)\s+)?((?:[\w']+\s+){0,3}(?:can|can't|could|will|would|is|it's|"
                   r"that's|there's|i'm|i'll|you|to|the|a))\s*,\s+(so|actually|well|no|anyway|or)\s+", re.I)
INS = re.compile(r"\b(the|a|this) (\w+), \1 (\w+) \2\b", re.I)
NUMWORDS = {'one', 'two', 'three', 'four', 'five', 'first', 'second', 'third', 'fourth', 'fifth'}
STOP = {'the', 'a', 'an', 'it', 'is', 'to', 'and', 'of', 'in', 'on', 'you', 'i', 'that', 'this', 'so', 'just', 'it\'s'}
POSITION = re.compile(r"\b(?:at the (?:top|bottom)(?: of the \w+)?|(?:top|bottom) (?:left|right)|on the (?:left|right)|"
                      r"over on the (?:left|right)|up top|down at the bottom|in the (?:middle|corner))\b", re.I)

# thresholds (spec section 7.3; "guess" ones to tune after the first batches)
WINDOW = 12
FILLER_MAX = {'saas': 2.8, 'course': 1.0, 'tour': 0.5}
SENTENCE_SPREAD_MIN = 0.35       # guess
PERSON_MAX = 0.6                 # guess
REPAIR_KIND_SHORT = 450          # words: under this, one repair kind at most once
BATCH_NEAR = 8                   # in a batch, the videos either side that count as neighbours (a viewer binges these)
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))


# ---- the narrator card -------------------------------------------------------------------------------------------
_CARDS = None


def narrator(voice_id=None):
    """The card for this voice (config/narrators/*.json), or {} when the voice has none."""
    global _CARDS
    if _CARDS is None:
        _CARDS = [json.load(open(p)) for p in sorted(glob.glob(os.path.join(ROOT, 'config', 'narrators', '*.json')))]
    return next((c for c in _CARDS if voice_id and c.get('voice_id') == voice_id), {})


def narrator_by_name(name):
    narrator()
    return next((c for c in _CARDS if name and c.get('name') == name), {})


def phrase_habits(card):
    """The habits that are phrases (hedge, reaction, aside, hunt): [(id, [texts], habit)]."""
    return [(h['id'], h.get('texts') or [h['text']], h) for h in card.get('habits', []) if h.get('kind') != 'filler']


def habit_hits(plain, card):
    low = plain.lower().replace('’', "'")
    return {hid: sum(len(re.findall(r'\b' + re.escape(t) + r'\b', low)) for t in texts)
            for hid, texts, _ in phrase_habits(card)}


def mask_habits(plain, card):
    """The text with the narrator's habit phrases blanked out, so they never count as a repeated phrase."""
    for _, texts, _ in phrase_habits(card):
        for t in texts:
            plain = re.sub(r'\b' + re.escape(t) + r'\b', ' | ', plain, flags=re.I)
    return plain


def plain_of(talk):
    return TAG.sub('', talk or '').strip()


def sentences(text):
    return [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]


def toks_of(text):
    return [w.lower().replace('’', "'") for w in re.findall(r"[\w'’-]+", text)]


def raw_of(text):
    return [w.lower().replace('’', "'") for w in re.findall(r"[\w'’-]+|[.,?!]", text)]


# ---- features ----------------------------------------------------------------------------------------------------
def start_class(plain):
    s = sentences(plain)
    first = toks_of(s[0]) if s else []
    t = toks_of(plain)
    if not t:
        return 'M0', None
    if 1 <= len(first) <= 2 and all(w in MARKERS or w in ('all', 'right') for w in first):
        return 'M3', ' '.join(first)
    pair = tuple(t[:2]) in MARKER2
    marker = ' '.join(t[:2]) if pair else (t[0] if t[0] in MARKERS else None)
    if marker:
        head = plain.lower()[:40]
        if re.match(r"^(okay|ok|right|all right|alright|now|so|well|anyway)\s*,", head) or \
           re.match(r"^(okay|right|all right|alright)\s*,?\s+so\s*,", head):
            return 'M2', marker
        return 'M1', marker
    return 'M0', None


def start_kind(plain):
    s = sentences(plain)
    first = s[0].lower() if s else ''
    rx = [('question', lambda: first.endswith('?')),
          ('scene', r"^(the first time you|when you first|you land|this is where you|right after you|as soon as you (join|open|log in))\b"),
          ('cond', r"^(if|when|once|while|before|after|the first time|as soon as)\b"),
          ('probably', r"^you('ve| have)? probably\b"),
          ('reason', r"^(because|since|quickest|easiest|simplest|the reason)\b"),
          ('opinion', r"^(honestly|personally|i think|i'd|to be fair|the best|the nicest|the only)\b"),
          ('lets', r"^(let's|let me)\b"),
          ('this-is', r"^(?:[\w']+,?\s+){0,2}(this|here)('s| is)\b"),
          ('marker', r"^(okay|ok|right|all right|alright|now|so|well|anyway)\s*[,.]"),
          ('action', r"^(i'm|i'll|i've|i)\b"),
          ('you', r"^(you|your)\b"),
          ('instr', r"^(go|click|open|head|hit|type|pick|scroll|press)\b"),
          ('count', r"^(\d+|one|two|three|four|five)\b"),
          ('wrong', r"^you'?d think\b")]
    for name, r in rx:
        if callable(r) and r():
            return name
        if not callable(r) and re.match(r, first):
            return name
    return 'noun'


def filler_slots(plain, type_texts=()):
    raw = raw_of(plain)
    out = []
    words_only = [(i, w) for i, w in enumerate(raw) if w not in '.,?!']
    # fillers inside a repeat ("book the, uh, book the") belong to the repair, not to a filler slot
    in_repeat = set()
    spans = [m.span() for m in REPEAT.finditer(plain) if m.group(2)]
    for m in re.finditer(r"\b(?:uh|um|er|erm)\b", plain, re.I):
        if any(a <= m.start() < b for a, b in spans):
            in_repeat.add(len(re.findall(r"[\w'’-]+", plain[:m.start()])))
    for k, (i, w) in enumerate(words_only):
        if w not in FILLER:
            continue
        if k in in_repeat:
            out.append({'w': w, 'slot': 'repeat', 'prev': words_only[k - 1][1] if k else None, 'next': None})
            continue
        prev = words_only[k - 1][1] if k > 0 else None
        nxt = words_only[k + 1][1] if k + 1 < len(words_only) else None
        before_prev = raw[words_only[k - 1][0] - 1] if k > 0 and words_only[k - 1][0] > 0 else '.'
        sent_start = k == 0 or raw[i - 1] in '.?!' or (raw[i - 1] == ',' and i >= 2 and raw[i - 2] in '.?!')
        if prev and prev == nxt:
            slot = 'repeat'
        elif sent_start or prev in CONJ or (before_prev in '.?!' and prev in MARKERS):
            slot = 'unit'
        elif prev in {'it', 'call', 'name', 'type', 'pick', 'say', 'like'} and nxt and (any(nxt in t.lower() for t in type_texts)):
            slot = 'value'
        elif prev in DET:
            slot = 'pre-noun'
        elif nxt in CONJ:            # after a clause, before "but / so" carries on
            slot = 'tail'
        elif prev in SUBJ:
            slot = 'pre-verb'
        elif nxt in {'those', 'that', 'it', 'they', 'this', 'these', 'which'} | SUBJ:
            slot = 'topic'
        else:
            slot = 'other'
        out.append({'w': w, 'slot': slot, 'prev': prev, 'next': nxt})
    return out


def repairs_of(plain, declared=()):
    found = []
    taken = []
    for m in REPEAT.finditer(plain):
        g = m.group(1)
        if g.lower() in REPEAT_OK or g[:1].isupper() and m.start() > 0 and plain[m.start() - 1] not in '.!? ':
            continue
        if g[:1].isupper() and not re.match(r"^(I|I'm|I'll|I'd|It|It's|You|The|A|And|So)$", g):
            continue        # an on-screen name ("Hide, and Hide again") is a step, not a slip
        kind = 'rep-f' if m.group(2) else ('rep-2' if ' ' in g else 'rep')
        found.append({'kind': kind, 'words': g.lower()})
        taken.append(m.span())
    for m in SUB.finditer(plain):
        a, b = m.group(1).lower(), m.group(3).lower()
        same = (a in NUMWORDS and b in NUMWORDS) or ({a, b} <= {'click', 'tap', 'press', 'hit'}) or \
               (m.group(1)[:1].isupper() and m.group(3)[:1].isupper()) or (a in DET and b in DET)
        if same:
            found.append({'kind': 'sub', 'words': f'{a}>{b}'})
            taken.append(m.span())
    for m in REPH.finditer(plain):
        before = set(toks_of(plain[:m.start()])[-6:]) - STOP
        after = set(toks_of(plain[m.end():])[:6]) - STOP
        if before & after:
            found.append({'kind': 'reph', 'words': m.group(1).lower()})
            taken.append(m.span())
    for m in FRESH.finditer(plain):
        if any(a <= m.start(2) < b for a, b in taken) or HUNT.search(m.group(0)):
            continue
        found.append({'kind': 'fresh', 'words': m.group(2).strip().lower()})
    for m in INS.finditer(plain):
        found.append({'kind': 'ins', 'words': m.group(0).lower()})
    for d in declared:
        if not any(f['kind'] == d for f in found):
            found.append({'kind': d, 'words': ''})
    return found


def end_class(plain):
    s = sentences(plain)
    last = s[-1].lower() if s else ''
    t = toks_of(last)
    if re.search(r",?\s*(okay|all right|alright|so yeah|anyway)\.$", last):
        return 'word'
    if re.search(r"(so that's \w+|that'll do|which is fine|more or less|for now)\.$", last):
        return 'under'
    if any(w in {'here', 'there', 'top', 'bottom', 'left', 'right', 'list', 'row', 'page', 'form', 'corner', 'side'} for w in t[-4:]):
        return 'place'
    if any(w in NUMWORDS or w.isdigit() for w in t[-6:]):
        return 'count'
    clause = re.split(r',\s*', last)[-1]
    if re.match(r"(you don't|it's not|none of|no need|because|since|i'd)\b", clause):
        return 'reason'
    return 'act'


def person_of(sent):
    s = sent.lower()
    if re.search(r"\blet's\b", s):
        return 'lets'
    if re.search(r"\b(i'm gonna|i'm going to|i'll|let me|i'd|i)\b", s):
        return 'i'
    if re.search(r"\byou\b", s):
        return 'you'
    if re.search(r"\bwe('ll| can)?\b", s):
        return 'we'
    if re.match(r"(go|click|open|head|hit|type|pick|scroll|press)\b", s):
        return 'imp'
    return None


def ngrams(plain, script, n, card=None):
    names = set()
    for sec in script.get('sections', []):
        for a in sec.get('actions', []):
            for k in ('target', 'text'):
                names |= set(toks_of(re.sub(r"[=\[\]'\"()]", ' ', str(a.get(k) or ''))))
    text = POSITION.sub(' | ', mask_habits(plain, card or {}))
    out = set()
    for sent in sentences(text):
        raw = re.findall(r"[\w'’-]+|\|", sent)
        caps = {i for i, w in enumerate(raw) if i > 0 and w[:1].isupper() and w not in ('I', "I'm", "I'll", "I'd")}
        t = [w.lower().replace('’', "'") for w in raw]
        for i in range(len(t) - n + 1):
            span = t[i:i + n]
            if '|' in span or any(j in caps for j in range(i, i + n)) or any(w in names and w not in STOP for w in span):
                continue
            out.add(' '.join(span))
    return out


# ---- the words themselves: skeletons, hinges, tics (Andy, 12 Nov 2026: "compare actual words across videos, not
# opening-type labels"). Two scripts with different opening "families" both opened "what's on screen, so action".
KEEP = {'i', "i'm", "i'll", "i'd", "i've", 'you', "you're", "you'll", "you'd", "you've", 'we', "we'll", "we're", 'it',
        "it's", "it'll", 'that', "that's", 'this', 'there', "there's", 'they', "they're", "let's", 'is', 'are', 'was',
        'be', 'can', 'will', 'would', 'gonna', 'wanna', 'need', 'want', 'have', 'has', 'do', "don't", 'and', 'but', 'so',
        'then', 'now', 'okay', 'right', 'well', 'because', 'or', 'if', 'when', 'once', 'while', 'which', 'the', 'a', 'an',
        'to', 'in', 'on', 'at', 'of', 'for', 'with', 'up', 'down', 'over', 'into', 'from', 'by', 'just', 'really',
        'actually', 'pretty', 'much', 'still', 'already', 'also', 'here', 'uh', 'um', 'my', 'your', 'its', 'one', 'all'}
TICWORDS = {"i'm", "i'll", "i'd", "we'll", "we're", "let's", "it'll", 'gonna', 'just', 'really', 'actually', 'pretty',
            'so', 'but', 'then', 'okay', "it's", "that's", "there's", 'i', 'we'}
HINGE = re.compile(r",\s+(so|and|but|then|which|because|cause)\b", re.I)
LEAD = re.compile(r"^(?:(?:okay|ok|right|all right|alright|so|now|well|and|then)\b[,.]?\s*)+", re.I)


def hinges_of(text):
    """", so" / ", but" / ", then"… joining clauses inside sentences; a marker that starts a sentence ("Okay, so this
    is…") is not a hinge."""
    return [m.group(1).lower() for x in sentences(text) for m in HINGE.finditer(LEAD.sub('', x))]


SOFTENERS = ('just', 'really', 'actually', 'basically', 'literally', 'simply')


def skeleton(sentence):
    """The sentence with its content words blanked: "Nothing on this list yet, so I'm gonna click in the box" ->
    "_ on this _ , so i'm gonna _ in the _"."""
    out = []
    for w in re.findall(r"[\w'’-]+|[,.?!]", sentence):
        t = w.lower().replace('’', "'")
        t = t if t in KEEP or t in ',.?!' else '_'
        if not (t == '_' and out and out[-1] == '_'):
            out.append(t)
    return out


def skel_ratio(a, b):
    import difflib
    return difflib.SequenceMatcher(None, a, b).ratio() if a and b else 0.0


def tics_of(plain):
    t = [w.lower().replace('’', "'") for w in re.findall(r"[\w'’-]+|[,.?!]", plain)]
    t = [x if x != '?' and x != '!' else '.' for x in t]
    out = set()
    for x, y in zip(t, t[1:]):
        if x in TICWORDS and y in TICWORDS and (x, y) not in {('so', 'i'), ('so', 'we'), ('but', 'i'), ('but', 'we')}:
            out.add(f'{x} {y}')
    for x, y, z in zip(t, t[1:], t[2:]):
        if x == ',' and y in ('so', 'but', 'then') and z in TICWORDS | {'you'}:
            out.add(f', {y} {z}')
    return out


def features(script):
    secs = []
    all_sents = []
    words_total = 0
    for sec in script.get('sections', []):
        plain = plain_of(sec.get('talk'))
        t = toks_of(plain)
        words_total += len(t)
        st, marker = start_class(plain)
        types = [a.get('text', '') for a in sec.get('actions', []) if a.get('do') == 'type']
        sents = sentences(plain)
        all_sents += sents
        hunts = [m.group(0).lower().strip() for m in HUNT.finditer(plain)]
        secs.append({'name': sec.get('name'), 'first': t[0] if t else '', 'first2': ' '.join(t[:2]), 'start': st,
                     'marker': marker, 'start_kind': start_kind(plain), 'fillers': filler_slots(plain, types),
                     'repairs': repairs_of(plain, sec.get('repairs', [])), 'hunts': hunts,
                     'hunt_action': any(a.get('kind') == 'hunt' for a in sec.get('actions', [])),
                     'hedges': [h for h in HEDGES for _ in re.finditer(r'\b' + re.escape(h) + r'\b', plain.lower())],
                     'end': end_class(plain), 'last3': ' '.join(t[-3:]), 'last_sentence': (sents[-1].lower() if sents else ''),
                     'person': Counter(p for p in (person_of(s) for s in sents) if p), 'words': len(t),
                     'hinges': hinges_of(plain),
                     'softeners': {w: len(re.findall(r'\b' + w + r'\b', plain.lower())) for w in SOFTENERS},
                     'skels': [' '.join(skeleton(x)) for x in sents], 'sentences_low': [x.lower() for x in sents],
                     'pre_action_fillers': _pre_action(plain, sec.get('actions', []))})
    lens = [len(toks_of(s)) for s in all_sents]
    mean = sum(lens) / len(lens) if lens else 0
    sd = (sum((x - mean) ** 2 for x in lens) / len(lens)) ** 0.5 if lens else 0
    fillers = [f for s in secs for f in s['fillers'] if f['slot'] != 'repeat']
    plain_all = ' '.join(plain_of(s.get('talk')) for s in script.get('sections', []))
    first_t = toks_of(plain_of(script['sections'][0].get('talk'))) if script.get('sections') else []
    style = script.get('style') or {}
    card = narrator(script.get('voice_id'))
    habits = habit_hits(plain_all, card)
    fw = Counter(x['w'] for s in secs for x in s['fillers'])
    return {'title': script.get('title'), 'kind': script.get('kind', 'saas'), 'voice_id': script.get('voice_id'),
            'habits': {k: v for k, v in habits.items() if v}, 'uh': fw['uh'], 'um': fw['um'],
            'section_habits': [habit_hits(plain_of(s.get('talk')), card) for s in script.get('sections', [])],
            'words': words_total, 'sections': secs, 'sentence_lengths': lens, 'sentence_mean': round(mean, 1),
            'sentence_cv': round(sd / mean, 2) if mean else 0,
            'fillers_per_100': round(100 * len(fillers) / words_total, 2) if words_total else 0,
            'opening': {'family': style.get('opening') or (secs[0]['start_kind'] if secs else None),
                        'first': first_t[0] if first_t else '', 'first2': ' '.join(first_t[:2])},
            'sentence_firsts': [' '.join(toks_of(s)[:2]) for s in all_sents],
            'ngrams4': sorted(ngrams(plain_all, script, 4, card)), 'ngrams5': sorted(ngrams(plain_all, script, 5, card)),
            'ngrams6': sorted(ngrams(plain_all, script, 6, card)), 'style': style,
            'open_sentence': sentences(plain_of(script['sections'][0].get('talk')))[0] if script.get('sections') and plain_of(script['sections'][0].get('talk')) else '',
            'open_hinges': sorted(set(hinges_of(sentences(plain_of(script['sections'][0].get('talk')))[0])) - {'and'}) if script.get('sections') and plain_of(script['sections'][0].get('talk')) else [],
            'open_frame': skeleton(sentences(plain_of(script['sections'][0].get('talk')))[0])[:3] if script.get('sections') and plain_of(script['sections'][0].get('talk')) else [],
            'tics': sorted(tics_of(plain_all)),
            'positions': sorted({m.group(0).lower() for m in POSITION.finditer(plain_all)})}



def _pre_action(plain, actions):
    """Fillers that sit right before the word an action fires on, or before typed text: "type, uh, call the dentist"."""
    cues = {str(a.get('on') or '').split(' ')[0].lower() for a in actions if a.get('on') and a.get('on') != 'start'}
    cues |= {str(a.get('text') or '').split(' ')[0].lower() for a in actions if a.get('text')}
    t = [w.lower() for w in re.findall(r"[\w'’-]+", plain)]
    n = sum(1 for i, w in enumerate(t[:-1]) if w in FILLER and t[i + 1] in cues - {''})
    return [n, sum(1 for w in t if w in FILLER)]


def filler_sig(f):
    return f"{f['w']}|{f['slot']}|{f['prev']}"


# ---- checks inside one script ------------------------------------------------------------------------------------
def check_within(f):
    out = []

    def add(level, code, section, msg):
        out.append({'level': level, 'code': code, 'section': section, 'message': msg})

    secs = f['sections']
    n = len(secs)
    kind = f['kind'] if f['kind'] in FILLER_MAX else 'saas'
    firsts = Counter(s['first'] for s in secs if s['first'])
    for w, k in firsts.items():
        if k > 1:
            add('warning' if n >= 6 else 'error', 'start-repeat', None,
                f'{k} sections start with "{w}". No two sections of a video start with the same word (voice-rules.md, How a step starts).')
    breathy = [i for i, s in enumerate(secs) if s['start'] in ('M2', 'M3')]
    if len(breathy) > (1 if n <= 4 else n // 4) or any(b - a == 1 for a, b in zip(breathy, breathy[1:])):
        add('error', 'start-marker', None,
            f'{len(breathy)} sections start with a marker and a comma or full stop ({", ".join(secs[i]["first2"] for i in breathy)}): '
            'the voice breathes in that comma, so every start sounds the same. At most one in a short video, never two in a row; start the rest on what\'s on screen.')
    if n >= 2 and sum(s['start'] == 'M0' for s in secs) < n / 2:
        add('warning', 'start-marker', None, 'Fewer than half the sections start on their content (no marker word).')
    drawn = (f.get('style') or {}).get('opening') in ('marker', 'this-is')
    worn_this = secs and secs[0]['start_kind'] == 'this-is' and secs[0]['first'] in MARKERS     # "So this is", not "This is what…"
    if secs and (secs[0]['start'] in ('M2', 'M3') or worn_this) and not drawn:
        add('warning', 'start-first', secs[0]['name'], f'The video opens "{secs[0]["first2"]}…": that\'s the most worn opening; open on an action, a reason, a question, a condition, where the viewer lands (voice-rules.md, How a video opens).')
    if n >= 3 and all(s['fillers'] or s['repairs'] for s in secs):
        add('error', 'filler-everywhere', None, 'Every section has a filler or a repair. Real narrators have whole stretches without either; leave at least one section clean.')
    fillers = [x for s in secs for x in s['fillers'] if x['slot'] != 'repeat']
    allowed_n = lambda rate: max(1, int(rate * f['words'] / 100 + 0.5)) if rate else 0
    if len(fillers) > allowed_n(FILLER_MAX[kind]):
        add('error', 'filler-rate', None, f'{f["fillers_per_100"]} fillers per 100 words, over the {FILLER_MAX[kind]} a {kind} video gets.')
    want = (f.get('style') or {}).get('filler_rate')
    if want is not None and f['fillers_per_100'] > want + 0.5 and len(fillers) > allowed_n(want + 0.5):
        add('warning', 'filler-rate', None, f'{f["fillers_per_100"]} fillers per 100 words; this video\'s style is about {want}.')
    sigs = Counter(filler_sig(x) for x in fillers)
    for s, k in sigs.items():
        if k > 1:
            add('error', 'filler-slot', None, f'The same filler in the same place twice ({s.replace("|", ", ")}).')
    slots = Counter(x['slot'] for x in fillers)
    if f['words'] < 300 and any(k > 1 for k in slots.values()):
        add('warning', 'filler-slot', None, f'The same filler slot twice in a short script ({", ".join(s for s, k in slots.items() if k > 1)}); spread them: clause start, after the topic, before a value, after a clause.')
    if len(fillers) >= 2 and all(x['slot'] == 'pre-noun' for x in fillers):
        add('warning', 'filler-slot', None, 'Every filler sits just before the thing named ("the, uh, X"). About a third should; most go at a clause start.')
    for s in secs:
        if len(s['repairs']) > 1:
            add('error', 'restarts', s['name'], f'{len(s["repairs"])} repairs ({", ".join(r["kind"] for r in s["repairs"])}): one per section at most, and most sections have none.')
    reps = [r for s in secs for r in s['repairs']]
    with_repair = sum(1 for s in secs if s['repairs'])
    allowed = 1 if kind == 'tour' else max(1, round(n * {'saas': 0.5, 'course': 0.34}[kind]))
    if with_repair > allowed:
        add('warning', 'repair-rate', None, f'Repairs in {with_repair} of {n} sections; that\'s more slips than a real {kind} narrator makes.')
    kinds = Counter(r['kind'] if not r['kind'].startswith('rep') else 'rep' for r in reps)
    if f['words'] < REPAIR_KIND_SHORT and any(k > 1 for k in kinds.values()):
        add('error', 'repair-shape', None, f'The same kind of repair twice ({", ".join(k for k, v in kinds.items() if v > 1)}). Use another kind: a repeat, an abandoned start, a correction, a rephrase.')
    rw = Counter(r['words'] for r in reps if r['kind'].startswith('rep'))
    for w, k in rw.items():
        if k > 1:
            add('error', 'repair-shape', None, f'"{w}" is repeated as a slip {k} times.')
    hunts = [h for s in secs for h in s['hunts']]
    if len(hunts) > 1:
        add('error', 'hunt', None, f'{len(hunts)} hunts; real narrators hunt about once in 20 to 30 minutes. One at most, only where it\'s really hard to find.')
    if hunts and kind in ('course', 'tour'):
        add('error', 'hunt', None, f'A hunt ("{hunts[0]}") in a {kind} video; hunts belong in casual SaaS demos only.')
    hedges = Counter(h for s in secs for h in s['hedges'])
    for h, k in hedges.items():
        if k > 2 and f['words'] < 300:
            add('warning', 'hedge-repeat', None, f'"{h}" {k} times; rotate hedges (actually, I think, kind of, honestly, pretty much…).')
    ends = [s['end'] for s in secs]
    for i, (a, b) in enumerate(zip(ends, ends[1:])):
        if a == b and a != 'act':
            add('warning', 'closer', secs[i + 1]['name'], f'Two sections in a row end the same way ({a}).')
    if sum(e in ('under', 'word') for e in ends) > 2:
        add('warning', 'closer', None, 'More than two sections end on a closer; most just stop on the action.')
    last3 = Counter(s['last3'] for s in secs)
    for l3, k in last3.items():
        if k > 1:
            add('error', 'end-repeat', None, f'Two sections end "…{l3}".')
    sf = Counter(x for x in f['sentence_firsts'] if x)
    for x, k in sf.items():
        if k > 2:
            add('warning', 'sentence-start', None, f'{k} sentences start "{x}…".')
    if len(f['sentence_lengths']) >= 8:
        firstw = Counter(x.split(' ')[0] for x in f['sentence_firsts'] if x)
        if firstw.get('so', 0) > 0.25 * len(f['sentence_lengths']) or firstw.get('and', 0) > 0.33 * len(f['sentence_lengths']):
            add('warning', 'sentence-start', None, 'Too many sentences start with "so" or "and".')
    lens = f['sentence_lengths']
    if len(lens) >= 6 and f['sentence_cv'] < SENTENCE_SPREAD_MIN and (f.get('style') or {}).get('sentences') != 'long':
        add('warning', 'sentence-shape', None, f'Sentence lengths barely vary (spread {f["sentence_cv"]}); mix long run-ons with a short line.')
    if any(all(x < 8 for x in lens[i:i + 3]) for i in range(len(lens) - 2)):
        add('warning', 'sentence-shape', None, 'Three short sentences in a row: the clipped pattern that sounded weakest (E2).')
    pc = Counter()
    for s in secs:
        pc.update(s['person'])
    lead = ((f.get('style') or {}).get('person') or [None])[0]
    top = pc.most_common(1)[0][0] if pc else None
    if sum(pc.values()) >= 6 and max(pc.values()) / sum(pc.values()) > (0.75 if top == lead else PERSON_MAX):
        add('warning', 'person', None, f'"{pc.most_common(1)[0][0]}" does almost every action; mix you, I, let\'s, plain instructions.')
    card = narrator(f.get('voice_id'))
    for hid, texts, h in phrase_habits(card):
        k = f.get('habits', {}).get(hid, 0)
        if k > h.get('max_per_video', 1):
            add('error', 'habit', None, f'"{texts[0]}" {k} times. It\'s one of {card["name"]}\'s habits: once in a video at most, and not in every video.')
        for s in secs:
            if any(re.search(r'\b' + re.escape(t) + r'\W*$', s['last_sentence']) for t in texts):
                add('error', 'habit-place', s['name'], f'Ends on "{texts[0]}". A habit is said in passing, mid-sentence; ending on it turns it into a catchphrase.')
    if any(h.get('kind') == 'filler' and h.get('text') == 'uh' for h in card.get('habits', [])) and \
            f.get('uh', 0) + f.get('um', 0) >= 3 and f.get('um', 0) > f.get('uh', 0):
        add('warning', 'habit', None, f'More "um" than "uh". {card["name"]}\'s filler is "uh"; "um" only where a real pause follows.')
    st = f.get('style') or {}
    if st and 'habits' in st:
        for hid in f.get('habits', {}):
            if hid not in st['habits'] and hid != 'hunt':
                add('warning', 'style', None, f'Uses the habit "{hid}", which this video\'s style doesn\'t bring out today ({", ".join(st["habits"]) or "none"}).')
    if not st:
        add('warning', 'style', None, 'No "style" (the style of the day): draw one with scripts/script/style.py before writing.')
    else:
        for s in secs:
            if s['marker'] and s['marker'] in st.get('markers_resting', []):
                add('warning', 'style', s['name'], f'Starts with "{s["marker"]}", which this video\'s style rests.')
            if s['start'] in ('M2', 'M3') and 'breath_sections' in st and s['name'] not in st['breath_sections']:
                add('warning', 'style', s['name'], f'Starts "{s["first2"]}," (a breath start), which this video\'s style keeps for {", ".join(st["breath_sections"]) or "no section"}.')
    # the words themselves (12 Nov 2026)
    hinge_secs = Counter(h for x in secs for h in set(x.get('hinges', [])) if h != 'and')
    for h, n in hinge_secs.items():
        if len(secs) >= 3 and n / len(secs) >= 0.6:
            add('error' if n / len(secs) >= 0.75 else 'warning', 'hinge', None,
                f'", {h}" joins clauses in {n} of {len(secs)} sections: it becomes the hinge of the whole video. Join them other ways, or start a new sentence.')
    for x in secs:
        for w, n in (x.get('softeners') or {}).items():
            if n >= 2:
                add('warning', 'repeat-word', x['name'], f'"{w}" {n} times in one section.')
    offer = [x['name'] for x in secs if any(re.match(r"^(?:it|it'll|it's|there's|you get|we get|it gives|it offers|it asks)\b[^.]*,\s+but\b", y)
                                           for y in [z.replace('’', "'") for z in x.get('sentences_low', [])])]
    if len(offer) >= 2:
        add('warning', 'same-move', None, f'"It offers X, but I…" in {", ".join(offer)}: the same move twice.')
    return out


# ---- checks against recent videos / a batch -----------------------------------------------------------------------
def _close_profiles(a, b):
    if not a or not b:
        return False
    keys = ['opening', 'lead_marker', 'filler_band', 'filler_slot', 'repair_kind', 'sentences', 'person', 'hedge']
    same = sum(1 for k in keys if a.get(k) is not None and a.get(k) == b.get(k))
    return same > 4


GENERIC_FIRST = {'the', 'a', 'an', 'you', "you're", "you've", 'i', "i'm", "i'll", "i'd", 'it', "it's", 'this', 'that',
                 "that's", "there's", 'there', 'we', "we'll", 'your', 'my'}


def open_key(op):
    """The opening's first word, or its first two when the first is a word every other sentence starts with."""
    return op['first2'] if op['first'] in GENERIC_FIRST else op['first']


def start_key(s):
    """What counts as "the same start" for a section: the marker word for a marker start, the first two words for a
    start on content ("you can", "the price"), where single words like "the" or "you" are bound to recur."""
    return s['first'] if s['start'] != 'M0' else s['first2']


def _near(f, others, k=BATCH_NEAR):
    """The batch videos closest to this one in batch order (positions in 'pos'), else the last k."""
    if f.get('pos') is not None and all(w.get('pos') is not None for w in others):
        return sorted([w for w in others if abs(w['pos'] - f['pos']) <= k], key=lambda w: (abs(w['pos'] - f['pos']), w['pos']))
    return list(others)[-k:]


def _before(f, others):
    if f.get('pos') is not None and all(w.get('pos') is not None for w in others):
        return sorted([w for w in others if w['pos'] < f['pos']], key=lambda w: w['pos'])
    return list(others)


def check_history(f, window, batch=False):
    """window: feature dicts of earlier scripts, newest last. batch=True applies the batch rules: tight between
    neighbours (the BATCH_NEAR nearest in batch order), shares across the whole batch."""
    out = []
    pre = 'batch-' if batch else ''

    def add(level, code, section, msg):
        out.append({'level': level, 'code': code, 'section': section, 'message': msg})

    if not window or (len(window) < 2 and not batch):
        return out
    secs = f['sections']

    def names(ws):
        shown = ', '.join(f'"{w["title"]}"' for w in ws[:3])
        return shown + (f' and {len(ws) - 3} more' if len(ws) > 3 else '')
    op = f['opening']
    near = _near(f, window) if batch else window
    if batch:
        same_first = [w for w in near if open_key(w['opening']) == open_key(op)]
        if same_first:
            add('error', 'batch-open', None, f'Opens with "{open_key(op)}", like {names(same_first)} near it in this batch.')
        same_fam = [w for w in _near(f, window, 5) if w['opening']['family'] == op['family']]
        if same_fam:
            add('error', 'batch-open', None, f'Opens the same way ({op["family"]}) as {names(same_fam)} near it in this batch.')
        n_all = len(window) + 1
        fam_all = sum(1 for w in window if w['opening']['family'] == op['family']) + 1
        if n_all >= 10 and fam_all > max(2, round(0.12 * n_all)):
            add('warning', 'batch-open', None, f'{fam_all} of the {n_all} videos in this batch open the same way ({op["family"]}).')
        if op['family'] in ('marker', 'this-is') and any(w['opening']['family'] in ('marker', 'this-is') for w in _near(f, window, 6)):
            add('error', 'batch-open', None, 'A "marker" or "So this is…" opening next to another one in this batch; at most one in six.')
    else:
        last8 = window[-8:]
        hit = [w for w in last8 if w['opening']['first2'] == op['first2']]
        if hit:
            add('error', 'open-repeat', None, f'Opens "{op["first2"]}…", like {names(hit)}.')
        if sum(1 for w in window[-5:] if open_key(w['opening']) == open_key(op)) >= 2:
            add('error', 'open-repeat', None, f'"{open_key(op)}" already opened two of the last five videos.')
        elif open_key(window[-1]['opening']) == open_key(op):
            add('warning', 'open-repeat', None, f'Same first words as the last video ("{open_key(op)}").')
        fam = op['family']
        if window[-1]['opening']['family'] == fam or sum(1 for w in window[-6:] if w['opening']['family'] == fam) >= 3:
            add('error', 'open-family', None, f'Opens the same way ({fam}) as the last video, or as half of the last six.')
        if fam in ('marker', 'this-is') and sum(1 for w in window[-5:] if w['opening']['family'] in ('marker', 'this-is')) >= 1:
            add('error', 'open-family', None, 'A "marker" or "So this is…" opening again; at most one video in six opens that way.')
        if op['first'] in ('okay', 'ok') and sum(1 for w in window[-7:] if w['opening']['first'] in ('okay', 'ok')) >= 1:
            add('error', 'open-family', None, '"Okay" opened one of the last eight videos already.')
    # same marker in the same slot
    for k, s in enumerate(secs):
        key = start_key(s)
        same_in = lambda ws: [w for w in ws if len(w['sections']) > k and start_key(w['sections'][k]) == key]
        if batch:
            same = same_in(near)
            if len(same) + 1 >= 2 and (len(same) + 1) > max(1, (len(near) + 1) / 4):
                add('error', 'batch-slot', s['name'], f'Section {k + 1} starts "{key}" in {len(same) + 1} neighbouring videos of this batch.')
            if s['start'] != 'M0' and len(window) >= 9 and len(same_in(window)) + 1 > 0.3 * (len(window) + 1):
                add('warning', 'batch-slot', s['name'], f'Section {k + 1} starts with "{key}" in {len(same_in(window)) + 1} of the {len(window) + 1} videos in this batch.')
            continue
        same = same_in(window[-4:])
        level = 'error' if s['start'] != 'M0' else 'warning'
        if len(same) >= 2:
            add(level, 'slot-marker', s['name'], f'Section {k + 1} starts "{key}", as it did in {names(same)}.')
        elif window[-1]['sections'][k:k + 1] and start_key(window[-1]['sections'][k]) == key:
            add('warning', 'slot-marker', s['name'], f'Section {k + 1} starts "{key}", as in the last video.')
    if len(secs) >= 2 and not batch:
        seq = (start_key(secs[0]), start_key(secs[1]))
        hit = [w for w in window[-5:] if len(w['sections']) >= 2 and (start_key(w['sections'][0]), start_key(w['sections'][1])) == seq]
        if hit:
            add('error', 'start-sequence', None, f'Sections 1 and 2 start "{seq[0]} … {seq[1]}", like {names(hit)}.')
    # breath starts: the same marker + comma anywhere in the video, in neighbouring videos of a batch
    if batch:
        for s in secs:
            if s['start'] in ('M2', 'M3'):
                same = [w for w in _near(f, window) if any(x['start'] in ('M2', 'M3') and x['first'] == s['first'] for x in w['sections'])]
                if len(same) >= 2:
                    add('error', 'batch-breath', s['name'], f'"{s["first2"]}," with its breath already starts a step in {names(same)} nearby; start this one on its content.')
    # phrases
    mine6, mine5, mine4 = set(f['ngrams6']), set(f['ngrams5']), set(f['ngrams4'])
    for w in window:
        shared = mine6 & set(w.get('ngrams6', []))
        if shared:
            add('error', 'phrase-repeat', None, f'"{sorted(shared)[0]}" is word for word from "{w["title"]}".')
        if batch and w in near:
            s5 = mine5 & set(w.get('ngrams5', []))
            if s5 and not shared:
                add('warning', 'batch-phrase', None, f'"{sorted(s5)[0]}" also appears in "{w["title"]}" in this batch.')
    if not batch:
        c4 = Counter(g for w in window for g in set(w.get('ngrams4', [])) & mine4)
        for g, k in c4.items():
            if k >= 2:
                add('warning', 'phrase-repeat', None, f'"{g}" is in {k} recent videos.')
    # fillers
    mine = Counter(filler_sig(x) for s in secs for x in s['fillers'] if x['slot'] != 'repeat')
    for sig in mine:
        k = sum(1 for w in window[-6:] if sig in {filler_sig(x) for s in w['sections'] for x in s['fillers']})
        if k >= 3:
            add('error', 'filler-pattern', None, f'The filler "{sig.replace("|", ", ")}" was in {k} of the last six videos.')
        elif window[-1] and sig in {filler_sig(x) for s in window[-1]['sections'] for x in s['fillers']}:
            add('warning', 'filler-pattern', None, f'The filler "{sig.replace("|", ", ")}" was in the last video too.')
    pool = [x for w in window + [f] for s in w['sections'] for x in s['fillers'] if x['slot'] != 'repeat']
    if len(pool) >= 6:
        slots = Counter(x['slot'] for x in pool)
        top, k = slots.most_common(1)[0]
        if k / len(pool) > 0.5:
            add('error', 'filler-spread', None, f'{k} of {len(pool)} recent fillers are "{top}". Real narrators put most at a clause start, about a third before the thing named.')
        elif len(pool) >= 8 and (slots['pre-noun'] / len(pool) > 0.4 or slots['unit'] / len(pool) < 0.25):
            add('warning', 'filler-spread', None, f'Recent fillers: {dict(slots)} (target: about 45% clause start, a third before the thing named).')
    # repairs
    rk = [r['kind'] for s in secs for r in s['repairs']]
    had = [w for w in window if any(s['repairs'] for s in w['sections'])][-2:]
    if rk and len(had) == 2 and all(any(r['kind'] == rk[0] for s in w['sections'] for r in s['repairs']) for w in had):
        add('warning', 'repair-pattern', None, f'The same kind of repair ({rk[0]}) as the last two videos.')
    rpool = [r['kind'] for w in window + [f] for s in w['sections'] for r in s['repairs']]
    if len(rpool) >= 5:
        reps = sum(1 for r in rpool if r.startswith('rep'))
        if reps / len(rpool) > 0.6 or rpool.count('rep-f') / len(rpool) > 0.4:
            add('error', 'repair-spread', None, f'{reps} of {len(rpool)} recent repairs are repeats ({rpool.count("rep-f")} with a filler between). Use abandoned starts, corrections and rephrases too.')
    # hunts
    card = narrator(f.get('voice_id'))
    habit_hunts = {t for hid, texts, h in phrase_habits(card) if h['kind'] == 'hunt' for t in texts}
    myh = {h for s in secs for h in s['hunts'] if h not in habit_hunts}
    for w in window:
        if myh & {h for s in w['sections'] for h in s['hunts']}:
            add('error', 'hunt-repeat', None, f'The hunt "{sorted(myh & {h for s in w["sections"] for h in s["hunts"]})[0]}" was already in "{w["title"]}".')
    if myh and not batch and sum(1 for w in window[-3:] if any(s['hunts'] for s in w['sections'])) >= 2:
        add('warning', 'hunt-repeat', None, 'Hunts in most of the recent videos; real narrators hunt about once in 20 to 30 minutes.')
    # the narrator's habits: allowed across videos, at about their rate, never in a run
    prev = _before(f, window) if batch else window
    for hid, texts, h in phrase_habits(card):
        if h['kind'] == 'hunt' or not f.get('habits', {}).get(hid):
            continue
        if len(prev) >= 3 and all(w.get('habits', {}).get(hid) for w in prev[-3:]):
            add('error', 'habit-rate', None, f'"{texts[0]}" was in each of the last three videos too. It\'s {card["name"]}\'s habit, at about {round(100 * h.get("rate", 0.3))}% of videos, so not every time.')
        last10 = prev[-10:]
        used = sum(1 for w in last10 if w.get('habits', {}).get(hid)) + 1
        if len(last10) >= 5 and used / (len(last10) + 1) > h.get('rate', 0.3) + 0.25:
            add('warning', 'habit-rate', None, f'"{texts[0]}" is in {used} of the last {len(last10) + 1} videos; it\'s meant for about {round(100 * h.get("rate", 0.3))}%.')
    # no "identity" nudge any more: his "uh" and his manner carry him; pushing a phrase in made catchphrases (12 Nov 2026)
    # the words themselves, against the last few videos (or the batch neighbours): not the family labels
    recent = (near if batch else window[-6:])
    prev1 = (near[-1:] if batch else window[-1:])
    # The whole-sentence skeleton ratio was tried and dropped (12 Nov 2026): it scored the pair Andy heard as alike
    # ("Nothing on this list yet, so I'm gonna…" / "Products is the page…, so it's Create product") at 0.38, and
    # unrelated openings up to 0.8. What that pair shares is the turn: ", so" in the first line. That is checked.
    if f.get('open_sentence'):
        mine = set(f.get('open_hinges', []))
        for w in recent[-3:]:
            both = mine & set(w.get('open_hinges', []))
            if both:
                h = sorted(both)[0]
                add('error', f'{pre}open-hinge', None, f'The first line turns on ", {h}" like "{w["title"]}"\'s: '
                    f'"{f["open_sentence"][:60]}" / "{w.get("open_sentence", "")[:60]}". Open another way.')
            fr = f.get('open_frame') or []
            if fr and fr == (w.get('open_frame') or []) and sum(1 for t in fr if t not in ('_', ',', '.')) >= 2:
                add('warning', f'{pre}open-frame', None, f'Starts "{" ".join(fr)}…" like "{w["title"]}".')
            if w['opening'].get('first') and w['opening']['first'] == f['opening'].get('first'):
                add('warning', f'{pre}open-first', None, f'First word "{f["opening"]["first"]}", like "{w["title"]}".')
    for w in prev1:
        shared = sorted(set(f.get('tics', [])) & set(w.get('tics', [])))
        if shared:
            add('error' if len(shared) >= 3 else 'warning', f'{pre}tic-repeat', None,
                f'Same little phrases as "{w["title"]}": {", ".join(chr(34) + x + chr(34) for x in shared)}.')
        pos = sorted(set(f.get('positions', [])) & set(w.get('positions', [])))
        if pos:
            add('warning', f'{pre}position-repeat', None, f'Says {", ".join(chr(34) + x + chr(34) for x in pos)} like "{w["title"]}": place things another way.')
        top = lambda g: (Counter(h for x in g['sections'] for h in x.get('hinges', []) if h != 'and').most_common(1) or [(None, 0)])[0][0]
        if top(f) and top(f) == top(w):
            add('warning', f'{pre}hinge-repeat', None, f'", {top(f)}" is the main hinge here and in "{w["title"]}".')
        mine = [sum(x) for x in zip(*[s.get('pre_action_fillers', [0, 0]) for s in secs])] or [0, 0]
        theirs = [sum(x) for x in zip(*[s.get('pre_action_fillers', [0, 0]) for s in w['sections']])] or [0, 0]
        if mine[1] and mine[0] == mine[1] and theirs[1] and theirs[0] == theirs[1]:
            add('warning', f'{pre}filler-place', None, f'Every filler sits right before a typed or clicked value, as in "{w["title"]}".')
    # endings
    if secs:
        for w in window:
            if w['sections'] and w['sections'][-1]['last_sentence'] == secs[-1]['last_sentence']:
                add('error', 'end-repeat', None, f'The last line is the same as "{w["title"]}"\'s.')
        recent3 = {s['last3'] for w in window for s in w['sections']}
        for s in secs:
            if s['last3'] in recent3 and not batch:
                add('warning', 'end-repeat', s['name'], f'Ends "…{s["last3"]}", like a recent video.')
    # shape and profile
    if not batch and len(window) >= 2 and f['fillers_per_100'] > 0:
        close = lambda w: abs(w['fillers_per_100'] - f['fillers_per_100']) <= 0.3 and w['sentence_mean'] and \
            abs(w['sentence_mean'] - f['sentence_mean']) <= 0.1 * w['sentence_mean'] and abs(w['sentence_cv'] - f['sentence_cv']) <= 0.1 * max(w['sentence_cv'], 0.01)
        if close(window[-1]) and close(window[-2]):
            add('warning', 'same-shape', None, 'Filler rate and sentence lengths match the last two videos; change the rhythm.')
    prof = (f.get('style') or {}).get('profile')
    if prof:
        others = near if batch else window[-1:]
        for w in others:
            if _close_profiles(prof, (w.get('style') or {}).get('profile')):
                add('error', f'{pre}profile' if batch else 'same-profile', None, f'The style of the day is too close to "{w["title"]}"\'s; draw another.')
    return out


def check_batch_spread(feats):
    out = []
    if len(feats) < 3:
        return out
    if all(any(s['fillers'] for s in f['sections']) for f in feats):
        out.append({'level': 'warning', 'code': 'batch-spread', 'section': None, 'message': 'Every video in the batch has a filler; some real days have none.'})
    if all(any(s['repairs'] for s in f['sections']) for f in feats):
        out.append({'level': 'warning', 'code': 'batch-spread', 'section': None, 'message': 'Every video in the batch has a repair; leave some clean.'})
    return out


# ---- history file -----------------------------------------------------------------------------------------------
def data_dir():
    return os.path.expanduser(os.environ.get('NAVI_DATA') or '~/Library/Application Support/NAVI')


def history_path():
    return os.path.join(data_dir(), 'script-history.jsonl')


def script_id(script):
    return hashlib.sha1(f"{script.get('title', '')}|{script.get('site', '')}".encode()).hexdigest()[:16]


def load_history(path=None, voice_id=None, exclude=None, real_only=True):
    """The recent videos the checks compare against: real ones only (approved or exported; see mark_real)."""
    path = path or history_path()
    if not os.path.exists(path):
        return []
    out = []
    for line in open(path):
        try:
            h = json.loads(line)
        except ValueError:
            continue
        if exclude and h.get('id') == exclude:
            continue
        if voice_id and h.get('voice_id') and h['voice_id'] != voice_id:
            continue
        if real_only and not h.get('real'):
            continue
        out.append(h)
    out.sort(key=lambda h: h.get('recorded', 0))
    return out[-WINDOW:]


def record(script, path=None, extra=None):
    """Add (or replace) this script's line in the history: called when its voice is made."""
    path = path or history_path()
    real = os.path.realpath(path)
    if real.startswith(ROOT + os.sep) and not real.startswith(os.path.realpath(os.path.join(ROOT, 'output')) + os.sep):
        raise ValueError(f'The script history must live outside the repo (NAVI_DATA), not in {path}.')
    f = features(script)
    f.update({'id': script_id(script), 'recorded': time.time(), 'date': time.strftime('%Y-%m-%d'),
              'batch': script.get('batch')}, **(extra or {}))
    f['sections'] = [{**s, 'person': dict(s['person'])} for s in f['sections']]
    lines = []
    if os.path.exists(path):
        for l in open(path):
            if not l.strip():
                continue
            if json.loads(l).get('id') == f['id']:
                f.setdefault('real', json.loads(l).get('real'))     # a new take of an approved video stays real
                continue
            lines.append(l)
    if not f.get('real'):
        f.pop('real', None)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as fh:
        fh.writelines(lines + [json.dumps(f) + '\n'])
    os.chmod(path, 0o600)
    return f


def mark_real(script, path=None, real=True):
    """This video was approved or exported: from now on the next videos are compared against it.
    real=False: it was only a test after all; it stops counting."""
    path = path or history_path()
    known = os.path.exists(path) and any(l.strip() and json.loads(l).get('id') == script_id(script) for l in open(path))
    if not known:
        return record(script, path, {'real': True}) if real else None
    lines = []
    for l in open(path):
        if l.strip():
            h = json.loads(l)
            if h.get('id') == script_id(script):
                if real:
                    h['real'] = True
                else:
                    h.pop('real', None)
                l = json.dumps(h) + '\n'
            lines.append(l)
    with open(path, 'w') as fh:
        fh.writelines(lines)
    os.chmod(path, 0o600)


def check(script, history=None, batch=None):
    """All variety checks for one script. history: feature dicts (default: the history file, without this script);
    batch: feature dicts of the other scripts in its batch."""
    f = features(script)
    f['pos'] = script.get('batch_pos')
    out = check_within(f)
    if history is None:
        history = load_history(voice_id=script.get('voice_id'), exclude=script_id(script))
    if history:
        out += check_history(f, history)
    elif not batch:
        out.append({'level': 'warning', 'code': 'history', 'section': None,
                    'message': 'No recent videos in the history yet, so repeats across videos can\'t be checked.'})
    if batch:
        out += check_history(f, batch, batch=True)
    return out
