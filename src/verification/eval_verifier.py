import json
from src.verification.verifier import verify_claim

rows = [json.loads(l) for l in open('tests/data/claim_gold.jsonl', encoding='utf-8-sig')]
ok = 0
for r in rows:
    pred = verify_claim(r['claim'], r['evidence'])['state']
    ok += pred == r['label']
    print(r['label'], '->', pred, '  ', r['claim'][:70])
print('accuracy', ok, '/', len(rows), '=', round(ok / len(rows), 2))
