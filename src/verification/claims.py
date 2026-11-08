import re
from src.generation.llm import chat

def sentences(text):
    return [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if len(s.strip()) > 20]

def extract_claims(answer, max_claims=8):
    if not answer or 'evidence does not say' in answer.lower():
        return []
    clean = re.sub(r'\[[^\]]*\]', '', answer)
    claims = []
    try:
        raw = chat(
            'List each separate factual claim in this answer, one per line, '
            'no numbering, no extra text.\n\nAnswer:\n' + clean
        )
        claims = [re.sub(r'^[-*0-9.)]+', '', line).strip() for line in raw.splitlines()]
        claims = [c for c in claims if len(c) > 15]
    except Exception:
        claims = []
    if not claims:
        claims = sentences(clean)
    seen, out = set(), []
    for c in claims:
        if c.lower() not in seen:
            seen.add(c.lower())
            out.append(c)
    return out[:max_claims]
