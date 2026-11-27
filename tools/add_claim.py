import json, os

path = 'data/eval/claim_gold.jsonl'
if os.path.exists(path) and os.path.getsize(path) and open(path, 'rb').read()[-1:] != b'\n':
    open(path, 'ab').write(b'\n')

claim = input('claim: ').strip()
texts = []
while True:
    t = input('evidence text (press Enter on an empty line to finish): ').strip()
    if not t:
        break
    texts.append(t)
label = input('label (SUPPORTED / PARTIALLY_SUPPORTED / CONTRADICTED / CONFLICTING_EVIDENCE / INSUFFICIENT_EVIDENCE / UNSUPPORTED): ').strip()

row = {
    'claim': claim,
    'evidence': [{'chunk_id': 'g' + str(i), 'text': t} for i, t in enumerate(texts)],
    'label': label
}
with open(path, 'a', encoding='utf-8') as f:
    f.write(json.dumps(row) + '\n')
print('saved')
