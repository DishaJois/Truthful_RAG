import glob, json
from src.adjudication.adjudicator import BAD

def load(cfg, split='tune'):
    files = sorted(glob.glob('results/runs/' + cfg + '_*.jsonl'))
    if not files:
        return []
    rows = [json.loads(l) for l in open(files[-1], encoding='utf-8-sig') if l.strip()]
    return [r for r in rows if r.get('split', 'tune') == split]

def abstains(r, t):
    cs = r.get('claims', [])
    if not cs:
        return True
    bad = sum(c['state'] in BAD for c in cs) / len(cs)
    high = any(c.get('risk_level') == 'high' and c['state'] in ('CONTRADICTED', 'UNSAFE_TO_ANSWER') for c in cs)
    return bad > t or high

rows = load('C')
if not rows:
    print('No results/runs/C_*.jsonl found yet. Run Config C on practice questions first.')
else:
    best = None
    print('threshold precision recall f1 | n =', len(rows))
    for t in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]:
        pred = [(abstains(r, t), r.get('type', 'answerable')) for r in rows]
        ab = [p for p in pred if p[0]]
        tp = sum(1 for p in ab if p[1] == 'unanswerable')
        un = sum(1 for p in pred if p[1] == 'unanswerable')
        prec = tp / len(ab) if ab else 0.0
        rec = tp / un if un else 0.0
        f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
        print(t, round(prec, 2), round(rec, 2), round(f1, 2))
        if best is None or f1 > best[1]:
            best = (t, f1)
    print('best threshold on the practice questions:', best[0])
