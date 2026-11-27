import csv
import json
from collections import defaultdict


def audit_precision(
    sample_path="data/kg/sample_to_label.csv",
    chunks_path="data/processed/ganavi_clean_chunks.jsonl",
):
    chunk_ids = set()
    with open(chunks_path, encoding="utf-8-sig") as handle:
        for line in handle:
            if line.strip():
                chunk_ids.add(json.loads(line)["chunk_id"])

    counts = defaultdict(lambda: {"correct": 0, "total": 0})
    with open(sample_path, encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))

    if len(rows) == 0:
        raise ValueError("No labeled triples found")

    for row in rows:
        value = str(row["correct"]).strip()
        if value not in {"0", "1"}:
            raise ValueError(
                f"Missing or invalid label for {row['chunk_id']}: {row['subject']} "
                f"{row['relation']} {row['object']}"
            )
        if row["chunk_id"] not in chunk_ids:
            raise ValueError(f"Unknown source chunk_id: {row['chunk_id']}")
        relation = row["relation"].lower().strip()
        counts[relation]["total"] += 1
        counts[relation]["correct"] += int(value)

    correct = sum(item["correct"] for item in counts.values())
    total = sum(item["total"] for item in counts.values())
    report = {
        "sample_size": total,
        "correct": correct,
        "incorrect": total - correct,
        "overall_precision": correct / total if total else None,
        "per_relation": {
            relation: {
                "precision": values["correct"] / values["total"],
                "correct": values["correct"],
                "total": values["total"],
            }
            for relation, values in sorted(counts.items())
        },
    }
    print(json.dumps(report, indent=2))
    return report


if __name__ == "__main__":
    audit_precision()
