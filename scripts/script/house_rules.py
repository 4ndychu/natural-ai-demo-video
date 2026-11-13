"""House rules a script can carry, checked with the rest (check_script.py):

  "never_name": ["NAVI", "ElevenLabs", ...]   words the voice and the captions must never say (a course that never
                                              names the tools its videos are made with). Matched as whole words,
                                              any case, also with a space or hyphen inside ("Eleven Labs").
  "spelling": "UK" | "US"                     the captions' spelling. A word spelt the other way is an error
                                              (colour/color, organise/organize, enrol/enroll, centre/center...).
                                              Only the captions: the voice reads either the same.
  "seats" + a section's "seat"                a video that uses two or more logins (X and Google Sheets, Claude and
                                              Grok): every section names the site whose login its steps use, that
                                              site must be one of the script's seats, and a page a section opens
                                              must belong to its seat's site.

  .venv/bin/python scripts/script/house_rules.py "<text>" UK|US     (prints the words spelt the other way)
"""
import re
import sys

# British -> American. Inflections are added below (organise -> organised, organises, organising, organisation...).
_ISE = ['organis', 'realis', 'recognis', 'optimis', 'prioritis', 'customis', 'personalis', 'summaris', 'monetis',
        'authoris', 'finalis', 'visualis', 'minimis', 'maximis', 'emphasis', 'apologis', 'specialis', 'standardis',
        'categoris', 'memoris', 'utilis', 'criticis', 'capitalis', 'centralis', 'characteris', 'familiaris',
        'generalis', 'harmonis', 'initialis', 'legalis', 'localis', 'mobilis', 'normalis', 'synchronis', 'systematis',
        'theoris', 'trivialis', 'stabilis', 'socialis', 'scrutinis', 'patronis', 'publicis', 'sympathis', 'energis',
        'digitalis', 'commercialis', 'productis', 'incentivis', 'operationalis', 'revolutionis', 'popularis',
        'jeopardis', 'brainstorm']
_OUR = ['colour', 'favour', 'behaviour', 'honour', 'labour', 'neighbour', 'humour', 'flavour', 'rumour', 'harbour',
        'endeavour', 'savour', 'vapour', 'armour', 'parlour', 'odour', 'valour', 'vigour', 'rigour', 'glamour']
_PAIRS = {
    'centre': 'center', 'centres': 'centers', 'centred': 'centered', 'metre': 'meter', 'metres': 'meters',
    'litre': 'liter', 'litres': 'liters', 'theatre': 'theater', 'fibre': 'fiber', 'calibre': 'caliber',
    'analyse': 'analyze', 'analysed': 'analyzed', 'analyses': 'analyzes', 'analysing': 'analyzing',
    'paralyse': 'paralyze', 'catalyse': 'catalyze',
    'catalogue': 'catalog', 'catalogues': 'catalogs', 'analogue': 'analog',
    'enrol': 'enroll', 'enrols': 'enrolls', 'enrolment': 'enrollment', 'enrolments': 'enrollments',
    'fulfil': 'fulfill', 'fulfils': 'fulfills', 'fulfilment': 'fulfillment', 'instalment': 'installment',
    'instalments': 'installments', 'skilful': 'skillful', 'wilful': 'willful',
    'travelled': 'traveled', 'travelling': 'traveling', 'traveller': 'traveler', 'travellers': 'travelers',
    'cancelled': 'canceled', 'cancelling': 'canceling', 'labelled': 'labeled', 'labelling': 'labeling',
    'modelled': 'modeled', 'modelling': 'modeling', 'levelled': 'leveled', 'levelling': 'leveling',
    'signalled': 'signaled', 'signalling': 'signaling', 'totalled': 'totaled', 'totalling': 'totaling',
    'fuelled': 'fueled', 'fuelling': 'fueling', 'counselling': 'counseling', 'jewellery': 'jewelry',
    'defence': 'defense', 'offence': 'offense', 'pretence': 'pretense', 'licence': 'license', 'licences': 'licenses',
    'programme': 'program', 'programmes': 'programs', 'cheque': 'check', 'cheques': 'checks',
    'grey': 'gray', 'greys': 'grays', 'judgement': 'judgment', 'judgements': 'judgments', 'ageing': 'aging',
    'acknowledgement': 'acknowledgment', 'mum': 'mom', 'tyre': 'tire', 'tyres': 'tires', 'aluminium': 'aluminum',
    'cosy': 'cozy', 'sceptical': 'skeptical', 'sceptic': 'skeptic', 'plough': 'plow', 'draught': 'draft',
    'manoeuvre': 'maneuver', 'oestrogen': 'estrogen', 'paediatric': 'pediatric', 'encyclopaedia': 'encyclopedia',
    'practise': 'practice', 'practised': 'practiced', 'practising': 'practicing', 'storey': 'story',
    'whilst': 'while', 'amongst': 'among', 'learnt': 'learned', 'spelt': 'spelled', 'dreamt': 'dreamed',
}
# Words the US list would wrongly flag in UK text, or that are fine both ways.
_BOTH = {'practice', 'license', 'program', 'programs', 'check', 'checks', 'story', 'draft', 'while', 'among',
         'learned', 'spelled', 'dreamed', 'emphasis', 'brainstorm', 'meter', 'meters', 'tire', 'tires', 'analyses'}


