KEEP = ('SUPPORTED', 'PARTIALLY_SUPPORTED')
POS = ('increas', 'enhanc', 'potentiat', 'elevat', 'rais', 'higher', 'greater')
NEG = ('decreas', 'reduc', 'lower', 'diminish', 'weaken')

def polarity(text):
    t = text.lower()
    p = sum(w in t for w in POS)
    n = sum(w in t for w in NEG)
    return (p > n) - (p < n)

def apply_channels(s, kg_edges, retrieved_ids):
    if s['state'] not in KEEP or not kg_edges:
        return s
    c = s.get('claim', '').lower()
    edges = [e for e in kg_edges if e['subject'] in c and e['object'] in c]
    if not edges:
        return s
    votes = sum(polarity(e['relation'].replace('_', ' ')) for e in edges)
    kg_pol = (votes > 0) - (votes < 0)
    claim_pol = polarity(c)
    s = dict(s)
    if kg_pol and claim_pol and kg_pol != claim_pol:
        s['state'] = 'CONFLICTING_EVIDENCE'
        s['reason'] = 'text-KG disagreement: ' + edges[0]['subject'] + ' ' + edges[0]['relation'] + ' ' + edges[0]['object']
        s['channel'] = 'disagree'
    elif kg_pol == claim_pol and any(e['chunk_id'] in (retrieved_ids or set()) for e in edges):
        s['confidence'] = min(1.0, round(s['confidence'] + 0.15, 2))
        s['channel'] = 'agree'
    return s
