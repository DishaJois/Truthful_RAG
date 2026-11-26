import json, os

CHECKS = [
    'data/processed/chunks.jsonl',
    'data/processed/chunk_ids.json',
    'data/processed/faiss.index',
    'data/processed/drugs_of.json',
    'data/processed/openfda_triples_p1_9.jsonl',
    'data/processed/openfda_chunks_p1_9.jsonl',
    'data/processed/chunks_dd.jsonl',
    'data/kg/triples.csv',
    'data/eval/questions.jsonl',
    'data/eval/claim_gold.jsonl'
]

for p in CHECKS:
    if os.path.exists(p):
        print('OK     ', p, round(os.path.getsize(p) / 1e6, 1), 'MB')
    else:
        print('MISSING', p)

def lines(p):
    return sum(1 for l in open(p, encoding='utf-8-sig') if l.strip().strip('\x00')) if os.path.exists(p) else None

print('chunks.jsonl lines:', lines('data/processed/chunks.jsonl'))
print('triples lines:', lines('data/processed/openfda_triples_p1_9.jsonl'))

if os.path.exists('data/processed/chunks.jsonl'):
    first = next(l.strip().strip('\x00') for l in open('data/processed/chunks.jsonl', encoding='utf-8-sig') if l.strip().strip('\x00').startswith('{'))
    r = json.loads(first)
    print('chunk keys:', list(r), ' first id:', r.get('chunk_id'), ' source:', r.get('source'))

if os.path.exists('data/processed/openfda_triples_p1_9.jsonl'):
    first = next(l.strip().strip('\x00') for l in open('data/processed/openfda_triples_p1_9.jsonl', encoding='utf-8-sig') if l.strip().strip('\x00').startswith('{'))
    t = json.loads(first)
    print('triple keys:', list(t))

if os.path.exists('data/eval/questions.jsonl'):
    n, bad = 0, 0
    for line in open('data/eval/questions.jsonl', encoding='utf-8-sig'):
        if line.strip():
            n += 1
            try:
                json.loads(line)
            except Exception:
                bad += 1
    print('questions:', n, 'lines,', bad, 'unparseable')

try:
    import faiss
    print('faiss vectors:', faiss.read_index('data/processed/faiss.index').ntotal)
except Exception as e:
    print('faiss not readable:', str(e)[:80])
