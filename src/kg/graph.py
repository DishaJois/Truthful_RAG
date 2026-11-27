import json
import os
import pickle

import networkx as nx
import pandas as pd


CSV = "data/kg/triples.csv"
CACHE = "data/kg/graph.pkl"


def _load():
    if (
        os.path.exists(CACHE)
        and os.path.getmtime(CACHE) >= os.path.getmtime(CSV)
        and os.path.getmtime(CACHE) >= os.path.getmtime(__file__)
    ):
        with open(CACHE, "rb") as handle:
            return pickle.load(handle)
    graph = nx.MultiDiGraph()
    frame = pd.read_csv(CSV, encoding="utf-8-sig")
    valid_chunk_ids = None
    chunk_ids_path = "data/processed/chunk_ids.json"
    if os.path.exists(chunk_ids_path):
        with open(chunk_ids_path, encoding="utf-8-sig") as handle:
            valid_chunk_ids = set(str(chunk_id) for chunk_id in json.load(handle))
    else:
        valid_chunk_ids = set()
        for chunk_path in (
            "data/processed/chunks.jsonl",
            "data/processed/ganavi_clean_chunks.jsonl",
            "data/processed/test_ganavi_clean_chunks.jsonl",
        ):
            if not os.path.exists(chunk_path):
                continue
            with open(chunk_path, encoding="utf-8-sig") as handle:
                for line in handle:
                    if line.strip():
                        valid_chunk_ids.add(str(json.loads(line)["chunk_id"]))
            break
    for row in frame.itertuples(index=False):
        subject = str(row.subject).lower().strip()
        object_name = str(row.object).lower().strip()
        chunk_id = str(row.chunk_id).strip()
        if valid_chunk_ids and chunk_id not in valid_chunk_ids:
            continue
        graph.add_edge(
            subject,
            object_name,
            relation=str(row.relation).lower().strip(),
            chunk_id=chunk_id,
        )
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    with open(CACHE, "wb") as handle:
        pickle.dump(graph, handle)
    return graph


G = _load()


def kg_lookup(entities, max_hops=1, max_edges=20):
    ents = [str(entity).lower() for entity in entities]
    frontier = {entity for entity in ents if entity in G}
    visited = set(frontier)
    edges = []
    seen = set()

    for _ in range(max_hops):
        following = set()
        for node in frontier:
            incident = list(G.out_edges(node, data=True)) + list(G.in_edges(node, data=True))
            for subject, object_name, data in incident:
                key = (subject, data["relation"], object_name, data["chunk_id"])
                if key in seen:
                    continue
                seen.add(key)
                edges.append({
                    "subject": subject,
                    "relation": data["relation"],
                    "object": object_name,
                    "chunk_id": data["chunk_id"],
                })
                following.update((subject, object_name))
        frontier = following - visited
        visited |= frontier

    pair = [
        edge for edge in edges
        if edge["subject"] in ents and edge["object"] in ents
    ]
    rest = [edge for edge in edges if edge not in pair]
    return (pair + rest)[:max_edges]
