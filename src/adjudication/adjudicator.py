KEEP = {'SUPPORTED', 'PARTIALLY_SUPPORTED'}
BAD = {'CONFLICTING_EVIDENCE', 'INSUFFICIENT_EVIDENCE', 'UNSUPPORTED', 'AMBIGUOUS_QUERY', 'UNSAFE_TO_ANSWER'}
DOMAIN_WORDS = ('drug', 'medicine', 'medication', 'tablet', 'dose', 'interact', 'side effect', 'take together')
ABSTAIN_MSG = 'I cannot answer this reliably from the available evidence.'
QUESTION_MSG = {
    'OUT_OF_SCOPE': 'This question is outside the drug-interaction domain this system covers.',
    'AMBIGUOUS_QUERY': 'The question is too vague. Please name the drugs you are asking about.',
}

def question_state(question, entities):
    if entities is None or entities:
        return None
    q = (question or '').lower()
    return 'AMBIGUOUS_QUERY' if any(w in q for w in DOMAIN_WORDS) else 'OUT_OF_SCOPE'

def kg_supports(claim, kg_edges, retrieved_ids):
    c = claim.lower()
    for e in kg_edges or []:
        if e['subject'] in c and e['object'] in c and e['chunk_id'] in (retrieved_ids or set()):
            return True
    return False

def should_abstain(claim_states, threshold=0.30):
    if not claim_states:
        return True
    bad = sum(1 for c in claim_states if c['state'] in BAD)
    high = any(c.get('risk_level') == 'high' and c['state'] in ('CONTRADICTED', 'UNSAFE_TO_ANSWER') for c in claim_states)
    return bad / len(claim_states) > threshold or high

def _row(claim, state, reason):
    return {
        'claim': claim,
        'state': state,
        'confidence': 1.0,
        'evidence_ids': [],
        'reason': reason,
        'risk_level': 'low'
    }

def adjudicate(verifications, question=None, entities=None, answer=None, kg_edges=None,
               retrieved_ids=None, filter_claims=False, use_abstention=False):
    q_state = question_state(question, entities)
    if q_state:
        return {
            'final_answer': QUESTION_MSG[q_state],
            'abstain': True,
            'claim_states': [_row(question, q_state, 'question-level check')]
        }

    if not verifications:
        return {
            'final_answer': ABSTAIN_MSG + ' No verifiable claims were produced.',
            'abstain': True,
            'claim_states': [_row(question or '', 'UNSUPPORTED', 'no claims to verify')]
        }

    states = []
    for v in verifications:
        s = dict(v)
        if s['state'] in KEEP and kg_supports(s.get('claim', ''), kg_edges, retrieved_ids):
            s['confidence'] = min(1.0, s['confidence'] + 0.15)
        if (s.get('risk_level') == 'high' and s['confidence'] < 0.6
                and s['state'] not in ('CONTRADICTED', 'UNSUPPORTED')):
            s['state'] = 'UNSAFE_TO_ANSWER'
        states.append(s)

    kept = [s for s in states if s['state'] in KEEP]
    abstain = should_abstain(states) if use_abstention else False

    if abstain:
        reasons = sorted({s['state'] for s in states if s['state'] not in KEEP})
        final = ABSTAIN_MSG + ' Reason: ' + ', '.join(reasons) + '.'
    elif filter_claims:
        final = ' '.join(s['claim'] for s in kept)
        removed = len(states) - len(kept)
        if removed:
            final += ' (Note: ' + str(removed) + ' claim(s) removed because the evidence did not support them.)'
        if not kept:
            abstain, final = True, ABSTAIN_MSG
    else:
        final = (answer or ' '.join(s['claim'] for s in states))
        final += ' [Verification: ' + str(len(kept)) + ' of ' + str(len(states)) + ' claims supported]'

    return {'final_answer': final, 'abstain': abstain, 'claim_states': states}
