import csv
import os


def test_filtered_triples_file_exists_and_resolves():
    triples = "data/kg/triples.csv"
    assert os.path.exists(triples)
    from src.kg.build_kg import load_chunks
    chunk_ids = set(load_chunks())

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
