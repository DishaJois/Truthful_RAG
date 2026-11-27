import json, random, sys

seed = int(sys.argv[1]) if len(sys.argv) > 1 else 1
random.seed(seed)
rows = [json.loads(l) for l in open('data/processed/chunks.jsonl', encoding='utf-8-sig') if l.strip()]
rows = [r for r in rows if len(r['text'].split()) > 40]
for r in random.sample(rows, 25):
    print(r['chunk_id'], r.get('drugs'))
    print(r['text'][:500].replace('\n', ' '))
    print('---')
