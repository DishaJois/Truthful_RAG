
import json
import os
from typing import Set


def load_names(path: str) -> Set[str]:
    names = set()

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            item = line.strip().lower()
            if item and not item.startswith("#") and len(item) >= 4:
                names.add(item)

    return names


def build_drugs_of(
    input_json_files: list,
    heldout_drugs_file: str,
    heldout_aliases_file: str,
    output_file: str
):
    master_drugs: Set[str] = set()

    # Check that every team drug-name file exists.
    missing_files = [
        path for path in input_json_files
        if not os.path.exists(path)
    ]

    if missing_files:
        raise FileNotFoundError(
            "Missing required drug-name files:\n" +
            "\n".join(missing_files)
        )

    # Combine drug names from all team members.
    for path in input_json_files:
        with open(path, "r", encoding="utf-8") as f:
            names = json.load(f)

        master_drugs.update(
            n.lower().strip()
            for n in names
            if isinstance(n, str) and len(n.strip()) >= 4
        )

    # Include canonical held-out names and their aliases.
    for path in [heldout_drugs_file, heldout_aliases_file]:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Missing held-out file: {path}")

        master_drugs.update(load_names(path))

    # Save the combined dictionary.
    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    sorted_drugs = sorted(master_drugs)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(sorted_drugs, f, indent=2)

    print(f"Master dictionary created: {output_file}")
    print(f"Total unique drug terms: {len(sorted_drugs)}")


if __name__ == "__main__":
    build_drugs_of(
        input_json_files=[
            "data/processed/drugs_ganavi.json",
            "data/processed/drugs_disha.json",
            "data/processed/drugs_sudarshan.json"
        ],
        heldout_drugs_file="docs/heldout_drugs.txt",
        heldout_aliases_file="docs/heldout_drug_aliases.txt",
        output_file="data/processed/drugs_of.json"
    )
