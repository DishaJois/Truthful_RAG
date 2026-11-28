# Review Record: Ganavi Triple Precision Audit

- **Artifact**: `data/kg/triples.csv`
- **Labeling sample**: `data/kg/sample_to_label.csv`
- **Producer**: Ganavi
- **Reviewer**: Disha
- **Sample size**: 50 triples
- **Sampling method**: Seeded sample across the available built CSV

## Audit status

The 50-row sample is labeled against its source passage:

- Correct: 16 triples
- Incorrect: 34 triples
- Overall precision: 32%
- Per-relation precision: `interacts_with` = 32% (16/50)

The low precision is attributable mainly to the broad extraction fallback treating
class names, symptoms, generic nouns, and duplicate drug-name variants as interaction
entities. These rows should not be presented as direct, clinically specific edges.

## Commands

```powershell
python -m src.kg.build_kg
python -m src.kg.kg_filter
python -m src.kg.show_sample
python -m src.kg.audit_precision
```

## Results

- **Correct**: 16
- **Incorrect**: 34
- **Per-relation precision**: `interacts_with` = 32%
- **Overall precision**: 32%

## Remaining work

The finalized held-out names and aliases are recorded in
`docs/heldout_drugs.txt` and `docs/heldout_drug_aliases.txt`.
