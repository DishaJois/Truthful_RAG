import json
import os
from collections import defaultdict
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from src.retrieval.entities import detect_entities

INDEX_PATH = "data/processed/faiss.index"
IDS_PATH = "data/processed/chunk_ids.json"
CHUNKS_PATH = "data/processed/chunks.jsonl"

SYNONYMS = {
    "aspirin": "acetylsalicylic acid",
    "acetylsalicylic acid": "aspirin",
    "acetaminophen": "paracetamol",
    "paracetamol": "acetaminophen",
}

_index = None
_chunk_ids = None
_chunks_by_id = None
_drug_to_cids = None
_model = None

def get_embedder():
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model

def _ensure_loaded():
    global _index, _chunk_ids, _chunks_by_id, _drug_to_cids
    if _chunks_by_id is None:
        _chunks_by_id = {}
        _drug_to_cids = defaultdict(list)
        if os.path.exists(CHUNKS_PATH):
            with open(CHUNKS_PATH, "r", encoding="utf-8-sig") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    rec = json.loads(line)
                    cid = rec["chunk_id"]
                    _chunks_by_id[cid] = rec
                    for d in rec.get("drugs", []):
                        _drug_to_cids[d.lower()].append(cid)
    if _index is None and os.path.exists(INDEX_PATH) and os.path.exists(IDS_PATH):
        _index = faiss.read_index(INDEX_PATH)
        with open(IDS_PATH, "r", encoding="utf-8-sig") as f:
            _chunk_ids = json.load(f)
    get_embedder()

def get_chunk(chunk_id):
    _ensure_loaded()
    rec = _chunks_by_id.get(chunk_id)
    if rec:
        return {
            "chunk_id": rec["chunk_id"],
            "text": rec["text"],
            "source": rec.get("source", "unknown"),
        }
    return None

def _expanded_entities(query):
    base = detect_entities(query)
    out = []
    for e in base:
        if e not in out:
            out.append(e)
        syn = SYNONYMS.get(e)
        if syn and syn not in out:
            out.append(syn)
    return out

def retrieve(query, k=5, ddi_cap=2):
    _ensure_loaded()
    if _index is None or not _chunk_ids:
        return []

    entities = _expanded_entities(query)
    ent_set = set(entities)
    model = get_embedder()
    q_vec = model.encode([query], normalize_embeddings=True).astype("float32")

    pool_size = min(max(k * 10, 50), _index.ntotal)
    scores, idxs = _index.search(q_vec, pool_size)

    cand_map = {}
    for score, idx in zip(scores[0], idxs[0]):
        if 0 <= idx < len(_chunk_ids):
            cid = _chunk_ids[idx]
            if cid in _chunks_by_id:
                cand_map[cid] = float(score)

    # Inject entity-matched chunks so multi-drug pairs are never missed by global top-K
    entity_cids = []
    if len(entities) >= 2:
        sets = [set(_drug_to_cids.get(e, [])) for e in entities if _drug_to_cids.get(e)]
        if len(sets) >= 2:
            both = list(sets[0] & sets[1])[:40]
            entity_cids.extend(both)
    for e in entities:
        entity_cids.extend(_drug_to_cids.get(e, [])[:25])

    missing = [cid for cid in dict.fromkeys(entity_cids) if cid not in cand_map and cid in _chunks_by_id]
    if missing:
        m_vecs = model.encode([_chunks_by_id[c]["text"] for c in missing], normalize_embeddings=True, batch_size=32).astype("float32")
        m_scores = (m_vecs @ q_vec[0]).tolist()
        for cid, sc in zip(missing, m_scores):
            cand_map[cid] = float(sc)

    scored = []
    for cid, base_score in cand_map.items():
        rec = _chunks_by_id[cid]
        chunk_drugs = {d.lower() for d in rec.get("drugs", [])}
        text_low = rec["text"].lower()
        drug_hits = sum(1 for e in ent_set if e in chunk_drugs or e in text_low)
        boosted = base_score + 0.15 * drug_hits
        scored.append((boosted, rec))

    scored.sort(key=lambda x: x[0], reverse=True)

    results = []
    ddi_count = 0
    for score, rec in scored:
        is_ddi = rec.get("source", "").lower() == "ddinter" or rec.get("is_synthetic", False)
        if is_ddi:
            if ddi_count >= ddi_cap:
                continue
            ddi_count += 1
        results.append({
            "chunk_id": rec["chunk_id"],
            "text": rec["text"],
            "score": round(float(score), 4),
            "source": rec.get("source", "unknown"),
        })
        if len(results) >= k:
            break
    return results
