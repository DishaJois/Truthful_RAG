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
