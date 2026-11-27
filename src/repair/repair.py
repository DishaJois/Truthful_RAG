from src.generation.llm import chat
from src.verification.verifier import verify_claim

KEEP = ('SUPPORTED', 'PARTIALLY_SUPPORTED')
PROMPTS = {
    'PARTIALLY_SUPPORTED': 'Rewrite the claim so that it states ONLY what the evidence supports. '
                           'Remove any part the evidence does not support.',
    'CONTRADICTED': 'The evidence contradicts the claim. Write one corrected sentence that states '
                    'what the evidence actually says.',
    'CONFLICTING_EVIDENCE': 'The evidence passages disagree. Write one sentence that reports both '
                            'positions neutrally, starting with: Sources disagree:',
}

def _pick(evidence, ids):
    chosen = [e for e in evidence if e['chunk_id'] in ids]
    return chosen or evidence[:3]

def _ask(instruction, claim, ev):
    text = '\n\n'.join('[' + e['chunk_id'] + '] ' + e['text'][:1000] for e in ev)
    prompt = (instruction + '\n\nEvidence:\n' + text + '\n\nClaim: ' + claim +
              '\n\nReply with the single sentence only, no explanation.')
    return chat(prompt).strip().split('\n')[0].strip()

def _out(orig, new, action, state):
    return {'original': orig, 'repaired': new, 'action': action, 'state': state}

def must_abstain(claim_states):
    return any(c.get('risk_level') == 'high' and c['state'] in ('CONTRADICTED', 'UNSAFE_TO_ANSWER')
               for c in claim_states)

def repair_claim(cs, evidence):
    state, claim = cs['state'], cs['claim']
    ev = _pick(evidence, cs.get('evidence_ids', []))
    if cs.get('channel') == 'disagree':
        extra = [e for e in evidence if e['text'].startswith('KG fact') and e not in ev]
        ev = ev + extra[:2]
    if state == 'SUPPORTED':
        return _out(claim, claim, 'keep', state)
    if state in PROMPTS:
        new = _ask(PROMPTS[state], claim, ev)
        if new:
            check = verify_claim(new, ev)['state']
            accepted = KEEP + (('CONFLICTING_EVIDENCE',) if state == 'CONFLICTING_EVIDENCE' else ())
            if check in accepted:
                return _out(claim, new, 'rewrite', state)
    if state == 'INSUFFICIENT_EVIDENCE':
        return _out(claim, 'The available evidence does not settle this point: ' + claim.rstrip('.') + '.', 'hedge', state)
    if state == 'CONFLICTING_EVIDENCE':
        return _out(claim, 'Sources disagree on whether the following holds: ' + claim.rstrip('.') + '.', 'hedge', state)
    return _out(claim, '', 'drop', state)

def repair_all(claim_states, evidence):
    items = [repair_claim(c, evidence) for c in claim_states]
    text = ' '.join(i['repaired'] for i in items if i['repaired'])
    return text, items
