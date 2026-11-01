import json
import os
from typing import Set

def build_drugs_of(input_json_files: list, heldout_aliases_file: str, output_file: str):
    master_drugs: Set[str] = set()

    for path in input_json_files:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                names = json.load(f)
                master_drugs.update(n.lower().strip() for n in names if len(n.strip()) >= 4)
            print(f"Loaded terms from {path}")
        else:
            print(f"File not found (skipped): {path}")

    # Invariant: Keep held-out generics and aliases in dictionary for detection!
    if os.path.exists(heldout_aliases_file):
        with open(heldout_aliases_file, "r", encoding="utf-8") as f:
            for line in f:
                item = line.strip().lower()
                if item and not item.startswith("#") and len(item) >= 4:
                    master_drugs.add(item)
        print(f"Loaded heldout aliases from {heldout_aliases_file}")

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    sorted_drugs = sorted(list(master_drugs))
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(sorted_drugs, f, indent=2)

    print(f"Master dictionary frozen at {output_file} with {len(sorted_drugs)} terms.")

if __name__ == "__main__":
    build_drugs_of(
        input_json_files=[
            "data/intermediate/openfda_names_p1_9.json",
            "data/processed/drugs_ganavi.json",
            "data/processed/drugs_disha.json",
            "data/processed/drugs_sudarshan.json"
        ],
        heldout_aliases_file="docs/heldout_drug_aliases.txt",
        output_file="data/processed/drugs_of.json"
    )
