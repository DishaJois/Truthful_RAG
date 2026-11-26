import json, re
from rapidfuzz import fuzz, process

# Mock or read drugs_of.json if exists, else provide default list
try:
    _raw = json.load(open('data/processed/drugs_of.json', encoding='utf-8'))
except Exception:
    _raw = ['warfarin', 'aspirin', 'ibuprofen', 'simvastatin', 'clarithromycin', 'naproxen']

_names = list(_raw.keys()) if isinstance(_raw, dict) else list(_raw)
DRUGS = sorted({str(n).lower().strip() for n in _names if len(str(n)) > 2})
_SET = set(DRUGS)
STOP = {'what', 'does', 'with', 'take', 'together', 'safe', 'drug', 'drugs', 'interaction',
        'interactions', 'between', 'and', 'can', 'the', 'for', 'which', 'about', 'effect', 'effects',
        'taking', 'risk', 'should', 'avoid', 'dose', 'tell', 'how', 'many'}

def detect_entities(text):
    toks = re.findall(r'[a-zA-Z][a-zA-Z-]+', text.lower())
    pairs = [a + b for a, b in zip(toks, toks[1:])]
    found = []
    for c in pairs + toks:
        if c in _SET and c not in STOP and c not in found:
            found.append(c)
    covered = set(w for f in found for w in f.split())
    for t in toks:
        if t in covered or t in STOP or len(t) < 6:
            continue
        m = process.extractone(t, DRUGS, scorer=fuzz.ratio, score_cutoff=90)
        if m and m[0] not in found:
            found.append(m[0])
    return found
