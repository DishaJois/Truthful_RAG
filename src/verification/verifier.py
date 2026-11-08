import json
import numpy as np
from sentence_transformers import SentenceTransformer
from src.generation.llm import chat

_emb = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
SIM_THRESHOLD = 0.25
HIGH_RISK = ('contraindicated', 'fatal', 'avoid', 'dose', 'overdose', 'death', 'life-threatening', 'severe')
LABELS = {'SUPPORTED', 'PARTIALLY_SUPPORTED', 'CONTRADICTED', 'CONFLICTING_EVIDENCE', 'INSUFFICIENT_EVIDENCE'}
BASE_CONF = {
    'SUPPORTED': 0.8,
    'CONTRADICTED': 0.8,
    'CONFLICTING_EVIDENCE': 0.7,
    'PARTIALLY_SUPPORTED': 0.65,
    'INSUFFICIENT_EVIDENCE': 0.5
}

def risk_level(claim):
    c = claim.lower()
    return 'high' if any(k in c for k in HIGH_RISK) else 'low'

def _similarities(claim, evidence):
    vecs = _emb.encode([claim] + [e['text'] for e in evidence], normalize_embeddings=True, batch_size=32)
    return (vecs[1:] @ vecs[0]).tolist()

def _prompt(claim, top):
    ev = '\n\n'.join('[' + e['chunk_id'] + '] ' + e['text'][:1200] for e in top)
    return (
        'You verify claims about drug interactions against evidence.\n\nEvidence:\n' + ev +
        '\n\nClaim: ' + claim + '\n\nChoose exactly one label:\n'
        'SUPPORTED: the evidence directly states the claim\n'
        'PARTIALLY_SUPPORTED: the evidence covers only part of the claim\n'
        'CONTRADICTED: the evidence states the opposite\n'
        'CONFLICTING_EVIDENCE: different passages disagree with each other\n'
        'INSUFFICIENT_EVIDENCE: the evidence is related but does not settle the claim\n\n'
        'Reply with JSON only, like {"label": "SUPPORTED", "reason": "one short sentence"}'
    )

def _parse(raw):
    start, end = raw.find('{'), raw.rfind('}')
    if start != -1 and end > start:
        try:
            d = json.loads(raw[start:end + 1])
            label = str(d.get('label', '')).strip().upper().replace(' ', '_')
            if label in LABELS:
                return label, str(d.get('reason', ''))
        except Exception:
            pass
    up = raw.upper()
    for label in ('PARTIALLY_SUPPORTED', 'CONFLICTING_EVIDENCE', 'CONTRADICTED', 'INSUFFICIENT_EVIDENCE', 'SUPPORTED'):
        if label in up:
            return label, 'parsed from free text'
    return None, ''

def _result(claim, state, conf, ids, reason, risk):
    return {
        'claim': claim,
        'state': state,
        'confidence': conf,
        'evidence_ids': ids,
        'reason': reason,
        'risk_level': risk
    }

def verify_claim(claim, evidence, top_n=3):
    risk = risk_level(claim)
    if not evidence:
        return _result(claim, 'UNSUPPORTED', 0.95, [], 'no evidence retrieved', risk)

    sims = _similarities(claim, evidence)
    order = list(np.argsort(sims)[::-1][:top_n])
    best = float(sims[order[0]])

    if best < SIM_THRESHOLD:
        return _result(claim, 'UNSUPPORTED', 0.9, [], 'max similarity ' + str(round(best, 2)) + ' is below threshold', risk)

    top = [evidence[i] for i in order]
    ids = [e['chunk_id'] for e in top]
    prompt = _prompt(claim, top)

    label, reason = None, ''
    for _ in range(2):
        label, reason = _parse(chat(prompt))
        if label:
            break
        prompt += '\nRemember: reply with JSON only.'

    if not label:
        label, reason = 'INSUFFICIENT_EVIDENCE', 'unparseable verifier output'

    conf = round(min(1.0, BASE_CONF[label] + 0.2 * (best - SIM_THRESHOLD)), 2)
    return _result(claim, label, conf, ids, reason, risk)
