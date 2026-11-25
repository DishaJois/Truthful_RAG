| date | command | result | file |
|---|---|---|---|
| 2026-11-25 | `python -m src.kg.build_kg` | Built 243770 deduplicated triples from the available Ganavi fallback artifact | `data/kg/triples.csv` |
| 2026-11-25 | `python -m src.kg.kg_filter` | Retained 92453 filtered `interacts_with` triples after quality filtering | `data/kg/triples.csv` |
| 2026-11-25 | `python -m src.kg.show_sample` | Created a 50-row source-passage labeling sample | `data/kg/sample_to_label.csv` |
| 2026-11-25 | `python -m pytest -q tests/test_ganavi_kg.py` | 2 focused KG tests passed | test runner output |
