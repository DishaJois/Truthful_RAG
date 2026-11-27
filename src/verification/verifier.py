import json
import numpy as np
from sentence_transformers import SentenceTransformer
from src.generation.llm import chat

_emb = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
SIM_THRESHOLD = 0.30
HIGH_RISK = ('contraindicated', 'fatal', 'overdose', 'life-threatening')
LABELS = {'SUPPORTED', 'PARTIALLY_SUPPORTED', 'CONTRADICTED', 'CONFLICTING_EVIDENCE', 'INSUFFICIENT_EVIDENCE'}
BASE_CONF = {
    'SUPPORTED': 0.85,
    'CONTRADICTED': 0.85,
    'CONFLICTING_EVIDENCE': 0.75,
    'PARTIALLY_SUPPORTED': 0.70,
    'INSUFFICIENT_EVIDENCE': 0.60
}

_RISK_POS = ('increase', 'risk', 'severe', 'avoid', 'contraindicated', 'hypertension', 'hypoglycemia', 'bleeding', 'toxicity')
_RISK_NEG = ('no clinically significant', 'well tolerated', 'no effect', 'no adverse', 'unaffected', 'safe')

def risk_level(claim):
    c = claim.lower()
    return 'high' if any(k in c for k in HIGH_RISK) else 'low'

def _similarities(claim, evidence):
    vecs = _emb.encode([claim] + [e['text'] for e in evidence], normalize_embeddings=True, batch_size=32)
    return (vecs[1:] @ vecs[0]).tolist()

def _passages_conflict(top):
    if len(top) < 2:
        return False
    has_pos = any(any(w in e['text'].lower() for w in _RISK_POS) for e in top)
    has_neg = any(any(w in e['text'].lower() for w in _RISK_NEG) for e in top)
    return has_pos and has_neg

def _prompt(claim, top):
    ev = '\n\n'.join(f"[{e['chunk_id']}] {e['text'][:1200]}" for e in top)
    return (
        "You verify claims about drug interactions against evidence. Choose exactly one label:\n"
        "- SUPPORTED: the evidence directly states or confirms the claim\n"
        "- PARTIALLY_SUPPORTED: the evidence confirms part of the claim, but the claim adds an extra unverified part\n"
        "- CONTRADICTED: the evidence states the opposite of the claim\n"
        "- CONFLICTING_EVIDENCE: different evidence passages disagree with each other\n"
        "- INSUFFICIENT_EVIDENCE: the evidence is related but does not settle the claim\n\n"
        f"Evidence:\n{ev}\n\n"
        f"Claim: {claim}\n\n"
        'Reply with JSON only: {"label": "SUPPORTED", "reason": "one short sentence"}'
    )

def _parse(raw):
    raw_str = raw.strip()
    start, end = raw_str.find('{'), raw_str.rfind('}')
    if start != -1 and end > start:
        try:
            d = json.loads(raw_str[start:end + 1])
            label = str(d.get('label', '')).strip().upper().replace(' ', '_')
            if label in LABELS:
                return label, str(d.get('reason', ''))
        except Exception:
            pass
    up = raw_str.upper()
    for label in ('CONFLICTING_EVIDENCE', 'PARTIALLY_SUPPORTED', 'CONTRADICTED', 'INSUFFICIENT_EVIDENCE', 'SUPPORTED'):
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
        return _result(claim, 'UNSUPPORTED', 0.9, [], f'max similarity {round(best, 2)} is below threshold', risk)

    top = [evidence[i] for i in order]
    ids = [e['chunk_id'] for e in top]

    if _passages_conflict(top):
        return _result(claim, 'CONFLICTING_EVIDENCE', round(min(1.0, 0.75 + 0.15 * (best - SIM_THRESHOLD)), 2),
                       ids, 'evidence passages disagree on interaction risk', risk)

    prompt = _prompt(claim, top)
    label, reason = None, ''
    for _ in range(2):
        label, reason = _parse(chat(prompt))
        if label:
            break
        prompt += '\nReply with JSON only: {"label": "SUPPORTED", "reason": "one short sentence"}'

    if not label:
        label, reason = 'INSUFFICIENT_EVIDENCE', 'unparseable verifier output'

    conf = round(min(1.0, BASE_CONF.get(label, 0.6) + 0.15 * (best - SIM_THRESHOLD)), 2)
    return _result(claim, label, conf, ids, reason, risk)
