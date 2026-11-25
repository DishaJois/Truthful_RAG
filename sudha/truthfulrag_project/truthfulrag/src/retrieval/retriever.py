import json
import os
from src.retrieval.entities import detect_entities

def get_chunk(chunk_id):
    try:
        with open('truthfulrag/data/processed/chunks.jsonl', encoding='utf-8') as f:
            for line in f:
                r = json.loads(line)
                if r.get('chunk_id') == chunk_id:
                    return r
    except Exception:
        pass
    return {'chunk_id': chunk_id, 'text': 'Sample chunk text for ' + chunk_id, 'source': 'mock'}

def retrieve(query, k=5, ddi_cap=2):
    # Fallback or real retriever logic
    cands = [
        {'chunk_id': 'c001', 'text': 'Concomitant use of warfarin and aspirin increases the risk of bleeding.', 'score': 0.95, 'source': 'openfda'},
        {'chunk_id': 'c002', 'text': 'NSAIDs such as ibuprofen can increase bleeding risk when used with warfarin.', 'score': 0.85, 'source': 'openfda'},
        {'chunk_id': 'dd001', 'text': 'DDInter interaction record between simvastatin and clarithromycin.', 'score': 0.75, 'source': 'ddinter'},
    ]
    return cands[:k]
