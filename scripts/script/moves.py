"""Moves a casual demo never makes, found by what the line does rather than by exact strings.

Andy, 12 Nov 2026: the first rewrites had "cringy AI catchphrases"; then the plain rewrites had the same asides in
new words ("nobody's seeing this yet", "while it's not finished" for "not that I'm sharing it yet", "while it's half
built"). "Your checker bans strings, not moves." So each move here is a few patterns built from word classes (who
might see it x a seeing verb x "yet"; a time clause x a state of being unfinished; ...), and the tests in
test_moves.py check them against paraphrases written after the patterns, not only the lines that started it.

A pattern list still only covers the wordings its classes cover: a new way of making the same move can get through.
The checker is the floor; the writer's brief (reference/script-writing.md) names the moves, not the phrases.

  from moves import find_moves      find_moves(sentence) -> [(move, matched text)]
"""
import re

W = r"[\w'’-]+"
GAP = lambda n: rf"(?:\s+{W}){{0,{n}}}\s+"          # up to n words in between

AUDIENCE = r"(?:nobody|no[- ]one|anyone|anybody|everyone|everybody|people|the world|the public|customers|buyers|members)"
SEEING = r"(?:see|sees|seeing|seen|look|looks|looking|share|shares|sharing|shared|know|knows|buy|buying|find|finding|get|getting|need|needs)"
YET = r"(?:yet|for now|just yet|right now|at the moment|till it'?s ready|until it'?s ready)"
UNFINISHED = (r"(?:not (?:quite )?(?:finished|done|ready|built|complete|sorted|live|public|out)|unfinished|incomplete|"
              r"half[- ](?:built|done|finished|made|baked|ready)|a work in progress|(?:still )?(?:being )?(?:built|made|worked on|put together)|"
              r"(?:still )?in progress|(?:still )?not ready|(?:not|isn'?t) (?:out|live|public) yet|ready to go out|ready for (?:anyone|people|the world))")
TIME = r"(?:while|until|till|before)"
NEG = r"(?:not|n't|never|no)"

