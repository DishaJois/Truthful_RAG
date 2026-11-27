import json, os, re
from rapidfuzz import fuzz, process

try:
    _raw = json.load(open('data/processed/drugs_of.json', encoding='utf-8-sig'))
except Exception:
    _raw = ['warfarin', 'aspirin', 'ibuprofen', 'simvastatin', 'clarithromycin', 'naproxen']

_names = list(_raw.keys()) if isinstance(_raw, dict) else list(_raw)
_names = [n['name'] if isinstance(n, dict) and 'name' in n else n for n in _names]
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
    pairs = [a + ' ' + b for a, b in zip(toks, toks[1:])]
    found = []
    for c in pairs + toks:
        if c in _SET and c not in STOP and c not in ALIASES and c not in found:
            found.append(c)
    for token in toks:
        generic = ALIASES.get(token.lower())
        if generic and generic not in found:
            found.append(generic)
    for pair in pairs:
        generic = ALIASES.get(pair.lower())
        if generic and generic not in found:
            found.append(generic)
    covered = set(w for f in found for w in f.split())
    for t in toks:
        if t in covered or t in STOP or t in ALIASES or len(t) < 6:
            continue
        m = process.extractOne(t, DRUGS, scorer=fuzz.ratio, score_cutoff=90)
        if m and m[0] not in found:
            found.append(m[0])
    return found
