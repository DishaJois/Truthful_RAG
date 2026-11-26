import json
from src.verification.verifier import verify_claim

rows = [json.loads(l) for l in open('data/eval/claim_gold.jsonl', encoding='utf-8-sig') if l.strip()]
ok = 0
for r in rows:
    ev = [{'chunk_id': r.get('chunk_id', 'gold'), 'text': r['evidence_sentence']}] if r.get('evidence_sentence') else []
    pred = verify_claim(r['claim'], ev)['state']
    ok += pred == r['label']
    print(r['label'], '->', pred, '  ', r['claim'][:70])
print('accuracy', ok, '/', len(rows), '=', round(ok / len(rows), 2))
