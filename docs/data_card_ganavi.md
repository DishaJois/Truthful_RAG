# Ganavi Data Card: Knowledge Graph

## Scope

The knowledge graph is built from drug-interaction triples for the TruthfulRAG prototype.
The canonical chunk and triple files are stored in `data/processed/`; the filtered graph
input is `data/kg/triples.csv`.

## Current build artifact

The repository branch does not contain `data/processed/openfda_triples_p1_9.jsonl`.
The locally available Ganavi partitions 1-5 intermediate corpus was reprocessed using
Sudarshan's finalized held-out reference. This produced 63,993 clean chunks and
201,613 triples in the local processed outputs. `src/kg/build_kg.py` uses those outputs
when present, otherwise it falls back to the checked-in test artifacts.

## Processing

1. Load triples and normalize entity and relation text.
2. Deduplicate `(subject, relation, object, chunk_id)` rows.
3. Remove rows whose chunk ID is absent from the available chunk corpus.
4. Apply the relation allowlist and remove low-quality dictionary terms.
5. Retain at most 100,000 rows for GitHub and memory constraints.

The committed KG export contains 100,000 rows due to the configured cap after stricter
quality filtering. It was
generated after excluding held-out entities and passages; a source triple can only be
included if its chunk ID resolves to a processed passage.

## Measurements

- Triple counts: record the command output in `docs/weekly_log.md`.
- KG precision: 32% overall (16/50) on the seeded 50-row source-passage audit.
- Recall@5: not yet measurable in this branch because Disha's retriever and the
  final merged 80-question file are not present; this is not an inferred number.
- KG coverage: not yet measurable in this branch because the final merged
  80-question file is not present; this is not an inferred number.

## Aliases

`docs/heldout_drugs.txt`, `docs/heldout_drug_aliases.txt`, and
`data/processed/aliases.json` contain the finalized 20-entity set supplied by Sudarshan.
Both canonical generic names and aliases are filtered using whole-phrase matching, so
multi-word names and punctuation variants (for example `Toprol-XL`) are detected.
