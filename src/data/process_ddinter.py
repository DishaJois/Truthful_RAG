import csv
import json
import os
import re
from pathlib import Path
from typing import Set, Dict, List, Tuple

def load_heldout(heldout_path: str, aliases_path: str) -> Set[str]:
    heldout = set()
    for path in [heldout_path, aliases_path]:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    item = line.strip().lower()
                    if item and not item.startswith("#"):
                        heldout.add(item)
    return heldout

def contains_heldout_text(text: str, heldout_set: Set[str]) -> bool:
    tokens = set(re.findall(r"\b\w+\b", text.lower()))
    return bool(tokens.intersection(heldout_set))

def process_ddinter(
    raw_dir: str = "data/raw/ddinter/",
    chunks_out: str = "data/processed/chunks_dd.jsonl",
    triples_out: str = "data/kg/triples_dd.csv",
    heldout_drugs_file: str = "docs/heldout_drugs.txt",
    heldout_aliases_file: str = "docs/heldout_drug_aliases.txt",
    filter_unknown_severity: bool = False
):
    heldout_set = load_heldout(heldout_drugs_file, heldout_aliases_file)
    os.makedirs(os.path.dirname(chunks_out), exist_ok=True)
    os.makedirs(os.path.dirname(triples_out), exist_ok=True)

    seen_pairs = set()
    tag_removals = 0
    text_removals = 0
    duplicate_removals = 0
    unknown_severity_count = 0

    chunk_records = []
    triple_records = []

    csv_files = list(Path(raw_dir).glob("*.csv")) if os.path.exists(raw_dir) else []
    chunk_counter = 1

    for filepath in csv_files:
        filename = filepath.name
        with open(filepath, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row_idx, row in enumerate(reader):
                keys = {k.lower(): k for k in row.keys()}
                drug_a = row.get(keys.get("drug_a", "drug_a"), "").strip().lower()
                drug_b = row.get(keys.get("drug_b", "drug_b"), "").strip().lower()
                severity = row.get(keys.get("level", "level"), row.get(keys.get("severity", "severity"), "Unknown")).strip()

                if not drug_a or not drug_b:
                    continue

                # Canonicalize pair order
                pair = tuple(sorted([drug_a, drug_b]))
                if pair in seen_pairs:
                    duplicate_removals += 1
                    continue
                seen_pairs.add(pair)

                # Held-out drug check
                if drug_a in heldout_set or drug_b in heldout_set:
                    tag_removals += 1
                    continue

                if severity.lower() == "unknown":
                    unknown_severity_count += 1
                    if filter_unknown_severity:
                        continue

                # Synthetic passage generation
                chunk_id = f"dd_{chunk_counter:06d}"
                doc_id = f"DDInter:{filename}:row_{row_idx}"
                text = (
                    f"DDInter reports an interaction between {drug_a} and {drug_b} "
                    f"with a severity rating of {severity}. Clinical monitoring is advised "
                    f"when co-administering these agents."
                )

                # Held-out text match check
                if contains_heldout_text(text, heldout_set):
                    text_removals += 1
                    continue

                chunk_entry = {
                    "chunk_id": chunk_id,
                    "doc_id": doc_id,
                    "text": text,
                    "source": "DDInter",
                    "drugs": list(pair),
                    "is_synthetic": True
                }
                chunk_records.append(chunk_entry)

                relation = f"interacts_with_{severity.lower().replace(' ', '_')}"
                triple_records.append({
                    "subject": pair[0],
                    "relation": relation,
                    "object": pair[1],
                    "chunk_id": chunk_id,
                    "source": "DDInter"
                })

                chunk_counter += 1

    # Write chunks JSONL
    with open(chunks_out, "w", encoding="utf-8") as f:
        for chunk in chunk_records:
            f.write(json.dumps(chunk) + "\n")

    # Write triples CSV (exact five columns)
    with open(triples_out, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["subject", "relation", "object", "chunk_id", "source"])
        writer.writeheader()
        writer.writerows(triple_records)

    print(f"=== DDInter Processing Complete ===")
    print(f"Chunks generated: {len(chunk_records)}")
    print(f"Triples generated: {len(triple_records)}")
    print(f"Duplicates removed: {duplicate_removals}")
    print(f"Held-out tag removals: {tag_removals}")
    print(f"Held-out text removals: {text_removals}")
    print(f"Unknown severity entries: {unknown_severity_count}")

if __name__ == "__main__":
    process_ddinter()
