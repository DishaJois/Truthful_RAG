STOP = {'the', 'and', 'with', 'that', 'this', 'from', 'have', 'been', 'will', 'may', 'are', 'for', 'not', 'when', 'which'}
KEEP = ('SUPPORTED', 'PARTIALLY_SUPPORTED')
BAD = ('CONTRADICTED', 'UNSUPPORTED')

def _words(text):
    return {w.strip('.,;:()[]') for w in text.lower().split()}

def recall_at_k(retrieved_ids, gold_ids, k=5):
    return 1.0 if set(retrieved_ids[:k]) & set(gold_ids) else 0.0

def keyword_match(answer, gold_answer, min_overlap=0.5):
    gold = {w for w in _words(gold_answer) if len(w) > 3 and w not in STOP}
    if not gold:
        return 0.0
    return 1.0 if len(gold & _words(answer)) / len(gold) >= min_overlap else 0.0

def faithfulness(claim_states):
    if not claim_states:
        return None
    return sum(c['state'] in KEEP for c in claim_states) / len(claim_states)

def hallucination_rate(claim_states):
    if not claim_states:
        return None
    return sum(c['state'] in BAD for c in claim_states) / len(claim_states)

def is_abstained(result):
    return bool(result.get('abstained') or 'does not say' in result.get('answer', '').lower())

def abstention_scores(rows):
    abst = [r for r in rows if r[0]]
    unans = [r for r in rows if r[1] == 'unanswerable']
    tp = sum(1 for r in abst if r[1] == 'unanswerable')
    return (tp / len(abst) if abst else None), (tp / len(unans) if unans else None)
