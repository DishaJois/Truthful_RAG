# Review Record: Ganavi 50-Triple Precision Audit

- **Artifact**: `triples_of_ganavi.csv` (50-sample stratified audit)
- **Producer / Commit**: Ganavi / `<commit-hash>`
- **Reviewer**: Disha
- **Sample Size**: 50 triples
- **Sampling Method**: Stratified by relation type across openFDA partitions 1–5

## Checks Performed
1. Validated subject entity matches primary drug of the openFDA label.
2. Validated object entity is an interacting co-occurring drug in the exact source sentence.
3. Verified relation cue phrase and ensured negation cues (e.g., "does not increase") are not misclassified.
4. Verified chunk ID resolves and follows canonical format.

## Results
- **Correct**: TBD / 50
- **Incorrect**: TBD / 50
- **Per-Relation Precision**:
  - `contraindicated_with`: TBD
  - `increases_effect_of`: TBD
  - `decreases_effect_of`: TBD
  - `interacts_with`: TBD

## Disagreements & Observations
- *None recorded yet (pending Ganavi's published audit sample).*

## Required Fixes
- *TBD*

## Disposition
- **Status**: PENDING REVIEW (Awaiting sample from Ganavi)
- **Date**: 2026-11-01
