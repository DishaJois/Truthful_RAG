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
- Ganavi's partitions 1-5 intermediate corpus is available locally; when processed,
  it is preferred over the smaller checked-in test fixture.
- The test fixture fallback is `data/processed/test_ganavi_clean_triples.csv`,
  resolved against `data/processed/test_ganavi_clean_chunks.jsonl`.
- The build excludes all canonical held-out names and aliases from both entity
  fields and source passage text. The finalized reference was supplied by Sudarshan.

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

## Remaining work

The finalized held-out names and aliases are now recorded in
`docs/heldout_drugs.txt` and `docs/heldout_drug_aliases.txt`. Disha must review the
labeled 50-row sample and enter the human judgments before precision can be reported.
