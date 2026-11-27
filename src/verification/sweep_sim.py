import src.verification.verifier as V
from src.verification.gold import load_gold

rows = load_gold()
for t in [0.15, 0.20, 0.25, 0.30, 0.35]:
    V.SIM_THRESHOLD = t
    ok = sum(V.verify_claim(r['claim'], r['evidence'])['state'] == r['label'] for r in rows)
    print(t, ok, '/', len(rows), round(ok / len(rows), 2))
