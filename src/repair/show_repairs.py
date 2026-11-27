import glob, json

files = sorted(glob.glob('results/runs/E_*.jsonl'))
if not files:
    print('No results/runs/E_*.jsonl found yet.')
else:
    rows = [json.loads(l) for l in open(files[-1], encoding='utf-8-sig') if l.strip()]
    n = 0
    for r in rows:
        for i in r.get('repairs', []):
            if i['action'] != 'keep':
                n += 1
                print(r.get('qid'), '|', i['state'], '|', i['action'])
                print('   before:', i['original'][:120])
                print('   after: ', i['repaired'][:120])
                if n >= 20:
                    raise SystemExit
