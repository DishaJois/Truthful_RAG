| date | command | result | file |
|---|---|---|---|
| 2026-11-25 | `python -m src.kg.build_kg` | Built 243770 deduplicated triples from the available Ganavi fallback artifact | `data/kg/triples.csv` |
| 2026-11-25 | `python -m src.kg.kg_filter` | Retained 92453 filtered `interacts_with` triples after quality filtering | `data/kg/triples.csv` |
| 2026-11-25 | `python -m src.kg.show_sample` | Created a 50-row source-passage labeling sample | `data/kg/sample_to_label.csv` |
| 2026-11-25 | `python -m pytest -q tests/test_ganavi_kg.py` | 2 focused KG tests passed | test runner output |
| 2026-11-26 | `python -m src.kg.build_kg` | Rebuilt 170645 triples after removing held-out entities and passages using Sudarshan's finalized reference | `data/kg/triples.csv` |
| 2026-11-26 | `python -m src.kg.kg_filter` | Retained 100000 quality-filtered `interacts_with` triples (configured cap) | `data/kg/triples.csv` |
| 2026-11-26 | `python -m pytest -q tests/test_heldout_aliases.py tests/test_ganavi_kg.py` | 5 tests passed; checked alias and phrase filtering | test runner output |
| 2026-11-26 | `python src/data/openfda_process.py --tag-intermediate ...` | Reprocessed partitions 1-5 with finalized held-out names: 63993 chunks, 201613 triples; 14593 primary/tag removals | local processed outputs |
| 2026-11-26 | `python -m src.kg.build_kg` and `python -m src.kg.kg_filter` | Built from Ganavi partitions 1-5 and wrote 100000 triples (configured cap) | `data/kg/triples.csv` |
| 2026-11-26 | Question-set contribution | Added 27 questions (13 answerable, 7 unanswerable, 7 tricky), grounded in processed Ganavi chunk IDs | `data/eval/q_ganavi.jsonl` |
| 2026-11-27 | `python -m src.kg.audit_precision` | Labeled 50 source-passage samples: 16 correct, 34 incorrect; overall precision 32% | `data/kg/sample_to_label.csv` |
| 2026-11-27 | `python -m src.kg.kg_filter` | Tightened generic, duplicate-name, and dictionary filtering; retained 100000 `interacts_with` triples (configured cap) | `data/kg/triples.csv` |
| 2026-11-27 | Ganavi alias/graph implementation | Converted `aliases.json` to alias-to-generic lookup and added chunk-ID validation to graph loading | `data/processed/aliases.json`, `src/kg/graph.py` |
| 2026-11-27 | `python -m src.kg.build_kg` | Rebuilt 201613 deduplicated triples from Ganavi's local clean triple artifact | `data/kg/triples.csv` |
| 2026-11-27 | `python -m src.kg.kg_filter` | Wrote 100000 filtered `interacts_with` triples (configured cap) | `data/kg/triples.csv` |
| 2026-11-27 | `python -m src.kg.audit_precision` | 50-row audit: 16 correct, 34 incorrect; overall precision 32% | `docs/reviews/ganavi_triple_audit_review.md` |
| 2026-11-27 | `python -m pytest -q tests/test_ganavi_kg.py tests/test_ganavi_questions.py tests/test_heldout_aliases.py` | 8 Ganavi-focused tests passed | test runner output |
