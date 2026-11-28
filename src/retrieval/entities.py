import json, os, re
from rapidfuzz import fuzz, process

# Mock or read drugs_of.json if exists, else provide default list
try:
    _raw = json.load(open('data/processed/drugs_of.json', encoding='utf-8-sig'))
except Exception:
    _raw = ['warfarin', 'aspirin', 'ibuprofen', 'simvastatin', 'clarithromycin', 'naproxen']

_names = list(_raw.keys()) if isinstance(_raw, dict) else list(_raw)
DRUGS = sorted({str(n).lower().strip() for n in _names if len(str(n)) > 2})
_SET = set(DRUGS)
ALIASES = {}
if os.path.exists('data/processed/aliases.json'):
    ALIASES = json.load(open('data/processed/aliases.json', encoding='utf-8-sig'))
STOP = {'what', 'does', 'with', 'take', 'together', 'safe', 'drug', 'drugs', 'interaction',
        'interactions', 'between', 'and', 'can', 'the', 'for', 'which', 'about', 'effect', 'effects',
        'taking', 'risk', 'should', 'avoid', 'dose', 'tell', 'how', 'many'}

def detect_entities(text):
    toks = re.findall(r'[a-zA-Z][a-zA-Z-]+', text.lower())
    pairs = [a + b for a, b in zip(toks, toks[1:])]
    found = []
    for c in pairs + toks:
        if c in _SET and c not in STOP and c not in ALIASES and c not in found:
            found.append(c)
    normalized_pairs = [a + ' ' + b for a, b in zip(toks, toks[1:])]
    for token in toks + normalized_pairs:
        generic = ALIASES.get(token.lower())
        if isinstance(generic, list):
            generic_names = generic
        elif isinstance(generic, str):
            generic_names = [generic]
        else:
            generic_names = []
        for generic_name in generic_names:
            generic_name = generic_name.lower()
            if generic_name not in found:
                found.append(generic_name)
    covered = set(w for f in found for w in f.split())
    for t in toks:
        if t in covered or t in STOP or len(t) < 6:
            continue
        m = process.extractOne(t, DRUGS, scorer=fuzz.ratio, score_cutoff=90)
        if m and m[0] not in found:
            found.append(m[0])
    return found
