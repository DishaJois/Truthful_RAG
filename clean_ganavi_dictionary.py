import json

input_file = "data/processed/drugs_ganavi.json"
output_file = "data/processed/drugs_ganavi_clean.json"

with open(input_file, encoding="utf-8") as f:
    drugs = json.load(f)

remove_exact = {
    "serum",
    "lead",
    "metabolism",
    "health",
    "diarrhea",
    "headache",
    "water",
    "treat"
}

cleaned = [
    name for name in drugs
    if name.strip().lower() not in remove_exact
]

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(cleaned, f, indent=2, ensure_ascii=False)

print("DICTIONARY CLEANING SUMMARY")
print("-" * 40)
print("Original entries :", len(drugs))
print("Cleaned entries  :", len(cleaned))
print("Removed entries  :", len(drugs) - len(cleaned))
print("Output file      :", output_file)

print("\nRemoved exact entries:")
for name in drugs:
    if name.strip().lower() in remove_exact:
        print("-", name)
