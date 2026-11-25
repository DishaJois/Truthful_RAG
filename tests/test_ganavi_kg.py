import csv
import os


def test_filtered_triples_file_exists_and_resolves():
    triples = "data/kg/triples.csv"
    chunks = "data/processed/test_ganavi_clean_chunks.jsonl"
    assert os.path.exists(triples)
    assert os.path.exists(chunks)

    chunk_ids = set()
    with open(chunks, encoding="utf-8-sig") as handle:
        import json
        for line in handle:
            if line.strip():
                chunk_ids.add(json.loads(line)["chunk_id"])

    with open(triples, encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert rows
    assert all(row["chunk_id"] in chunk_ids for row in rows)


def test_graph_lookup_prioritizes_pair_edges():
    from src.kg.graph import kg_lookup
    edges = kg_lookup(["warfarin", "aspirin"])
    assert edges
    pair_edges = [
        edge for edge in edges
        if edge["subject"] in {"warfarin", "aspirin"}
        and edge["object"] in {"warfarin", "aspirin"}
    ]
    assert pair_edges == edges[:len(pair_edges)]