MOVES = [
    # the product's private or unfinished state, said as an aside ("not that I'm sharing it yet")
    ('state-aside', 'an aside about it being private or unfinished; the screen already shows the step, so just do it', [
        rf"\b{AUDIENCE}\b{GAP(4)}{SEEING}\b(?:{GAP(4)})?{YET}\b",
        rf"\b{AUDIENCE}\s+{SEEING}\b{GAP(4)}{YET}\b",
        rf"\b{AUDIENCE}'?s\s+{SEEING}\b",                     # "nobody's seeing this"
        rf"\bnot that (?:i|i'?m|we|we'?re|you|anyone|anybody|it)\b",
        rf"\b{TIME}\b{GAP(3)}{UNFINISHED}\b",
        rf"\b(?:it'?s|it is|this is|that'?s)\s+(?:still\s+)?{UNFINISHED}\b",
        rf"\b{NEG}\b{GAP(2)}(?:sharing|showing|going out|launching|selling|publishing|announcing)\b(?:{GAP(3)}|\s+){YET}\b",
        rf"\b(?:sharing|showing|going out|launching|publishing)\b{GAP(2)}(?:can|will|'ll) wait\b",
        rf"\bwhich can wait\b",
        rf"\b(?:keep|keeping)\s+it\s+(?:under wraps|quiet|secret|out of sight)\b",
    ]),
    # talking to the viewer's assumptions: a hook, or a myth set up to be knocked down
    ('hook', 'a hook aimed at what the viewer thinks; just say what you are doing', [
        rf"\byou(?:'d| would| might| may| probably| likely)?\s+(?:think|expect|assume|guess|imagine|figure|reckon)\b",
        rf"\byou'?ve\s+(?:probably|likely|definitely|maybe|almost certainly)\b",
        rf"\b(?:most|a lot of|lots of|plenty of)\s+people\b{GAP(5)}(?:think|miss|expect|assume|get (?:it|this) wrong|forget|don'?t know)\b",
        rf"\bever\s+(?:wondered|noticed|tried|wanted)\b",
        rf"\bguess\s+(?:what|where|how)\b",
        rf"\b(?:what|how|where|why)\s+(?:do|does|did|would|can)\s+you\b[^.?!]*\?",
    ]),
    # a reveal or a twist
    ('reveal', 'a reveal; nothing on screen is a surprise', [
        rf"\bbut\s+(?:it'?s|it is|they'?re|that'?s)\s+(?:actually|really|just|right|literally)\s+(?:there|here|on|in|the)\b",
        rf"\bturns?\s+out\b", rf"\b(?:surprisingly|funnily enough|believe it or not|spoiler|plot twist)\b",
        rf"\b(?:buried|hidden away|tucked away)\b",
    ]),
    # selling: rating the product instead of using it
    ('selling', 'rating the product instead of using it', [
        rf"\b(?:the\s+)?(?:nicest|best|coolest|greatest|neatest|favourite|favorite|smartest|cleverest)\b{GAP(3)}(?:thing|part|bit|feature|touch)\b",
        rf"\b(?:the\s+)?(?:nice|good|great|cool|neat|clever|smart)\s+(?:thing|part|bit)\s+(?:about|is|here)\b",
        rf"\b(?:i\s+)?love\s+(?:how|that)\b", rf"\bi\s+like\s+how\b",
        rf"\bwhich\s+is\s+(?:handy|nice|great|useful|neat|cool|convenient|lovely|brilliant|perfect)\b",
        rf"\b(?:super|really|so|dead)\s+(?:easy|simple|handy|quick|nice|useful|smooth|clean)\b",
        rf"\b(?:game[- ]changer|magic happens|the good news|the beauty of)\b",
    ]),
    # framing and teasing
    ('framing', 'framing the video instead of doing it', [
        rf"\bhere'?s\s+(?:the|where|what)\b{GAP(2)}(?:thing|trick|catch|kicker|magic|fun|interesting)\b",
        rf"\bthe\s+(?:catch|trick|kicker|secret|magic)\b(?:\s+is|\s+here)?",
        rf"\bthe\s+bit\s+(?:that|where|people|everyone|you)\b",
        rf"\b(?:let'?s|we'?ll|i'?ll|we can)\s+skip\s+(?:the\s+bit|the\s+part|over)\b",
        rf"\bthere'?s\s+(?:two|three|a couple of)\s+ways\b",
    ]),
    # writing, not talking
    ('written', 'written English nobody says while clicking', [
        rf"\bi'?d\s+sooner\b", rf"\bneeds?\s+to\s+exist\b", rf"\bin\s+order\s+to\b", rf"\bshould\s+you\s+wish\b",
        rf"\bwhereupon\b", rf"\bthus\b",
    ]),
    # a performed wrong word with an apology
    ('performed-slip', 'a performed wrong-word slip; a natural slip repeats or restarts, it doesn\'t apologise', [
        rf"\b{W},\s+(?:sorry|oops|whoops|no wait|wait no|my bad|or rather|i mean|scratch that),\s+{W}",
    ]),
]
_COMPILED = [(name, why, [re.compile(p, re.I) for p in pats]) for name, why, pats in MOVES]


def find_moves(sentence):
    """[(move, why, matched text)] for one sentence."""
    s = sentence.replace('’', "'")
    out = []
    for name, why, pats in _COMPILED:
        for p in pats:
            m = p.search(s)
            if m:
                out.append((name, why, m.group(0)))
                break
    return out


# ---- the model review: finds the moves in new words, which the patterns above miss ----------------------------------
# Measured on lines written by a separate writer who never saw the patterns or this brief (test_moves.py), because a
# pattern list built from the lines that started it caught 11 of 38 new wordings. It runs the local `claude` CLI, so it
# needs no key of its own; the writer runs it on every draft (drafts.py pick --moves), and any line it finds is an error.
import json as _json
import os as _os
import random as _random
import shutil as _shutil
import subprocess as _subprocess
import sys as _sys

BRIEF = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), 'move_review.md')
REVIEW_MODEL = None   # None: the "checks" job's model and effort (config/defaults.json "jobs"); never an alias


