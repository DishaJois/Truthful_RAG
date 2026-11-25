# Review Record: Ganavi Triple Precision Audit

- **Artifact**: `data/kg/triples.csv`
- **Labeling sample**: `data/kg/sample_to_label.csv`
- **Producer**: Ganavi
- **Reviewer**: Disha
- **Sample size**: 50 triples
- **Sampling method**: Seeded sample across the available built CSV

## Audit status

The source passages and labeled rows are required to determine precision. This file does
not publish invented precision numbers.

The current repository build has the following evidence:

- The final openFDA partitions 1-9 triple file was not present on this branch.
- A checked-in Ganavi test artifact was used as the build fallback:
  `data/processed/test_ganavi_clean_triples.csv`.
- That artifact contains `interacts_with` triples and resolves against
  `data/processed/test_ganavi_clean_chunks.jsonl`.

## Commands

```powershell
python -m src.kg.build_kg
python -m src.kg.kg_filter
python -m src.kg.show_sample
```

## Results

- **Correct**: TBD, pending source-passage labels
- **Incorrect**: TBD, pending source-passage labels
- **Per-relation precision**: TBD
- **Overall precision**: TBD

## Required fixes

Sudarshan must provide the finalized held-out aliases before alias coverage can be
completed. Disha must review the labeled 50-row sample.
