import argparse
import os


def tune_hybrid(weights=(0.5, 0.6, 0.7, 0.8, 1.0), question_path="data/eval/questions.jsonl"):
    if not os.path.exists(question_path):
        raise FileNotFoundError("Question set is missing")
    from src.kg.eval_retrieval import eval_retrieval
    print("Evaluate each weight only on tuning questions:")
    for weight in weights:
        print(f"w_dense={weight}")
        eval_retrieval(question_path=question_path, split="tune", w_dense=weight)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--question-path", default="data/eval/questions.jsonl")
    args = parser.parse_args()
    tune_hybrid(question_path=args.question_path)