def _ask(prompt, model=None, timeout=240):
    """One question to the checks subagent (scripts/jobs/jobs.py: the configured model, its fallbacks, logged in the
    batch report). The answer's text, or None when it didn't run."""
    jobs_dir = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..', 'jobs')
    if jobs_dir not in _sys.path:
        _sys.path.insert(0, jobs_dir)
    import jobs
    import hashlib
    import tempfile
    # the same lines get the same review: a draft that didn't change between two rounds of `drafts.py pick` isn't
    # sent again (kept next to the batch's job log, or in the temp folder)
    j = jobs.config()['checks']
    key = hashlib.sha256(_json.dumps([model or j['model'], j['effort'], prompt]).encode()).hexdigest()
    log = jobs.log_path()
    cache = _os.path.join(_os.path.dirname(_os.path.abspath(log)) if log else tempfile.gettempdir(), 'line-reviews.json')
    try:
        seen = _json.load(open(cache))
    except (OSError, ValueError):
        seen = {}
    if key in seen:
        return seen[key]
    try:
        txt = jobs.run('checks', prompt, tools=None, timeout=timeout, model=model, note='line review')['text']
    except jobs.JobError:
        return None
    seen[key] = txt
    try:
        with open(cache, 'w') as f:
            _json.dump(seen, f)
    except OSError:
        pass
    return txt


def _last_array(txt):
    """The last JSON array in the answer: the model sometimes corrects itself and answers twice; the last one counts."""
    dec, last = _json.JSONDecoder(), None
    for i, ch in enumerate(txt):
        if ch == '[':
            try:
                v, _ = dec.raw_decode(txt[i:])
            except ValueError:
                continue
            if isinstance(v, list) and all(isinstance(x, dict) for x in v):
                last = v
    return last


def review(lines, model=REVIEW_MODEL, timeout=240):
    """lines: [str]. Returns [{'n', 'move', 'words', 'line'}] for the lines that make a move (n is 0-based), or None
    when the claude CLI isn't there or didn't answer (the caller says the review didn't run)."""
    if not lines:
        return []
    prompt = open(BRIEF).read() + '\n\nLines:\n' + '\n'.join(f'{i + 1}. {l}' for i, l in enumerate(lines))
    txt = _ask(prompt, model, timeout)
    if txt is None:
        return None
    found = _last_array(txt)
    if found is None:
        return None
    out = []
    for x in found:
        try:
            n = int(x['n']) - 1
        except (KeyError, TypeError, ValueError):
            continue
        if 0 <= n < len(lines):
            out.append({'n': n, 'move': x.get('move', '?'), 'words': x.get('words', ''), 'line': lines[n]})
    return out


def review_script(script, model=REVIEW_MODEL):
    """Every sentence of a script's talk, reviewed: [{'section', 'move', 'words', 'line'}], or None if it didn't run."""
    sys_path = _os.path.dirname(_os.path.abspath(__file__))
    if sys_path not in _sys.path:
        _sys.path.insert(0, sys_path)
    import variety
    rows = [(s.get('name'), x) for s in script.get('sections', []) for x in variety.sentences(variety.plain_of(s.get('talk')))]
    found = review([x for _, x in rows], model)
    if found is None:
        return None
    return [{'section': rows[f['n']][0], 'move': f['move'], 'words': f['words'], 'line': f['line']} for f in found]


if __name__ == '__main__':
    sc = _json.load(open(_sys.argv[1]))
    res = review_script(sc)
    if res is None:
        _sys.exit('The move review did not run (no claude CLI, or no answer).')
    for f in res:
        print(f"{f['section']}: ({f['move']}) \"{f['words']}\" in: {f['line']}")
    print(f'{len(res)} lines make a move.')
    _sys.exit(1 if res else 0)


ALIKE_BRIEF = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), 'alike_review.md')


def alike(new_line, earlier, model=REVIEW_MODEL, timeout=240):
    """Does a new opening sound like recent ones, by ear (shape, move, rhythm), not just by words? The word checks in
    variety.py missed both pairs a reviewer heard as alike in ten openings (12 Nov 2026). Returns
    [{'earlier': i (0-based), 'strength', 'shared', 'line'}], or None if the review didn't run."""
    if not earlier:
        return []
    prompt = open(ALIKE_BRIEF).read() + '\n\nEARLIER:\n' + '\n'.join(f'{i + 1}. {l}' for i, l in enumerate(earlier)) + f'\n\nNEW:\n{new_line}'
    txt = _ask(prompt, model, timeout)
    if txt is None:
        return None
    found = _last_array(txt)
    if found is None:
        return None
    out = []
    for x in found:
        try:
            i = int(x['earlier']) - 1
        except (KeyError, TypeError, ValueError):
            continue
        if 0 <= i < len(earlier):
            out.append({'earlier': i, 'strength': x.get('strength', 'mild'), 'shared': x.get('shared', ''), 'line': earlier[i]})
    return out
