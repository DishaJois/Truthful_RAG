import json
import os
import re
import numpy as np
import faiss
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer
from src.retrieval.entities import detect_entities

INDEX_PATH = "data/processed/faiss.index"
IDS_PATH = "data/processed/chunk_ids.json"
CHUNKS_PATH = "data/processed/chunks.jsonl"

_index = None
_chunk_ids = None
_chunks_by_id = None
_model = None

def _ensure_loaded():
    global _index, _chunk_ids, _chunks_by_id, _model
    if _chunks_by_id is None:
        _chunks_by_id = {}
        if os.path.exists(CHUNKS_PATH):
            with open(CHUNKS_PATH, "r", encoding="utf-8-sig") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    rec = json.loads(line)
                    _chunks_by_id[rec["chunk_id"]] = rec
    if _index is None and os.path.exists(INDEX_PATH) and os.path.exists(IDS_PATH):
        _index = faiss.read_index(INDEX_PATH)
        with open(IDS_PATH, "r", encoding="utf-8-sig") as f:
            _chunk_ids = json.load(f)
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")

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

def hybrid_rerank(query, candidates, w_dense):
    if w_dense >= 1.0 or not candidates:
        return candidates
    bm25 = BM25Okapi([re.findall(r"[a-z0-9]+", c["text"].lower()) for c in candidates])
    raw = bm25.get_scores(re.findall(r"[a-z0-9]+", query.lower()))
    top = max(raw) if len(raw) and max(raw) > 0 else 1.0
    for candidate, bm25_score in zip(candidates, raw):
        candidate["score"] = (
            w_dense * float(candidate["score"])
            + (1.0 - w_dense) * float(bm25_score) / top
        )
    candidates.sort(key=lambda item: item["score"], reverse=True)
    return candidates

def retrieve(query, k=5, ddi_cap=2, w_dense=0.7):
    _ensure_loaded()
    if _index is None or not _chunk_ids:
        return []

    entities = set(detect_entities(query))
    q_vec = _model.encode([query], normalize_embeddings=True).astype("float32")
    pool_size = min(max(k * 8, 40), _index.ntotal)
    scores, idxs = _index.search(q_vec, pool_size)

    scored = []
    for score, idx in zip(scores[0], idxs[0]):
        if idx < 0 or idx >= len(_chunk_ids):
            continue
        cid = _chunk_ids[idx]
        rec = _chunks_by_id.get(cid)
        if not rec:
            continue
        chunk_drugs = {d.lower() for d in rec.get("drugs", [])}
        overlap = len(entities & chunk_drugs)
        boosted = float(score) + 0.12 * overlap
        scored.append((boosted, rec))

    scored.sort(key=lambda x: x[0], reverse=True)

    results = [{
        "chunk_id": rec["chunk_id"],
        "text": rec["text"],
        "score": float(score),
        "source": rec.get("source", "unknown"),
    } for score, rec in scored]
    results = hybrid_rerank(query, results, w_dense)

    output = []
    ddi_count = 0
    for rec in results:
        is_ddi = rec["source"].lower().startswith("ddinter") or rec["source"].lower() == "ddinter"
        if is_ddi:
            if ddi_count >= ddi_cap:
                continue
            ddi_count += 1
        rec["score"] = round(float(rec["score"]), 4)
        output.append(rec)
        if len(output) >= k:
            break
    return output
