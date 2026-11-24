import json
import re

with open("data/processed/drugs_ganavi.json", encoding="utf-8") as f:
    drugs = json.load(f)

terms = [
    "serum", "lead", "alcohol", "sodium", "metabolism",
    "health", "diarrhea", "headache", "water", "calcium",
    "potassium", "treat"
]

print("RELATED DICTIONARY ENTRIES")
print("=" * 65)

for term in terms:
    matches = [
        name for name in drugs
        if re.search(r"\b" + re.escape(term) + r"\b", name, re.IGNORECASE)
    ]

    print(f"\n{term.upper()} — {len(matches)} matching entries")
    for name in matches[:15]:
        print("  ", name)

    if len(matches) > 15:
        print(f"  ... and {len(matches) - 15} more")
