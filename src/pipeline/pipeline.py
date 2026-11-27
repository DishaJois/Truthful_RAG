import time
from src.retrieval.retriever import retrieve, get_chunk
from src.retrieval.entities import detect_entities
from src.kg.graph import kg_lookup
from src.generation.generate import generate
from src.verification.claims import extract_claims
from src.verification.verifier import verify_claim
from src.adjudication.adjudicator import adjudicate

def merge_kg(evidence, edges, max_total=5):
    out = [dict(e) for e in evidence]
    for e in edges:
        fact = e['subject'] + ' ' + e['relation'].replace('_', ' ') + ' ' + e['object']
        hit = next((x for x in out if x['chunk_id'] == e['chunk_id']), None)
        if hit is not None:
            if not hit['text'].startswith('KG fact'):
                hit['text'] = 'KG fact: ' + fact + '. ' + hit['text']
            continue
        c = get_chunk(e['chunk_id'])
        if c and len(out) < max_total:
            out.append({'chunk_id': e['chunk_id'], 'text': 'KG fact: ' + fact + '. ' + c['text'], 'score': 1.0, 'source': 'KG'})
    return out

def run_pipeline(question, config):
    t0 = time.perf_counter()
    config = config.upper()
    entities = detect_entities(question)
    evidence = retrieve(question, k=5)
    kg_edges = []
    if config in ('B', 'D'):
        kg_edges = kg_lookup(entities, max_edges=5)
        evidence = merge_kg(evidence, kg_edges, max_total=5)
    answer = generate(question, evidence)
    claims, final, abstained = [], answer, False
    if config in ('C', 'D'):
        verifications = [verify_claim(c, evidence) for c in extract_claims(answer)]
        res = adjudicate(verifications, question=question, entities=entities, answer=answer,
                         kg_edges=kg_edges, retrieved_ids={e['chunk_id'] for e in evidence},
                         filter_claims=(config == 'D'), use_abstention=(config == 'D'))
        claims, final, abstained = res['claim_states'], res['final_answer'], res['abstain']
    return {'question': question, 'config': config, 'answer': final, 'abstained': abstained,
            'evidence': evidence, 'claims': claims, 'latency_s': round(time.perf_counter() - t0, 2)}
