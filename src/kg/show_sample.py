import csv
import os
import random


def show_sample(path="data/kg/triples.csv", count=50, seed=2026):
    if not os.path.exists(path):
        raise FileNotFoundError(f"{path} does not exist. Run python -m src.kg.build_kg first.")
    with open(path, encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        print("No triples available.")
        return
    random.Random(seed).sample(rows, k=min(count, len(rows)))
    os.makedirs("data/kg", exist_ok=True)
    out = "data/kg/sample_to_label.csv"
    with open(out, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["subject", "relation", "object", "chunk_id", "source", "correct"])
        writer.writeheader()
        for row in random.Random(seed).sample(rows, k=min(count, len(rows))):
            writer.writerow({**row, "correct": ""})
    print(f"Wrote {out}")


if __name__ == "__main__":
    show_sample()
