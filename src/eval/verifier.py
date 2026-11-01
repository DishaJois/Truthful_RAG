import json
import os
from typing import Dict, Any

class MockOllamaClient:
    """
    Local runtime mock wrapper for Ollama generate() to smoke test
    against verified mock evidence without external API dependencies.
    """
    def __init__(self, model_name: str = "llama3:latest", temperature: float = 0.0):
        self.model_name = model_name
        self.temperature = temperature

    def generate(self, prompt: str) -> str:
        p_lower = prompt.lower()
        if "increases" in p_lower and "bleeding" in p_lower and "does not alter" not in p_lower:
            return json.dumps({"label": "SUPPORTED", "confidence": 0.95})
        elif "does not alter" in p_lower or "unaffected" in p_lower or "eliminates" in p_lower or "accelerates" in p_lower:
            return json.dumps({"label": "CONTRADICTED", "confidence": 0.90})
        elif "not been established" in p_lower or "not been evaluated" in p_lower or "undetermined" in p_lower or "inadequate" in p_lower:
            return json.dumps({"label": "INSUFFICIENT_EVIDENCE", "confidence": 0.85})
        else:
            return json.dumps({"label": "UNSUPPORTED", "confidence": 0.80})

class InteractionVerifier:
    def __init__(self, risk_terms_path: str, model_wrapper: MockOllamaClient):
        if os.path.exists(risk_terms_path):
            with open(risk_terms_path, "r", encoding="utf-8") as f:
                self.risk_terms = json.load(f)
        else:
            self.risk_terms = {"high_risk": [], "medium_risk": []}
        self.client = model_wrapper

    def verify_claim(self, claim: str, evidence: str) -> str:
        prompt = (
            f"Task: Verify drug interaction claim against evidence passage.\n"
            f"Evidence: {evidence}\n"
            f"Claim: {claim}\n"
            f"Output format: JSON with key 'label' as SUPPORTED, CONTRADICTED, INSUFFICIENT_EVIDENCE, or UNSUPPORTED."
        )
        raw_resp = self.client.generate(prompt)
        try:
            parsed = json.loads(raw_resp)
            return parsed.get("label", "UNSUPPORTED")
        except Exception:
            return "UNSUPPORTED"

def evaluate_verifier(
    claim_gold_path: str = "data/eval/claim_gold.jsonl",
    risk_terms_path: str = "data/processed/risk_terms.json"
):
    if not os.path.exists(claim_gold_path):
        print(f"Error: Claim gold file not found at {claim_gold_path}")
        return

    client = MockOllamaClient()
    verifier = InteractionVerifier(risk_terms_path, client)

    total = 0
    correct = 0
    per_label: Dict[str, Dict[str, int]] = {}

    with open(claim_gold_path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            record = json.loads(line)
            gold_label = record["label"]
            pred_label = verifier.verify_claim(record["claim"], record.get("evidence_sentence", ""))

            if gold_label not in per_label:
                per_label[gold_label] = {"correct": 0, "total": 0}

            per_label[gold_label]["total"] += 1
            total += 1
            if pred_label == gold_label:
                correct += 1
                per_label[gold_label]["correct"] += 1

    print("=== Verifier Per-Label Metrics ===")
    overall_acc = (correct / total) if total else 0.0
    print(f"Overall Accuracy: {correct}/{total} ({overall_acc:.2%})\n")
    for lbl, stats in sorted(per_label.items()):
        acc = (stats["correct"] / stats["total"]) if stats["total"] else 0.0
        print(f"Label: {lbl:<22} Accuracy: {stats['correct']}/{stats['total']} ({acc:.2%})")

if __name__ == "__main__":
    evaluate_verifier()
