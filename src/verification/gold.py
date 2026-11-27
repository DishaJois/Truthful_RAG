import json

PATH = 'data/eval/claim_gold.jsonl'
CLAIM_KEY, EVID_KEY, LABEL_KEY = 'claim', 'evidence_sentence', 'label'

def load_gold():
    rows = [json.loads(l) for l in open(PATH, encoding='utf-8-sig') if l.strip()]
    out = []
    for i, r in enumerate(rows):
        ev = r.get(EVID_KEY) or r.get('evidence') or []
        if isinstance(ev, str):
            ev = [ev] if ev else []
        ev = [e if isinstance(e, dict) else {'chunk_id': r.get('chunk_id', 'g' + str(i) + '_' + str(j)), 'text': e}
              for j, e in enumerate(ev)]
        out.append({'claim': r[CLAIM_KEY], 'evidence': ev, 'label': r[LABEL_KEY]})
    return out
