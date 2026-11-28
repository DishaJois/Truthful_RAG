import argparse
import json
import os


def recall_at_k(retrieved_ids, gold_ids):
    if not gold_ids:
        return None
    return len(set(retrieved_ids).intersection(gold_ids)) / len(set(gold_ids))


def eval_retrieval(question_path="data/eval/questions.jsonl", split="tune", k=5, w_dense=None):
    if not os.path.exists(question_path):
        raise FileNotFoundError(
            "Question set is missing. Sudarshan must build data/eval/questions.jsonl first."
        )
    try:
        from src.retrieval.retriever import retrieve
    except Exception as exc:
        raise RuntimeError("Disha's retrieval module is not available on this branch") from exc

    scores = []
    with open(question_path, encoding="utf-8-sig") as handle:
        for line in handle:
            if not line.strip():
                continue
            row = json.loads(line)
            if row.get("split", "tune") != split:
                continue
            if w_dense is None:
                retrieved = retrieve(row["question"], k=k)
            else:
                retrieved = retrieve(row["question"], k=k, w_dense=w_dense)
            ids = [item["chunk_id"] for item in retrieved]
            score = recall_at_k(ids, row.get("gold_chunk_ids", []))
            if score is not None:
                scores.append(score)
    mean = sum(scores) / len(scores) if scores else None
    print(json.dumps({"split": split, "k": k, "questions": len(scores), "recall": mean}))
    return mean


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--question-path", default="data/eval/questions.jsonl")
    parser.add_argument("--split", choices=["tune", "heldout"], default="tune")
    parser.add_argument("--k", type=int, default=5)
    args = parser.parse_args()
    eval_retrieval(args.question_path, args.split, args.k)
