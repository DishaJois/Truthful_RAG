import csv
import os
from collections import defaultdict

TRIPLES_PATH = "data/processed/openfda_triples_p1_9.jsonl"
_adj = None

def _ensure_loaded():
    global _adj
    if _adj is not None:
        return
    _adj = defaultdict(list)
    if not os.path.exists(TRIPLES_PATH):
        return
    with open(TRIPLES_PATH, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            subj = (row.get("subject") or "").strip().lower()
            rel = (row.get("relation") or "").strip()
            obj = (row.get("object") or "").strip().lower()
            cid = (row.get("chunk_id") or "").strip()
            if not subj or not obj or not rel:
                continue
            edge = {
                "subject": subj,
                "relation": rel,
                "object": obj,
                "chunk_id": cid,
            }
            _adj[subj].append(edge)
            _adj[obj].append(edge)

def kg_lookup(entities, max_hops=1, max_edges=20):
    _ensure_loaded()
    ents = [e.lower().strip() for e in (entities or []) if e]
    if not ents:
        return []
    ent_set = set(ents)

    both_match = []
    single_match = []
    seen = set()

    for ent in ents:
        for edge in _adj.get(ent, []):
            key = (edge["subject"], edge["relation"], edge["object"], edge["chunk_id"])
            if key in seen:
                continue
            seen.add(key)
            if edge["subject"] in ent_set and edge["object"] in ent_set:
                both_match.append(edge)
            else:
                single_match.append(edge)

    return (both_match + single_match)[:max_edges]
