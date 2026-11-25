import csv
import os


BAD_TERMS = {
    "serum", "lead", "metabolism", "health", "diarrhea", "headache",
    "water", "treat", "prevention", "thyroid", "alcohol", "sodium",
    "calcium", "potassium",
}
ALLOWED_RELATIONS = {"interacts_with", "increases_effect_of", "decreases_effect_of", "contraindicated_with"}


def kg_filter(source="data/kg/triples.csv", output="data/kg/triples.csv", max_rows=100000):
    if not os.path.exists(source):
        raise FileNotFoundError(f"{source} does not exist")
    kept = []
    counts = {}
    with open(source, encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            relation = row["relation"].lower().strip()
            subject = row["subject"].lower().strip()
            object_name = row["object"].lower().strip()
            if relation not in ALLOWED_RELATIONS:
                continue
            if subject in BAD_TERMS or object_name in BAD_TERMS:
                continue
            if len(subject) < 3 or len(object_name) < 3:
                continue
            kept.append(row)
            counts[relation] = counts.get(relation, 0) + 1
            if len(kept) >= max_rows:
                break

    os.makedirs(os.path.dirname(output), exist_ok=True)
    with open(output, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["subject", "relation", "object", "chunk_id", "source"])
        writer.writeheader()
        writer.writerows(kept)
    print(f"Wrote {len(kept)} filtered triples to {output}")
    print(counts)


if __name__ == "__main__":
    kg_filter()
