import json
import os

from src.kg.graph import kg_lookup
from src.retrieval.entities import detect_entities


def kg_coverage(question_path="data/eval/questions.jsonl", split="tune"):
    if not os.path.exists(question_path):
        raise FileNotFoundError("Question set is missing")
    covered = 0
    total = 0
    with open(question_path, encoding="utf-8-sig") as handle:
        for line in handle:
            if not line.strip():
                continue
            row = json.loads(line)
            if row.get("split", "tune") != split:
                continue
            entities = detect_entities(row["question"])
            if len(entities) >= 2:
                total += 1
                if kg_lookup(entities):
                    covered += 1
    print(json.dumps({"split": split, "two_drug_questions": total, "covered": covered,
                      "coverage": covered / total if total else None}))


if __name__ == "__main__":
    kg_coverage()
