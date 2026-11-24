import json
import csv

input_file = "data/processed/drugs_ganavi.json"
output_file = "data/processed/drug_dictionary_review.csv"

with open(input_file, encoding="utf-8") as f:
    drugs = json.load(f)

review_terms = {
    "serum": ("REMOVE_CANDIDATE", "Ordinary medical term"),
    "lead": ("REMOVE_CANDIDATE", "Element; not a standalone drug name"),
    "alcohol": ("REVIEW", "May refer to ethanol or a general substance"),
    "sodium": ("REVIEW", "Element; valid in compound ingredient names"),
    "metabolism": ("REMOVE_CANDIDATE", "Biological process"),
    "health": ("REMOVE_CANDIDATE", "General medical term"),
    "diarrhea": ("REMOVE_CANDIDATE", "Medical condition"),
    "headache": ("REMOVE_CANDIDATE", "Medical symptom"),
    "water": ("REMOVE_CANDIDATE", "General substance"),
    "calcium": ("REVIEW", "Can occur in valid medicinal compounds"),
    "potassium": ("REVIEW", "Can occur in valid medicinal compounds"),
    "treat": ("REMOVE_CANDIDATE", "Ordinary verb"),
}

rows = []
for term, (decision, reason) in review_terms.items():
    if term in drugs:
        rows.append({
            "term": term,
            "decision": decision,
            "reason": reason
        })

with open(output_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["term", "decision", "reason"])
    writer.writeheader()
    writer.writerows(rows)

print("Review report created:", output_file)
print("Terms found:", len(rows))
for row in rows:
    print(row["term"], "->", row["decision"])
