import datetime, os
from src.verification.gold import load_gold
from src.verification.verifier import verify_claim

rows = load_gold()
ok, mixed = 0, {}
for r in rows:
    pred = verify_claim(r['claim'], r['evidence'])['state']
    ok += pred == r['label']
    if pred != r['label']:
        mixed[(r['label'], pred)] = mixed.get((r['label'], pred), 0) + 1
    print(r['label'], '->', pred, '|', r['claim'][:70])

line = 'accuracy: ' + str(ok) + ' / ' + str(len(rows)) + ' = ' + str(round(ok / len(rows), 2))
print(line)
for (g, p), n in sorted(mixed.items()):
    print('mixed up:', g, 'as', p, n, 'times')

os.makedirs('results', exist_ok=True)
with open('results/verifier_accuracy.txt', 'a', encoding='utf-8') as f:
    f.write(datetime.date.today().isoformat() + ' | ' + line + '\n')