def _expand():
    uk_us = dict(_PAIRS)
    for stem in _ISE:
        if stem in ('emphasis', 'brainstorm'):
            continue
        us = stem[:-1] + 'z'
        for end in ('e', 'ed', 'es', 'ing', 'ation', 'ations', 'er', 'ers'):
            uk_us[stem + end] = us + end
    for w in _OUR:
        us = w[:-2] + 'r'
        for end in ('', 's', 'ed', 'ing', 'ite', 'ites', 'able', 'ful', 'less', 'ism'):
            uk_us[w + end] = us + end
    uk_us['emphasise'], uk_us['emphasised'], uk_us['emphasising'] = 'emphasize', 'emphasized', 'emphasizing'
    return uk_us


UK_US = _expand()
US_UK = {}
for _uk, _us in UK_US.items():
    US_UK.setdefault(_us, _uk)


def other_spellings(text, spelling):
    """Words in `text` spelt the other way: [(word as written, the spelling wanted)]."""
    want = (spelling or '').upper().replace('GB', 'UK')
    if want not in ('UK', 'US'):
        return []
    wrong = US_UK if want == 'UK' else UK_US
    out = []
    for m in re.finditer(r"[A-Za-z][A-Za-z']*", text or ''):
        w = m.group(0)
        low = w.lower()
        if low in _BOTH or low not in wrong:
            continue
        # in UK text: "program" (software) and "practice" (noun) are fine; and the US words that are also UK nouns
        if want == 'UK' and low in ('program', 'programs', 'practice', 'license', 'check', 'checks', 'draft', 'story'):
            continue
        fix = wrong[low]
        out.append((w, fix.capitalize() if w[0].isupper() else fix))
    return out


def _names_rx(word):
    # split on spaces, hyphens and case changes: "ElevenLabs" also matches "Eleven Labs" and "eleven-labs"
    parts = [re.escape(p) for p in re.findall(r'[A-Z]+(?![a-z])|[A-Z]?[a-z]+|\d+|[^\sA-Za-z\d-]+', word.strip()) if p]
    return re.compile(r'(?<![A-Za-z0-9])' + r'[\s-]?'.join(parts) + r'(?![A-Za-z0-9])', re.I)


def _site(url):
    m = re.match(r'^(?:[a-z]+://)?([^/:?#]+)', (url or '').strip().lower())
    return m.group(1).removeprefix('www.') if m else ''


def _covers(site, seat_site):
    """Does a page on `site` belong to the login on `seat_site`? (docs.google.com is the google.com login)"""
    return site == seat_site or site.endswith('.' + seat_site) or seat_site.endswith('.' + site)


def check(script):
    """[(level, code, section name or None, message)]"""
    out = []
    never = [w for w in (script.get('never_name') or []) if isinstance(w, str) and w.strip()]
    rxs = [(w, _names_rx(w)) for w in never]
    spelling = script.get('spelling')
    seat_sites = [s.get('site') for s in (script.get('seats') or []) if isinstance(s, dict) and s.get('site')]
    for si, sec in enumerate(script.get('sections') or []):
        name = sec.get('name') or f'section {si + 1}'
        for field, label in (('talk', 'The voice'), ('caption', 'The caption')):
            text = sec.get(field) or ''
            for w, rx in rxs:
                if rx.search(text):
                    out.append(('error', 'never-name', name, f'{label} names "{w}". This video must never name it '
                                '(the script\'s "never_name" list). Say what is happening on screen instead.'))
        for w, fix in other_spellings(sec.get('caption') or '', spelling):
            out.append(('error', 'spelling', name, f'Caption spells "{w}" the {"British" if spelling.upper() == "US" else "American"} way; '
                        f'this video uses {"American" if spelling.upper() == "US" else "British"} spelling: "{fix}".'))
        if len(seat_sites) > 1:
            sec_seat = sec.get('seat')
            sec_site = sec_seat.get('site') if isinstance(sec_seat, dict) else sec_seat
            if not sec_site:
                out.append(('error', 'seat', name, 'This video uses more than one login (' + ', '.join(seat_sites) + '): '
                            'give the section a "seat" naming the site whose login its steps use.'))
                continue
            if sec_site not in seat_sites:
                out.append(('error', 'seat', name, f'The section\'s seat "{sec_site}" isn\'t one of the script\'s seats ({", ".join(seat_sites)}).'))
                continue
            for a in sec.get('actions') or []:
                if a.get('do') == 'goto' and a.get('target'):
                    site = _site(a['target'])
                    if any(_covers(site, s) for s in seat_sites) and not _covers(site, sec_site):
                        out.append(('error', 'seat', name, f'The section opens {site} but its seat is {sec_site}: '
                                    'put this step in a section on that seat, or change the section\'s seat.'))
    return out


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    for w, fix in other_spellings(sys.argv[1], sys.argv[2]):
        print(f'{w} -> {fix}')
