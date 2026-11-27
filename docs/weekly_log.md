2026-11-27 | python -m src.verification.eval_verifier | accuracy 22/30 = 0.73 (first measurement, SIM_THRESHOLD=0.25) | results/verifier_accuracy.txt
2026-11-27 | python -m src.verification.sweep_sim | SIM_THRESHOLD=0.30 selected (23/30 = 0.77 vs 0.73 at 0.25) | src/verification/verifier.py
2026-11-27 | python -m src.verification.eval_verifier | accuracy 25/40 = 0.62 (40-claim gold set, SIM_THRESHOLD=0.30) | results/verifier_accuracy.txt
2026-11-27 | python -m src.verification.sweep_sim | SIM_THRESHOLD=0.30 confirmed on 40-claim gold set (25/40 = 0.62 vs 0.60 at 0.25) | src/verification/verifier.py
2026-11-27 | python -m src.verification.eval_verifier | before Day 3 fix: accuracy 25/40 = 0.62 (CONFLICTING_EVIDENCE 0/4, broad HIGH_RISK) | results/verifier_accuracy.txt
2026-11-27 | python -m src.verification.eval_verifier | after Day 3 fix: accuracy 30/40 = 0.75 (multi-passage conflict detection + trimmed HIGH_RISK + concise prompt v2) | results/verifier_accuracy.txt
2026-11-27 | python -m src.adjudication.tune_threshold | abstain threshold=0.50 selected (precision=0.50, recall=1.00, F1=0.67 vs F1=0.64 at 0.30) | src/adjudication/adjudicator.py
2026-11-27 | python -m src.repair.show_repairs | repairs checked by hand: 11 | good 6 | harmless 3 | wrong 2 | results/runs/E_*.jsonl
