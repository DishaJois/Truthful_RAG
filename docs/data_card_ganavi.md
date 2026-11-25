# Ganavi Data Card: Knowledge Graph

## Scope

The knowledge graph is built from drug-interaction triples for the TruthfulRAG prototype.
The canonical chunk and triple files are stored in `data/processed/`; the filtered graph
input is `data/kg/triples.csv`.

## Current build artifact

The repository branch does not contain `data/processed/openfda_triples_p1_9.jsonl`.
For a reproducible local fallback, `src/kg/build_kg.py` uses
`data/processed/test_ganavi_clean_triples.csv` and verifies chunk IDs against
`data/processed/test_ganavi_clean_chunks.jsonl`.

## Processing

1. Load triples and normalize entity and relation text.
2. Deduplicate `(subject, relation, object, chunk_id)` rows.
3. Remove rows whose chunk ID is absent from the available chunk corpus.
4. Apply the relation allowlist and remove low-quality dictionary terms.
5. Retain at most 100,000 rows for GitHub and memory constraints.

## Measurements

- Triple counts: record the command output in `docs/weekly_log.md`.
- KG precision: pending human labels in `data/kg/sample_to_label.csv`.
- Recall@5: pending the shared 80-question set.
- KG coverage: pending the shared 80-question set.

## Aliases

`data/processed/aliases.json` is empty until Sudarshan publishes the finalized held-out
drug brands and aliases.
