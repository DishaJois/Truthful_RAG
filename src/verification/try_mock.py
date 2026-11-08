from src.generation.mock_evidence import MOCKS
from src.generation.generate import generate
from src.verification.claims import extract_claims
from src.verification.verifier import verify_claim

for m in MOCKS:
    ans = generate(m['question'], m['evidence'])
    print('Q:', m['question'])
    print('A:', ans)
    for c in extract_claims(ans):
        v = verify_claim(c, m['evidence'])
        print('  ', v['state'], v['confidence'], ':', c[:80])
    print('---')
