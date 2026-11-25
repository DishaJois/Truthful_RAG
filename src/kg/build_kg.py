import csv
import json
import os
from pathlib import Path


SRC = "data/processed/openfda_triples_p1_9.jsonl"
OUT = "data/kg/triples.csv"
FALLBACK_CSV = "data/processed/test_ganavi_clean_triples.csv"
CHUNKS = "data/processed/test_ganavi_clean_chunks.jsonl"


def load_chunk_ids():
    for path in (
        "data/processed/chunks.jsonl",
        "data/processed/test_ganavi_clean_chunks.jsonl",
    ):
        if not os.path.exists(path):
            continue
        ids = set()
        with open(path, encoding="utf-8-sig") as handle:
            for line in handle:
                if line.strip():
                    ids.add(json.loads(line)["chunk_id"])
        return ids
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

    fallback = Path(FALLBACK_CSV)
    if not fallback.exists():
        raise FileNotFoundError(
            f"Missing {SRC} and fallback {FALLBACK_CSV}. Download/share the source triples first."
        )
    with fallback.open(encoding="utf-8-sig", newline="") as handle:
        rows = []
        for row in csv.DictReader(handle):
            rows.append({
                "subject": row["subject"].lower().strip(),
                "relation": row["relation"].lower().strip(),
                "object": row["object"].lower().strip(),
                "chunk_id": row["chunk_id"].strip(),
                "source": row.get("source", "openFDA"),
            })
    return rows, str(fallback)


def build_kg():
    rows, source = load_triples()
    valid_ids = load_chunk_ids()
    seen = set()
    cleaned = []
    for row in rows:
        key = (row["subject"], row["relation"], row["object"], row["chunk_id"])
        if not all(key[:3]) or key in seen:
            continue
        if valid_ids is not None and row["chunk_id"] not in valid_ids:
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
