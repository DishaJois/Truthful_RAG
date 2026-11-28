import csv
import json
import os
from pathlib import Path

from src.data.openfda_process import build_term_trie, load_heldout, match_trie

SRC = "data/processed/openfda_triples_p1_9.jsonl"
OUT = "data/kg/triples.csv"
FALLBACK_SOURCES = (
    "data/processed/ganavi_clean_triples.csv",
    "data/processed/test_ganavi_clean_triples.csv",
)
CHUNK_SOURCES = (
    "data/processed/chunks.jsonl",
    "data/processed/ganavi_clean_chunks.jsonl",
    "data/processed/test_ganavi_clean_chunks.jsonl",
)


def load_chunks():
    for path in CHUNK_SOURCES:
        if not os.path.exists(path):
            continue
        chunks = {}
        with open(path, encoding="utf-8-sig") as handle:
            for line in handle:
                if line.strip():
                    chunk = json.loads(line)
                    chunks[chunk["chunk_id"]] = chunk.get("text", "")
        return chunks
    return None


def load_triples():
    source = Path(SRC)
    if source.exists():
        rows = []
        with source.open(encoding="utf-8-sig") as handle:
            for line in handle:
                if line.strip():
                    row = json.loads(line)
                    rows.append({
                        "subject": str(row.get("subject", row.get("head", ""))).lower().strip(),
                        "relation": str(row.get("relation", row.get("predicate", ""))).lower().strip(),
                        "object": str(row.get("object", row.get("tail", ""))).lower().strip(),
                        "chunk_id": str(row.get("chunk_id", "")).strip(),
                        "source": str(row.get("source", "openFDA")),
                    })
        return rows, str(source)

    for fallback in FALLBACK_SOURCES:
        path = Path(fallback)
        if not path.exists():
            continue
        with path.open(encoding="utf-8-sig", newline="") as handle:
            rows = []
            for row in csv.DictReader(handle):
                rows.append({
                    "subject": row["subject"].lower().strip(),
                    "relation": row["relation"].lower().strip(),
                    "object": row["object"].lower().strip(),
                    "chunk_id": row["chunk_id"].strip(),
                    "source": row.get("source", "openFDA"),
                })
        return rows, str(path)
    raise FileNotFoundError(
        f"Missing {SRC} and fallback sources {', '.join(FALLBACK_SOURCES)}. "
        "Run the Ganavi OpenFDA processing pipeline first."
    )


def build_kg():
    rows, source = load_triples()
    chunks = load_chunks()
    heldout = load_heldout("docs/heldout_drugs.txt", "docs/heldout_drug_aliases.txt")
    heldout_trie = build_term_trie(heldout)
    seen = set()
    cleaned = []
    for row in rows:
        key = (row["subject"], row["relation"], row["object"], row["chunk_id"])
        if not all(key[:3]) or key in seen:
            continue
        if chunks is not None and row["chunk_id"] not in chunks:
            continue
        if match_trie(row["subject"], heldout_trie) or match_trie(row["object"], heldout_trie):
            continue
        if chunks is not None and match_trie(chunks[row["chunk_id"]], heldout_trie):
            continue
        seen.add(key)
        cleaned.append(row)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["subject", "relation", "object", "chunk_id", "source"])
        writer.writeheader()
        writer.writerows(cleaned)
    print(f"Built {OUT}: {len(cleaned)} triples from {source}")


if __name__ == "__main__":
    build_kg()
